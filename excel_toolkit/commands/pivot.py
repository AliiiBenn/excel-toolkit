"""Pivot command implementation.

Create pivot table-like summaries from data.
"""

from pathlib import Path
from typing import Any

import typer
import pandas as pd


from excel_toolkit.core import HandlerFactory, ExcelHandler, CSVHandler
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import display_table


def pivot(
    file_path: str = typer.Argument(..., help="Path to input file"),
    rows: str | None = typer.Option(None, "--rows", "-r", help="Column(s) to use as rows (comma-separated)"),
    columns: str | None = typer.Option(None, "--columns", "-c", help="Column(s) to use as columns (comma-separated)"),
    values: str | None = typer.Option(None, "--values", "-v", help="Column(s) to use as values (comma-separated)"),
    aggfunc: str = typer.Option("sum", "--aggfunc", "-a", help="Aggregation function (sum, mean, count, min, max, median)"),
    fill_value: str | None = typer.Option(None, "--fill", "-f", help="Value to fill NaN with"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Create pivot table summaries from data.

    Create a pivot table by specifying row, column, and value dimensions.
    Supported aggregation functions: sum, mean, avg, count, min, max, median.

    Examples:
        xl pivot data.xlsx --rows "Date" --columns "Product" --values "Sales:sum" --output pivot.xlsx
        xl pivot sales.csv --rows "Region,Category" --columns "Month" --values "Revenue" --aggfunc mean --output monthly.xlsx
        xl pivot data.xlsx --rows "Department" --columns "Year" --values "Employees" --aggfunc count --output count.xlsx
    """
    path = Path(file_path)
    factory = HandlerFactory()

    # Step 1: Validate file exists
    if not path.exists():
        typer.echo(f"File not found: {file_path}", err=True)
        raise typer.Exit(1)

    # Step 2: Validate required parameters
    if not rows:
        typer.echo("Error: Must specify --rows columns", err=True)
        raise typer.Exit(1)

    if not columns:
        typer.echo("Error: Must specify --columns columns", err=True)
        raise typer.Exit(1)

    if not values:
        typer.echo("Error: Must specify --values columns", err=True)
        raise typer.Exit(1)

    # Step 3: Validate aggregation function
    valid_funcs = ["sum", "mean", "avg", "count", "min", "max", "median"]
    if aggfunc.lower() not in valid_funcs:
        typer.echo(f"Error: Invalid aggregation function '{aggfunc}'", err=True)
        typer.echo(f"Valid functions: {', '.join(valid_funcs)}", err=True)
        raise typer.Exit(1)

    # Normalize avg to mean
    agg_func_normalized = "mean" if aggfunc.lower() == "avg" else aggfunc.lower()

    # Step 4: Get handler
    handler_result = factory.get_handler(path)
    if is_err(handler_result):
        error = unwrap_err(handler_result)
        typer.echo(f"{error}", err=True)
        raise typer.Exit(1)

    handler = unwrap(handler_result)

    # Step 5: Read file
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

    # Step 6: Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # Step 7: Parse column specifications
    row_columns = [c.strip() for c in rows.split(",")]
    col_columns = [c.strip() for c in columns.split(",")]
    value_columns = [c.strip() for c in values.split(",")]

    # Step 8: Validate columns exist
    missing_rows = [c for c in row_columns if c not in df.columns]
    missing_cols = [c for c in col_columns if c not in df.columns]
    missing_vals = [c for c in value_columns if c not in df.columns]

    if missing_rows:
        typer.echo(f"Error: Row columns not found: {', '.join(missing_rows)}", err=True)
        typer.echo(f"Available columns: {', '.join(df.columns)}")
        raise typer.Exit(1)

    if missing_cols:
        typer.echo(f"Error: Column columns not found: {', '.join(missing_cols)}", err=True)
        typer.echo(f"Available columns: {', '.join(df.columns)}")
        raise typer.Exit(1)

    if missing_vals:
        typer.echo(f"Error: Value columns not found: {', '.join(missing_vals)}", err=True)
        typer.echo(f"Available columns: {', '.join(df.columns)}")
        raise typer.Exit(1)

    # Step 9: Parse fill value
    fill_value_parsed = None
    if fill_value:
        if fill_value.lower() == "none":
            fill_value_parsed = None
        elif fill_value.lower() == "0":
            fill_value_parsed = 0
        elif fill_value.lower() == "nan":
            fill_value_parsed = float('nan')
        else:
            # Try to parse as number
            try:
                fill_value_parsed = int(fill_value)
            except ValueError:
                try:
                    fill_value_parsed = float(fill_value)
                except ValueError:
                    fill_value_parsed = fill_value  # Keep as string

    # Step 10: Create pivot table
    try:
        pivot_table = df.pivot_table(
            index=row_columns,
            columns=col_columns,
            values=value_columns,
            aggfunc=agg_func_normalized,
            fill_value=fill_value_parsed,
            observed=True,  # Only use observed categories for categorical data
        )

        # Flatten column names if MultiIndex
        if isinstance(pivot_table.columns, pd.MultiIndex):
            pivot_table.columns = ['_'.join(map(str, col)).strip() for col in pivot_table.columns.values]

        # Flatten index if MultiIndex
        if isinstance(pivot_table.index, pd.MultiIndex):
            pivot_table.index = ['_'.join(map(str, idx)).strip() for idx in pivot_table.index.values]

        # Reset index to make rows into columns
        pivot_table = pivot_table.reset_index()

    except Exception as e:
        typer.echo(f"Error creating pivot table: {str(e)}", err=True)
        raise typer.Exit(1)

    pivot_count = len(pivot_table)
    pivot_cols = len(pivot_table.columns)

    # Step 11: Display summary
    typer.echo(f"Original rows: {original_count}")
    typer.echo(f"Pivoted rows: {pivot_count}")
    typer.echo(f"Rows: {', '.join(row_columns)}")
    typer.echo(f"Columns: {', '.join(col_columns)}")
    typer.echo(f"Values: {', '.join(value_columns)}")
    typer.echo(f"Aggregation: {aggfunc}")
    if fill_value is not None:
        typer.echo(f"Fill value: {fill_value}")
    typer.echo("")

    # Step 12: Handle dry-run mode
    if dry_run:
        typer.echo("Preview of pivot table:")
        preview_rows = min(5, pivot_count)
        display_table(pivot_table.head(preview_rows))
        raise typer.Exit(0)

    # Step 13: Write output or display
    if output:
        output_path = Path(output)
        write_result = factory.write_file(pivot_table, output_path)
        if is_err(write_result):
            error = unwrap_err(write_result)
            typer.echo(f"Error writing file: {error}", err=True)
            raise typer.Exit(1)
        typer.echo(f"Written to: {output}")
    else:
        # Display data
        display_table(pivot_table)


# Create CLI app for this command
app = typer.Typer(help="Create pivot table summaries")

# Register the command
app.command()(pivot)
