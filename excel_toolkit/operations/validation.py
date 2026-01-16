"""Validation operations for DataFrames.

This module provides data validation operations for pandas DataFrames.
All functions return Result types for explicit error handling.
"""

from typing import Any

import pandas as pd

from excel_toolkit.fp import ok, err, is_ok, is_err, unwrap, unwrap_err, Result
from excel_toolkit.models.error_types import (
    ColumnNotFoundError,
    TypeMismatchError,
    ValueOutOfRangeError,
    NullValueThresholdExceededError,
    UniquenessViolationError,
    InvalidRuleError,
    ValidationReport,
)


# =============================================================================
# Column Existence Validation
# =============================================================================


def validate_column_exists(
    df: pd.DataFrame,
    columns: list[str] | str
) -> Result[None, ColumnNotFoundError]:
    """Validate that columns exist in DataFrame.

    Args:
        df: DataFrame to validate
        columns: Column name or list of column names

    Returns:
        Result[None, ColumnNotFoundError] - Success or error

    Errors:
        - ColumnNotFoundError: One or more columns don't exist

    Implementation:
        - Convert single column to list
        - Check each column exists in df.columns
        - Collect missing columns
        - Return error with missing columns if any
        - Return ok(None) if all exist

    Examples:
        columns=["ID", "Name", "Age"]
        columns="ID"
    """
    # Convert single column to list
    if isinstance(columns, str):
        columns = [columns]

    # Check each column exists
    missing_columns = [col for col in columns if col not in df.columns]

    if missing_columns:
        return err(ColumnNotFoundError(
            column=missing_columns[0] if len(missing_columns) == 1 else f"{', '.join(missing_columns[:-1])} and {missing_columns[-1]}",
            available=list(df.columns)
        ))

    return ok(None)


# =============================================================================
# Column Type Validation
# =============================================================================


def validate_column_type(
    df: pd.DataFrame,
    column_types: dict[str, str | list[str]]
) -> Result[None, ColumnNotFoundError | TypeMismatchError]:
    """Validate column data types.

    Args:
        df: DataFrame to validate
        column_types: Dictionary mapping column names to expected types
                      Types: "int", "float", "str", "bool", "datetime", "numeric"
                      Can specify list of valid types (e.g., ["int", "float"])

    Returns:
        Result[None, ColumnNotFoundError | TypeMismatchError] - Success or error

    Errors:
        - ColumnNotFoundError: Column doesn't exist
        - TypeMismatchError: Column type doesn't match expected

    Implementation:
        - Validate all columns exist
        - For each column, check dtype
        - If type is list, check if any match
        - Collect mismatches
        - Return error with mismatches if any

    Examples:
        {"Age": "int", "Name": "str", "Salary": ["int", "float"]}
    """
    # First, validate all columns exist
    columns_to_check = list(column_types.keys())
    existence_check = validate_column_exists(df, columns_to_check)
    if is_err(existence_check):
        return existence_check

    # Check each column type
    for column, expected_types in column_types.items():
        actual_type = str(df[column].dtype)

        # Normalize to list
        if isinstance(expected_types, str):
            expected_types = [expected_types]

        # Check type match
        type_matches = False
        for expected_type in expected_types:
            if _check_type_match(actual_type, expected_type):
                type_matches = True
                break

        if not type_matches:
            return err(TypeMismatchError(
                column=column,
                expected_type=expected_types,
                actual_type=actual_type
            ))

    return ok(None)


def _check_type_match(actual: str, expected: str) -> bool:
    """Check if actual dtype matches expected type.

    Helper function for validate_column_type.
    """
    actual_lower = actual.lower()
    expected_lower = expected.lower()

    if expected_lower == "int":
        return actual_lower.startswith("int") or actual_lower.startswith("int64")
    elif expected_lower == "float":
        return "float" in actual_lower
    elif expected_lower == "str":
        return actual_lower == "object" or "str" in actual_lower
    elif expected_lower == "bool":
        return "bool" in actual_lower
    elif expected_lower == "datetime":
        return "datetime" in actual_lower
    elif expected_lower == "numeric":
        return actual_lower.startswith("int") or "float" in actual_lower

    return False


# =============================================================================
# Value Range Validation
# =============================================================================


def validate_value_range(
    df: pd.DataFrame,
    column: str,
    min_value: Any | None = None,
    max_value: Any | None = None,
    allow_equal: bool = True
) -> Result[None, ColumnNotFoundError | ValueOutOfRangeError]:
    """Validate values are within range.

    Args:
        df: DataFrame to validate
        column: Column to validate
        min_value: Minimum value (None = no minimum)
        max_value: Maximum value (None = no maximum)
        allow_equal: Whether to allow equality with bounds

    Returns:
        Result[None, ColumnNotFoundError | ValueOutOfRangeError] - Success or error

    Errors:
        - ColumnNotFoundError: Column doesn't exist
        - ValueOutOfRangeError: Values outside range

    Implementation:
        - Validate column exists
        - If both min_value and max_value are None, return ok(None)
        - Check values against range
        - Count violations
        - Return error with violation details if any

    Examples:
        column="Age", min_value=0, max_value=120
        column="Score", min_value=0, max_value=100, allow_equal=False
    """
    # Validate column exists
    existence_check = validate_column_exists(df, column)
    if is_err(existence_check):
        return existence_check

    # If no bounds specified, pass
    if min_value is None and max_value is None:
        return ok(None)

    # Check values
    violations = []

    if min_value is not None:
        if allow_equal:
            below_min = df[df[column] < min_value]
        else:
            below_min = df[df[column] <= min_value]

        if len(below_min) > 0:
            violations.append(f"{len(below_min)} values below minimum")

    if max_value is not None:
        if allow_equal:
            above_max = df[df[column] > max_value]
        else:
            above_max = df[df[column] >= max_value]

        if len(above_max) > 0:
            violations.append(f"{len(above_max)} values above maximum")

    if violations:
        return err(ValueOutOfRangeError(
            column=column,
            min_value=min_value,
            max_value=max_value,
            violation_count=len(df) if (min_value is None and max_value is None) else
                              (len(below_min) if min_value is not None else 0) +
                              (len(above_max) if max_value is not None else 0)
        ))

    return ok(None)


# =============================================================================
# Null Value Validation
# =============================================================================


def check_null_values(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    threshold: float | None = None
) -> Result[ValidationReport, NullValueThresholdExceededError]:
    """Check null values in DataFrame.

    Args:
        df: DataFrame to check
        columns: Columns to check (None = all columns)
        threshold: Maximum allowed null percentage (0-1)

    Returns:
        Result[ValidationReport, NullValueThresholdExceededError] - Report or error

    Errors:
        - NullValueThresholdExceededError: Null values exceed threshold

    Implementation:
        - If columns is None, check all columns
        - Count null values in each column
        - Calculate null percentages
        - If threshold specified, check each column
        - Return ValidationReport with results
        - Return error if any column exceeds threshold

    Examples:
        columns=None, threshold=0.5 → Allow up to 50% null values
        columns=["Name", "Age"] → Check only these columns
    """
    # Determine columns to check
    if columns is None:
        columns = df.columns.tolist()

    # Validate columns exist
    existence_check = validate_column_exists(df, columns)
    if is_err(existence_check):
        # For validation, we'll just report this as a failed check
        return ok(ValidationReport(
            passed=0,
            failed=1,
            errors=[{"error": "Column not found"}],
            warnings=[]
        ))

    # Check null values
    errors = []
    warnings = []
    passed = 0
    failed = 0

    for col in columns:
        null_count = df[col].isna().sum()
        null_percent = null_count / len(df) if len(df) > 0 else 0

        if threshold is not None and null_percent > threshold:
            failed += 1
            errors.append({
                "column": col,
                "null_count": null_count,
                "null_percent": null_percent,
                "threshold": threshold
            })
        else:
            passed += 1
            if null_count > 0:
                warnings.append({
                    "column": col,
                    "null_count": int(null_count),
                    "null_percent": float(null_percent)
                })

    # Check if threshold was exceeded
    if failed > 0 and threshold is not None:
        # Find the first column that exceeded threshold
        for col in columns:
            null_count = df[col].isna().sum()
            null_percent = null_count / len(df) if len(df) > 0 else 0
            if null_percent > threshold:
                return err(NullValueThresholdExceededError(
                    column=col,
                    null_count=int(null_count),
                    null_percent=float(null_percent),
                    threshold=threshold
                ))

    return ok(ValidationReport(
        passed=passed,
        failed=failed,
        errors=errors if errors else None,
        warnings=warnings if warnings else None
    ))


# =============================================================================
# Uniqueness Validation
# =============================================================================


def validate_unique(
    df: pd.DataFrame,
    columns: list[str] | str,
    ignore_null: bool = True
) -> Result[None, UniquenessViolationError]:
    """Validate that values are unique.

    Args:
        df: DataFrame to validate
        columns: Column(s) to check for uniqueness
        ignore_null: Whether to ignore null values when checking uniqueness

    Returns:
        Result[None, UniquenessViolationError] - Success or error

    Errors:
        - ColumnNotFoundError: Columns don't exist
        - UniquenessViolationError: Duplicate values found

    Implementation:
        - Validate columns exist
        - Convert single column to list
        - Check for duplicates in specified columns
        - If ignore_null, exclude null values from check
        - Count duplicates
        - Return error with details if duplicates found
        - Return ok(None) if all unique

    Examples:
        columns=["ID"] → Check ID is unique
        columns=["FirstName", "LastName"] → Check combination is unique
    """
    # Convert single column to list
    if isinstance(columns, str):
        columns = [columns]

    # Validate columns exist
    existence_check = validate_column_exists(df, columns)
    if is_err(existence_check):
        return existence_check

    # Check for duplicates
    subset = df[columns]

    if ignore_null:
        subset = subset.dropna()

    duplicates = subset.duplicated(keep='first')
    duplicate_count = duplicates.sum()

    if duplicate_count > 0:
        # Get sample duplicates (all duplicate rows)
        duplicate_rows = subset[duplicates]
        sample_duplicates = duplicate_rows.to_dict('records') if len(duplicate_rows) > 0 else []

        return err(UniquenessViolationError(
            columns=columns,
            duplicate_count=int(duplicate_count),
            sample_duplicates=sample_duplicates
        ))

    return ok(None)


# =============================================================================
# Comprehensive DataFrame Validation
# =============================================================================


def validate_dataframe(
    df: pd.DataFrame,
    rules: list[dict]
) -> Result[ValidationReport, InvalidRuleError]:
    """Validate DataFrame against multiple rules.

    Args:
        df: DataFrame to validate
        rules: List of validation rules

    Returns:
        Result[ValidationReport, InvalidRuleError] - Validation report or error

    Errors:
        - InvalidRuleError: Invalid rule specification

    Rule Types:
        - "column_exists": {"columns": list[str]}
        - "column_type": {"column_types": dict}
        - "value_range": {"column": str, "min": Any, "max": Any}
        - "unique": {"columns": list[str], "ignore_null": bool}
        - "null_threshold": {"columns": list[str], "threshold": float}

    Implementation:
        - Validate each rule structure
        - Apply rules in order
        - Collect results
        - Return ValidationReport with summary

    Examples:
        rules=[
            {"type": "column_exists", "columns": ["ID", "Name"]},
            {"type": "value_range", "column": "Age", "min": 0, "max": 120}
        ]
    """
    errors = []
    warnings = []
    passed = 0
    failed = 0

    for i, rule in enumerate(rules):
        rule_type = rule.get("type")

        try:
            if rule_type == "column_exists":
                columns = rule.get("columns")
                result = validate_column_exists(df, columns)
                if is_err(result):
                    failed += 1
                    error = unwrap_err(result)
                    errors.append({
                        "rule": i,
                        "type": "column_exists",
                        "error": str(error)
                    })
                else:
                    passed += 1

            elif rule_type == "column_type":
                column_types = rule.get("column_types")
                result = validate_column_type(df, column_types)
                if is_err(result):
                    failed += 1
                    error = unwrap_err(result)
                    errors.append({
                        "rule": i,
                        "type": "column_type",
                        "error": str(error)
                    })
                else:
                    passed += 1

            elif rule_type == "value_range":
                column = rule.get("column")
                min_value = rule.get("min")
                max_value = rule.get("max")
                allow_equal = rule.get("allow_equal", True)
                result = validate_value_range(df, column, min_value, max_value, allow_equal)
                if is_err(result):
                    failed += 1
                    error = unwrap_err(result)
                    errors.append({
                        "rule": i,
                        "type": "value_range",
                        "error": str(error)
                    })
                else:
                    passed += 1

            elif rule_type == "unique":
                columns = rule.get("columns")
                ignore_null = rule.get("ignore_null", True)
                result = validate_unique(df, columns, ignore_null)
                if is_err(result):
                    failed += 1
                    error = unwrap_err(result)
                    errors.append({
                        "rule": i,
                        "type": "unique",
                        "error": str(error)
                    })
                else:
                    passed += 1

            elif rule_type == "null_threshold":
                columns = rule.get("columns")
                threshold = rule.get("threshold")
                result = check_null_values(df, columns, threshold)
                if is_err(result):
                    failed += 1
                    error = unwrap_err(result)
                    errors.append({
                        "rule": i,
                        "type": "null_threshold",
                        "error": str(error)
                    })
                else:
                    report = unwrap(result)
                    passed += report.passed
                    failed += report.failed
                    if report.errors:
                        errors.extend([{"rule": i, **e} for e in report.errors])
                    if report.warnings:
                        warnings.extend([{"rule": i, **w} for w in report.warnings])

            else:
                return err(InvalidRuleError(
                    rule_type=rule_type or "unknown",
                    reason=f"Unknown rule type: {rule_type}"
                ))

        except Exception as e:
            return err(InvalidRuleError(
                rule_type=rule_type or "unknown",
                reason=f"Rule execution failed: {str(e)}"
            ))

    return ok(ValidationReport(
        passed=passed,
        failed=failed,
        errors=errors if errors else None,
        warnings=warnings if warnings else None
    ))
