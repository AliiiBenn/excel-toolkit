"""Group command implementation.

Group data and perform aggregations.
"""

from pathlib import Path
from typing import Any

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory, ExcelHandler, CSVHandler
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import display_table


def group(
    file_path: str = typer.Argument(..., help="Path to input file"),
    by: str | None = typer.Option(None, "--by", "-b", help="Columns to group by (comma-separated)"),
    aggregate: str | None = typer.Option(None, "--aggregate", "-a", help="Aggregations: column:func (comma-separated)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Group data and perform aggregations.

    Group by specified columns and calculate aggregations for value columns.
    Supported aggregation functions: sum, mean, avg, median, min, max, count, std, var.

    Examples:
        xl group sales.xlsx --by "Region" --aggregate "Amount:sum,Quantity:avg" --output grouped.xlsx
        xl group data.csv --by "Category,Subcategory" --aggregate "Sales:sum,Profit:mean" --output summary.xlsx
        xl group transactions.xlsx --by "Date" --aggregate "Amount:sum,Count:count" --output daily.xlsx
    """
    path = Path(file_path)
    factory = HandlerFactory()

    # Step 1: Validate file exists
    if not path.exists():
        typer.echo(f"File not found: {file_path}", err=True)
        raise typer.Exit(1)

    # Step 2: Validate group columns
    if not by:
        typer.echo("Error: Must specify --by columns for grouping", err=True)
        raise typer.Exit(1)

    # Step 3: Validate aggregation specifications
    if not aggregate:
        typer.echo("Error: Must specify --aggregate specifications", err=True)
        typer.echo("Format: column:function (e.g., 'Amount:sum,Quantity:avg')")
        typer.echo("Supported functions: sum, mean, avg, median, min, max, count, std, var")
        raise typer.Exit(1)

    # Step 4: Parse aggregation specifications
    valid_funcs = ["sum", "mean", "avg", "median", "min", "max", "count", "std", "var"]
    agg_specs = {}
    parse_errors = []

    for spec in aggregate.split(","):
        spec = spec.strip()
        if ":" not in spec:
            parse_errors.append(f"Invalid format: '{spec}' (expected column:function)")
            continue

        col_name, func = spec.split(":", 1)
        col_name = col_name.strip()
        func = func.strip().lower()

        if func == "avg":
            func = "mean"  # Normalize avg to mean

        if func not in valid_funcs:
            parse_errors.append(f"Invalid function '{func}' in '{spec}'")
            continue

        if col_name in agg_specs:
            parse_errors.append(f"Duplicate column '{col_name}'")
            continue

        agg_specs[col_name] = func

    if parse_errors:
        typer.echo("Error parsing aggregation specifications:", err=True)
        for error in parse_errors:
            typer.echo(f"  - {error}", err=True)
        raise typer.Exit(1)

    if not agg_specs:
        typer.echo("Error: No valid aggregation specifications", err=True)
        raise typer.Exit(1)

    # Step 5: Get handler
    handler_result = factory.get_handler(path)
    if is_err(handler_result):
        error = unwrap_err(handler_result)
        typer.echo(f"{error}", err=True)
        raise typer.Exit(1)

    handler = unwrap(handler_result)

    # Step 6: Read file
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
    original_cols = len(df.columns)

    # Step 7: Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # Step 8: Parse group columns
    group_columns = [c.strip() for c in by.split(",")]
    # Validate group columns exist
    missing_cols = [c for c in group_columns if c not in df.columns]
    if missing_cols:
        typer.echo(f"Error: Group columns not found: {', '.join(missing_cols)}", err=True)
        typer.echo(f"Available columns: {', '.join(df.columns)}")
        raise typer.Exit(1)

    # Step 9: Validate aggregation columns exist
    agg_columns = list(agg_specs.keys())
    missing_agg_cols = [c for c in agg_columns if c not in df.columns]
    if missing_agg_cols:
        typer.echo(f"Error: Aggregation columns not found: {', '.join(missing_agg_cols)}", err=True)
        typer.echo(f"Available columns: {', '.join(df.columns)}")
        raise typer.Exit(1)

    # Check if aggregation columns are the same as group columns
    overlap_cols = set(group_columns) & set(agg_columns)
    if overlap_cols:
        typer.echo(f"Error: Cannot aggregate on group columns: {', '.join(overlap_cols)}", err=True)
        raise typer.Exit(1)

    # Step 10: Build aggregation dictionary for pandas
    agg_dict = {}
    for col, func in agg_specs.items():
        if func == "count":
            # Count is special - count non-null values
            agg_dict[col] = func
        else:
            agg_dict[col] = func

    # Step 11: Perform groupby and aggregation
    try:
        df_grouped = df.groupby(group_columns, as_index=False, dropna=False).agg(agg_dict)

        # Flatten column names (MultiIndex from agg)
        if isinstance(df_grouped.columns, pd.MultiIndex):
            df_grouped.columns = ['_'.join(col).strip() for col in df_grouped.columns.values]

        # Rename columns to match aggregation spec format
        new_column_names = {}
        for col in group_columns:
            new_column_names[col] = col

        for col, func in agg_specs.items():
            # Find the actual column name (might be col_func or just col)
            matching_cols = [c for c in df_grouped.columns if c.startswith(col)]
            if matching_cols:
                new_column_names[matching_cols[0]] = f"{col}_{func}"

        df_grouped.rename(columns=new_column_names, inplace=True)

    except Exception as e:
        typer.echo(f"Error performing aggregation: {str(e)}", err=True)
        raise typer.Exit(1)

    grouped_count = len(df_grouped)
    grouped_cols = len(df_grouped.columns)

    # Step 12: Display summary
    typer.echo(f"Original rows: {original_count}")
    typer.echo(f"Grouped rows: {grouped_count}")
    typer.echo(f"Grouped by: {', '.join(group_columns)}")
    typer.echo(f"Aggregations: {aggregate}")
    typer.echo("")

    # Step 13: Handle dry-run mode
    if dry_run:
        typer.echo("Preview of grouped data:")
        preview_rows = min(5, grouped_count)
        display_table(df_grouped.head(preview_rows))
        raise typer.Exit(0)

    # Step 14: Write output or display
    if output:
        output_path = Path(output)
        write_result = factory.write_file(df_grouped, output_path)
        if is_err(write_result):
            error = unwrap_err(write_result)
            typer.echo(f"Error writing file: {error}", err=True)
            raise typer.Exit(1)
        typer.echo(f"Written to: {output}")
    else:
        # Display data
        display_table(df_grouped)


# Create CLI app for this command
app = typer.Typer(help="Group data and perform aggregations")

# Register the command
app.command()(group)
