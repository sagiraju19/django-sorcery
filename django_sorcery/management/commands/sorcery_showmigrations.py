# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import os
import sys

from ..alembic import AlembicCommand


class ShowMigrations(AlembicCommand):
    help = "Display alembic revisions"

    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--rev_range",
            action="store",
            dest="rev_range",
            default=None,
            help="Specify a revision range; format is [start]:[end].",
        )

    def handle(self, rev_range=None, verbosity=0, **kwargs):
        verbose = bool(verbosity - 1)

        if rev_range is not None:
            if ":" not in rev_range:
                self.stderr.write("History range requires [start]:[end], [start]:, or :[end]")
                sys.exit(2)
            base, head = rev_range.strip().split(":")
        else:
            base = head = None

        self.print_history(verbose, base, head)

    def print_history(self, verbose, base, head):
        for db, config in self.configs.items():
            self.stdout.write(self.style.SUCCESS("Migrations for %s" % db.alias))
            script = self.get_script(config)
            for rev in script.walk_revisions(base=base or "base", head=head or "heads"):
                app = self.version_path_app.get(os.path.dirname(rev.path))
                if verbose:
                    self.stdout.write(
                        "".join(
                            [
                                "App: ",
                                app.label,
                                "\n",
                                rev.cmd_format(
                                    verbose=verbose, include_branches=True, include_doc=True, include_parents=True
                                ),
                            ]
                        )
                    )
                else:
                    self.stdout.write(
                        "".join(
                            [
                                rev.cmd_format(
                                    verbose=verbose, include_branches=True, include_doc=True, include_parents=True
                                ),
                                " [",
                                app.label,
                                "] ",
                            ]
                        )
                    )


Command = ShowMigrations
