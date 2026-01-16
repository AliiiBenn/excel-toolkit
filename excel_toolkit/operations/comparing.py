"""Comparing operations for DataFrames.

This module provides comparison operations that can be applied to pandas DataFrames.
All functions return Result types for explicit error handling.
"""

from dataclasses import dataclass
from typing import Any

import pandas as pd

from excel_toolkit.fp import ok, err, is_ok, is_err, unwrap, unwrap_err, Result
from excel_toolkit.fp.immutable import immutable
from excel_toolkit.models.error_types import (
    KeyColumnsNotFoundError,
    ComparisonFailedError,
    CompareError,
)


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class DifferencesResult:
    """Result of finding differences between two DataFrames.

    Attributes:
        only_df1: Set of indices only in df1 (deleted rows)
        only_df2: Set of indices only in df2 (added rows)
        modified_rows: List of indices with different values (modified rows)
    """
    only_df1: set
    only_df2: set
    modified_rows: list


@dataclass
class ComparisonResult:
    """Result of comparing two DataFrames.

    Attributes:
        df_result: Comparison result DataFrame with _diff_status column
        added_count: Number of rows only in df2 (added)
        deleted_count: Number of rows only in df1 (deleted)
        modified_count: Number of rows with different values (modified)
    """
    df_result: pd.DataFrame
    added_count: int
    deleted_count: int
    modified_count: int


# =============================================================================
# Validation Functions
# =============================================================================


def validate_key_columns(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    key_columns: list[str] | None
) -> Result[list[str], CompareError]:
    """Validate key columns for comparison.

    Args:
        df1: First DataFrame
        df2: Second DataFrame
        key_columns: Columns to use as keys (None = use row position)

    Returns:
        Result[list[str], CompareError] - Validated key columns or error

    Errors:
        - KeyColumnsNotFoundError: Key columns don't exist in both DataFrames

    Implementation:
        - If key_columns is None, return empty list (use row position)
        - If key_columns is provided, check they exist in both DataFrames
        - Return validated key columns
    """
    if key_columns is None:
        return ok([])

    # Check key columns exist in df1
    missing_df1 = [c for c in key_columns if c not in df1.columns]

    # Check key columns exist in df2
    missing_df2 = [c for c in key_columns if c not in df2.columns]

    # Collect all missing columns
    all_missing = list(set(missing_df1 + missing_df2))

    if all_missing:
        # Report missing from df1 if any, otherwise from df2
        if missing_df1:
            return err(KeyColumnsNotFoundError(
                missing=all_missing,
                available=list(df1.columns)
            ))
        else:
            return err(KeyColumnsNotFoundError(
                missing=all_missing,
                available=list(df2.columns)
            ))

    return ok(key_columns)


# =============================================================================
# Comparison Functions
# =============================================================================


def compare_rows(row1: pd.Series, row2: pd.Series) -> bool:
    """Compare two rows for equality.

    Args:
        row1: First row
        row2: Second row

    Returns:
        bool: True if rows are equal, False otherwise

    Implementation:
        - Convert to dict for comparison (handles MultiIndex)
        - Compare all values element-wise
        - Handle NaN values (NaN == NaN is OK)
        - Return False if any difference found
    """
    # Convert to dict to avoid MultiIndex issues
    dict1 = row1.to_dict()
    dict2 = row2.to_dict()

    # Check if rows have same length
    if len(dict1) != len(dict2):
        return False

    # Compare each value
    for key in dict1:
        val1 = dict1[key]
        val2 = dict2.get(key)

        # Handle missing keys
        if key not in dict2:
            return False

        # Handle NaN comparison
        if pd.isna(val1) and pd.isna(val2):
            continue
        elif pd.isna(val1) or pd.isna(val2):
            return False
        elif val1 != val2:
            return False

    return True


def find_differences(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    key_columns: list[str]
) -> DifferencesResult:
    """Find differences between two DataFrames.

    Args:
        df1: First DataFrame
        df2: Second DataFrame
        key_columns: Columns to use as keys (empty = use row position)

    Returns:
        DifferencesResult - Sets of indices for each difference type

    Implementation:
        - If key_columns is empty, use row position as key
        - Set key columns as index for both DataFrames
        - Find indices only in df1 (deleted)
        - Find indices only in df2 (added)
        - Find common indices and compare values
        - Return DifferencesResult
    """
    # Make copies to avoid modifying originals
    df1_copy = df1.copy()
    df2_copy = df2.copy()

    if key_columns:
        # Use key columns as index
        df1_indexed = df1_copy.set_index(key_columns)
        df2_indexed = df2_copy.set_index(key_columns)
    else:
        # Use row position as index
        df1_indexed = df1_copy.reset_index(drop=True)
        df2_indexed = df2_copy.reset_index(drop=True)

    # Find indices only in df1 (deleted)
    only_df1 = set(df1_indexed.index) - set(df2_indexed.index)

    # Find indices only in df2 (added)
    only_df2 = set(df2_indexed.index) - set(df1_indexed.index)

    # Find common indices
    common_indices = set(df1_indexed.index) & set(df2_indexed.index)

    # Find modified rows
    modified_rows = []
    for idx in common_indices:
        row1 = df1_indexed.loc[idx]
        row2 = df2_indexed.loc[idx]

        # Compare rows
        if not compare_rows(row1, row2):
            modified_rows.append(idx)

    return DifferencesResult(
        only_df1=only_df1,
        only_df2=only_df2,
        modified_rows=modified_rows
    )


def build_comparison_result(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    differences: DifferencesResult,
    key_columns: list[str]
) -> pd.DataFrame:
    """Build comparison result DataFrame.

    Args:
        df1: First DataFrame
        df2: Second DataFrame
        differences: DifferencesResult from find_differences()
        key_columns: Columns used as keys

    Returns:
        pd.DataFrame - Result with _diff_status column

    Implementation:
        - Create result DataFrame
        - Add rows only in df1 (deleted)
        - Add rows only in df2 (added)
        - Add rows with differences (modified)
        - Add _diff_status column ("deleted", "added", "modified", "unchanged")
        - Reset index to make keys into columns
        - Reorder columns: keys first, then _diff_status, then other columns
    """
    result_rows = []

    # Make copies to avoid modifying originals
    df1_copy = df1.copy()
    df2_copy = df2.copy()

    if key_columns:
        # Use key columns as index
        df1_indexed = df1_copy.set_index(key_columns)
        df2_indexed = df2_copy.set_index(key_columns)
    else:
        # Use row position as index
        df1_indexed = df1_copy.reset_index(drop=True)
        df2_indexed = df2_copy.reset_index(drop=True)

    # Add deleted rows (only in df1)
    for idx in differences.only_df1:
        row = df1_indexed.loc[idx].copy()
        row_dict = row.to_dict()
        if key_columns:
            # Add key columns to dict
            if isinstance(idx, tuple):
                for i, col in enumerate(key_columns):
                    row_dict[col] = idx[i]
            else:
                row_dict[key_columns[0]] = idx
        row_dict['_diff_status'] = 'deleted'
        result_rows.append(row_dict)

    # Add added rows (only in df2)
    for idx in differences.only_df2:
        row = df2_indexed.loc[idx].copy()
        row_dict = row.to_dict()
        if key_columns:
            # Add key columns to dict
            if isinstance(idx, tuple):
                for i, col in enumerate(key_columns):
                    row_dict[col] = idx[i]
            else:
                row_dict[key_columns[0]] = idx
        row_dict['_diff_status'] = 'added'
        result_rows.append(row_dict)

    # Find unchanged rows and add modified rows
    common_indices = set(df1_indexed.index) & set(df2_indexed.index)
    for idx in common_indices:
        row1 = df1_indexed.loc[idx]
        row2 = df2_indexed.loc[idx]

        # Use df2 values (current state)
        row_dict = row2.to_dict()
        if key_columns:
            # Add key columns to dict
            if isinstance(idx, tuple):
                for i, col in enumerate(key_columns):
                    row_dict[col] = idx[i]
            else:
                row_dict[key_columns[0]] = idx

        if idx in differences.modified_rows:
            row_dict['_diff_status'] = 'modified'
        else:
            row_dict['_diff_status'] = 'unchanged'

        result_rows.append(row_dict)

    # Create result DataFrame
    df_result = pd.DataFrame(result_rows)

    if df_result.empty:
        # Handle empty result
        if key_columns:
            df_result = pd.DataFrame(columns=list(key_columns) + ['_diff_status'])
        else:
            df_result = pd.DataFrame(columns=['_diff_status'])

    # Reorder columns: keys first, then _diff_status, then other columns
    if not df_result.empty:
        other_columns = [col for col in df_result.columns if col != '_diff_status' and col not in key_columns]
        column_order = list(key_columns) + ['_diff_status'] + other_columns
        df_result = df_result[column_order]

    return df_result


# =============================================================================
# Main Operations
# =============================================================================


def compare_dataframes(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    key_columns: list[str] | None = None
) -> Result[ComparisonResult, CompareError]:
    """Compare two DataFrames.

    Args:
        df1: First DataFrame (before)
        df2: Second DataFrame (after)
        key_columns: Columns to use as keys (None = use row position)

    Returns:
        Result[ComparisonResult, CompareError] - Comparison result or error

    Errors:
        - ComparisonFailedError: Comparison failed

    Implementation:
        1. Validate key columns
        2. Find differences
        3. Build comparison result
        4. Return ComparisonResult with counts

    Examples:
        - Compare with key columns: compare_dataframes(df1, df2, ["ID"])
        - Compare by position: compare_dataframes(df1, df2)
    """
    # Validate key columns
    validation_result = validate_key_columns(df1, df2, key_columns)
    if is_err(validation_result):
        error = unwrap_err(validation_result)
        return err(ComparisonFailedError(
            f"Key columns not found: {', '.join(error.missing)}. "
            f"Available in df1: {', '.join(error.available)}"
        ))

    validated_keys = unwrap(validation_result)

    # Find differences
    try:
        differences = find_differences(df1, df2, validated_keys)
    except Exception as e:
        return err(ComparisonFailedError(f"Failed to find differences: {str(e)}"))

    # Build comparison result
    try:
        df_result = build_comparison_result(df1, df2, differences, validated_keys)
    except Exception as e:
        return err(ComparisonFailedError(f"Failed to build result: {str(e)}"))

    # Create comparison result
    result = ComparisonResult(
        df_result=df_result,
        added_count=len(differences.only_df2),
        deleted_count=len(differences.only_df1),
        modified_count=len(differences.modified_rows)
    )

    return ok(result)
