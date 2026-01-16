"""Compare command implementation.

Compare two files or sheets to identify differences.
"""

from pathlib import Path

import typer

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.comparing import (
    compare_dataframes,
    ComparisonResult,
)
from excel_toolkit.commands.common import (
    read_data_file,
    write_or_display,
)


def compare(
    file1: str = typer.Argument(..., help="Path to first file (baseline)"),
    file2: str = typer.Argument(..., help="Path to second file (comparison)"),
    key_columns: str | None = typer.Option(None, "--key-columns", "-k", help="Columns to use as key for matching rows (comma-separated)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    show_diffs_only: bool = typer.Option(False, "--diffs-only", "-d", help="Show only differing rows"),
    sheet1: str | None = typer.Option(None, "--sheet1", "-s1", help="Sheet name for first file"),
    sheet2: str | None = typer.Option(None, "--sheet2", "-s2", help="Sheet name for second file"),
) -> None:
    """Compare two files or sheets to identify differences.

    Compare two datasets row by row or by key columns to identify added, deleted, and modified rows.

    Examples:
        xl compare old.xlsx new.xlsx --output differences.xlsx
        xl compare baseline.csv current.csv --key-columns "ID" --output changes.xlsx
        xl compare data1.xlsx data2.xlsx --key-columns "ID,Date" --diffs-only --output changes.xlsx
        xl compare old.xlsx new.xlsx --sheet1 "Sheet1" --sheet2 "Sheet2" --output diff.xlsx
    """
    # 1. Read both files
    df1 = read_data_file(file1, sheet1)
    df2 = read_data_file(file2, sheet2)

    # 2. Handle empty files
    if df1.empty and df2.empty:
        typer.echo("Both files are empty")
        raise typer.Exit(0)

    if df1.empty:
        typer.echo(f"File1 is empty, File2 has {len(df2)} rows")
        # Mark all as added
        df2['_diff_status'] = 'added'
        factory = HandlerFactory()
        write_or_display(df2, factory, output, "table")
        raise typer.Exit(0)

    if df2.empty:
        typer.echo(f"File2 is empty, File1 has {len(df1)} rows")
        # Mark all as deleted
        df1['_diff_status'] = 'deleted'
        factory = HandlerFactory()
        write_or_display(df1, factory, output, "table")
        raise typer.Exit(0)

    # 3. Parse key columns
    key_cols = None
    if key_columns:
        key_cols = [c.strip() for c in key_columns.split(",")]

    # 4. Compare dataframes
    result = compare_dataframes(df1, df2, key_cols)
    if is_err(result):
        error = unwrap_err(result)
        typer.echo(f"Error comparing data: {error}", err=True)
        raise typer.Exit(1)

    comparison: ComparisonResult = unwrap(result)

    # 5. Display summary
    typer.echo(f"File1 ({file1}): {len(df1)} rows")
    typer.echo(f"File2 ({file2}): {len(df2)} rows")
    typer.echo("")
    typer.echo(f"Added rows: {comparison.added_count}")
    typer.echo(f"Deleted rows: {comparison.deleted_count}")
    typer.echo(f"Modified rows: {comparison.modified_count}")
    total_diffs = comparison.added_count + comparison.deleted_count + comparison.modified_count
    typer.echo(f"Total differences: {total_diffs}")
    typer.echo("")

    if total_diffs == 0:
        typer.echo("No differences found - files are identical")
        raise typer.Exit(0)

    # 6. Filter if diffs only requested
    df_result = comparison.df_result
    if show_diffs_only:
        df_result = df_result[df_result['_diff_status'] != 'unchanged']
        if df_result.empty:
            typer.echo("No differences to display")
            raise typer.Exit(0)

    # 7. Write or display
    factory = HandlerFactory()
    write_or_display(df_result, factory, output, "table")


# Create CLI app for this command
app = typer.Typer(help="Compare two files or sheets")

# Register the command
app.command()(compare)
