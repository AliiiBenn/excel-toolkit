"""Transforming operations for DataFrames.

This module provides data transformation operations that can be applied to pandas DataFrames.
All functions return Result types for explicit error handling.
"""

from typing import Any, Callable
import re

import pandas as pd
import numpy as np

from excel_toolkit.fp import ok, err, is_ok, is_err, unwrap, unwrap_err, Result
from excel_toolkit.models.error_types import (
    ColumnNotFoundError,
    InvalidExpressionError,
    InvalidTypeError,
    CastFailedError,
    InvalidTransformationError,
    TransformingError,
)


# =============================================================================
# Expression Operations
# =============================================================================

# Dangerous patterns to block in expressions
DANGEROUS_PATTERNS = [
    r'\bimport\b',
    r'\bexec\b',
    r'\beval\b',
    r'\b__',
    r'\\_|__',
    r'\borg\.',
    r'\bsys\.',
    r'\bos\.',
    r'\bopen\b',
    r'\bcompile\b',
    r'\bgetattr\b',
    r'\bsetattr\b',
    r'\bdelaylass\b',
    r'\bglobals\b',
    r'\blocals\b',
    r'\bvars\b',
]


def validate_expression_security(expression: str) -> Result[None, InvalidExpressionError]:
    """Validate expression for dangerous patterns.

    Args:
        expression: Expression to validate

    Returns:
        Result[None, InvalidExpressionError] - Ok if safe, err if dangerous
    """
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, expression, re.IGNORECASE):
            return err(InvalidExpressionError(
                expression=expression,
                reason=f"Contains dangerous pattern: {pattern}"
            ))

    # Check for balanced parentheses, brackets
    if expression.count('(') != expression.count(')'):
        return err(InvalidExpressionError(
            expression=expression,
            reason="Unbalanced parentheses"
        ))

    if expression.count('[') != expression.count(']'):
        return err(InvalidExpressionError(
            expression=expression,
            reason="Unbalanced brackets"
        ))

    return ok(None)


def apply_expression(
    df: pd.DataFrame,
    column: str,
    expression: str,
    validate: bool = True
) -> Result[pd.DataFrame, InvalidExpressionError | ColumnNotFoundError | TransformingError]:
    """Apply expression to create or modify column.

    Args:
        df: Source DataFrame
        column: Column name to create or modify
        expression: Expression to evaluate (e.g., "Age * 2", "Name.upper()")
        validate: Whether to validate expression security

    Returns:
        Result[pd.DataFrame, InvalidExpressionError | ColumnNotFoundError | TransformingError] - Transformed DataFrame or error

    Errors:
        - InvalidExpressionError: Expression is invalid or contains dangerous patterns
        - ColumnNotFoundError: Referenced columns don't exist
        - TransformingError: Transformation failed

    Implementation:
        - If validate, check for dangerous patterns (same as filtering)
        - Use pandas.eval() with local_vars for column references
        - Support basic operations: +, -, *, /, **, comparisons, string methods
        - Create/modify column with result
        - Return modified DataFrame copy

    Security:
        - Validate against dangerous patterns if validate=True
        - Use restricted eval environment
        - Only allow column references and safe operations

    Examples:
        column="Total", expression="Price * Quantity"
        column="FullName", expression="FirstName + ' ' + LastName"
    """
    # Validate security if requested
    if validate:
        validation = validate_expression_security(expression)
        if is_err(validation):
            return validation

    # Create a copy to avoid modifying original
    df_transform = df.copy()

    try:
        # Try to evaluate the expression using df.eval() for better column reference support
        try:
            # Don't specify engine to let pandas choose the best one
            result = df_transform.eval(expression)
            df_transform[column] = result
        except NameError as e:
            # Column referenced in expression doesn't exist
            missing_col = str(e).split("'")[1] if "'" in str(e) else "unknown"
            return err(ColumnNotFoundError(
                column=missing_col,
                available=list(df.columns)
            ))
        except TypeError:
            # If eval fails with TypeError, try direct Series operations
            # This handles string concatenation and other operations
            try:
                # Build a namespace with Series
                series_dict = {col: df_transform[col] for col in df_transform.columns}
                # Evaluate the expression in the namespace
                result = eval(expression, {"__builtins__": {}}, series_dict)
                df_transform[column] = result
            except Exception as e:
                return err(TransformingError(
                    message=f"Failed to apply expression: {str(e)}"
                ))

        return ok(df_transform)

    except Exception as e:
        # Check if it's a KeyError (column not found)
        if isinstance(e, KeyError):
            missing_col = str(e).strip("'\"")
            return err(ColumnNotFoundError(
                column=missing_col,
                available=list(df.columns)
            ))
        return err(TransformingError(
            message=f"Failed to apply expression: {str(e)}"
        ))


# =============================================================================
# Type Casting Operations
# =============================================================================


def cast_columns(
    df: pd.DataFrame,
    column_types: dict[str, str]
) -> Result[pd.DataFrame, ColumnNotFoundError | InvalidTypeError | CastFailedError]:
    """Cast columns to specified types.

    Args:
        df: Source DataFrame
        column_types: Dictionary mapping column names to types
                     Types: "int", "float", "str", "bool", "datetime", "category"

    Returns:
        Result[pd.DataFrame, ColumnNotFoundError | InvalidTypeError | CastFailedError] - DataFrame with casted columns or error

    Errors:
        - ColumnNotFoundError: Specified columns don't exist
        - InvalidTypeError: Invalid type specified
        - CastFailedError: Casting failed (e.g., "abc" to int)

    Implementation:
        - Validate all columns exist
        - Validate all types are supported
        - For each column, apply conversion
        - Return modified DataFrame copy

    Examples:
        {"Age": "int", "Price": "float", "Active": "bool"}
    """
    valid_types = ["int", "float", "str", "bool", "datetime", "category"]

    # Validate columns exist
    missing_columns = [col for col in column_types.keys() if col not in df.columns]
    if missing_columns:
        return err(ColumnNotFoundError(
            column=missing_columns[0] if len(missing_columns) == 1 else f"{', '.join(missing_columns[:-1])} and {missing_columns[-1]}",
            available=list(df.columns)
        ))

    # Validate types
    invalid_types = [t for t in column_types.values() if t not in valid_types]
    if invalid_types:
        return err(InvalidTypeError(
            type_name=invalid_types[0] if len(invalid_types) == 1 else f"{', '.join(invalid_types[:-1])} and {invalid_types[-1]}",
            valid_types=valid_types
        ))

    # Create a copy
    df_cast = df.copy()

    # Cast each column
    for col, target_type in column_types.items():
        try:
            if target_type == "int":
                # Convert to numeric first, then to int
                df_cast[col] = pd.to_numeric(df_cast[col], errors="raise")
                # Check for NaN values (can't convert to int with NaN)
                if df_cast[col].isna().any():
                    return err(CastFailedError(
                        column=col,
                        target_type=target_type,
                        reason="Cannot convert column with NaN values to int"
                    ))
                df_cast[col] = df_cast[col].astype(int)

            elif target_type == "float":
                df_cast[col] = pd.to_numeric(df_cast[col], errors="raise").astype(float)

            elif target_type == "str":
                df_cast[col] = df_cast[col].astype(str)

            elif target_type == "bool":
                # Handle various boolean representations
                def to_bool(val):
                    if pd.isna(val):
                        return False
                    if isinstance(val, str):
                        val_lower = val.lower()
                        if val_lower in ['true', 'yes', '1', 't', 'y']:
                            return True
                        elif val_lower in ['false', 'no', '0', 'f', 'n']:
                            return False
                        else:
                            raise ValueError(f"Cannot convert {val} to bool")
                    return bool(val)

                df_cast[col] = df_cast[col].apply(to_bool)

            elif target_type == "datetime":
                # Try flexible parsing first
                df_cast[col] = pd.to_datetime(df_cast[col], errors="coerce", format="mixed")
                # If that fails, try default parsing
                if df_cast[col].isna().any():
                    original_was_na = df_cast[col].isna()
                    df_cast[col] = pd.to_datetime(df_cast[col], errors="coerce")
                    # Check if we made progress or if all values are still NaT
                    if df_cast[col].isna().all() and not original_was_na.all():
                        return err(CastFailedError(
                            column=col,
                            target_type=target_type,
                            reason="Could not parse any values as datetime"
                        ))

            elif target_type == "category":
                df_cast[col] = df_cast[col].astype("category")

        except ValueError as e:
            return err(CastFailedError(
                column=col,
                target_type=target_type,
                reason=str(e)
            ))
        except Exception as e:
            return err(CastFailedError(
                column=col,
                target_type=target_type,
                reason=str(e)
            ))

    return ok(df_cast)


# =============================================================================
# Mathematical Transformations
# =============================================================================


def transform_column(
    df: pd.DataFrame,
    column: str,
    transformation: str | Callable,
    params: dict[str, Any] | None = None
) -> Result[pd.DataFrame, ColumnNotFoundError | InvalidTransformationError | TransformingError]:
    """Apply transformation to column.

    Args:
        df: Source DataFrame
        column: Column name to transform
        transformation: Named transformation or callable
                       Named: "log", "sqrt", "abs", "exp", "standardize", "normalize"
        params: Additional parameters for transformation

    Returns:
        Result[pd.DataFrame, ColumnNotFoundError | InvalidTransformationError | TransformingError] - Transformed DataFrame or error

    Errors:
        - ColumnNotFoundError: Column doesn't exist
        - InvalidTransformationError: Invalid transformation name
        - TransformingError: Transformation failed

    Implementation:
        - Validate column exists
        - If transformation is string, apply named transformation
        - If transformation is callable, apply it to column
        - Handle errors (e.g., log of negative number)
        - Return modified DataFrame copy

    Examples:
        transformation="log" → Apply logarithm
        transformation="standardize" → Z-score normalization
        transformation=lambda x: x ** 2 → Square values
    """
    valid_transformations = ["log", "sqrt", "abs", "exp", "standardize", "normalize"]
    params = params or {}

    # Validate column exists
    if column not in df.columns:
        return err(ColumnNotFoundError(
            column=column,
            available=list(df.columns)
        ))

    # Create a copy
    df_transform = df.copy()

    try:
        if isinstance(transformation, str):
            # Named transformation
            if transformation not in valid_transformations:
                return err(InvalidTransformationError(
                    transformation=transformation,
                    valid_transformations=valid_transformations
                ))

            col_data = df_transform[column]

            if transformation == "log":
                # Check for non-positive values
                if (col_data <= 0).any():
                    return err(TransformingError(
                        message=f"Cannot apply log to column with non-positive values"
                    ))
                df_transform[column] = np.log(col_data)

            elif transformation == "sqrt":
                # Check for negative values
                if (col_data < 0).any():
                    return err(TransformingError(
                        message=f"Cannot apply sqrt to column with negative values"
                    ))
                df_transform[column] = np.sqrt(col_data)

            elif transformation == "abs":
                df_transform[column] = np.abs(col_data)

            elif transformation == "exp":
                df_transform[column] = np.exp(col_data)

            elif transformation == "standardize":
                # Z-score normalization: (x - mean) / std
                mean = col_data.mean()
                std = col_data.std()
                if std == 0:
                    return err(TransformingError(
                        message=f"Cannot standardize column with zero standard deviation"
                    ))
                df_transform[column] = (col_data - mean) / std

            elif transformation == "normalize":
                # Min-max normalization: (x - min) / (max - min)
                min_val = col_data.min()
                max_val = col_data.max()
                if max_val == min_val:
                    return err(TransformingError(
                        message=f"Cannot normalize column where min == max"
                    ))
                df_transform[column] = (col_data - min_val) / (max_val - min_val)

        elif callable(transformation):
            # Custom callable transformation
            df_transform[column] = df_transform[column].apply(transformation)

        else:
            return err(InvalidTransformationError(
                transformation=str(transformation),
                valid_transformations=valid_transformations
            ))

        return ok(df_transform)

    except Exception as e:
        return err(TransformingError(
            message=f"Transformation failed: {str(e)}"
        ))
