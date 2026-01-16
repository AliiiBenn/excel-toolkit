"""Rename command implementation.

Rename columns in a dataset.
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
    # 1. Validate mapping specified
    if not mapping:
        typer.echo("Error: Must specify --mapping", err=True)
        raise typer.Exit(1)

    # 2. Parse mapping
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

    # 3. Read file
    df = read_data_file(file_path, sheet)
    original_count = len(df)
    original_cols = len(df.columns)

    # 4. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 5. Validate old column names exist
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

    # 6. Apply rename
    df_renamed = df.rename(columns=rename_dict)

    # 7. Display summary
    renamed_count = len(rename_dict)
    typer.echo(f"Renamed {renamed_count} column(s)")
    for old_name, new_name in rename_dict.items():
        typer.echo(f"  {old_name} -> {new_name}")
    typer.echo(f"Rows: {original_count}")
    typer.echo("")

    # 8. Handle dry-run mode
    if dry_run:
        typer.echo("Preview of renamed data:")
        preview_rows = min(5, original_count)
        display_table(df_renamed.head(preview_rows))
        raise typer.Exit(0)

    # 9. Write or display
    factory = HandlerFactory()
    write_or_display(df_renamed, factory, output, "table")


# Create CLI app for this command
app = typer.Typer(help="Rename columns in a data file")

# Register the command
app.command()(rename)
