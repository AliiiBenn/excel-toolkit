"""Join command implementation.

Join two datasets based on common columns.
"""

from pathlib import Path

import typer

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.joining import join_dataframes
from excel_toolkit.commands.common import (
    read_data_file,
    write_or_display,
)


def join(
    left_file: str = typer.Argument(..., help="Path to left input file"),
    right_file: str = typer.Argument(..., help="Path to right input file"),
    on: str | None = typer.Option(None, "--on", help="Column name to join on (must exist in both files)"),
    left_on: str | None = typer.Option(None, "--left-on", help="Column name in left file"),
    right_on: str | None = typer.Option(None, "--right-on", help="Column name in right file"),
    how: str = typer.Option("inner", "--how", "-h", help="Join type: inner, left, right, outer"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    left_sheet: str | None = typer.Option(None, "--left-sheet", help="Sheet name for left file"),
    right_sheet: str | None = typer.Option(None, "--right-sheet", help="Sheet name for right file"),
) -> None:
    """Join two datasets based on common columns.

    Perform SQL-like joins between two files.
    Supports inner, left, right, and outer joins.

    Examples:
        xl join customers.xlsx orders.xlsx --on "customer_id" --output merged.xlsx
        xl join left.xlsx right.xlsx --left-on "id" --right-on "user_id" --output joined.xlsx
        xl join data1.xlsx data2.xlsx --on "key" --how left --output left_join.xlsx
    """
    # 1. Read both files
    df_left = read_data_file(left_file, left_sheet)
    df_right = read_data_file(right_file, right_sheet)

    # 2. Handle empty files
    if df_left.empty:
        typer.echo("Left file is empty (no data rows)")
        raise typer.Exit(0)

    if df_right.empty:
        typer.echo("Right file is empty (no data rows)")
        raise typer.Exit(0)

    # 3. Parse join columns
    on_cols = None
    left_on_cols = None
    right_on_cols = None

    if on:
        on_cols = [on]
    else:
        if left_on and right_on:
            left_on_cols = [c.strip() for c in left_on.split(",")]
            right_on_cols = [c.strip() for c in right_on.split(",")]
        elif left_on or right_on:
            typer.echo("Error: Must specify both --left-on and --right-on", err=True)
            raise typer.Exit(1)
        else:
            typer.echo("Error: Must specify either --on or both --left-on and --right-on", err=True)
            raise typer.Exit(1)

    # 4. Join dataframes using operation
    result = join_dataframes(
        df_left,
        df_right,
        how=how,
        on=on_cols,
        left_on=left_on_cols,
        right_on=right_on_cols,
        suffixes=("_left", "_right")
    )

    if is_err(result):
        error = unwrap_err(result)
        typer.echo(f"Error joining data: {error}", err=True)
        raise typer.Exit(1)

    df_joined = unwrap(result)

    # 5. Display summary
    joined_rows = len(df_joined)
    left_rows = len(df_left)
    right_rows = len(df_right)

    typer.echo(f"Join type: {how}")
    if on:
        typer.echo(f"On column: {on}")
    else:
        typer.echo(f"Left on: {', '.join(left_on_cols)}")
        typer.echo(f"Right on: {', '.join(right_on_cols)}")
    typer.echo(f"Left rows: {left_rows}")
    typer.echo(f"Right rows: {right_rows}")
    typer.echo(f"Joined rows: {joined_rows}")
    typer.echo("")

    # 6. Write or display
    factory = HandlerFactory()
    write_or_display(df_joined, factory, output, "table")


# Create CLI app for this command
app = typer.Typer(help="Join two datasets based on common columns")

# Register the command
app.command()(join)
