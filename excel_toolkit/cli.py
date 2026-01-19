"""Main CLI application for Excel Toolkit."""

from importlib.metadata import version

import typer

# Configure warnings first (before importing other modules)
from excel_toolkit.warnings_config import *  # noqa: F401, F403

from excel_toolkit.commands.info import info as info_command
from excel_toolkit.commands.head import head as head_command
from excel_toolkit.commands.filter import filter as filter_command
from excel_toolkit.commands.sort import sort as sort_command
from excel_toolkit.commands.stats import stats as stats_command
from excel_toolkit.commands.validate import validate as validate_command
from excel_toolkit.commands.clean import clean as clean_command
from excel_toolkit.commands.select import select as select_command
from excel_toolkit.commands.dedupe import dedupe as dedupe_command
from excel_toolkit.commands.fill import fill as fill_command
from excel_toolkit.commands.group import group as group_command
from excel_toolkit.commands.unique import unique as unique_command
from excel_toolkit.commands.transform import transform as transform_command
from excel_toolkit.commands.rename import rename as rename_command
from excel_toolkit.commands.search import search as search_command
from excel_toolkit.commands.convert import convert as convert_command
from excel_toolkit.commands.merge import merge as merge_command
from excel_toolkit.commands.join import join as join_command
from excel_toolkit.commands.tail import tail as tail_command
from excel_toolkit.commands.count import count as count_command
from excel_toolkit.commands.append import append as append_command
from excel_toolkit.commands.strip import strip as strip_command
from excel_toolkit.commands.export import export as export_command
from excel_toolkit.commands.extract import extract as extract_command
from excel_toolkit.commands.calculate import calculate as calculate_command
from excel_toolkit.commands.pivot import pivot as pivot_command
from excel_toolkit.commands.aggregate import aggregate as aggregate_command
from excel_toolkit.commands.compare import compare as compare_command

try:
    __version__ = version("excel-toolkit")
except Exception:
    __version__ = "0.1.0-dev"

app = typer.Typer(
    help="Excel CLI Toolkit - Command-line toolkit for Excel data manipulation and analysis"
)


@app.command()
def version():
    """Show version information."""
    typer.echo(f"Excel CLI Toolkit v{__version__}")


@app.command()
def sysinfo():
    """Show system information."""
    typer.echo("Excel CLI Toolkit")
    typer.echo("Command-line toolkit for Excel data manipulation and analysis")
    typer.echo(f"Version: {__version__}")
    typer.echo(f"Python: 3.14")


# Register commands from commands module
app.command()(info_command)
app.command()(head_command)
app.command()(filter_command)
app.command()(sort_command)
app.command()(stats_command)
app.command()(validate_command)
app.command()(clean_command)
app.command()(select_command)
app.command()(dedupe_command)
app.command()(fill_command)
app.command()(group_command)
app.command()(unique_command)
app.command()(transform_command)
app.command()(rename_command)
app.command()(search_command)
app.command()(convert_command)
app.command()(merge_command)
app.command()(join_command)
app.command()(tail_command)
app.command()(count_command)
app.command()(append_command)
app.command()(strip_command)
app.command()(export_command)
app.command()(extract_command)
app.command()(calculate_command)
app.command()(pivot_command)
app.command()(aggregate_command)
app.command()(compare_command)


if __name__ == "__main__":
    app()
