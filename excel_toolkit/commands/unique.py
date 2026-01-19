"""Unique command implementation.

Extract unique values from a dataset.
"""

from pathlib import Path

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import (
    read_data_file,
    write_or_display,
    display_table,
    resolve_column_references,
)


def unique(
    file_path: str = typer.Argument(..., help="Path to input file"),
    columns: str | None = typer.Option(None, "--columns", "-c", help="Columns to get unique values from (comma-separated)"),
    count: bool = typer.Option(False, "--count", help="Show count of each unique value"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Extract unique values from a data file.

    Get unique values from specified columns or unique rows across all columns.

    Column references can be:
        - Column name: "Category"
        - Column index (1-based): "1"
        - Negative index: "-1" (last column)

    Examples:
        xl unique data.xlsx --columns "Category" --output categories.xlsx
        xl unique data.csv --columns "Region,Product" --output unique.xlsx
        xl unique contacts.xlsx --columns "Email" --count --output email-counts.xlsx
        xl unique data.xlsx --columns "3" --output third-col-unique.xlsx
        xl unique data.xlsx --columns "-1" --output last-col-unique.xlsx
    """
    # 1. Validate columns specified
    if not columns:
        typer.echo("Error: Must specify --columns", err=True)
        raise typer.Exit(1)

    # 2. Read file
    df = read_data_file(file_path, sheet)
    original_count = len(df)

    # 3. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 4. Parse columns (supports both names and indices)
    column_list = [c.strip() for c in columns.split(",")]
    # Resolve column references (names or indices)
    column_list = resolve_column_references(column_list, df)

    # 5. Get unique values
    if len(column_list) == 1:
        # Single column - get unique values
        col = column_list[0]
        unique_values = df[col].dropna().unique()

        if count:
            # Get value counts
            value_counts = df[col].value_counts().reset_index()
            value_counts.columns = [col, 'count']
            df_unique = value_counts
        else:
            # Just unique values
            df_unique = pd.DataFrame({col: unique_values})
    else:
        # Multiple columns - get unique rows
        df_subset = df[column_list].copy()
        df_unique = df_subset.drop_duplicates().reset_index(drop=True)

        if count:
            # Add count column
            df_unique['count'] = df_subset.groupby(column_list, dropna=False).size().values

    unique_count = len(df_unique)

    # 6. Display summary
    typer.echo(f"Original rows: {original_count}")
    typer.echo(f"Unique rows: {unique_count}")
    if len(column_list) == 1:
        typer.echo(f"Column: {column_list[0]}")
    else:
        typer.echo(f"Columns: {', '.join(column_list)}")
    typer.echo("")

    # 7. Handle dry-run mode
    if dry_run:
        typer.echo("Preview of unique values:")
        preview_rows = min(5, unique_count)
        display_table(df_unique.head(preview_rows))
        raise typer.Exit(0)

    # 8. Write or display
    factory = HandlerFactory()
    write_or_display(df_unique, factory, output, "table")


# Create CLI app for this command
app = typer.Typer(help="Extract unique values from a data file")

# Register the command
app.command()(unique)
