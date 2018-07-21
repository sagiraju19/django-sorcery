# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import os

from ..alembic import AlembicCommand


class ShowHeads(AlembicCommand):
    help = "Display revision heads"

    def handle(self, verbosity=0, **kwargs):
        verbosity = bool(verbosity - 1)

        for db in self.db_apps:
            self.stdout.write(self.style.SUCCESS("Heads for %s" % db.alias))
            config = self.configs[db]
            script = self.get_script(config)
            for rev in script.get_revisions("heads"):
                app = self.config.version_locations.get(os.path.dirname(rev.path))
                if verbosity:
                    self.stdout.write(
                        "".join(
                            [
                                "[",
                                app.label,
                                "]\n",
                                rev.cmd_format(verbosity, include_branches=True, tree_indicators=False),
                            ]
                        )
                    )
                else:
                    self.stdout.write(
                        "".join(
                            [
                                rev.cmd_format(verbosity, include_branches=True, tree_indicators=False),
                                " <",
                                app.label,
                                "> ",
                            ]
                        )
                    )


Command = ShowHeads
