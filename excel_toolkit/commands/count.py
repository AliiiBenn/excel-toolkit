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
    resolve_column_references,
)


def count(
    file_path: str = typer.Argument(..., help="Path to input file"),
    columns: str = typer.Option(..., "--columns", "-c", help="Columns to count (comma-separated)"),
    sort: str | None = typer.Option(None, "--sort", help="Sort by: count, name, or none"),
    ascending: bool = typer.Option(False, "--ascending", help="Sort in ascending order"),
    limit: int | None = typer.Option(None, "--limit", "-n", help="Limit number of results"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Count occurrences of unique values in specified columns.

    Count the frequency of unique values in one or more columns.
    Results can be sorted by count or name, and limited to top N results.

    Column references can be:
        - Column name: "Region"
        - Column index (1-based): "1"
        - Negative index: "-1" (last column)

    Examples:
        xl count data.xlsx --columns "Status" --output counts.xlsx
        xl count data.csv --columns "Region,Category" --output counts.xlsx
        xl count data.xlsx --columns "Product" --sort count --limit 10
        xl count data.xlsx --columns "Category" --sort name -n 15
        xl count data.xlsx --columns "3" --sort count --limit 20
        xl count data.xlsx --columns "Product" --sort count -n 10
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

    # 4. Parse columns (supports both names and indices)
    column_list = [c.strip() for c in columns.split(",")]
    # Resolve column references (names or indices)
    column_list = resolve_column_references(column_list, df)

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

    # 6.5. Apply limit if specified
    if limit is not None:
        if limit <= 0:
            typer.echo(f"Error: Limit must be a positive integer", err=True)
            raise typer.Exit(1)
        df_counts = df_counts.head(limit)

    # 7. Display summary
    typer.echo(f"Total rows: {original_count}")
    typer.echo(f"Columns: {', '.join(column_list)}")
    if sort:
        typer.echo(f"Sorted by: {sort} ({'ascending' if ascending else 'descending'})")
    if limit is not None:
        typer.echo(f"Limited to: {limit} rows")
    typer.echo("")

    # 8. Write or display
    factory = HandlerFactory()
    write_or_display(df_counts, factory, output, "table")


# Create CLI app for this command
app = typer.Typer(help="Count occurrences of unique values in specified columns")

# Register the command
app.command()(count)
