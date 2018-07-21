# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from .. import NamespacedCommand
from .sorcery_branches import ShowBranches
from .sorcery_createall import CreateAll
from .sorcery_current import Current
from .sorcery_dropall import DropAll
from .sorcery_heads import ShowHeads
from .sorcery_makemigrations import MakeMigrations
from .sorcery_migrate import Migrate
from .sorcery_showmigrations import ShowMigrations


class Command(NamespacedCommand):
    help = "django-sorcery management commands"

    createall = CreateAll
    dropall = DropAll
    showmigrations = ShowMigrations
    branches = ShowBranches
    makemigrations = MakeMigrations
    heads = ShowHeads
    migrate = Migrate
    current = Current

    class Meta:
        namespace = "sorcery"
