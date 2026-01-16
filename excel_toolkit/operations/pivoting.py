"""Pivoting operations for DataFrames.

This module provides pivot table operations that can be applied to pandas DataFrames.
All functions return Result types for explicit error handling.
"""

from typing import Any

import pandas as pd

from excel_toolkit.fp import ok, err, is_ok, is_err, unwrap, unwrap_err, Result
from excel_toolkit.models.error_types import (
    InvalidFunctionError,
    NoRowsError,
    NoColumnsError,
    NoValuesError,
    RowColumnsNotFoundError,
    ColumnColumnsNotFoundError,
    ValueColumnsNotFoundError,
    PivotFailedError,
    PivotValidationError,
    PivotError,
)


# =============================================================================
# Constants
# =============================================================================

VALID_AGGREGATION_FUNCTIONS = [
    "sum",
    "mean",
    "avg",
    "count",
    "min",
    "max",
    "median",
    "std",
    "var",
    "first",
    "last",
]


# =============================================================================
# Validation Functions
# =============================================================================


def validate_aggregation_function(func: str) -> Result[str, PivotValidationError]:
    """Validate and normalize aggregation function name.

    Args:
        func: Aggregation function name

    Returns:
        Result[str, PivotValidationError] - Normalized function name or error

    Errors:
        - InvalidFunctionError: Function not supported

    Normalization:
        "avg" → "mean"
    """
    if func.lower() not in VALID_AGGREGATION_FUNCTIONS:
        return err(InvalidFunctionError(
            function=func,
            valid_functions=VALID_AGGREGATION_FUNCTIONS
        ))

    # Normalize "avg" to "mean"
    normalized = "mean" if func.lower() == "avg" else func.lower()
    return ok(normalized)


def validate_pivot_columns(
    df: pd.DataFrame,
    rows: list[str],
    columns: list[str],
    values: list[str]
) -> Result[None, PivotValidationError]:
    """Validate pivot columns exist in DataFrame.

    Args:
        df: DataFrame to validate against
        rows: Row columns
        columns: Column columns
        values: Value columns

    Returns:
        Result[None, PivotValidationError]

    Errors:
        - NoRowsError: No row columns specified
        - NoColumnsError: No column columns specified
        - NoValuesError: No value columns specified
        - RowColumnsNotFoundError: Row columns don't exist
        - ColumnColumnsNotFoundError: Column columns don't exist
        - ValueColumnsNotFoundError: Value columns don't exist
    """
    if not rows:
        return err(NoRowsError())

    if not columns:
        return err(NoColumnsError())

    if not values:
        return err(NoValuesError())

    # Check row columns
    missing_rows = [c for c in rows if c not in df.columns]
    if missing_rows:
        return err(RowColumnsNotFoundError(
            missing=missing_rows,
            available=list(df.columns)
        ))

    # Check column columns
    missing_cols = [c for c in columns if c not in df.columns]
    if missing_cols:
        return err(ColumnColumnsNotFoundError(
            missing=missing_cols,
            available=list(df.columns)
        ))

    # Check value columns
    missing_vals = [c for c in values if c not in df.columns]
    if missing_vals:
        return err(ValueColumnsNotFoundError(
            missing=missing_vals,
            available=list(df.columns)
        ))

    return ok(None)


# =============================================================================
# Helper Functions
# =============================================================================


def parse_fill_value(value: str | None) -> Any:
    """Parse fill value for pivot table.

    Args:
        value: String value to parse

    Returns:
        Parsed value (None, 0, float('nan'), int, float, or str)

    Parsing rules:
        - None or "none" → None
        - "0" → 0
        - "nan" → float('nan')
        - Try int → int
        - Try float → float
        - Otherwise → keep as string
    """
    if value is None:
        return None

    if value.lower() == "none":
        return None

    if value.lower() == "0":
        return 0

    if value.lower() == "nan":
        return float('nan')

    # Try to parse as int
    try:
        return int(value)
    except ValueError:
        pass

    # Try to parse as float
    try:
        return float(value)
    except ValueError:
        pass

    # Keep as string
    return value


def flatten_multiindex(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten MultiIndex columns and index in pivot table.

    Args:
        df: DataFrame with potential MultiIndex

    Returns:
        DataFrame with flattened columns and index

    Implementation:
        1. Check if columns are MultiIndex
        2. If yes, join with '_' and strip
        3. Check if index is MultiIndex
        4. If yes, join with '_' and strip
        5. Reset index to make rows into columns
    """
    result = df.copy()

    # Flatten columns if MultiIndex
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = ['_'.join(map(str, col)).strip()
                         for col in result.columns.values]

    # Flatten index if MultiIndex
    if isinstance(result.index, pd.MultiIndex):
        result.index = ['_'.join(map(str, idx)).strip()
                       for idx in result.index.values]

    # Reset index
    result = result.reset_index()

    return result


# =============================================================================
# Main Operations
# =============================================================================


def create_pivot_table(
    df: pd.DataFrame,
    rows: list[str],
    columns: list[str],
    values: list[str],
    aggfunc: str = "sum",
    fill_value: Any = None
) -> Result[pd.DataFrame, PivotError]:
    """Create pivot table from DataFrame.

    Args:
        df: Source DataFrame
        rows: Columns to use as rows (index)
        columns: Columns to use as columns
        values: Columns to use as values
        aggfunc: Aggregation function
        fill_value: Value to fill NaN with

    Returns:
        Result[pd.DataFrame, PivotError] - Pivot table or error

    Errors:
        - PivotFailedError: Pivot table creation failed
    """
    # Validate aggregation function
    agg_result = validate_aggregation_function(aggfunc)
    if is_err(agg_result):
        error = unwrap_err(agg_result)
        return err(PivotFailedError(f"Invalid aggregation function: {error.function}. Valid: {', '.join(error.valid_functions)}"))

    agg_func_normalized = unwrap(agg_result)

    # Validate pivot columns
    validation_result = validate_pivot_columns(df, rows, columns, values)
    if is_err(validation_result):
        error = unwrap_err(validation_result)
        if isinstance(error, NoRowsError):
            return err(PivotFailedError("No row columns specified"))
        elif isinstance(error, NoColumnsError):
            return err(PivotFailedError("No column columns specified"))
        elif isinstance(error, NoValuesError):
            return err(PivotFailedError("No value columns specified"))
        elif isinstance(error, RowColumnsNotFoundError):
            return err(PivotFailedError(f"Row columns not found: {', '.join(error.missing)}. Available: {', '.join(error.available)}"))
        elif isinstance(error, ColumnColumnsNotFoundError):
            return err(PivotFailedError(f"Column columns not found: {', '.join(error.missing)}. Available: {', '.join(error.available)}"))
        elif isinstance(error, ValueColumnsNotFoundError):
            return err(PivotFailedError(f"Value columns not found: {', '.join(error.missing)}. Available: {', '.join(error.available)}"))

    # Create pivot table
    try:
        pivot_table = df.pivot_table(
            index=rows,
            columns=columns,
            values=values,
            aggfunc=agg_func_normalized,
            fill_value=fill_value,
            observed=True,  # Only use observed categories for categorical data
        )
    except Exception as e:
        return err(PivotFailedError(f"Pivot table creation failed: {str(e)}"))

    # Flatten MultiIndex
    pivot_table = flatten_multiindex(pivot_table)

    return ok(pivot_table)
