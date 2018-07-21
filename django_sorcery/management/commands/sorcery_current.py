# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from functools import partial

import alembic

from ..alembic import AlembicCommand


class Current(AlembicCommand):
    help = "Show current db revisions"

    def handle(self, verbosity=0, **kwargs):
        verbose = bool(verbosity - 1)

        for db in self.db_apps:
            self.stdout.write(self.style.SUCCESS("Revision for %s" % db.alias))
            config = self.configs[db]
            script = self.get_script(config)
            with alembic.context.EnvironmentContext(
                config, script, fn=partial(self.display_version, verbose=verbose, script=script)
            ) as context:
                self.run_env(context, db)

    def display_version(self, rev, context, verbose=False, script=None):
        if verbose:
            self.stdout.write("Current revision(s) for {!r}".format(context.connection.engine.url))
        for rev in script.get_all_current(rev):
            self.stdout.write(rev.cmd_format(verbose))

        return []
