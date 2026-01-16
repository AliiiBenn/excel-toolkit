"""Aggregate command implementation.

Perform custom aggregations on grouped data.
"""

from pathlib import Path
from typing import Any

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory, ExcelHandler, CSVHandler
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import display_table


def aggregate(
    file_path: str = typer.Argument(..., help="Path to input file"),
    group: str | None = typer.Option(None, "--group", "-g", help="Columns to group by (comma-separated)"),
    functions: str | None = typer.Option(None, "--functions", "-f", help="Aggregations: column:func1,func2 (comma-separated)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Perform custom aggregations on grouped data.

    Group by specified columns and apply multiple aggregation functions to value columns.
    Multiple functions can be applied to the same column by specifying the column multiple times.
    Supported functions: sum, mean, avg, median, min, max, count, std, var, first, last.

    Examples:
        xl aggregate sales.xlsx --group "Region" --functions "Revenue:sum,Revenue:mean" --output summary.xlsx
        xl aggregate data.csv --group "Category" --functions "Sales:sum,Sales:min,Sales:max,Profit:mean" --output stats.xlsx
        xl aggregate transactions.xlsx --group "Date,Type" --functions "Amount:sum,Amount:count,Quantity:mean" --output daily.xlsx
    """
    path = Path(file_path)
    factory = HandlerFactory()

    # Step 1: Validate file exists
    if not path.exists():
        typer.echo(f"File not found: {file_path}", err=True)
        raise typer.Exit(1)

    # Step 2: Validate group columns
    if not group:
        typer.echo("Error: Must specify --group columns", err=True)
        raise typer.Exit(1)

    # Step 3: Validate aggregation specifications
    if not functions:
        typer.echo("Error: Must specify --functions", err=True)
        typer.echo("Format: column:func1,func2 (e.g., 'Amount:sum,mean')", err=True)
        typer.echo("Supported functions: sum, mean, avg, median, min, max, count, std, var, first, last")
        raise typer.Exit(1)

    # Step 4: Parse aggregation specifications
    valid_funcs = ["sum", "mean", "avg", "median", "min", "max", "count", "std", "var", "first", "last"]
    agg_specs = {}
    parse_errors = []

    for spec in functions.split(","):
        spec = spec.strip()
        if ":" not in spec:
            parse_errors.append(f"Invalid format: '{spec}' (expected column:func1,func2)")
            continue

        col_name, funcs = spec.split(":", 1)
        col_name = col_name.strip()
        func_list = [f.strip().lower() for f in funcs.split(",")]

        # Normalize avg to mean
        func_list = ["mean" if f == "avg" else f for f in func_list]

        # Validate functions
        invalid_funcs = [f for f in func_list if f not in valid_funcs]
        if invalid_funcs:
            parse_errors.append(f"Invalid functions in '{spec}': {', '.join(invalid_funcs)}")
            continue

        # Merge with existing functions if column already specified
        if col_name in agg_specs:
            agg_specs[col_name].extend(func_list)
        else:
            agg_specs[col_name] = func_list

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

    # Step 7: Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # Step 8: Parse group columns
    group_columns = [c.strip() for c in group.split(",")]
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
    for col, func_list in agg_specs.items():
        agg_dict[col] = func_list

    # Step 11: Perform groupby and aggregation
    try:
        df_aggregated = df.groupby(group_columns, as_index=False, dropna=False).agg(agg_dict)

        # Flatten column names (MultiIndex from agg with multiple functions)
        if isinstance(df_aggregated.columns, pd.MultiIndex):
            df_aggregated.columns = ['_'.join(col).strip() for col in df_aggregated.columns.values]

    except Exception as e:
        typer.echo(f"Error performing aggregation: {str(e)}", err=True)
        raise typer.Exit(1)

    aggregated_count = len(df_aggregated)

    # Step 12: Display summary
    typer.echo(f"Original rows: {original_count}")
    typer.echo(f"Aggregated rows: {aggregated_count}")
    typer.echo(f"Grouped by: {', '.join(group_columns)}")
    typer.echo(f"Aggregations: {functions}")
    typer.echo("")

    # Step 13: Handle dry-run mode
    if dry_run:
        typer.echo("Preview of aggregated data:")
        preview_rows = min(5, aggregated_count)
        display_table(df_aggregated.head(preview_rows))
        raise typer.Exit(0)

    # Step 14: Write output or display
    if output:
        output_path = Path(output)
        write_result = factory.write_file(df_aggregated, output_path)
        if is_err(write_result):
            error = unwrap_err(write_result)
            typer.echo(f"Error writing file: {error}", err=True)
            raise typer.Exit(1)
        typer.echo(f"Written to: {output}")
    else:
        # Display data
        display_table(df_aggregated)


# Create CLI app for this command
app = typer.Typer(help="Perform custom aggregations on grouped data")

# Register the command
app.command()(aggregate)
