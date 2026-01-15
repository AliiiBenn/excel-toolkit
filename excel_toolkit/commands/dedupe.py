"""Dedupe command implementation.

Remove duplicate rows from a dataset.
"""

from pathlib import Path
from typing import Any

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory, ExcelHandler, CSVHandler
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import display_table


def dedupe(
    file_path: str = typer.Argument(..., help="Path to input file"),
    by: str | None = typer.Option(None, "--by", "-b", help="Columns to use for deduplication (comma-separated)"),
    keep: str = typer.Option("first", "--keep", "-k", help="Which duplicate to keep: first, last, or none"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Remove duplicate rows from a data file.

    Remove duplicates based on all columns or specific key columns.
    Control which occurrence to keep (first, last) or remove all duplicates.

    Examples:
        xl dedupe data.xlsx --by "email" --keep first --output unique.xlsx
        xl dedupe data.csv --keep last --output latest.xlsx
        xl dedupe contacts.xlsx --output clean.xlsx
    """
    path = Path(file_path)
    factory = HandlerFactory()

    # Step 1: Validate file exists
    if not path.exists():
        typer.echo(f"File not found: {file_path}", err=True)
        raise typer.Exit(1)

    # Step 2: Validate keep option
    valid_keep_values = ["first", "last", "none"]
    if keep not in valid_keep_values:
        typer.echo(f"Error: Invalid keep value '{keep}'", err=True)
        typer.echo(f"Valid values: {', '.join(valid_keep_values)}")
        raise typer.Exit(1)

    # Step 3: Get handler
    handler_result = factory.get_handler(path)
    if is_err(handler_result):
        error = unwrap_err(handler_result)
        typer.echo(f"{error}", err=True)
        raise typer.Exit(1)

    handler = unwrap(handler_result)

    # Step 4: Read file
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

    # Step 5: Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # Step 6: Parse columns for deduplication
    subset = None
    if by:
        column_list = [c.strip() for c in by.split(",")]
        # Validate columns exist
        missing_cols = [c for c in column_list if c not in df.columns]
        if missing_cols:
            typer.echo(f"Error: Columns not found: {', '.join(missing_cols)}", err=True)
            typer.echo(f"Available columns: {', '.join(df.columns)}")
            raise typer.Exit(1)
        subset = column_list

    # Step 7: Identify duplicates
    # Count duplicates before removal
    if keep == "none":
        # Remove ALL occurrences of duplicates
        duplicated_mask = df.duplicated(subset=subset, keep=False)
        duplicate_count = duplicated_mask.sum()
    else:
        # Keep first or last occurrence
        duplicated_mask = df.duplicated(subset=subset, keep=keep)
        duplicate_count = duplicated_mask.sum()

    if duplicate_count == 0:
        typer.echo("No duplicates found")
        if not dry_run and not output:
            # Display data if no duplicates and no output
            display_table(df)
        raise typer.Exit(0)

    # Step 8: Remove duplicates
    if keep == "none":
        # Remove all rows that have duplicates
        df_dedupe = df[~duplicated_mask].copy()
    else:
        # Keep first or last occurrence
        df_dedupe = df[~duplicated_mask].copy()

    deduped_count = len(df_dedupe)
    removed_count = original_count - deduped_count

    # Step 9: Display summary
    typer.echo(f"Original rows: {original_count}")
    typer.echo(f"Duplicate rows found: {duplicate_count}")
    typer.echo(f"Rows removed: {removed_count}")
    typer.echo(f"Remaining rows: {deduped_count}")
    if subset:
        typer.echo(f"Key columns: {', '.join(subset)}")
    else:
        typer.echo("Key columns: all columns")
    typer.echo(f"Keep strategy: {keep}")
    typer.echo("")

    # Step 10: Handle dry-run mode
    if dry_run:
        typer.echo("Preview of deduplicated data:")
        preview_rows = min(5, deduped_count)
        display_table(df_dedupe.head(preview_rows))

        if removed_count > 0:
            typer.echo("")
            typer.echo("Preview of removed duplicate rows:")
            removed_rows = min(5, removed_count)
            if keep == "none":
                # Show all duplicate rows (both first and subsequent occurrences)
                all_dupes = df[df.duplicated(subset=subset, keep=False) | df.duplicated(subset=subset, keep=False)]
                # Get unique duplicate rows for preview
                display_table(all_dupes.head(removed_rows))
            else:
                # Show only the rows that were removed
                display_table(df[duplicated_mask].head(removed_rows))
        raise typer.Exit(0)

    # Step 11: Write output or display
    if output:
        output_path = Path(output)
        write_result = factory.write_file(df_dedupe, output_path)
        if is_err(write_result):
            error = unwrap_err(write_result)
            typer.echo(f"Error writing file: {error}", err=True)
            raise typer.Exit(1)
        typer.echo(f"Written to: {output}")
    else:
        # Display data
        display_table(df_dedupe)


# Create CLI app for this command
app = typer.Typer(help="Remove duplicate rows from a data file")

# Register the command
app.command()(dedupe)
