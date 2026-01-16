"""Append command implementation.

Concatenate multiple datasets vertically by adding rows.
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
)


def append(
    main_file: str = typer.Argument(..., help="Path to main input file"),
    additional_files: list[str] = typer.Argument(..., help="Paths to files to append"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    ignore_index: bool = typer.Option(False, "--ignore-index", help="Reset index in result"),
    sort: bool = typer.Option(False, "--sort", help="Sort result by first column"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
    additional_sheets: list[str] = typer.Option(None, "--sheet", help="Sheet names for additional files"),
) -> None:
    """Append datasets from multiple files vertically.

    Concatenate rows from multiple files into a single dataset.
    All files must have the same column structure.

    Examples:
        xl append main.xlsx data2.xlsx data3.xlsx --output combined.xlsx
        xl append main.csv extra.csv --ignore-index --output combined.csv
        xl append main.xlsx additional.xlsx --sort --output sorted.xlsx
    """
    # 1. Read main file
    main_df = read_data_file(main_file, sheet)

    # 2. Handle empty main file
    if main_df.empty:
        typer.echo("Main file is empty (no data rows)")
        raise typer.Exit(0)

    # 3. Read and append additional files
    dfs = [main_df]
    total_main_rows = len(main_df)

    for i, file_path in enumerate(additional_files):
        # Determine sheet name for this file
        file_sheet = None
        if additional_sheets and i < len(additional_sheets):
            file_sheet = additional_sheets[i]

        # Read file using helper
        file_df = read_data_file(str(file_path), file_sheet)

        # Check column compatibility
        if not file_df.empty:
            if list(file_df.columns) != list(main_df.columns):
                typer.echo(f"Warning: Column mismatch in {Path(file_path).name}", err=True)
                typer.echo(f"  Expected: {', '.join(main_df.columns)}", err=True)
                typer.echo(f"  Found: {', '.join(file_df.columns)}", err=True)
                typer.echo("  Attempting to align columns...", err=True)

                # Align columns
                file_df = file_df.reindex(columns=main_df.columns)

            dfs.append(file_df)

    # 4. Concatenate all DataFrames
    if ignore_index:
        result_df = pd.concat(dfs, ignore_index=True)
    else:
        result_df = pd.concat(dfs)

    total_rows = len(result_df)
    appended_rows = total_rows - total_main_rows

    # 5. Sort if requested
    if sort:
        first_col = result_df.columns[0]
        result_df = result_df.sort_values(by=first_col)
        result_df = result_df.reset_index(drop=True)

    # 6. Display summary
    typer.echo(f"Main file rows: {total_main_rows}")
    typer.echo(f"Appended rows: {appended_rows}")
    typer.echo(f"Total rows: {total_rows}")
    typer.echo(f"Files processed: {len(dfs)}")
    typer.echo("")

    # 7. Write or display
    factory = HandlerFactory()
    if output:
        write_or_display(result_df, factory, output, "table")
    else:
        # Display result
        display_table(result_df.head(20))
        if total_rows > 20:
            typer.echo(f"\n... and {total_rows - 20} more rows")


# Create CLI app for this command
app = typer.Typer(help="Append multiple datasets vertically")

# Register the command
app.command()(append)
