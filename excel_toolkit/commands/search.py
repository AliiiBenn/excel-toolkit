"""Search command implementation.

Search for patterns in a dataset.
"""

from pathlib import Path

import typer
import pandas as pd
import re

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import (
    read_data_file,
    write_or_display,
    display_table,
)


def search(
    file_path: str = typer.Argument(..., help="Path to input file"),
    pattern: str = typer.Option(..., "--pattern", "-p", help="Search pattern (supports regex)"),
    columns: str | None = typer.Option(None, "--columns", "-c", help="Columns to search (comma-separated, default: all)"),
    case_sensitive: bool = typer.Option(False, "--case-sensitive", help="Case-sensitive search"),
    regex: bool = typer.Option(False, "--regex", help="Treat pattern as regular expression"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Search for patterns in a data file.

    Search for specific values or patterns across columns.
    Supports literal text matching and regular expressions.

    Examples:
        xl search data.xlsx --pattern "ERROR" --column "Status"
        xl search data.csv --pattern "^[A-Z]" --regex --columns "Name"
        xl search logs.xlsx --pattern "error|warning" --regex --case-sensitive
    """
    # 1. Validate pattern specified
    if not pattern:
        typer.echo("Error: Must specify --pattern", err=True)
        raise typer.Exit(1)

    # 2. Read file
    df = read_data_file(file_path, sheet)
    original_count = len(df)

    # 3. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 4. Determine columns to search
    if columns:
        column_list = [c.strip() for c in columns.split(",")]
        # Validate columns exist
        missing_cols = [c for c in column_list if c not in df.columns]
        if missing_cols:
            typer.echo(f"Error: Columns not found: {', '.join(missing_cols)}", err=True)
            typer.echo(f"Available columns: {', '.join(df.columns)}")
            raise typer.Exit(1)
        search_columns = column_list
    else:
        # Search all columns
        search_columns = df.columns.tolist()

    # 5. Compile regex pattern if needed
    flags = 0 if case_sensitive else re.IGNORECASE

    if regex:
        try:
            search_pattern = re.compile(pattern, flags)
        except re.error as e:
            typer.echo(f"Error: Invalid regular expression: {e}", err=True)
            raise typer.Exit(1)
    else:
        # Escape special regex characters for literal search
        pattern_literal = re.escape(pattern)
        search_pattern = re.compile(pattern_literal, flags)

    # 6. Search for pattern
    matches = []

    for col in search_columns:
        # Convert to string for searching
        col_str = df[col].astype(str)

        # Find matches
        mask = col_str.str.contains(search_pattern, regex=True, na=False)
        matching_rows = df[mask]

        if len(matching_rows) > 0:
            # Add column info
            for idx, row in matching_rows.iterrows():
                matches.append({
                    'row': idx,
                    'column': col,
                    'value': row[col]
                })

    match_count = len(matches)

    if match_count == 0:
        typer.echo(f"No matches found for pattern: {pattern}")
        raise typer.Exit(0)

    # 7. Create results DataFrame
    df_results = pd.DataFrame(matches)

    # Get matching rows (unique rows that have at least one match)
    matching_row_indices = df_results['row'].unique()
    df_matched = df.loc[matching_row_indices].reset_index(drop=True)

    # 8. Display summary
    typer.echo(f"Pattern: {pattern}")
    if columns:
        typer.echo(f"Columns: {', '.join(search_columns)}")
    else:
        typer.echo(f"Columns: all columns")
    typer.echo(f"Matches found: {match_count}")
    typer.echo(f"Rows with matches: {len(matching_row_indices)}")
    typer.echo(f"Case sensitive: {case_sensitive}")
    typer.echo(f"Regex: {regex}")
    typer.echo("")

    # 9. Write or display
    factory = HandlerFactory()
    if output:
        write_or_display(df_matched, factory, output, "table")
    else:
        # Display matching rows
        display_table(df_matched)
        # Also show match details
        if match_count > 0:
            typer.echo("")
            typer.echo("Match details:")
            display_table(df_results.head(10))  # Show first 10 matches


# Create CLI app for this command
app = typer.Typer(help="Search for patterns in a data file")

# Register the command
app.command()(search)
