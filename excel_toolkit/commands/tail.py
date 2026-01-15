"""Tail command implementation.

Displays the last N rows of a data file in various formats.
"""

from pathlib import Path
from typing import Any

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory, ExcelHandler, CSVHandler
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import (
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
    path = Path(file_path)
    factory = HandlerFactory()

    # Step 1: Validate file exists
    if not path.exists():
        typer.echo(f"File not found: {file_path}", err=True)
        raise typer.Exit(1)

    # Step 2: Get handler
    handler_result = factory.get_handler(path)
    if is_err(handler_result):
        error = unwrap_err(handler_result)
        typer.echo(f"{error}", err=True)
        typer.echo("\nSupported formats: .xlsx, .xls, .csv")
        raise typer.Exit(1)

    handler = unwrap(handler_result)

    # Step 3: Read file
    sheet_name_display = None
    if isinstance(handler, ExcelHandler):
        # Determine which sheet to read
        sheet_name = sheet
        if sheet_name is None:
            # Get first sheet name
            names_result = handler.get_sheet_names(path)
            if is_ok(names_result):
                sheets = unwrap(names_result)
                sheet_name = sheets[0] if sheets else None

        sheet_name_display = sheet_name

        # Read Excel file
        kwargs = {"sheet_name": sheet_name} if sheet_name else {}
        read_result = handler.read(path, **kwargs)

        if is_err(read_result):
            error = unwrap_err(read_result)
            typer.echo(f"Error reading Excel file: {error}", err=True)
            raise typer.Exit(1)

    elif isinstance(handler, CSVHandler):
        # Detect encoding
        encoding_result = handler.detect_encoding(path)
        encoding = unwrap(encoding_result) if is_ok(encoding_result) else "utf-8"

        # Detect delimiter
        delimiter_result = handler.detect_delimiter(path, encoding)
        delimiter = unwrap(delimiter_result) if is_ok(delimiter_result) else ","

        # Read CSV file
        read_result = handler.read(path, encoding=encoding, delimiter=delimiter)

        if is_err(read_result):
            error = unwrap_err(read_result)
            typer.echo(f"Error reading CSV file: {error}", err=True)
            raise typer.Exit(1)

    else:
        typer.echo("Unsupported file format", err=True)
        raise typer.Exit(1)

    df = unwrap(read_result)

    # Step 4: Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        # Still show column info if requested
        if show_columns:
            display_column_types(df)
        raise typer.Exit(0)

    # Step 5: Display file info if columns requested
    if show_columns:
        file_info = format_file_info(
            str(path), sheet=sheet_name_display, total_rows=len(df), total_cols=len(df.columns)
        )
        typer.echo(file_info)
        display_column_types(df)
        raise typer.Exit(0)

    # Step 6: Get last N rows
    tail_rows = min(rows, len(df))
    df_tail = df.tail(tail_rows)

    # Step 7: Display based on format
    if format == "table":
        # Limit columns if requested
        if max_columns and len(df_tail.columns) > max_columns:
            df_tail = df_tail.iloc[:, :max_columns]

        display_table(df_tail)

    elif format == "csv":
        display_csv(df_tail)

    elif format == "json":
        display_json(df_tail)

    else:
        typer.echo(f"Unknown format: {format}", err=True)
        typer.echo("Supported formats: table, csv, json")
        raise typer.Exit(1)


# Create CLI app for this command
app = typer.Typer(help="Display the last N rows of a data file")

# Register the command
app.command()(tail)
