"""Convert command implementation.

Convert between different file formats.
"""

from pathlib import Path

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import read_data_file


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

    # 1. Validate output format
    output_ext = output_path.suffix.lower()
    supported_formats = {'.xlsx', '.xlsm', '.csv', '.json'}

    if output_ext not in supported_formats:
        typer.echo(f"Error: Unsupported output format: {output_ext}", err=True)
        typer.echo(f"Supported formats: {', '.join(sorted(supported_formats))}")
        raise typer.Exit(1)

    # 2. Read input file
    df = read_data_file(file_path, sheet)

    # 3. Handle empty file
    if df.empty:
        typer.echo("Warning: Input file is empty (no data rows)", err=True)

    # 4. Write to output format
    write_result = factory.write_file(df, output_path)
    if is_err(write_result):
        error = unwrap_err(write_result)
        typer.echo(f"Error writing file: {error}", err=True)
        raise typer.Exit(1)

    # 5. Display summary
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
