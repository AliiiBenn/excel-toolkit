"""Commands module for Excel CLI Toolkit.

This module contains all CLI commands for the toolkit.
Each command is a separate module that can be imported and tested.
"""

# Command imports
from excel_toolkit.commands.info import info, app as info_app
from excel_toolkit.commands.head import head, app as head_app
from excel_toolkit.commands.filter import filter, app as filter_app
from excel_toolkit.commands.sort import sort, app as sort_app
from excel_toolkit.commands.stats import stats, app as stats_app
from excel_toolkit.commands.validate import validate, app as validate_app
from excel_toolkit.commands.clean import clean, app as clean_app
from excel_toolkit.commands.select import select, app as select_app
from excel_toolkit.commands.dedupe import dedupe, app as dedupe_app
from excel_toolkit.commands.fill import fill, app as fill_app
from excel_toolkit.commands.group import group, app as group_app
from excel_toolkit.commands.unique import unique, app as unique_app
from excel_toolkit.commands.transform import transform, app as transform_app
from excel_toolkit.commands.rename import rename, app as rename_app
from excel_toolkit.commands.search import search, app as search_app
from excel_toolkit.commands.convert import convert, app as convert_app
from excel_toolkit.commands.merge import merge, app as merge_app
from excel_toolkit.commands.join import join, app as join_app
from excel_toolkit.commands.tail import tail, app as tail_app
from excel_toolkit.commands.count import count, app as count_app
from excel_toolkit.commands.append import append, app as append_app
from excel_toolkit.commands.strip import strip, app as strip_app
from excel_toolkit.commands.export import export, app as export_app

__all__ = [
    "info",
    "info_app",
    "head",
    "head_app",
    "filter",
    "filter_app",
    "sort",
    "sort_app",
    "stats",
    "stats_app",
    "validate",
    "validate_app",
    "clean",
    "clean_app",
    "select",
    "select_app",
    "dedupe",
    "dedupe_app",
    "fill",
    "fill_app",
    "group",
    "group_app",
    "unique",
    "unique_app",
    "transform",
    "transform_app",
    "rename",
    "rename_app",
    "search",
    "search_app",
    "convert",
    "convert_app",
    "merge",
    "merge_app",
    "join",
    "join_app",
    "tail",
    "tail_app",
    "count",
    "count_app",
    "append",
    "append_app",
    "strip",
    "strip_app",
    "export",
    "export_app",
]
