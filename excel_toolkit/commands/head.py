"""Head command implementation.

Displays the first N rows of a data file in various formats.
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


def head(
    file_path: str,
    rows: int = typer.Option(5, "--rows", "-n", help="Number of rows to display"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
    show_columns: bool = typer.Option(False, "--show-columns", "-c", help="Show column information"),
    max_columns: int | None = typer.Option(None, "--max-columns", help="Limit columns displayed"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, csv, json)"),
) -> None:
    """Display the first N rows of a data file.

    Shows the beginning of a file to quickly inspect its contents.
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
    if isinstance(handler, ExcelHandler):
        # Determine which sheet to read
        sheet_name = sheet
        if sheet_name is None:
            # Get first sheet name
            names_result = handler.get_sheet_names(path)
            if is_ok(names_result):
                sheets = unwrap(names_result)
                sheet_name = sheets[0] if sheets else None

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
        typer.echo(f"Unsupported handler type", err=True)
        raise typer.Exit(1)

    df = unwrap(read_result)

    # Step 4: Handle empty DataFrame
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # Step 5: Get first N rows
    df_head = df.head(rows)

    # Step 6: Display file info
    sheet_name_display = sheet_name if isinstance(handler, ExcelHandler) else None
    file_info = format_file_info(
        str(path), sheet=sheet_name_display, total_rows=len(df), total_cols=len(df.columns)
    )
    typer.echo(file_info)

    # Step 7: Show column info if requested
    if show_columns:
        display_column_types(df)
        typer.echo("")  # Empty line before data

    # Step 8: Display data in requested format
    try:
        if format == "table":
            display_table(df_head, max_columns=max_columns)
        elif format == "csv":
            display_csv(df_head)
        elif format == "json":
            display_json(df_head)
        else:
            typer.echo(f"Unknown format: {format}", err=True)
            typer.echo("Supported formats: table, csv, json")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error displaying data: {str(e)}", err=True)
        raise typer.Exit(1)


# Create CLI app for this command (can be used standalone or imported)
app = typer.Typer(help="Display the first N rows of a data file")

# Register the command
app.command()(head)
