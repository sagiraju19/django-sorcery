# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from ..alembic import AlembicCommand


class ShowBranches(AlembicCommand):
    help = "Display alembic branches"

    def handle(self, verbosity=0, **kwargs):
        verbosity = bool(verbosity - 1)

        for db, config in self.configs.items():
            self.stdout.write(self.style.SUCCESS("Branches for %s" % db.alias))
            script = self.get_script(config)
            for rev in script.walk_revisions():
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
