"""Joining operations for DataFrames.

This module provides data joining/merging operations for pandas DataFrames.
All functions return Result types for explicit error handling.
"""

from typing import Any
from functools import reduce

import pandas as pd

from excel_toolkit.fp import ok, err, is_ok, is_err, unwrap, unwrap_err, Result
from excel_toolkit.models.error_types import (
    ColumnNotFoundError,
    InvalidJoinTypeError,
    InvalidJoinParametersError,
    JoinColumnsNotFoundError,
    JoiningError,
    MergeColumnsNotFoundError,
    InsufficientDataFramesError,
)


# =============================================================================
# Join Validation
# =============================================================================


def validate_join_columns(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    on: list[str] | None = None,
    left_on: list[str] | None = None,
    right_on: list[str] | None = None,
    left_index: bool = False,
    right_index: bool = False,
    how: str = "inner"
) -> Result[None, InvalidJoinParametersError | JoinColumnsNotFoundError]:
    """Validate join columns exist.

    Args:
        df1: Left DataFrame
        df2: Right DataFrame
        on: Columns to join on (both DataFrames)
        left_on: Left DataFrame join columns
        right_on: Right DataFrame join columns
        left_index: Use left DataFrame index
        right_index: Use right DataFrame index
        how: Join type (cross joins don't need columns)

    Returns:
        Result[None, InvalidJoinParametersError | JoinColumnsNotFoundError] - Success or error

    Errors:
        - InvalidJoinParametersError: Invalid parameter combination
        - JoinColumnsNotFoundError: Join columns don't exist

    Implementation:
        - Validate parameter combinations
        - Cross joins don't need join columns
        - If 'on' is specified, validate columns exist in both DataFrames
        - If 'left_on'/'right_on' specified, validate each in respective DataFrame
        - If index flags set, validate no conflicting parameters
        - Return ok(None) if valid

    Examples:
        on=["ID"] → Validate ID exists in both
        left_on=["Key1"], right_on=["Key2"] → Validate each in respective DataFrame
    """
    # Validate parameter combinations
    if on is not None:
        if left_on is not None or right_on is not None:
            return err(InvalidJoinParametersError(
                reason="Cannot use both 'on' and 'left_on'/'right_on' parameters"
            ))
        if left_index or right_index:
            return err(InvalidJoinParametersError(
                reason="Cannot use 'on' parameter with index flags"
            ))

        # Validate columns exist in both DataFrames
        missing_in_left = [col for col in on if col not in df1.columns]
        missing_in_right = [col for col in on if col not in df2.columns]

        if missing_in_left or missing_in_right:
            return err(JoinColumnsNotFoundError(
                missing_in_left=missing_in_left,
                missing_in_right=missing_in_right
            ))

    elif left_on is not None or right_on is not None:
        # Both must be specified together
        if left_on is None or right_on is None:
            return err(InvalidJoinParametersError(
                reason="Must specify both 'left_on' and 'right_on' together"
            ))

        if len(left_on) != len(right_on):
            return err(InvalidJoinParametersError(
                reason="'left_on' and 'right_on' must have the same length"
            ))

        if left_index or right_index:
            return err(InvalidJoinParametersError(
                reason="Cannot use 'left_on'/'right_on' with index flags"
            ))

        # Validate columns exist in respective DataFrames
        missing_in_left = [col for col in left_on if col not in df1.columns]
        missing_in_right = [col for col in right_on if col not in df2.columns]

        if missing_in_left or missing_in_right:
            return err(JoinColumnsNotFoundError(
                missing_in_left=missing_in_left,
                missing_in_right=missing_in_right
            ))

    elif not (left_index and right_index):
        # If no columns specified and not using both indexes, need at least some specification
        # Exceptions:
        # - Cross joins don't need any keys
        # - Empty DataFrames can be joined without keys (result will be empty)
        if not (left_index or right_index) and how != "cross":
            # Check if DataFrames are empty (no columns)
            if len(df1.columns) > 0 or len(df2.columns) > 0:
                return err(InvalidJoinParametersError(
                    reason="Must specify join columns ('on', 'left_on'/'right_on', or index flags)"
                ))

    return ok(None)


# =============================================================================
# Join Operations
# =============================================================================


def join_dataframes(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    how: str = "inner",
    on: list[str] | None = None,
    left_on: list[str] | None = None,
    right_on: list[str] | None = None,
    left_index: bool = False,
    right_index: bool = False,
    suffixes: tuple[str, str] = ("_x", "_y")
) -> Result[pd.DataFrame, InvalidJoinTypeError | InvalidJoinParametersError | JoinColumnsNotFoundError | JoiningError]:
    """Join two DataFrames.

    Args:
        df1: Left DataFrame
        df2: Right DataFrame
        how: Join type ("inner", "left", "right", "outer", "cross")
        on: Columns to join on (both DataFrames)
        left_on: Left DataFrame join columns
        right_on: Right DataFrame join columns
        left_index: Use left DataFrame index
        right_index: Use right DataFrame index
        suffixes: Suffixes for overlapping columns

    Returns:
        Result[pd.DataFrame, InvalidJoinTypeError | InvalidJoinParametersError | JoinColumnsNotFoundError | JoiningError] - Joined DataFrame or error

    Errors:
        - InvalidJoinTypeError: Invalid join type
        - InvalidJoinParametersError: Invalid parameter combination
        - JoinColumnsNotFoundError: Join columns don't exist
        - JoiningError: Join operation failed

    Implementation:
        - Validate join type
        - Validate join columns using validate_join_columns()
        - Use pd.merge() with specified parameters
        - Handle suffixes for overlapping columns
        - Return joined DataFrame

    Examples:
        how="inner", on=["ID"] → Inner join on ID
        how="left", left_on=["Key1"], right_on=["Key2"] → Left join on different keys
    """
    valid_join_types = ["inner", "left", "right", "outer", "cross"]

    # Validate join type
    if how not in valid_join_types:
        return err(InvalidJoinTypeError(
            join_type=how,
            valid_types=valid_join_types
        ))

    # Validate join columns
    validation = validate_join_columns(
        df1, df2, on, left_on, right_on, left_index, right_index, how
    )
    if is_err(validation):
        return validation

    # Perform the join
    try:
        # Special case: both DataFrames are empty (no columns)
        if len(df1.columns) == 0 and len(df2.columns) == 0:
            return ok(pd.DataFrame())

        result = pd.merge(
            df1,
            df2,
            how=how,
            on=on,
            left_on=left_on,
            right_on=right_on,
            left_index=left_index,
            right_index=right_index,
            suffixes=suffixes
        )

        return ok(result)

    except Exception as e:
        return err(JoiningError(
            message=f"Join failed: {str(e)}"
        ))


# =============================================================================
# Merge Operations
# =============================================================================


def merge_dataframes(
    dataframes: list[pd.DataFrame],
    how: str = "inner",
    on: list[str] | None = None,
    suffixes: tuple[str, str] = ("_x", "_y")
) -> Result[pd.DataFrame, InsufficientDataFramesError | MergeColumnsNotFoundError | JoiningError]:
    """Merge multiple DataFrames sequentially.

    Args:
        dataframes: List of DataFrames to merge (must have 2+)
        how: Join type for all merges
        on: Columns to join on (must exist in all DataFrames)
        suffixes: Suffixes for overlapping columns

    Returns:
        Result[pd.DataFrame, InsufficientDataFramesError | MergeColumnsNotFoundError | JoiningError] - Merged DataFrame or error

    Errors:
        - InsufficientDataFramesError: Less than 2 DataFrames provided
        - MergeColumnsNotFoundError: Join columns don't exist in all DataFrames
        - JoiningError: Merge operation failed

    Implementation:
        - Validate at least 2 DataFrames
        - If 'on' specified, validate exists in all DataFrames
        - Sequentially merge DataFrames using reduce
        - Generate unique suffixes for each merge (_0, _1, _2, etc.)
        - Return final merged DataFrame

    Examples:
        Merge [df1, df2, df3] on ["ID"]
        Merge [df1, df2, df3] with no keys (cross merge)
    """
    # Validate we have at least 2 DataFrames
    if len(dataframes) < 2:
        return err(InsufficientDataFramesError(
            count=len(dataframes)
        ))

    # If 'on' specified, validate exists in all DataFrames
    if on is not None:
        missing = {}
        for i, df in enumerate(dataframes):
            missing_cols = [col for col in on if col not in df.columns]
            if missing_cols:
                missing[i] = missing_cols

        if missing:
            return err(MergeColumnsNotFoundError(
                missing=missing
            ))

    # Sequentially merge DataFrames
    try:
        def merge_two(acc, df):
            # Generate unique suffixes for this merge
            merge_suffixes = (f"_{len(dataframes)}", f"_{len(dataframes)+1}")
            result = pd.merge(acc, df, how=how, on=on, suffixes=merge_suffixes)
            return result

        result = reduce(merge_two, dataframes)

        return ok(result)

    except Exception as e:
        return err(JoiningError(
            message=f"Merge failed: {str(e)}"
        ))
