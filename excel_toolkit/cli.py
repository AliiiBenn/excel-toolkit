"""Main CLI application for Excel Toolkit."""

from importlib.metadata import version

import typer

from excel_toolkit.commands.info import info as info_command
from excel_toolkit.commands.head import head as head_command
from excel_toolkit.commands.filter import filter as filter_command
from excel_toolkit.commands.sort import sort as sort_command
from excel_toolkit.commands.stats import stats as stats_command

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


if __name__ == "__main__":
    app()
