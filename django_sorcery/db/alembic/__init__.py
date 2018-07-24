# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django_sorcery.db import signals


@signals.alembic_config_created.connect
def setup_config(config):
    config.set_section_option("loggers", "keys", "root,sqlalchemy,alembic")
    config.set_section_option("handlers", "keys", "console")
    config.set_section_option("formatters", "keys", "generic")
    config.set_section_option("logger_root", "level", "WARN")
    config.set_section_option("logger_root", "handlers", "console")
    config.set_section_option("logger_sqlalchemy", "level", "WARN")
    config.set_section_option("logger_sqlalchemy", "qualname", "sqlalchemy.engine")
    config.set_section_option("logger_alembic", "level", "INFO")
    config.set_section_option("logger_alembic", "qualname", "alembic")
    config.set_section_option("handler_console", "class", "StreamHandler")
    config.set_section_option("handler_console", "formatter", "generic")


def include_symbol(tablename, schema):
    results = signals.alembic_include_symbol.send(tablename, schema=schema)
    if len(results) > 0:
        return all([res[1] for res in results])

    return True


def include_object(obj, name, type_, reflected, compare_to):
    results = signals.alembic_include_object.send(
        obj, name=name, type_=type_, reflected=reflected, compare_to=compare_to
    )
    if len(results) > 0:
        return all([res[1] for res in results])

    return True


def process_revision_directives(context, revision, directives):
    signals.alembic_process_revision_directives.send(context, revision=revision, directives=directives)
