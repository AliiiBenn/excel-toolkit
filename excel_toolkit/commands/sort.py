"""Sort command implementation.

Sorts rows from data files by column values.
"""

from pathlib import Path
import typer

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.sorting import (
    validate_sort_columns,
    sort_dataframe,
)
from excel_toolkit.operations.filtering import (
    validate_condition,
    normalize_condition,
    apply_filter,
)
from excel_toolkit.commands.common import (
    read_data_file,
    write_or_display,
)


def sort(
    file_path: str = typer.Argument(..., help="Path to input file"),
    columns: str = typer.Option(..., "--columns", "-c", help="Column(s) to sort by (comma-separated)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    rows: int | None = typer.Option(None, "--rows", "-n", help="Limit number of results"),
    desc: bool = typer.Option(False, "--desc", "-d", help="Sort in descending order"),
    where: str | None = typer.Option(None, "--where", "-w", help="Filter condition before sorting"),
    na_placement: str = typer.Option("last", "--na-placement", help="Where to place NaN values ('first' or 'last')"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, csv, json)"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Sort rows from a data file by column values.

    Sorts data by one or more columns in ascending or descending order.
    Optionally filter rows before sorting.

    Examples:
        xl sort data.xlsx --columns salary
        xl sort data.xlsx --columns city,age --rows 10
        xl sort data.csv --columns price --desc --output sorted.csv
        xl sort data.xlsx --columns name --where "age > 30"
        xl sort data.csv --columns date --na-placement first
    """
    # 1. Read file
    df = read_data_file(file_path, sheet)

    # 2. Validate na_placement
    if na_placement not in ["first", "last"]:
        typer.echo(f"Invalid na_placement: {na_placement}. Must be 'first' or 'last'", err=True)
        raise typer.Exit(1)

    # 3. Parse column list
    column_list = [c.strip() for c in columns.split(",")]
    if not column_list:
        typer.echo("Error: At least one column must be specified", err=True)
        raise typer.Exit(1)

    # 4. Validate columns
    validation = validate_sort_columns(df, column_list)
    if is_err(validation):
        error = unwrap_err(validation)
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(1)

    # 5. Apply filter if specified
    if where:
        # Validate condition
        validation = validate_condition(where)
        if is_err(validation):
            error = unwrap_err(validation)
            typer.echo(f"Invalid filter condition: {error}", err=True)
            raise typer.Exit(1)

        # Normalize and apply
        normalized = unwrap(normalize_condition(where))
        result = apply_filter(df, normalized)
        if is_err(result):
            error = unwrap_err(result)
            typer.echo(f"Error filtering data: {error}", err=True)
            raise typer.Exit(1)

        df = unwrap(result)
        filtered_count = len(df)

        if filtered_count == 0:
            typer.echo("No rows match the filter condition")
            typer.echo(f"Condition: {where}")
            raise typer.Exit(0)
    else:
        filtered_count = len(df)

    # 6. Build sort columns specification
    sort_columns = [{"column": col, "ascending": not desc} for col in column_list]

    # 7. Sort data
    result = sort_dataframe(df, sort_columns, na_placement=na_placement, limit=rows)
    if is_err(result):
        error = unwrap_err(result)
        typer.echo(f"Error sorting data: {error}", err=True)
        raise typer.Exit(1)

    df_sorted = unwrap(result)
    final_count = len(df_sorted)

    # 8. Display summary
    typer.echo(f"Sorted {final_count} rows")
    typer.echo(f"Columns: {columns}")
    typer.echo(f"Order: {'descending' if desc else 'ascending'}")
    if where:
        typer.echo(f"Filter: {where} ({filtered_count} of {len(read_data_file(file_path, sheet))} rows matched)")
    if na_placement:
        typer.echo(f"NaN placement: {na_placement}")
    typer.echo("")

    # 9. Write or display
    factory = HandlerFactory()
    write_or_display(df_sorted, factory, output, format)


# Create CLI app for this command
app = typer.Typer(help="Sort rows from data files")

# Register the command
app.command()(sort)
