"""Fill command implementation.

Fill missing values in a dataset.
"""

from pathlib import Path

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.cleaning import fill_missing_values
from excel_toolkit.commands.common import (
    read_data_file,
    write_or_display,
    display_table,
)


def fill(
    file_path: str = typer.Argument(..., help="Path to input file"),
    columns: str | None = typer.Option(None, "--columns", "-c", help="Columns to fill (comma-separated)"),
    value: str | None = typer.Option(None, "--value", "-v", help="Constant value to fill with"),
    strategy: str | None = typer.Option(None, "--strategy", "-s", help="Statistical strategy: mean, median, mode, min, max, ffill, bfill"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
    sheet: str | None = typer.Option(None, "--sheet", help="Sheet name for Excel files"),
) -> None:
    """Fill missing values in a data file.

    Fill NaN/None values with constants, statistical measures, or forward/backward fill.

    Examples:
        xl fill data.xlsx --columns "Age" --value "0" --output filled.xlsx
        xl fill data.csv --strategy "mean" --output filled.xlsx
        xl fill data.xlsx --columns "Price" --strategy "median" --output filled.xlsx
        xl fill sales.xlsx --strategy "ffill" --output filled.xlsx
    """
    # 1. Validate fill options
    if value is None and strategy is None:
        typer.echo("Error: Must specify either --value or --strategy", err=True)
        typer.echo("Available strategies: mean, median, mode, min, max, ffill, bfill")
        raise typer.Exit(1)

    if value is not None and strategy is not None:
        typer.echo("Error: Cannot use both --value and --strategy", err=True)
        raise typer.Exit(1)

    # 2. Map CLI strategies to operation strategies
    strategy_mapping = {
        "ffill": "forward",
        "bfill": "backward",
    }

    fill_strategy = strategy_mapping.get(strategy, strategy) if strategy else None
    fill_value = value

    # 3. Read file
    df = read_data_file(file_path, sheet)
    original_count = len(df)

    # 4. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 5. Determine columns to fill
    if columns:
        column_list = [c.strip() for c in columns.split(",")]
        # Validate columns exist
        missing_cols = [c for c in column_list if c not in df.columns]
        if missing_cols:
            typer.echo(f"Error: Columns not found: {', '.join(missing_cols)}", err=True)
            typer.echo(f"Available columns: {', '.join(df.columns)}")
            raise typer.Exit(1)
        target_columns = column_list
    else:
        # Fill all columns with missing values
        target_columns = df.columns[df.isnull().any()].tolist()

    if not target_columns:
        typer.echo("No columns with missing values found")
        raise typer.Exit(0)

    # 6. Count missing values before filling
    missing_before = df[target_columns].isnull().sum().sum()

    # 7. Apply fill strategy using operation
    if fill_value:
        # Convert value to appropriate type
        try:
            # Try numeric conversion
            numeric_value = float(fill_value)
            fill_value_arg = numeric_value
        except ValueError:
            # Use as string
            fill_value_arg = fill_value

        result = fill_missing_values(df, strategy="constant", columns=target_columns, value=fill_value_arg)
    else:
        result = fill_missing_values(df, strategy=fill_strategy, columns=target_columns)

    if is_err(result):
        error = unwrap_err(result)
        typer.echo(f"Error filling missing values: {error}", err=True)
        raise typer.Exit(1)

    df_filled = unwrap(result)

    # 8. Count missing values after filling
    missing_after = df_filled[target_columns].isnull().sum().sum()
    filled_count = missing_before - missing_after

    if filled_count == 0:
        typer.echo("No missing values were filled")
        if not dry_run and not output:
            display_table(df)
        raise typer.Exit(0)

    # 9. Display summary
    typer.echo(f"Missing values before: {missing_before}")
    typer.echo(f"Missing values after: {missing_after}")
    typer.echo(f"Values filled: {filled_count}")
    if strategy:
        typer.echo(f"Strategy: {strategy}")
    else:
        typer.echo(f"Value: {value}")
    if columns:
        typer.echo(f"Columns: {', '.join(target_columns)}")
    else:
        typer.echo(f"Columns: all columns with missing values")
    typer.echo("")

    # 10. Handle dry-run mode
    if dry_run:
        typer.echo("Preview of filled data:")
        preview_rows = min(5, original_count)
        display_table(df_filled.head(preview_rows))
        raise typer.Exit(0)

    # 11. Write or display
    factory = HandlerFactory()
    write_or_display(df_filled, factory, output, "table")


# Create CLI app for this command
app = typer.Typer(help="Fill missing values in a data file")

# Register the command
app.command()(fill)
