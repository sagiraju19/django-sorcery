# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import sys

import alembic

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
        app = self.lookup_app(app_label)
        db = self.app_dbs.get(app)
        config = self.configs[db]
        script = self.get_script(config)
        version_path = self.app_version_paths[app]

        command_args = dict(
            autogenerate=True,
            branch_label=branch_label,
            depends_on=depends_on,
            head=head,
            rev_id=None,
            message=name,
            splice=splice,
            sql=False,
            version_path=version_path,
        )
        self.revision_context = alembic.autogenerate.RevisionContext(config, script, command_args)
        with alembic.context.EnvironmentContext(
            config,
            script,
            fn=self.retrieve_migrations,
            as_sql=False,
            template_args=self.revision_context.template_args,
            revision_context=self.revision_context,
        ) as context:
            self.run_env(context, db)

        [script for script in self.revision_context.generate_scripts()]

    def retrieve_migrations(self, rev, context):
        try:
            self.revision_context.run_autogenerate(rev, context)
        except alembic.util.exc.CommandError as ex:
            self.stderr.write(str(ex))
            sys.exit(2)

        return []


Command = MakeMigrations
