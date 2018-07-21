# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import os
import sys

import alembic
import alembic.config

from django.apps import apps
from django.core.management.base import BaseCommand

import django_sorcery.db.alembic
from django_sorcery.db import SQLAlchemy, signals
from django_sorcery.db.alembic import include_object, include_symbol, process_revision_directives


SORCERY_ALEMBIC_CONFIG_FOLDER = os.path.dirname(django_sorcery.db.alembic.__file__)


class AlembicCommand(BaseCommand):
    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(AlembicCommand, self).__init__(stdout, stderr, no_color)

        self.app_version_paths = {}
        self.version_path_app = {}
        self.app_dbs = {}
        self.db_apps = {}
        self.configs = {}
        for app in apps.app_configs.values():
            db = self._get_app_db(app)
            if db is not None:
                self.app_version_paths[app] = self.get_app_version_path(app)
                self.version_path_app[self.get_app_version_path(app)] = app
                self.app_dbs[app] = db
                self.db_apps.setdefault(db, []).append(app)
                config = alembic.config.Config()
                config.set_main_option("script_location", SORCERY_ALEMBIC_CONFIG_FOLDER)
                signals.alembic_config_created.send(config)
                self.configs[db] = config

        for db, config in self.configs.items():
            config.set_main_option(
                "version_locations", " ".join([self.app_version_paths[app] for app in self.db_apps[db]])
            )

        # self.script = alembic.script.ScriptDirectory.from_config(self.config)

    def get_script(self, config):
        return alembic.script.ScriptDirectory.from_config(config)

    def lookup_app(self, app_label):
        try:
            app = apps.get_app_config(app_label)
        except LookupError:
            self.stderr.write("App '%s' could not be found. Is it in INSTALLED_APPS?" % app_label)
            sys.exit(2)

        db = self.app_dbs.get(app)
        if not db:
            self.stderr.write("App '%s' is missing magic. Is it a sorcery app?" % app_label)
            sys.exit(2)

        return app

    def get_app_version_path(self, app):
        return os.path.join(app.path, "migrations")

    def _get_app_db(self, app):
        models_module = getattr(app, "models_module", None)
        if models_module is None:
            return

        if hasattr(models_module, "db") and isinstance(models_module.db, SQLAlchemy):
            return models_module.db

        for val in vars(models_module).values():
            if isinstance(val, SQLAlchemy):
                return val

    def app_dbs(self, app):
        return self

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

    def run_env(self, context, db):
        if context.is_offline_mode():
            self.run_migrations_offline(context, db)
        else:
            self.run_migrations_online(context, db)

    def run_migrations_online(self, context, db):
        with db.engine.connect() as connection:
            context.configure(connection=connection, target_metadata=db.metadata, **self.get_common_config(context))

            with context.begin_transaction():
                context.run_migrations()

    def run_migrations_offline(self, context, db):
        context.configure(
            url=db.url, literal_binds=True, target_metadata=db.metadata, **self.get_common_config(context)
        )
        with context.begin_transaction():
            context.run_migrations()
