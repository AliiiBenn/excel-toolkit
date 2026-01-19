"""Calculate command implementation.

Perform calculations on columns (cumulative, growth, etc.).
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
    resolve_column_reference,
)


def calculate(
    file_path: str = typer.Argument(..., help="Path to input file"),
    column: str = typer.Option(..., "--column", "-c", help="Column to calculate on"),
    operation: str = typer.Option(..., "--operation", "-op", help="Operation: cumsum, cummean, growth, growth_pct, diff"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Perform calculations on a column.

    Calculate cumulative sums, growth rates, and other derived values.

    Column references can be:
        - Column name: "Sales"
        - Column index (1-based): "1"
        - Negative index: "-1" (last column)

    Available operations:
        cumsum:      Cumulative sum (running total)
        cummean:     Cumulative mean (running average)
        growth:      Absolute growth (difference from previous row)
        growth_pct:  Percentage growth (percent change from previous row)
        diff:        Difference from previous row

    Examples:
        xl calculate sales.xlsx --column "Sales" --operation cumsum
        xl calculate sales.xlsx --column "Revenue" --operation growth_pct
        xl calculate data.csv -c "Price" -op diff -o calculated.xlsx
    """
    # 1. Validate operation
    valid_operations = ["cumsum", "cummean", "growth", "growth_pct", "diff"]
    if operation not in valid_operations:
        typer.echo(f"Error: Invalid operation '{operation}'", err=True)
        typer.echo(f"Valid operations: {', '.join(valid_operations)}")
        raise typer.Exit(1)

    # 2. Read file
    df = read_data_file(file_path, sheet)
    original_count = len(df)
    original_cols = len(df.columns)

    # 3. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 4. Resolve column reference (supports both name and index)
    resolved_column = resolve_column_reference(column, df)

    # 5. Validate column is numeric
    if not pd.api.types.is_numeric_dtype(df[resolved_column]):
        typer.echo(f"Error: Column '{resolved_column}' is not numeric", err=True)
        typer.echo(f"Column type: {df[resolved_column].dtype}")
        raise typer.Exit(1)

    # 6. Perform calculation
    result_col_name = f"{resolved_column}_{operation}"

    if operation == "cumsum":
        df[result_col_name] = df[resolved_column].cumsum()
    elif operation == "cummean":
        df[result_col_name] = df[resolved_column].expanding().mean()
    elif operation == "growth":
        df[result_col_name] = df[resolved_column].diff()
    elif operation == "growth_pct":
        df[result_col_name] = df[resolved_column].pct_change() * 100
    elif operation == "diff":
        df[result_col_name] = df[resolved_column].diff()

    # 7. Display summary
    typer.echo(f"Calculated {operation} on '{resolved_column}'")
    typer.echo(f"Rows: {original_count}")
    typer.echo(f"Original columns: {original_cols}")
    typer.echo(f"New columns: {original_cols + 1}")
    typer.echo(f"Result column: {result_col_name}")
    typer.echo("")

    # 8. Handle dry-run mode
    if dry_run:
        typer.echo("Preview of calculated data:")
        preview_cols = [resolved_column, result_col_name]
        preview_rows = min(5, original_count)
        display_table(df[preview_cols].head(preview_rows))
        raise typer.Exit(0)

    # 9. Write or display
    factory = HandlerFactory()
    write_or_display(df, factory, output, "table")


# Create CLI app for this command
app = typer.Typer(help="Perform calculations on columns")

# Register the command
app.command()(calculate)
