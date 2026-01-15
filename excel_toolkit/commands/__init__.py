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
]
