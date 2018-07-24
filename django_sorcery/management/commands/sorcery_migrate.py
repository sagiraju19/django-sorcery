# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from functools import partial

import alembic

from ..alembic import AlembicCommand


class Migrate(AlembicCommand):
    help = "Apply migration revisions"

    def add_arguments(self, parser):
        parser.add_argument("app_label", nargs="?", help="App label of application to limit the output to.")
        parser.add_argument(
            "-r",
            "--revision",
            default="head",
            help="Database state will be brought to the state after that "
            'migration. Use the name "base" to unapply all migrations.',
        )

    def handle(self, app_label=None, revision=None, **kwargs):
        appconfigs = [self.lookup_app(app_label)] if app_label is not None else self.sorcery_apps.values()

        for appconfig in sorted(appconfigs, key=lambda appconfig: appconfig.name):
            self.stdout.write(
                self.style.SUCCESS("Running migrations for %s on database %s" % (appconfig.name, appconfig.db.alias))
            )
            self.migrate(appconfig, revision)

    def migrate(self, appconfig, revision, starting_rev=None):
        if "head" not in revision:
            with alembic.context.EnvironmentContext(
                appconfig.config,
                appconfig.script,
                fn=partial(self.downgrade, appconfig=appconfig, revision=revision),
                as_sql=False,
                starting_rev=starting_rev,
                destination_rev=revision,
            ) as context:
                self.run_env(context, appconfig)

        with alembic.context.EnvironmentContext(
            appconfig.config,
            appconfig.script,
            fn=partial(self.upgrade, appconfig=appconfig, revision=revision),
            as_sql=False,
            starting_rev=starting_rev,
            destination_rev=revision,
        ) as context:
            self.run_env(context, appconfig)

    def downgrade(self, rev, context, appconfig, revision):
        return appconfig.script._downgrade_revs(revision, rev)

    def upgrade(self, rev, context, appconfig, revision):
        return appconfig.script._upgrade_revs(revision, rev)
