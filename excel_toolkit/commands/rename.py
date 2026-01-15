"""Rename command implementation.

Rename columns in a dataset.
"""

from pathlib import Path
from typing import Any

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory, ExcelHandler, CSVHandler
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import display_table


def rename(
    file_path: str = typer.Argument(..., help="Path to input file"),
    mapping: str = typer.Option(..., "--mapping", "-m", help="Column rename mapping: old:new (comma-separated)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Rename columns in a data file.

    Rename columns using old_name:new_name format.

    Examples:
        xl rename data.xlsx --mapping "old_name:new_name,first_name:fname" --output renamed.xlsx
        xl rename data.csv --mapping "id:ID,name:FullName" --output renamed.csv
    """
    path = Path(file_path)
    factory = HandlerFactory()

    # Step 1: Validate file exists
    if not path.exists():
        typer.echo(f"File not found: {file_path}", err=True)
        raise typer.Exit(1)

    # Step 2: Validate mapping specified
    if not mapping:
        typer.echo("Error: Must specify --mapping", err=True)
        raise typer.Exit(1)

    # Step 3: Parse mapping
    rename_dict = {}
    parse_errors = []

    for spec in mapping.split(","):
        spec = spec.strip()
        if ":" not in spec:
            parse_errors.append(f"Invalid format: '{spec}' (expected old:new)")
            continue

        old_name, new_name = spec.split(":", 1)
        old_name = old_name.strip()
        new_name = new_name.strip()

        if not old_name or not new_name:
            parse_errors.append(f"Empty name in '{spec}'")
            continue

        if old_name in rename_dict:
            parse_errors.append(f"Duplicate old name '{old_name}'")
            continue

        rename_dict[old_name] = new_name

    if parse_errors:
        typer.echo("Error parsing mapping:", err=True)
        for error in parse_errors:
            typer.echo(f"  - {error}", err=True)
        raise typer.Exit(1)

    if not rename_dict:
        typer.echo("Error: No valid rename mappings", err=True)
        raise typer.Exit(1)

    # Step 4: Get handler
    handler_result = factory.get_handler(path)
    if is_err(handler_result):
        error = unwrap_err(handler_result)
        typer.echo(f"{error}", err=True)
        raise typer.Exit(1)

    handler = unwrap(handler_result)

    # Step 5: Read file
    if isinstance(handler, ExcelHandler):
        sheet_name = sheet
        kwargs = {"sheet_name": sheet_name} if sheet_name else {}
        read_result = handler.read(path, **kwargs)
    elif isinstance(handler, CSVHandler):
        # Auto-detect encoding and delimiter
        encoding_result = handler.detect_encoding(path)
        encoding = unwrap(encoding_result) if is_ok(encoding_result) else "utf-8"

        delimiter_result = handler.detect_delimiter(path, encoding)
        delimiter = unwrap(delimiter_result) if is_ok(delimiter_result) else ","

        read_result = handler.read(path, encoding=encoding, delimiter=delimiter)
    else:
        typer.echo("Unsupported handler type", err=True)
        raise typer.Exit(1)

    if is_err(read_result):
        error = unwrap_err(read_result)
        typer.echo(f"Error reading file: {error}", err=True)
        raise typer.Exit(1)

    df = unwrap(read_result)
    original_count = len(df)
    original_cols = len(df.columns)

    # Step 6: Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # Step 7: Validate old column names exist
    missing_cols = [old for old in rename_dict.keys() if old not in df.columns]
    if missing_cols:
        typer.echo(f"Error: Columns not found: {', '.join(missing_cols)}", err=True)
        typer.echo(f"Available columns: {', '.join(df.columns)}")
        raise typer.Exit(1)

    # Check for duplicate new names with existing columns
    existing_cols = set(df.columns)
    new_names = set(rename_dict.values())
    overlap = existing_cols & (new_names - set(rename_dict.keys()))
    if overlap:
        typer.echo(f"Error: New column names conflict with existing columns: {', '.join(overlap)}", err=True)
        raise typer.Exit(1)

    # Step 8: Apply rename
    df_renamed = df.rename(columns=rename_dict)

    # Step 9: Display summary
    renamed_count = len(rename_dict)
    typer.echo(f"Renamed {renamed_count} column(s)")
    for old_name, new_name in rename_dict.items():
        typer.echo(f"  {old_name} -> {new_name}")
    typer.echo(f"Rows: {original_count}")
    typer.echo("")

    # Step 10: Handle dry-run mode
    if dry_run:
        typer.echo("Preview of renamed data:")
        preview_rows = min(5, original_count)
        display_table(df_renamed.head(preview_rows))
        raise typer.Exit(0)

    # Step 11: Write output or display
    if output:
        output_path = Path(output)
        write_result = factory.write_file(df_renamed, output_path)
        if is_err(write_result):
            error = unwrap_err(write_result)
            typer.echo(f"Error writing file: {error}", err=True)
            raise typer.Exit(1)
        typer.echo(f"Written to: {output}")
    else:
        # Display data
        display_table(df_renamed)


# Create CLI app for this command
app = typer.Typer(help="Rename columns in a data file")

# Register the command
app.command()(rename)
