"""Merge command implementation.

Merge multiple files vertically.
"""

from pathlib import Path
from typing import Any
import glob

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import (
    read_data_file,
    write_or_display,
)


def merge(
    files: str = typer.Option(..., "--files", "-f", help="Input files (comma-separated, supports wildcards)"),
    output: str = typer.Option(..., "--output", "-o", help="Output file path"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
    ignore_index: bool = typer.Option(False, "--ignore-index", help="Reset index in merged file"),
) -> None:
    """Merge multiple files vertically.

    Combine multiple files by stacking rows on top of each other.
    All files must have the same columns.

    Examples:
        xl merge --files file1.xlsx,file2.xlsx,file3.xlsx --output combined.xlsx
        xl merge --files "data/*.csv" --output all-data.csv
        xl merge --files file1.xlsx,file2.xlsx --output merged.xlsx --ignore-index
    """
    output_path = Path(output)
    factory = HandlerFactory()

    # 1. Expand file paths (handle wildcards)
    expanded_paths = []
    for file_pattern in files.split(","):
        file_pattern = file_pattern.strip()
        # Check if it contains wildcards
        if '*' in file_pattern or '?' in file_pattern:
            matched = glob.glob(file_pattern)
            if not matched:
                typer.echo(f"Error: No files found matching pattern: {file_pattern}", err=True)
                raise typer.Exit(1)
            expanded_paths.extend([Path(p) for p in sorted(matched)])
        else:
            path = Path(file_pattern)
            if not path.exists():
                typer.echo(f"Error: File not found: {file_pattern}", err=True)
                raise typer.Exit(1)
            expanded_paths.append(path)

    if not expanded_paths:
        typer.echo("Error: No files to merge", err=True)
        raise typer.Exit(1)

    # 2. Read all files
    dfs = []
    columns_per_file = []
    rows_per_file = []

    for file_path in expanded_paths:
        # Read file using helper
        df = read_data_file(str(file_path), sheet)
        dfs.append(df)
        columns_per_file.append(set(df.columns))
        rows_per_file.append(len(df))

    # 3. Check if all files have the same columns
    if len(columns_per_file) > 1:
        first_columns = columns_per_file[0]
        for i, cols in enumerate(columns_per_file[1:], 1):
            if cols != first_columns:
                typer.echo(f"Error: Column mismatch in file {i}", err=True)
                typer.echo(f"Expected columns: {sorted(first_columns)}")
                typer.echo(f"Found columns: {sorted(cols)}")
                raise typer.Exit(1)

    # 4. Merge DataFrames
    try:
        df_merged = pd.concat(dfs, ignore_index=ignore_index)
    except Exception as e:
        typer.echo(f"Error merging files: {e}", err=True)
        raise typer.Exit(1)

    # 5. Display summary
    typer.echo(f"Files merged: {len(expanded_paths)}")
    for i, (file_path, rows) in enumerate(zip(expanded_paths, rows_per_file), 1):
        typer.echo(f"  {i}. {file_path.name}: {rows} rows")
    typer.echo(f"Total rows: {len(df_merged)}")
    typer.echo(f"Total columns: {len(df_merged.columns)}")
    typer.echo("")

    # 6. Write output
    write_result = factory.write_file(df_merged, output_path)
    if is_err(write_result):
        error = unwrap_err(write_result)
        typer.echo(f"Error writing file: {error}", err=True)
        raise typer.Exit(1)

    typer.echo(f"Written to: {output}")


# Create CLI app for this command
app = typer.Typer(help="Merge multiple files vertically")

# Register the command
app.command()(merge)
