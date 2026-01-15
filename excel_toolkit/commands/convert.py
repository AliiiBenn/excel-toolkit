"""Convert command implementation.

Convert between different file formats.
"""

from pathlib import Path
from typing import Any

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory, ExcelHandler, CSVHandler
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err


def convert(
    file_path: str = typer.Argument(..., help="Path to input file"),
    output: str = typer.Option(..., "--output", "-o", help="Output file path"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files (for multi-sheet files)"),
) -> None:
    """Convert between different file formats.

    Convert files between Excel, CSV, and JSON formats while preserving data types and structure.

    Examples:
        xl convert data.xlsx --output data.csv
        xl convert data.csv --output data.xlsx
        xl convert data.xlsx --output data.json
        xl convert multi_sheet.xlsx --sheet "Sheet2" --output sheet2.csv
    """
    input_path = Path(file_path)
    output_path = Path(output)
    factory = HandlerFactory()

    # Step 1: Validate input file exists
    if not input_path.exists():
        typer.echo(f"File not found: {file_path}", err=True)
        raise typer.Exit(1)

    # Step 2: Validate output format
    output_ext = output_path.suffix.lower()
    supported_formats = {'.xlsx', '.xlsm', '.csv', '.json'}

    if output_ext not in supported_formats:
        typer.echo(f"Error: Unsupported output format: {output_ext}", err=True)
        typer.echo(f"Supported formats: {', '.join(sorted(supported_formats))}")
        raise typer.Exit(1)

    # Step 3: Get handler for input file
    handler_result = factory.get_handler(input_path)
    if is_err(handler_result):
        error = unwrap_err(handler_result)
        typer.echo(f"{error}", err=True)
        raise typer.Exit(1)

    handler = unwrap(handler_result)

    # Step 4: Read input file
    if isinstance(handler, ExcelHandler):
        sheet_name = sheet
        kwargs = {"sheet_name": sheet_name} if sheet_name else {}
        read_result = handler.read(input_path, **kwargs)
    elif isinstance(handler, CSVHandler):
        # Auto-detect encoding and delimiter
        encoding_result = handler.detect_encoding(input_path)
        encoding = unwrap(encoding_result) if is_ok(encoding_result) else "utf-8"

        delimiter_result = handler.detect_delimiter(input_path, encoding)
        delimiter = unwrap(delimiter_result) if is_ok(delimiter_result) else ","

        read_result = handler.read(input_path, encoding=encoding, delimiter=delimiter)
    else:
        typer.echo("Unsupported handler type", err=True)
        raise typer.Exit(1)

    if is_err(read_result):
        error = unwrap_err(read_result)
        typer.echo(f"Error reading file: {error}", err=True)
        raise typer.Exit(1)

    df = unwrap(read_result)

    # Step 5: Handle empty file
    if df.empty:
        typer.echo("Warning: Input file is empty (no data rows)", err=True)

    # Step 6: Write to output format
    write_result = factory.write_file(df, output_path)
    if is_err(write_result):
        error = unwrap_err(write_result)
        typer.echo(f"Error writing file: {error}", err=True)
        raise typer.Exit(1)

    # Step 7: Display summary
    input_format = input_path.suffix.lower()
    typer.echo(f"Input format: {input_format}")
    typer.echo(f"Output format: {output_ext}")
    typer.echo(f"Rows: {len(df)}")
    typer.echo(f"Columns: {len(df.columns)}")
    typer.echo(f"Written to: {output}")


# Create CLI app for this command
app = typer.Typer(help="Convert between different file formats")

# Register the command
app.command()(convert)
