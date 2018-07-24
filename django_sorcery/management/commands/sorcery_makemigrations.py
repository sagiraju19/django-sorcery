# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import sys
from functools import partial

import alembic

from django_sorcery.db import signals

from ..alembic import AlembicCommand


class MakeMigrations(AlembicCommand):
    help = "Create a migration revision"

    def add_arguments(self, parser):
        parser.add_argument(
            "args", metavar="app_label", nargs=1, help="Specify the app label to create migrations for."
        )
        parser.add_argument(
            "-n", "--name", action="store", dest="name", default=None, help="Use this name for migration file(s)."
        )

    def handle(self, app_label, name=None, head=None, splice=None, branch_label=None, depends_on=None, **kwargs):
        appconfig = self.lookup_app(app_label)

        @signals.alembic_include_object.connect
        def include_object(obj=None, name=None, type_=None, reflected=None, compare_to=None):
            if type_ == "table" and "alembic" in name:
                return False

            return True

        command_args = dict(
            autogenerate=True,
            branch_label=branch_label,
            depends_on=depends_on,
            head=head,
            rev_id=None,
            message=name,
            splice=splice,
            sql=False,
            version_path=appconfig.version_path,
        )
        self.revision_context = alembic.autogenerate.RevisionContext(appconfig.config, appconfig.script, command_args)
        with alembic.context.EnvironmentContext(
            appconfig.config,
            appconfig.script,
            fn=partial(self.retrieve_migrations, appconfig=appconfig),
            as_sql=False,
            template_args=self.revision_context.template_args,
            revision_context=self.revision_context,
        ) as context:
            self.run_env(context, appconfig)

        [script for script in self.revision_context.generate_scripts()]

    def retrieve_migrations(self, rev, context, appconfig=None):
        try:
            self.revision_context.run_autogenerate(rev, context)
        except alembic.util.exc.CommandError as ex:
            self.stderr.write(str(ex))
            sys.exit(2)

        return []


Command = MakeMigrations
