"""Filter command implementation.

Filters rows from data files based on conditions.
"""

from pathlib import Path
import typer

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.filtering import (
    validate_condition,
    normalize_condition,
    apply_filter,
)
from excel_toolkit.commands.common import (
    read_data_file,
    write_or_display,
    display_table,
    resolve_column_references,
)


def filter(
    file_path: str = typer.Argument(..., help="Path to input file"),
    condition: str = typer.Argument(..., help="Filter condition (e.g., 'age > 30')"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    rows: int | None = typer.Option(None, "--rows", "-n", help="Limit number of results"),
    columns: str | None = typer.Option(None, "--columns", "-c", help="Comma-separated columns to keep"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, csv, json)"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
) -> None:
    """Filter rows from a data file based on a condition.

    Uses pandas query syntax for conditions:
    - Numeric: age > 30, price >= 100
    - String: name == 'Alice', category in ['A', 'B']
    - Logical: age > 25 and city == 'Paris'
    - Null: value.isna(), value.notna()

    Column references can be:
        - Column name: "name"
        - Column index (1-based): "1"
        - Negative index: "-1" (last column)

    Examples:
        xl filter data.xlsx "age > 30"
        xl filter data.csv "price > 100" --output filtered.xlsx
        xl filter data.xlsx "city == 'Paris'" --columns name,age
        xl filter data.csv "status == 'active'" --dry-run
        xl filter data.xlsx "age > 30" --columns "1,2,3"
    """
    # 1. Read file
    df = read_data_file(file_path, sheet)
    original_count = len(df)

    # 2. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 3. Validate condition
    validation = validate_condition(condition)
    if is_err(validation):
        error = unwrap_err(validation)
        typer.echo(f"Invalid condition: {error}", err=True)
        raise typer.Exit(1)

    # 4. Normalize condition
    normalized = normalize_condition(condition, df)

    # 5. Parse columns (supports both names and indices)
    col_list = None
    if columns:
        col_list = [c.strip() for c in columns.split(",")]
        # Resolve column references (names or indices)
        col_list = resolve_column_references(col_list, df)

    # 6. Apply filter
    result = apply_filter(df, normalized, columns=col_list, limit=rows)
    if is_err(result):
        error = unwrap_err(result)
        typer.echo(f"Error filtering data: {error}", err=True)
        raise typer.Exit(1)

    df_filtered = unwrap(result)
    filtered_count = len(df_filtered)

    # 7. Handle dry-run
    if dry_run:
        percentage = (filtered_count / original_count * 100) if original_count > 0 else 0
        typer.echo(f"Would filter {filtered_count} of {original_count} rows ({percentage:.1f}%)")
        typer.echo(f"Condition: {condition}")
        typer.echo("")
        if filtered_count > 0:
            preview_rows = min(5, filtered_count)
            typer.echo("Preview of first matches:")
            display_table(df_filtered.head(preview_rows))
        else:
            typer.echo("No rows match the condition")
        raise typer.Exit(0)

    # 8. Handle empty result
    if filtered_count == 0:
        typer.echo("No rows match the filter condition")
        typer.echo(f"Condition: {condition}")
        if output:
            factory = HandlerFactory()
            write_or_display(df_filtered, factory, output, format)
        raise typer.Exit(0)

    # 9. Display summary
    percentage = (filtered_count / original_count * 100) if original_count > 0 else 0
    typer.echo(f"Filtered {filtered_count} of {original_count} rows ({percentage:.1f}%)")
    typer.echo(f"Condition: {condition}")

    if filtered_count == original_count:
        typer.echo("Warning: All rows match the condition", err=True)

    typer.echo("")

    # 10. Write or display
    factory = HandlerFactory()
    write_or_display(df_filtered, factory, output, format)


# Create CLI app for this command
app = typer.Typer(help="Filter rows from data files")

# Register the command
app.command()(filter)
