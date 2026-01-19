"""Common utilities for commands.

This module contains shared functions for formatting and displaying data
across different commands.
"""

from pathlib import Path
from typing import Any
import pandas as pd
import json
import typer
from tabulate import tabulate

from excel_toolkit.core import HandlerFactory, ExcelHandler, CSVHandler
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err


def display_table(
    df: pd.DataFrame,
    max_rows: int | None = None,
    max_columns: int | None = None,
    max_col_width: int = 20,
) -> None:
    """Display DataFrame as formatted ASCII table.

    Args:
        df: DataFrame to display
        max_rows: Maximum rows to display (None = all)
        max_columns: Maximum columns to display (None = all)
        max_col_width: Maximum width for column values
    """
    # Limit rows if specified
    if max_rows is not None and len(df) > max_rows:
        df = df.head(max_rows)

    # Limit columns if specified
    if max_columns is not None and len(df.columns) > max_columns:
        df = df.iloc[:, :max_columns]

    # Truncate long values
    df_truncated = df.copy()
    for col in df_truncated.columns:
        df_truncated[col] = df_truncated[col].apply(
            lambda x: _truncate_value(x, max_col_width) if pd.notna(x) else x
        )

    # Convert to list format for tabulate
    table_data = [df_truncated.columns.tolist()] + df_truncated.values.tolist()

    # Display with tabulate
    print(tabulate(table_data, headers="firstrow", tablefmt="grid"))


def display_csv(df: pd.DataFrame) -> None:
    """Display DataFrame as CSV.

    Args:
        df: DataFrame to display
    """
    print(df.to_csv(index=False))


def display_json(df: pd.DataFrame, indent: int = 2) -> None:
    """Display DataFrame as JSON.

    Args:
        df: DataFrame to display
        indent: JSON indentation spaces
    """
    # Convert DataFrame to dict records
    records = df.to_dict(orient="records")

    # Handle NaN values (convert to None)
    def clean_nan(obj: Any) -> Any:
        if isinstance(obj, float):
            if pd.isna(obj):
                return None
        return obj

    records_cleaned = [{k: clean_nan(v) for k, v in record.items()} for record in records]

    # Print JSON
    print(json.dumps(records_cleaned, indent=indent, default=str))


def display_column_types(df: pd.DataFrame) -> None:
    """Display column names and their data types.

    Args:
        df: DataFrame to analyze
    """
    print("\nColumns:")
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        null_count = len(df) - non_null
        print(f"  - {col} ({dtype})" + (f" [{null_count} nulls]" if null_count > 0 else ""))


def truncate_dataframe(df: pd.DataFrame, max_rows: int) -> pd.DataFrame:
    """Truncate DataFrame to first N rows.

    Args:
        df: DataFrame to truncate
        max_rows: Maximum number of rows

    Returns:
        Truncated DataFrame
    """
    return df.head(max_rows)


def _truncate_value(value: Any, max_width: int) -> str:
    """Truncate a value to maximum width.

    Args:
        value: Value to truncate
        max_width: Maximum width

    Returns:
        Truncated string representation
    """
    str_val = str(value)
    if len(str_val) > max_width:
        return str_val[: max_width - 3] + "..."
    return str_val


def format_file_info(path: str, sheet: str | None = None, total_rows: int = 0, total_cols: int = 0) -> str:
    """Format file information string.

    Args:
        path: File path
        sheet: Sheet name (for Excel)
        total_rows: Total number of rows
        total_cols: Total number of columns

    Returns:
        Formatted information string
    """
    from pathlib import Path

    path_obj = Path(path)
    lines = [f"File: {path_obj.name}"]

    if sheet:
        lines.append(f"Sheet: {sheet}")

    if total_rows > 0:
        lines.append(f"Showing data ({total_rows} rows x {total_cols} columns)")

    return "\n".join(lines)


# =============================================================================
# Helper Functions for Command Refactoring (Phase 3)
# =============================================================================


def read_data_file(
    file_path: str,
    sheet: str | None = None,
) -> pd.DataFrame:
    """Read a data file (Excel or CSV) with auto-detection.

    This function handles the common pattern of reading Excel or CSV files
    with automatic encoding and delimiter detection for CSV files.

    Args:
        file_path: Path to input file
        sheet: Sheet name for Excel files (optional)

    Returns:
        DataFrame with file contents

    Raises:
        typer.Exit: If file cannot be read (always exits with code 1)
    """
    path = Path(file_path)

    # Validate file exists
    if not path.exists():
        typer.echo(f"File not found: {file_path}", err=True)
        raise typer.Exit(1)

    factory = HandlerFactory()

    # Get appropriate handler
    handler_result = factory.get_handler(path)
    if is_err(handler_result):
        error = unwrap_err(handler_result)
        typer.echo(f"{error}", err=True)
        raise typer.Exit(1)

    handler = unwrap(handler_result)

    # Read file based on handler type
    if isinstance(handler, ExcelHandler):
        kwargs = {"sheet_name": sheet} if sheet else {}
        read_result = handler.read(path, **kwargs)
    elif isinstance(handler, CSVHandler):
        # Auto-detect encoding
        encoding_result = handler.detect_encoding(path)
        encoding = unwrap(encoding_result) if is_ok(encoding_result) else "utf-8"

        # Auto-detect delimiter
        delimiter_result = handler.detect_delimiter(path, encoding)
        delimiter = unwrap(delimiter_result) if is_ok(delimiter_result) else ","

        read_result = handler.read(path, encoding=encoding, delimiter=delimiter)
    else:
        typer.echo("Unsupported file type", err=True)
        raise typer.Exit(1)

    # Check for read errors
    if is_err(read_result):
        error = unwrap_err(read_result)
        typer.echo(f"Error reading file: {error}", err=True)
        raise typer.Exit(1)

    return unwrap(read_result)


def write_or_display(
    df: pd.DataFrame,
    factory: HandlerFactory,
    output: str | None,
    format: str,
) -> None:
    """Write DataFrame to file or display to console.

    This function handles the common pattern of either writing results to
    a file or displaying them in the specified format.

    Args:
        df: DataFrame to write/display
        factory: HandlerFactory for writing files
        output: Output file path (None = display to console)
        format: Display format (table, csv, json)

    Raises:
        typer.Exit: If write operation fails (exits with code 1)
    """
    if output:
        # Write to file
        output_path = Path(output)
        write_result = factory.write_file(df, output_path)
        if is_err(write_result):
            error = unwrap_err(write_result)
            typer.echo(f"Error writing file: {error}", err=True)
            raise typer.Exit(1)
        typer.echo(f"Written to: {output}")
    else:
        # Display to console
        if format == "table":
            display_table(df)
        elif format == "csv":
            display_csv(df)
        elif format == "json":
            display_json(df)
        else:
            typer.echo(f"Unknown format: {format}", err=True)
            typer.echo("Supported formats: table, csv, json")
            raise typer.Exit(1)


def resolve_column_reference(
    col_ref: str,
    df: pd.DataFrame,
) -> str:
    """Resolve a column reference to a column name.

    Supports both column names and position-based indexing:
    - Integer N: Column at position N (1-based)
    - Negative integer -N: Nth column from end (-1 = last column)
    - String: Column name (existing behavior)

    Args:
        col_ref: Column reference (name or index)
        df: DataFrame to resolve column from

    Returns:
        Resolved column name

    Raises:
        typer.Exit: If column reference is invalid
    """
    columns = df.columns.tolist()
    num_cols = len(columns)

    # Try to parse as integer index
    try:
        idx = int(col_ref)

        # Handle negative indexing (Python-style)
        if idx < 0:
            idx = num_cols + idx  # -1 becomes last column

        # Convert to 0-based index
        idx -= 1

        # Validate index is in range
        if idx < 0 or idx >= num_cols:
            typer.echo(
                f"Error: Column index {col_ref} out of range (file has {num_cols} columns)",
                err=True
            )
            typer.echo(f"Valid range: 1 to {num_cols} (or -1 to -{num_cols} for positions from end)")
            raise typer.Exit(1)

        return columns[idx]

    except ValueError:
        # Not an integer, treat as column name
        if col_ref not in columns:
            available = ", ".join(columns[:10])
            if num_cols > 10:
                available += f", ... ({num_cols} total)"
            typer.echo(f"Error: Column '{col_ref}' not found", err=True)
            typer.echo(f"Available columns: {available}")
            raise typer.Exit(1)
        return col_ref


def resolve_column_references(
    col_refs: list[str],
    df: pd.DataFrame,
) -> list[str]:
    """Resolve multiple column references to column names.

    Args:
        col_refs: List of column references (names or indices)
        df: DataFrame to resolve columns from

    Returns:
        List of resolved column names

    Raises:
        typer.Exit: If any column reference is invalid
    """
    return [resolve_column_reference(ref, df) for ref in col_refs]


def handle_operation_error(error: Exception) -> None:
    """Handle operation errors with user-friendly messages.

    This function converts operation errors into user-friendly error messages
    and exits with appropriate error code.

    Args:
        error: Error from operation (Result Err variant)

    Raises:
        typer.Exit: Always exits with error code 1
    """
    error_type = type(error).__name__
    error_msg = str(error)

    # Map error types to user-friendly messages using match/case
    match error_type:
        case et if "ColumnNotFoundError" in et:
            typer.echo(f"Error: {error_msg}", err=True)
        case et if "TypeMismatchError" in et:
            typer.echo(f"Type mismatch: {error_msg}", err=True)
        case et if "ValueOutOfRangeError" in et:
            typer.echo(f"Value out of range: {error_msg}", err=True)
        case et if "InvalidConditionError" in et:
            typer.echo(f"Invalid condition: {error_msg}", err=True)
        case et if "FilteringError" in et:
            typer.echo(f"Filter error: {error_msg}", err=True)
        case et if "SortingError" in et:
            typer.echo(f"Sort error: {error_msg}", err=True)
        case et if "PivotingError" in et:
            typer.echo(f"Pivot error: {error_msg}", err=True)
        case et if "AggregatingError" in et:
            typer.echo(f"Aggregation error: {error_msg}", err=True)
        case et if "ComparingError" in et:
            typer.echo(f"Comparison error: {error_msg}", err=True)
        case et if "CleaningError" in et:
            typer.echo(f"Cleaning error: {error_msg}", err=True)
        case et if "TransformingError" in et:
            typer.echo(f"Transform error: {error_msg}", err=True)
        case et if "JoiningError" in et:
            typer.echo(f"Join error: {error_msg}", err=True)
        case et if "ValidationError" in et:
            typer.echo(f"Validation error: {error_msg}", err=True)
        case _:
            # Generic error handling
            typer.echo(f"Error: {error_msg}", err=True)

    raise typer.Exit(1)
