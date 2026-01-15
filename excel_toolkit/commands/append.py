"""Append command implementation.

Concatenate multiple datasets vertically by adding rows.
"""

from pathlib import Path
from typing import Any

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory, ExcelHandler, CSVHandler
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import display_table


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
    factory = HandlerFactory()

    # Step 1: Validate all files exist
    main_path = Path(main_file)
    if not main_path.exists():
        typer.echo(f"Main file not found: {main_file}", err=True)
        raise typer.Exit(1)

    additional_paths = [Path(f) for f in additional_files]
    for f in additional_paths:
        if not f.exists():
            typer.echo(f"File not found: {f}", err=True)
            raise typer.Exit(1)

    # Step 2: Read main file
    handler_result = factory.get_handler(main_path)
    if is_err(handler_result):
        error = unwrap_err(handler_result)
        typer.echo(f"{error}", err=True)
        raise typer.Exit(1)

    handler = unwrap(handler_result)

    # Read main file
    if isinstance(handler, ExcelHandler):
        sheet_name = sheet
        kwargs = {"sheet_name": sheet_name} if sheet_name else {}
        read_result = handler.read(main_path, **kwargs)
    elif isinstance(handler, CSVHandler):
        encoding_result = handler.detect_encoding(main_path)
        encoding = unwrap(encoding_result) if is_ok(encoding_result) else "utf-8"

        delimiter_result = handler.detect_delimiter(main_path, encoding)
        delimiter = unwrap(delimiter_result) if is_ok(delimiter_result) else ","

        read_result = handler.read(main_path, encoding=encoding, delimiter=delimiter)
    else:
        typer.echo("Unsupported handler type", err=True)
        raise typer.Exit(1)

    if is_err(read_result):
        error = unwrap_err(read_result)
        typer.echo(f"Error reading main file: {error}", err=True)
        raise typer.Exit(1)

    main_df = unwrap(read_result)

    # Step 3: Handle empty main file
    if main_df.empty:
        typer.echo("Main file is empty (no data rows)")
        raise typer.Exit(0)

    # Step 4: Read and append additional files
    dfs = [main_df]
    total_main_rows = len(main_df)

    for i, file_path in enumerate(additional_paths):
        # Get handler for this file
        file_handler_result = factory.get_handler(file_path)
        if is_err(file_handler_result):
            error = unwrap_err(file_handler_result)
            typer.echo(f"Error with file {file_path.name}: {error}", err=True)
            raise typer.Exit(1)

        file_handler = unwrap(file_handler_result)

        # Determine sheet name for this file
        file_sheet = None
        if additional_sheets and i < len(additional_sheets):
            file_sheet = additional_sheets[i]

        # Read file
        if isinstance(file_handler, ExcelHandler):
            kwargs = {"sheet_name": file_sheet} if file_sheet else {}
            file_read_result = file_handler.read(file_path, **kwargs)
        elif isinstance(file_handler, CSVHandler):
            enc_result = file_handler.detect_encoding(file_path)
            file_encoding = unwrap(enc_result) if is_ok(enc_result) else "utf-8"

            del_result = file_handler.detect_delimiter(file_path, file_encoding)
            file_delimiter = unwrap(del_result) if is_ok(del_result) else ","

            file_read_result = file_handler.read(file_path, encoding=file_encoding, delimiter=file_delimiter)
        else:
            typer.echo(f"Unsupported file type: {file_path.name}", err=True)
            raise typer.Exit(1)

        if is_err(file_read_result):
            error = unwrap_err(file_read_result)
            typer.echo(f"Error reading {file_path.name}: {error}", err=True)
            raise typer.Exit(1)

        file_df = unwrap(file_read_result)

        # Check column compatibility
        if not file_df.empty:
            if list(file_df.columns) != list(main_df.columns):
                typer.echo(f"Warning: Column mismatch in {file_path.name}", err=True)
                typer.echo(f"  Expected: {', '.join(main_df.columns)}", err=True)
                typer.echo(f"  Found: {', '.join(file_df.columns)}", err=True)
                typer.echo("  Attempting to align columns...", err=True)

                # Align columns
                file_df = file_df.reindex(columns=main_df.columns)

            dfs.append(file_df)

    # Step 5: Concatenate all DataFrames
    if ignore_index:
        result_df = pd.concat(dfs, ignore_index=True)
    else:
        result_df = pd.concat(dfs)

    total_rows = len(result_df)
    appended_rows = total_rows - total_main_rows

    # Step 6: Sort if requested
    if sort:
        first_col = result_df.columns[0]
        result_df = result_df.sort_values(by=first_col)
        result_df = result_df.reset_index(drop=True)

    # Step 7: Display summary
    typer.echo(f"Main file rows: {total_main_rows}")
    typer.echo(f"Appended rows: {appended_rows}")
    typer.echo(f"Total rows: {total_rows}")
    typer.echo(f"Files processed: {len(dfs)}")
    typer.echo("")

    # Step 8: Write output or display
    if output:
        output_path = Path(output)
        write_result = factory.write_file(result_df, output_path)
        if is_err(write_result):
            error = unwrap_err(write_result)
            typer.echo(f"Error writing file: {error}", err=True)
            raise typer.Exit(1)
        typer.echo(f"Written to: {output}")
    else:
        # Display result
        display_table(result_df.head(20))
        if total_rows > 20:
            typer.echo(f"\n... and {total_rows - 20} more rows")


# Create CLI app for this command
app = typer.Typer(help="Append multiple datasets vertically")

# Register the command
app.command()(append)
