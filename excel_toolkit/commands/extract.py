"""Extract command implementation.

Extract date/time components from datetime columns.
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


def extract(
    file_path: str = typer.Argument(..., help="Path to input file"),
    column: str = typer.Option(..., "--column", "-c", help="Datetime column to extract from"),
    parts: str = typer.Option(..., "--parts", "-p", help="Parts to extract (comma-separated): year, month, day, hour, minute, second, quarter, dayofweek, weekofyear"),
    suffix: str | None = typer.Option(None, "--suffix", help="Suffix for new columns (default: _part)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Extract date/time components from a datetime column.

    Extract specified components from a datetime column and add them as new columns.

    Column references can be:
        - Column name: "Date"
        - Column index (1-based): "1"
        - Negative index: "-1" (last column)

    Available parts:
        year, month, day, hour, minute, second
        quarter, dayofweek (0=Monday, 6=Sunday), weekofyear

    Examples:
        xl extract sales.xlsx --column "Date" --parts "year,month,day" --output with_dates.xlsx
        xl extract data.csv -c "Timestamp" -p "year,quarter,month" -o extracted.xlsx
        xl extract data.xlsx -c "1" -p "year,month" --suffix "_extracted"
    """
    # 1. Validate parts
    valid_parts = {
        "year", "month", "day", "hour", "minute", "second",
        "quarter", "dayofweek", "weekofyear"
    }
    parts_list = [p.strip().lower() for p in parts.split(",")]
    invalid_parts = [p for p in parts_list if p not in valid_parts]
    if invalid_parts:
        typer.echo(f"Error: Invalid parts: {', '.join(invalid_parts)}", err=True)
        typer.echo(f"Valid parts: {', '.join(sorted(valid_parts))}")
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
    from excel_toolkit.commands.common import resolve_column_reference
    resolved_column = resolve_column_reference(column, df)

    # 5. Validate column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[resolved_column]):
        typer.echo(f"Error: Column '{resolved_column}' is not a datetime column", err=True)
        typer.echo(f"Column type: {df[resolved_column].dtype}")
        raise typer.Exit(1)

    # 6. Extract parts
    new_columns = {}
    for part in parts_list:
        if suffix:
            col_name = f"{resolved_column}{suffix}_{part}"
        else:
            col_name = f"{resolved_column}_{part}"

        if part == "year":
            new_columns[col_name] = df[resolved_column].dt.year
        elif part == "month":
            new_columns[col_name] = df[resolved_column].dt.month
        elif part == "day":
            new_columns[col_name] = df[resolved_column].dt.day
        elif part == "hour":
            new_columns[col_name] = df[resolved_column].dt.hour
        elif part == "minute":
            new_columns[col_name] = df[resolved_column].dt.minute
        elif part == "second":
            new_columns[col_name] = df[resolved_column].dt.second
        elif part == "quarter":
            new_columns[col_name] = df[resolved_column].dt.quarter
        elif part == "dayofweek":
            new_columns[col_name] = df[resolved_column].dt.dayofweek
        elif part == "weekofyear":
            new_columns[col_name] = df[resolved_column].dt.isocalendar().week

    # 7. Add new columns to dataframe
    for col_name, col_data in new_columns.items():
        df[col_name] = col_data

    # 8. Display summary
    typer.echo(f"Extracted {len(new_columns)} parts from '{resolved_column}'")
    typer.echo(f"Parts: {', '.join(parts_list)}")
    typer.echo(f"Rows: {original_count}")
    typer.echo(f"Original columns: {original_cols}")
    typer.echo(f"New columns: {original_cols + len(new_columns)}")
    typer.echo("")

    # 9. Handle dry-run mode
    if dry_run:
        typer.echo("Preview of extracted data:")
        preview_cols = [resolved_column] + list(new_columns.keys())
        preview_rows = min(5, original_count)
        display_table(df[preview_cols].head(preview_rows))
        raise typer.Exit(0)

    # 10. Write or display
    factory = HandlerFactory()
    write_or_display(df, factory, output, "table")


# Create CLI app for this command
app = typer.Typer(help="Extract date/time components from datetime columns")

# Register the command
app.command()(extract)
