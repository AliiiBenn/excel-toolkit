"""Tail command implementation.

Displays the last N rows of a data file in various formats.
"""

from pathlib import Path

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import (
    read_data_file,
    display_table,
    display_csv,
    display_json,
    display_column_types,
    format_file_info,
)


def tail(
    file_path: str,
    rows: int = typer.Option(5, "--rows", "-n", help="Number of rows to display"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
    show_columns: bool = typer.Option(False, "--show-columns", "-c", help="Show column information"),
    max_columns: int | None = typer.Option(None, "--max-columns", help="Limit columns displayed"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, csv, json)"),
) -> None:
    """Display the last N rows of a data file.

    Shows the end of a file to quickly inspect its contents.
    Supports Excel and CSV files with multiple output formats.

    Args:
        file_path: Path to the file
        rows: Number of rows to display (default: 5)
        sheet: Sheet name for Excel files (default: first sheet)
        show_columns: Show column names and types
        max_columns: Maximum number of columns to display
        format: Output format: table, csv, or json

    Raises:
        typer.Exit: If file cannot be read
    """
    # 1. Read file
    df = read_data_file(file_path, sheet)

    # 2. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 3. Limit columns if requested
    if max_columns and len(df.columns) > max_columns:
        df = df.iloc[:, :max_columns]

    # 4. Get last N rows
    df_tail = df.tail(rows)

    # 5. Display file info
    path = Path(file_path)
    format_file_info(path, len(df), len(df.columns))

    # 6. Show column information if requested
    if show_columns:
        display_column_types(df)

    # 7. Display data based on format
    if format == "table":
        display_table(df_tail)
    elif format == "csv":
        display_csv(df_tail)
    elif format == "json":
        display_json(df_tail)


# Create CLI app for this command
app = typer.Typer(help="Display the last N rows of a data file")

# Register the command
app.command()(tail)
