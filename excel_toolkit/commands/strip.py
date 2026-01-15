"""Strip command implementation.

Remove leading and trailing whitespace from cell values.
"""

from pathlib import Path
from typing import Any

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory, ExcelHandler, CSVHandler
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import display_table


def strip(
    file_path: str = typer.Argument(..., help="Path to input file"),
    columns: str | None = typer.Option(None, "--columns", "-c", help="Columns to strip (comma-separated, default: all string columns)"),
    left: bool = typer.Option(True, "--left", help="Strip leading whitespace (default: True)"),
    right: bool = typer.Option(True, "--right", help="Strip trailing whitespace (default: True)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Strip leading and trailing whitespace from cell values.

    Clean text data by removing extra spaces from the beginning and end of cell values.
    By default, strips all whitespace from both sides of all string columns.

    Examples:
        xl strip data.xlsx --output cleaned.xlsx
        xl strip data.csv --columns "Name,Email" --output cleaned.csv
        xl strip data.xlsx --left --right --output cleaned.xlsx
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
        raise typer.Exit(1)

    handler = unwrap(handler_result)

    # Step 3: Read file
    if isinstance(handler, ExcelHandler):
        sheet_name = sheet
        kwargs = {"sheet_name": sheet_name} if sheet_name else {}
        read_result = handler.read(path, **kwargs)
    elif isinstance(handler, CSVHandler):
        # Auto-detect encoding and delimiter
        encoding_result = handler.detect_encoding(path)
        encoding = unwrap(encoding_result) if is_ok(encoding_result) else "utf-8"

        delimiter_result = handler.detect_delimiter(path, encoding)
        delimiter = unwrap(delimiter_result) if is_ok(delimiter_result) else ","

        read_result = handler.read(path, encoding=encoding, delimiter=delimiter)
    else:
        typer.echo("Unsupported handler type", err=True)
        raise typer.Exit(1)

    if is_err(read_result):
        error = unwrap_err(read_result)
        typer.echo(f"Error reading file: {error}", err=True)
        raise typer.Exit(1)

    df = unwrap(read_result)
    original_count = len(df)

    # Step 4: Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # Step 5: Determine columns to process
    if columns:
        column_list = [c.strip() for c in columns.split(",")]
        # Validate columns exist
        missing_cols = [c for c in column_list if c not in df.columns]
        if missing_cols:
            typer.echo(f"Error: Columns not found: {', '.join(missing_cols)}", err=True)
            typer.echo(f"Available columns: {', '.join(df.columns)}")
            raise typer.Exit(1)
    else:
        # Default: all string columns
        column_list = df.select_dtypes(include=['object']).columns.tolist()

    # Step 6: Strip whitespace from specified columns
    cells_modified = 0

    for col in column_list:
        if col in df.columns:
            # Check if column is string type
            if df[col].dtype == 'object':
                # Count cells with leading/trailing whitespace before stripping
                if left and right:
                    before = df[col].str.strip().ne(df[col]).sum()
                    df[col] = df[col].str.strip()
                    cells_modified += before
                elif left:
                    before = df[col].str.lstrip().ne(df[col]).sum()
                    df[col] = df[col].str.lstrip()
                    cells_modified += before
                elif right:
                    before = df[col].str.rstrip().ne(df[col]).sum()
                    df[col] = df[col].str.rstrip()
                    cells_modified += before

    # Step 7: Display summary
    typer.echo(f"Total rows: {original_count}")
    typer.echo(f"Columns processed: {len(column_list)}")
    if columns:
        typer.echo(f"Specified columns: {', '.join(column_list)}")
    else:
        typer.echo(f"All string columns: {', '.join(column_list)}")
    typer.echo(f"Cells modified: {cells_modified}")
    typer.echo(f"Strip mode: {'left' if left else ''}{'/' if left and right else ''}{'right' if right else ''}")
    typer.echo("")

    # Step 8: Write output or display
    if output:
        output_path = Path(output)
        write_result = factory.write_file(df, output_path)
        if is_err(write_result):
            error = unwrap_err(write_result)
            typer.echo(f"Error writing file: {error}", err=True)
            raise typer.Exit(1)
        typer.echo(f"Written to: {output}")
    else:
        # Display preview
        display_table(df.head(20))
        if original_count > 20:
            typer.echo(f"\n... and {original_count - 20} more rows")


# Create CLI app for this command
app = typer.Typer(help="Strip leading and trailing whitespace from cell values")

# Register the command
app.command()(strip)
