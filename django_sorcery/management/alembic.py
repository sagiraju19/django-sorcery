# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import os
import sys
from collections import OrderedDict, namedtuple

import alembic
import alembic.config

from django.apps import apps
from django.core.management.base import BaseCommand
from django.utils.functional import cached_property

import django_sorcery.db.alembic
from django_sorcery.db import databases, signals
from django_sorcery.db.alembic import include_object, include_symbol, process_revision_directives


SORCERY_ALEMBIC_CONFIG_FOLDER = os.path.dirname(django_sorcery.db.alembic.__file__)


AlembicAppConfig = namedtuple("AlembicAppConfig", ["name", "config", "script", "db", "app", "version_path"])


class AlembicCommand(BaseCommand):
    @cached_property
    def sorcery_apps(self):
        configs = OrderedDict()
        for db in databases.values():
            table_class_map = {
                model.__table__: model
                for model in db.Model._decl_class_registry.values()
                if hasattr(model, "__table__")
            }
            for table in db.metadata.sorted_tables:
                model = table_class_map.get(table)
                if model:
                    app = apps.get_containing_app_config(model.__module__)
                    if app.label not in configs:
                        config = self.get_app_config(app)
                        configs[app.label] = AlembicAppConfig(
                            name=app.label,
                            config=config,
                            db=db,
                            script=self.get_config_script(config),
                            version_path=self.get_app_version_path(app),
                            app=app,
                        )
        return configs

    def get_app_config(self, app):
        config = alembic.config.Config()
        config.set_main_option("script_location", SORCERY_ALEMBIC_CONFIG_FOLDER)
        config.set_main_option("version_locations", self.get_app_version_path(app))
        config.set_main_option("version_table", "alembic_version_%s" % app.label.lower())
        signals.alembic_config_created.send(config)
        return config

    def get_config_script(self, config):
        return alembic.script.ScriptDirectory.from_config(config)

    def lookup_app(self, app_label):
        try:
            apps.get_app_config(app_label)
        except LookupError:
            self.stderr.write("App '%s' could not be found. Is it in INSTALLED_APPS?" % app_label)
            sys.exit(2)

        if app_label not in self.sorcery_apps:
            self.stderr.write("App '%s' is missing magic. Is it a sorcery app?" % app_label)
            sys.exit(2)

        return self.sorcery_apps[app_label]

    def get_app_version_path(self, app):
        return os.path.join(app.path, "migrations")

    def get_common_config(self, context):
        config = context.config
        return dict(
            include_object=include_object,
            include_symbol=include_symbol,
            process_revision_directives=process_revision_directives,
            # TODO: read these from django db settings
            version_table=config.get_main_option("version_table") or "alembic_version",
            version_table_schema=config.get_main_option("version_table_schema"),
        )

    def run_env(self, context, appconfig):
        if context.is_offline_mode():
            self.run_migrations_offline(context, appconfig)
        else:
            self.run_migrations_online(context, appconfig)

    def run_migrations_online(self, context, appconfig):
        with appconfig.db.engine.connect() as connection:
            context.configure(
                connection=connection, target_metadata=appconfig.db.metadata, **self.get_common_config(context)
            )

            with context.begin_transaction():
                context.run_migrations()

    def run_migrations_offline(self, context, appconfig):
        context.configure(
            url=appconfig.db.url,
            literal_binds=True,
            target_metadata=appconfig.db.metadata,
            **self.get_common_config(context)
        )
        with context.begin_transaction():
            context.run_migrations()
