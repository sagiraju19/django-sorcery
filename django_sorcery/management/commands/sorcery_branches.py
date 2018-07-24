# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from ..alembic import AlembicCommand


class ShowBranches(AlembicCommand):
    help = "Display alembic branches"

    def add_arguments(self, parser):
        parser.add_argument("app_label", nargs="?", help="App label of application to limit the output to.")

    def handle(self, app_label=None, verbosity=0, **kwargs):
        verbosity = bool(verbosity - 1)
        appconfigs = [self.lookup_app(app_label)] if app_label is not None else self.sorcery_apps.values()

        for appconfig in appconfigs:
            self.stdout.write(
                self.style.SUCCESS("Branches for %s on database %s" % (appconfig.name, appconfig.db.alias))
            )
            for rev in appconfig.script.walk_revisions():
                if rev.is_branch_point:
                    self.stdout.write(
                        "%s\n%s\n",
                        rev.cmd_format(verbosity, include_branches=True),
                        "\n".join(
                            "%s -> %s"
                            % (
                                " " * len(str(rev.revision)),
                                rev_obj.cmd_format(False, include_branches=True, include_doc=verbosity),
                            )
                            for rev_obj in (self.script.get_revision(child) for child in rev.nextrev)
                        ),
                    )


Command = ShowBranches
