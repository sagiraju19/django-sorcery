# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import sys
from functools import partial

import alembic

from django_sorcery.db import databases

from ..alembic import AlembicCommand


class Migrate(AlembicCommand):
    help = "Apply migration revisions"

    def add_arguments(self, parser):
        parser.add_argument("database", nargs="?", help="Specify the database to apply migrations for.")
        parser.add_argument(
            "-r",
            "--revision",
            default="head",
            help="Database state will be brought to the state after that "
            'migration. Use the name "base" to unapply all migrations.',
        )

    def handle(self, database=None, revision=None, verbosity=0, **kwargs):
        try:
            dbs = [databases.get(database)] if database else databases.values()
        except LookupError:
            self.stderr.write("Database '%s' could not be found." % database)
            sys.exit(2)

        for db in dbs:
            self.stdout.write(self.style.SUCCESS("Running migrations for %s" % db.alias))
            config = self.configs[db]
            script = self.get_script(config)
            self.migrate(db, config, script, revision)

    def migrate(self, db, config, script, revision, starting_rev=None):
        if "head" not in revision:
            with alembic.context.EnvironmentContext(
                config,
                script,
                fn=partial(self.downgrade, script=script, revision=revision),
                as_sql=False,
                starting_rev=starting_rev,
                destination_rev=revision,
            ) as context:
                self.run_env(context, db)

        with alembic.context.EnvironmentContext(
            config,
            script,
            fn=partial(self.upgrade, script=script, revision=revision),
            as_sql=False,
            starting_rev=starting_rev,
            destination_rev=revision,
        ) as context:
            self.run_env(context, db)

    def downgrade(self, rev, context, script, revision):
        return script._downgrade_revs(revision, rev)

    def upgrade(self, rev, context, script, revision):
        return script._upgrade_revs(revision, rev)
