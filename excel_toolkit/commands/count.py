"""Count command implementation.

Count occurrences of unique values in specified columns.
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
)


def count(
    file_path: str = typer.Argument(..., help="Path to input file"),
    columns: str = typer.Option(..., "--columns", "-c", help="Columns to count (comma-separated)"),
    sort: str | None = typer.Option(None, "--sort", help="Sort by: count, name, or none"),
    ascending: bool = typer.Option(False, "--ascending", help="Sort in ascending order"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Count occurrences of unique values in specified columns.

    Count the frequency of unique values in one or more columns.
    Results can be sorted by count or name.

    Examples:
        xl count data.xlsx --columns "Status" --output counts.xlsx
        xl count data.csv --columns "Region,Category" --output counts.xlsx
        xl count data.xlsx --columns "Product" --sort count --output top-products.xlsx
        xl count data.xlsx --columns "Category" --sort name --ascending --output categories.xlsx
    """
    # 1. Validate sort option
    valid_sort_values = ["count", "name", "none", None]
    if sort not in valid_sort_values:
        typer.echo(f"Error: Invalid sort value '{sort}'", err=True)
        typer.echo("Valid values: count, name, none")
        raise typer.Exit(1)

    # 2. Read file
    df = read_data_file(file_path, sheet)
    original_count = len(df)

    # 3. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 4. Parse columns
    column_list = [c.strip() for c in columns.split(",")]
    # Validate columns exist
    missing_cols = [c for c in column_list if c not in df.columns]
    if missing_cols:
        typer.echo(f"Error: Columns not found: {', '.join(missing_cols)}", err=True)
        typer.echo(f"Available columns: {', '.join(df.columns)}")
        raise typer.Exit(1)

    # 5. Count occurrences for each column
    count_dfs = []

    for col in column_list:
        # Get value counts
        value_counts = df[col].value_counts().reset_index()
        value_counts.columns = [col, 'count']

        # Add column name for multi-column case
        if len(column_list) > 1:
            value_counts = value_counts.rename(columns={col: 'value'})
            value_counts.insert(0, 'column', col)

        count_dfs.append(value_counts)

    # Combine all counts
    if len(count_dfs) == 1:
        df_counts = count_dfs[0]
    else:
        df_counts = pd.concat(count_dfs, ignore_index=True)

    # 6. Sort if requested
    if sort == "count":
        # Sort by count (descending by default)
        sort_column = 'count'
        ascending_order = ascending
        df_counts = df_counts.sort_values(by=sort_column, ascending=ascending_order)
    elif sort == "name":
        # Sort by value name (ascending by default)
        if len(column_list) == 1:
            sort_column = column_list[0]
        else:
            sort_column = 'value'
        ascending_order = ascending
        df_counts = df_counts.sort_values(by=sort_column, ascending=ascending_order)

    # Reset index after sorting
    df_counts = df_counts.reset_index(drop=True)

    # 7. Display summary
    typer.echo(f"Total rows: {original_count}")
    typer.echo(f"Columns: {', '.join(column_list)}")
    if sort:
        typer.echo(f"Sorted by: {sort} ({'ascending' if ascending else 'descending'})")
    typer.echo("")

    # 8. Write or display
    factory = HandlerFactory()
    write_or_display(df_counts, factory, output, "table")


# Create CLI app for this command
app = typer.Typer(help="Count occurrences of unique values in specified columns")

# Register the command
app.command()(count)
