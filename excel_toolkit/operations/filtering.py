"""Filtering operations for DataFrames.

This module provides filtering operations that can be applied to pandas DataFrames.
All functions return Result types for explicit error handling.
"""

import re
from typing import Any

import pandas as pd

from excel_toolkit.fp import ok, err, Result
from excel_toolkit.models.error_types import (
    DangerousPatternError,
    ConditionTooLongError,
    UnbalancedParenthesesError,
    UnbalancedBracketsError,
    UnbalancedQuotesError,
    ColumnNotFoundError,
    QueryFailedError,
    ColumnMismatchError,
    ColumnsNotFoundError,
    FilterError,
    ValidationError,
)

# =============================================================================
# Constants
# =============================================================================

MAX_CONDITION_LENGTH = 1000

ALLOWED_PATTERNS = [
    r"\w+\s*[=!<>]+\s*[\w'\"]+",  # Comparisons: x == 5, x > 3
    r"\w+\s+in\s+\[[^\]]+\]",  # in operator: x in [a, b, c]
    r"\w+\.isna\(\)",  # Null check: x.isna()
    r"\w+\.notna\(\)",  # Null check: x.notna()
    r"\w+\s+contains\s+['\"][^'\"]+['\"]",  # String contains
    r"\w+\s+startswith\s+['\"][^'\"]+['\"]",  # String starts with
    r"\w+\s+endswith\s+['\"][^'\"]+['\"]",  # String ends with
    r"\s+and\s+",  # Logical AND
    r"\s+or\s+",  # Logical OR
    r"\s+not\s+",  # Logical NOT
    r"\([^)]+\)",  # Parentheses for grouping
]

DANGEROUS_PATTERNS = [
    "import",
    "exec",
    "eval",
    "__",
    "open(",
    "file(",
    "os.",
    "sys.",
    "subprocess",
    "pickle",
]

# =============================================================================
# Validation Functions
# =============================================================================


def validate_condition(condition: str) -> Result[str, ValidationError]:
    """Validate filter condition for security and syntax.

    Args:
        condition: User-provided condition string

    Returns:
        Result[str, ValidationError] - Valid condition or error message

    Errors:
        - DangerousPatternError: Contains dangerous code pattern
        - ConditionTooLongError: Exceeds max length
        - UnbalancedParenthesesError: Mismatched parentheses
        - UnbalancedBracketsError: Mismatched brackets
        - UnbalancedQuotesError: Mismatched quotes
    """
    # Check for dangerous patterns
    condition_lower = condition.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern in condition_lower:
            return err(DangerousPatternError(pattern=pattern))

    # Check length
    if len(condition) > MAX_CONDITION_LENGTH:
        return err(
            ConditionTooLongError(
                length=len(condition),
                max_length=MAX_CONDITION_LENGTH
            )
        )

    # Check balanced parentheses
    open_count = condition.count("(")
    close_count = condition.count(")")
    if open_count != close_count:
        return err(
            UnbalancedParenthesesError(
                open_count=open_count,
                close_count=close_count
            )
        )

    # Check balanced brackets
    open_brackets = condition.count("[")
    close_brackets = condition.count("]")
    if open_brackets != close_brackets:
        return err(
            UnbalancedBracketsError(
                open_count=open_brackets,
                close_count=close_brackets
            )
        )

    # Check balanced quotes
    single_quotes = condition.count("'")
    if single_quotes % 2 != 0:
        return err(UnbalancedQuotesError(quote_type="'", count=single_quotes))

    double_quotes = condition.count('"')
    if double_quotes % 2 != 0:
        return err(UnbalancedQuotesError(quote_type='"', count=double_quotes))

    return ok(condition)


def normalize_condition(condition: str) -> str:
    """Normalize condition syntax for pandas.query().

    Handles special syntax and converts to pandas-compatible form.

    Args:
        condition: User-provided condition

    Returns:
        Normalized condition string

    Transformations:
        1. "value is None" → "value.isna()"
        2. "value is not None" → "value.notna()"
        3. "value between X and Y" → "value >= X and value <= Y"
        4. "value not in " → "value not in " (case normalization)
    """
    # Convert 'value is None' to 'value.isna()'
    condition = re.sub(r"(\w+)\s+is\s+None\b", r"\1.isna()", condition)
    condition = re.sub(r"(\w+)\s+is\s+not\s+None\b", r"\1.notna()", condition)

    # Convert 'value between X and Y' to 'value >= X and value <= Y'
    # Case insensitive
    pattern = r"(\w+)\s+between\s+([^ ]+)\s+and\s+([^ ]+)"
    replacement = r"\1 >= \2 and \1 <= \3"
    condition = re.sub(pattern, replacement, condition, flags=re.IGNORECASE)

    # Handle 'not in'
    condition = re.sub(r"(\w+)\s+not\s+in\s+", r"\1 not in ", condition, flags=re.IGNORECASE)

    return condition


# =============================================================================
# Helper Functions
# =============================================================================


def _extract_column_name(error_msg: str) -> str:
    """Extract column name from pandas error message.

    Args:
        error_msg: Error message from pandas

    Returns:
        Extracted column name or "unknown"
    """
    match = re.search(r"'([^']+)'", error_msg)
    return match.group(1) if match else "unknown"


# =============================================================================
# Main Operations
# =============================================================================


def apply_filter(
    df: pd.DataFrame,
    condition: str,
    columns: list[str] | None = None,
    limit: int | None = None
) -> Result[pd.DataFrame, FilterError]:
    """Apply filter condition to DataFrame.

    Args:
        df: Source DataFrame
        condition: Normalized filter condition (pandas query syntax)
        columns: Optional list of columns to select after filtering
        limit: Optional maximum number of rows to return

    Returns:
        Result[pd.DataFrame, FilterError] - Filtered DataFrame or error

    Errors:
        - ColumnNotFoundError: Referenced column doesn't exist
        - QueryFailedError: Query execution failed
        - ColumnMismatchError: Type mismatch in comparison
        - ColumnsNotFoundError: Selected columns don't exist
    """
    try:
        df_filtered = df.query(condition)
    except pd.errors.UndefinedVariableError as e:
        col = _extract_column_name(str(e))
        return err(ColumnNotFoundError(col, list(df.columns)))
    except Exception as e:
        error_msg = str(e)
        if "could not convert" in error_msg or "cannot compare" in error_msg:
            return err(ColumnMismatchError(error_msg, condition))
        return err(QueryFailedError(error_msg, condition))

    # Select columns if specified
    if columns:
        missing = [c for c in columns if c not in df_filtered.columns]
        if missing:
            return err(ColumnsNotFoundError(missing, list(df_filtered.columns)))
        df_filtered = df_filtered[columns]

    # Limit rows if specified
    if limit is not None:
        df_filtered = df_filtered.head(limit)

    return ok(df_filtered)
