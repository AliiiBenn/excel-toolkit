"""Common utilities for commands.

This module contains shared functions for formatting and displaying data
across different commands.
"""

from typing import Any
import pandas as pd
import json
from tabulate import tabulate


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
