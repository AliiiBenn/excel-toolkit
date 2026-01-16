"""Strip command implementation.

Remove leading and trailing whitespace from cell values.
"""

from pathlib import Path

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.cleaning import trim_whitespace
from excel_toolkit.commands.common import (
    read_data_file,
    write_or_display,
    display_table,
)


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
    # 1. Read file
    df = read_data_file(file_path, sheet)
    original_count = len(df)

    # 2. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 3. Determine columns to process
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

    # 4. Count cells modified before stripping
    cells_modified = 0
    for col in column_list:
        if col in df.columns and df[col].dtype == 'object':
            if left and right:
                cells_modified += df[col].str.strip().ne(df[col]).sum()
            elif left:
                cells_modified += df[col].str.lstrip().ne(df[col]).sum()
            elif right:
                cells_modified += df[col].str.rstrip().ne(df[col]).sum()

    # 5. Determine strip side
    if left and right:
        side = "both"
    elif left:
        side = "left"
    elif right:
        side = "right"
    else:
        side = "both"

    # 6. Strip whitespace using operation
    result = trim_whitespace(df, columns=column_list, side=side)

    if is_err(result):
        error = unwrap_err(result)
        typer.echo(f"Error stripping whitespace: {error}", err=True)
        raise typer.Exit(1)

    df_stripped = unwrap(result)

    # 7. Display summary
    typer.echo(f"Total rows: {original_count}")
    typer.echo(f"Columns processed: {len(column_list)}")
    if columns:
        typer.echo(f"Specified columns: {', '.join(column_list)}")
    else:
        typer.echo(f"All string columns: {', '.join(column_list)}")
    typer.echo(f"Cells modified: {cells_modified}")
    typer.echo(f"Strip mode: {'left' if left else ''}{'/' if left and right else ''}{'right' if right else ''}")
    typer.echo("")

    # 8. Write or display
    factory = HandlerFactory()
    if output:
        write_or_display(df_stripped, factory, output, "table")
    else:
        # Display preview
        display_table(df_stripped.head(20))
        if original_count > 20:
            typer.echo(f"\n... and {original_count - 20} more rows")


# Create CLI app for this command
app = typer.Typer(help="Strip leading and trailing whitespace from cell values")

# Register the command
app.command()(strip)
