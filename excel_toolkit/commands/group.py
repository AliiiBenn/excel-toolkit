"""Group command implementation.

Group data and perform aggregations.
"""

from pathlib import Path

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.aggregating import (
    parse_aggregation_specs,
    validate_aggregation_columns,
    aggregate_groups,
)
from excel_toolkit.commands.common import (
    read_data_file,
    write_or_display,
    display_table,
    resolve_column_references,
)


def group(
    file_path: str = typer.Argument(..., help="Path to input file"),
    by: str | None = typer.Option(None, "--by", "-b", help="Columns to group by (comma-separated)"),
    aggregate: str | None = typer.Option(None, "--aggregate", "-a", help="Aggregations: column:func (comma-separated)"),
    sort: str | None = typer.Option(None, "--sort", help="Sort results by aggregation column (asc or desc)"),
    sort_column: str | None = typer.Option(None, "--sort-column", help="Column to sort by (default: first aggregation column)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Group data and perform aggregations.

    Group by specified columns and calculate aggregations for value columns.
    Supported aggregation functions: sum, mean, avg, median, min, max, count, std, var.

    Column references can be:
        - Column name: "Region"
        - Column index (1-based): "1"
        - Negative index: "-1" (last column)

    Examples:
        xl group sales.xlsx --by "Region" --aggregate "Amount:sum" --output grouped.xlsx
        xl group sales.xlsx --by "Region" --aggregate "Amount:sum" --sort desc
        xl group data.csv --by "Category" --aggregate "Sales:sum,Profit:mean" --sort asc
        xl group transactions.xlsx --by "Date" --aggregate "Amount:sum,Count:count" --sort desc --sort-column "Amount_sum"
        xl group data.xlsx --by "1,2" --aggregate "3:sum" --sort desc
    """
    # 1. Validate group columns
    if not by:
        typer.echo("Error: Must specify --by columns for grouping", err=True)
        raise typer.Exit(1)

    # 2. Validate aggregation specifications
    if not aggregate:
        typer.echo("Error: Must specify --aggregate specifications", err=True)
        typer.echo("Format: column:function (e.g., 'Amount:sum,Quantity:avg')")
        typer.echo("Supported functions: sum, mean, avg, median, min, max, count, std, var")
        raise typer.Exit(1)

    # 2.5. Validate sort option
    if sort is not None and sort not in ["asc", "desc"]:
        typer.echo(f"Error: Invalid sort value '{sort}'", err=True)
        typer.echo("Valid values: asc, desc")
        raise typer.Exit(1)

    # 3. Read file
    df = read_data_file(file_path, sheet)
    original_count = len(df)
    original_cols = len(df.columns)

    # 4. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 5. Parse aggregation specifications
    parse_result = parse_aggregation_specs(aggregate)
    if is_err(parse_result):
        error = unwrap_err(parse_result)
        typer.echo(f"Error parsing aggregation specifications: {error}", err=True)
        raise typer.Exit(1)

    agg_specs = unwrap(parse_result)

    # 6. Parse group columns (supports both names and indices)
    group_cols = [c.strip() for c in by.split(",")]
    # Resolve column references (names or indices)
    group_cols = resolve_column_references(group_cols, df)

    # 6.5. Resolve aggregation column references (supports both names and indices)
    agg_column_refs = list(agg_specs.keys())
    resolved_agg_cols = resolve_column_references(agg_column_refs, df)

    # Build new agg_specs with resolved column names
    resolved_agg_specs = {}
    for old_col, new_col in zip(agg_column_refs, resolved_agg_cols):
        resolved_agg_specs[new_col] = agg_specs[old_col]
    agg_specs = resolved_agg_specs

    # 7. Validate columns
    validation = validate_aggregation_columns(df, group_cols, list(agg_specs.keys()))
    if is_err(validation):
        error = unwrap_err(validation)
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(1)

    # 8. Aggregate
    result = aggregate_groups(df, group_cols, agg_specs)
    if is_err(result):
        error = unwrap_err(result)
        typer.echo(f"Error aggregating data: {error}", err=True)
        raise typer.Exit(1)

    df_grouped = unwrap(result)
    grouped_count = len(df_grouped)
    grouped_cols = len(df_grouped.columns)

    # 8.5. Sort if requested
    if sort:
        # Determine sort column
        if sort_column:
            # Validate sort_column exists
            if sort_column not in df_grouped.columns:
                typer.echo(f"Error: Sort column '{sort_column}' not found in grouped data", err=True)
                typer.echo(f"Available columns: {', '.join(df_grouped.columns)}")
                raise typer.Exit(1)
            sort_col = sort_column
        else:
            # Default to first aggregation column
            # The aggregation columns are those not in group_cols
            agg_cols = [col for col in df_grouped.columns if col not in group_cols]
            if not agg_cols:
                typer.echo("Error: No aggregation columns found for sorting", err=True)
                raise typer.Exit(1)
            sort_col = agg_cols[0]

        # Sort the dataframe
        ascending = (sort == "asc")
        df_grouped = df_grouped.sort_values(by=sort_col, ascending=ascending)
        # Reset index after sorting
        df_grouped = df_grouped.reset_index(drop=True)

    # 9. Display summary
    typer.echo(f"Original rows: {original_count}")
    typer.echo(f"Grouped rows: {grouped_count}")
    typer.echo(f"Grouped by: {', '.join(group_cols)}")
    typer.echo(f"Aggregations: {aggregate}")
    if sort:
        sort_col_display = sort_column if sort_column else [col for col in df_grouped.columns if col not in group_cols][0]
        typer.echo(f"Sorted by: {sort_col_display} ({sort})")
    typer.echo("")

    # 10. Handle dry-run mode
    if dry_run:
        typer.echo("Preview of grouped data:")
        preview_rows = min(5, grouped_count)
        display_table(df_grouped.head(preview_rows))
        raise typer.Exit(0)

    # 11. Write or display
    factory = HandlerFactory()
    write_or_display(df_grouped, factory, output, "table")


# Create CLI app for this command
app = typer.Typer(help="Group data and perform aggregations")

# Register the command
app.command()(group)
