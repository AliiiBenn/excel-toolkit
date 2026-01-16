"""Select command implementation.

Select specific columns from a dataset.
"""

from pathlib import Path

import typer
import pandas as pd
import numpy as np

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import (
    read_data_file,
    write_or_display,
    display_table,
)


def select(
    file_path: str = typer.Argument(..., help="Path to input file"),
    columns: str | None = typer.Option(None, "--columns", "-c", help="Columns to select (comma-separated)"),
    exclude: str | None = typer.Option(None, "--exclude", "-e", help="Columns to exclude (comma-separated)"),
    only_numeric: bool = typer.Option(False, "--only-numeric", help="Select only numeric columns"),
    only_string: bool = typer.Option(False, "--only-string", help="Select only string columns"),
    only_datetime: bool = typer.Option(False, "--only-datetime", help="Select only datetime columns"),
    only_non_empty: bool = typer.Option(False, "--only-non-empty", help="Select only columns with no empty values"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Select specific columns from a data file.

    Select columns by name, type, or exclude unwanted columns.
    Can reorder columns by specifying them in the desired order.

    Examples:
        xl select data.xlsx --columns "id,name,email" --output reduced.xlsx
        xl select data.csv --exclude "temp_column,internal_id"
        xl select large.xlsx --only-numeric --output numbers.xlsx
        xl select data.xlsx --columns "id,name->full_name,email" --output renamed.xlsx
    """
    # 1. Check selection options
    selection_options = [
        columns is not None,
        exclude is not None,
        only_numeric,
        only_string,
        only_datetime,
        only_non_empty
    ]

    if sum(selection_options) == 0:
        typer.echo("Error: At least one selection option must be specified", err=True)
        typer.echo("Available options: --columns, --exclude, --only-numeric, --only-string, --only-datetime, --only-non-empty")
        raise typer.Exit(1)

    if sum(selection_options) > 1:
        typer.echo("Error: Cannot combine multiple selection options", err=True)
        typer.echo("Use only one of: --columns, --exclude, --only-numeric, --only-string, --only-datetime, --only-non-empty")
        raise typer.Exit(1)

    # 2. Read file
    df = read_data_file(file_path, sheet)
    original_count = len(df)
    original_cols = len(df.columns)

    # 3. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 4. Determine columns to select
    selected_columns = []

    if columns:
        # Parse column list with potential renaming
        column_specs = [c.strip() for c in columns.split(",")]
        selected_columns = column_specs
    elif exclude:
        # Exclude specified columns
        exclude_list = [c.strip() for c in exclude.split(",")]
        # Validate excluded columns exist
        missing_cols = [c for c in exclude_list if c not in df.columns]
        if missing_cols:
            typer.echo(f"Error: Columns to exclude not found: {', '.join(missing_cols)}", err=True)
            typer.echo(f"Available columns: {', '.join(df.columns)}")
            raise typer.Exit(1)
        selected_columns = [c for c in df.columns if c not in exclude_list]
    elif only_numeric:
        selected_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    elif only_string:
        selected_columns = df.select_dtypes(include=['object']).columns.tolist()
    elif only_datetime:
        selected_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
    elif only_non_empty:
        selected_columns = [col for col in df.columns if df[col].notna().all()]

    if not selected_columns:
        typer.echo("No columns match the selection criteria")
        raise typer.Exit(0)

    # 5. Validate and select columns
    if columns:
        # Parse original column names (before renaming)
        column_names = []
        rename_mapping = {}

        for spec in selected_columns:
            if "->" in spec:
                # Has renaming: "old_name->new_name"
                parts = spec.split("->")
                original_name = parts[0].strip()
                new_name = parts[1].strip()
                column_names.append(original_name)
                rename_mapping[original_name] = new_name
            else:
                # No renaming
                column_names.append(spec)

        # Validate columns exist
        missing_cols = [c for c in column_names if c not in df.columns]
        if missing_cols:
            typer.echo(f"Error: Columns not found: {', '.join(missing_cols)}", err=True)
            typer.echo(f"Available columns: {', '.join(df.columns)}")
            raise typer.Exit(1)

        # Select columns
        df_selected = df[column_names].copy()

        # Apply renaming if specified
        if rename_mapping:
            df_selected = df_selected.rename(columns=rename_mapping)
            selected_column_names = [rename_mapping.get(c, c) for c in column_names]
        else:
            selected_column_names = column_names
    else:
        # For other selection methods
        try:
            df_selected = df[selected_columns].copy()
        except Exception as e:
            typer.echo(f"Error selecting columns: {str(e)}", err=True)
            raise typer.Exit(1)

        selected_column_names = selected_columns

    # 6. Display summary
    typer.echo(f"Selected {len(selected_column_names)} of {original_cols} columns")
    if columns:
        typer.echo(f"Columns: {', '.join(selected_column_names)}")
    elif exclude:
        typer.echo(f"Excluded: {exclude}")
    elif only_numeric:
        typer.echo("Filter: numeric columns only")
    elif only_string:
        typer.echo("Filter: string columns only")
    elif only_datetime:
        typer.echo("Filter: datetime columns only")
    elif only_non_empty:
        typer.echo("Filter: columns with no empty values")
    typer.echo(f"Rows: {original_count}")
    typer.echo("")

    # 7. Handle dry-run mode
    if dry_run:
        typer.echo("Preview of selected data:")
        preview_rows = min(5, original_count)
        display_table(df_selected.head(preview_rows))
        raise typer.Exit(0)

    # 8. Write or display
    factory = HandlerFactory()
    write_or_display(df_selected, factory, output, "table")


# Create CLI app for this command
app = typer.Typer(help="Select specific columns from a data file")

# Register the command
app.command()(select)
