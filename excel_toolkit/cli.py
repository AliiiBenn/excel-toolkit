"""Main CLI application for Excel Toolkit."""

from importlib.metadata import version

import typer

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
def info():
    """Show system information."""
    typer.echo("Excel CLI Toolkit")
    typer.echo("Command-line toolkit for Excel data manipulation and analysis")


if __name__ == "__main__":
    app()
