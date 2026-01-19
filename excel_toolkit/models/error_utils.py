"""Utility functions and mixins for error serialization and handling.

This module provides helper functions and a base mixin class for converting
error types to JSON-serializable dictionaries, making them suitable for AI
agent consumption.
"""

from dataclasses import asdict, is_dataclass
from datetime import datetime
from difflib import get_close_matches
from typing import Any
import pandas as pd


class ErrorSerializable:
    """Mixin class that adds to_dict() method to error types.

    This mixin provides a consistent serialization interface for all error
    types. It should be inherited by all error dataclasses.

    Example:
        @dataclass
        @immutable
        class MyError(ErrorSerializable):
            error_code: int = 1001
            message: str

        error = MyError(message="Something went wrong")
        error_dict = error.to_dict()
    """

    def to_dict(self) -> dict:
        """Convert the error to a JSON-serializable dictionary.

        Returns:
            Dictionary representation of the error with all values serializable

        Example:
            >>> error = ColumnNotFoundError(column="Age", available=["Name", "Email"])
            >>> error.to_dict()
            {
                'error_type': 'ColumnNotFoundError',
                'ERROR_CODE': 1011,
                'column': 'Age',
                'available': ['Name', 'Email'],
                'suggestions': [...]
            }
        """
        if not is_dataclass(self):
            return {
                "error_type": type(self).__name__,
                "ERROR_CODE": get_error_code_value(self),
                "message": str(self)
            }

        # Get the dataclass as a dict
        result = asdict(self)

        # Add error_type
        result["error_type"] = type(self).__name__

        # Ensure all values are JSON-serializable
        result = _make_json_serializable(result)

        # Add automatic suggestions
        result = _add_suggestions(self, result)

        return result


def error_to_dict(error: Any) -> dict:
    """Convert an error object to a JSON-serializable dictionary.

    This function handles the conversion of error dataclasses to dictionaries,
    ensuring that all values are JSON-serializable. It handles special cases
    like pandas dtypes, datetime objects, and converts them to strings.
    Also adds automatic suggestions for typos and invalid inputs.

    Args:
        error: Error object (typically a dataclass error type)

    Returns:
        Dictionary representation of the error with all values serializable

    Example:
        >>> error = ColumnNotFoundError(column="Aeg", available=["Name", "Age", "Email"])
        >>> error_dict = error_to_dict(error)
        >>> print(error_dict)
        {
            'error_type': 'ColumnNotFoundError',
            'ERROR_CODE': 1011,
            'column': 'Aeg',
            'available': ['Name', 'Age', 'Email'],
            'suggestions': [
                {'field': 'column', 'provided': 'Aeg', 'suggestions': ['Age', 'Name']}
            ]
        }
    """
    if not is_dataclass(error):
        return {
            "error_type": type(error).__name__,
            "ERROR_CODE": get_error_code_value(error),
            "message": str(error)
        }

    # Get the dataclass as a dict
    result = asdict(error)

    # Add error_type
    result["error_type"] = type(error).__name__

    # Ensure all values are JSON-serializable
    result = _make_json_serializable(result)

    # Add automatic suggestions
    result = _add_suggestions(error, result)

    return result


def _make_json_serializable(obj: Any) -> Any:
    """Convert an object to a JSON-serializable format.

    Args:
        obj: Object to convert

    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_make_json_serializable(item) for item in obj]
    elif isinstance(obj, pd.DataFrame):
        # Convert DataFrame to dict representation
        return obj.to_dict(orient="records")
    elif hasattr(obj, "dtype"):  # numpy dtype, pandas dtype, etc.
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif callable(obj):
        return str(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj


def get_error_type_name(error: Any) -> str:
    """Get the type name of an error.

    Args:
        error: Error object

    Returns:
        Name of the error type

    Example:
        >>> error = ColumnNotFoundError(column="Age", available=[])
        >>> get_error_type_name(error)
        'ColumnNotFoundError'
    """
    return type(error).__name__


def get_error_code_value(error: Any) -> int | None:
    """Get the error code value from an error object.

    Args:
        error: Error object

    Returns:
        Error code value or None if not present

    Example:
        >>> error = ColumnNotFoundError(column="Age", available=[])
        >>> get_error_code_value(error)
        1011
    """
    # Try ERROR_CODE (class attribute) first, then error_code (instance attribute)
    return getattr(error, "ERROR_CODE", None) or getattr(error, "error_code", None)


def _add_suggestions(error: Any, error_dict: dict) -> dict:
    """Add automatic suggestions to error dictionary based on error type.

    Uses fuzzy matching to suggest similar values for typos and invalid inputs.

    Args:
        error: Error object
        error_dict: Dictionary representation of the error

    Returns:
        Enhanced error dictionary with suggestions field
    """
    error_type = type(error).__name__
    suggestions = []

    # ColumnNotFoundError: suggest similar column names
    if error_type == "ColumnNotFoundError" and hasattr(error, "available"):
        column = getattr(error, "column", "")
        available = getattr(error, "available", [])
        matches = get_close_matches(column, available, n=3, cutoff=0.6)
        if matches:
            suggestions.append({
                "field": "column",
                "provided": column,
                "suggestions": matches
            })

    # ColumnsNotFoundError: suggest similar column names for each missing column
    elif error_type == "ColumnsNotFoundError" and hasattr(error, "missing") and hasattr(error, "available"):
        missing = getattr(error, "missing", [])
        available = getattr(error, "available", [])
        for column in missing:
            matches = get_close_matches(column, available, n=3, cutoff=0.6)
            if matches:
                suggestions.append({
                    "field": "columns",
                    "provided": column,
                    "suggestions": matches
                })

    # InvalidFunctionError: suggest similar function names
    elif error_type == "InvalidFunctionError" and hasattr(error, "valid_functions"):
        function = getattr(error, "function", "")
        valid = getattr(error, "valid_functions", [])
        matches = get_close_matches(function, valid, n=3, cutoff=0.6)
        if matches:
            suggestions.append({
                "field": "function",
                "provided": function,
                "suggestions": matches
            })

    # InvalidFillStrategyError: suggest similar strategies
    elif error_type == "InvalidFillStrategyError" and hasattr(error, "valid_strategies"):
        strategy = getattr(error, "strategy", "")
        valid = getattr(error, "valid_strategies", [])
        matches = get_close_matches(strategy, valid, n=3, cutoff=0.6)
        if matches:
            suggestions.append({
                "field": "strategy",
                "provided": strategy,
                "suggestions": matches
            })

    # InvalidTypeError: suggest similar types
    elif error_type == "InvalidTypeError" and hasattr(error, "valid_types"):
        type_name = getattr(error, "type_name", "")
        valid = getattr(error, "valid_types", [])
        matches = get_close_matches(type_name, valid, n=3, cutoff=0.6)
        if matches:
            suggestions.append({
                "field": "type",
                "provided": type_name,
                "suggestions": matches
            })

    # InvalidTransformationError: suggest similar transformations
    elif error_type == "InvalidTransformationError" and hasattr(error, "valid_transformations"):
        transformation = getattr(error, "transformation", "")
        valid = getattr(error, "valid_transformations", [])
        matches = get_close_matches(transformation, valid, n=3, cutoff=0.6)
        if matches:
            suggestions.append({
                "field": "transformation",
                "provided": transformation,
                "suggestions": matches
            })

    # InvalidJoinTypeError: suggest similar join types
    elif error_type == "InvalidJoinTypeError" and hasattr(error, "valid_types"):
        join_type = getattr(error, "join_type", "")
        valid = getattr(error, "valid_types", [])
        matches = get_close_matches(join_type, valid, n=3, cutoff=0.6)
        if matches:
            suggestions.append({
                "field": "join_type",
                "provided": join_type,
                "suggestions": matches
            })

    # InvalidParameterError: suggest similar parameter values
    elif error_type == "InvalidParameterError" and hasattr(error, "valid_values") and getattr(error, "valid_values"):
        parameter = getattr(error, "parameter", "")
        value = getattr(error, "value", "")
        valid = getattr(error, "valid_values", [])
        # Try to match value against valid values
        if isinstance(value, str):
            matches = get_close_matches(value, valid, n=3, cutoff=0.6)
            if matches:
                suggestions.append({
                    "field": parameter,
                    "provided": value,
                    "suggestions": matches
                })

    # Add suggestions to error_dict if any were found
    if suggestions:
        error_dict["suggestions"] = suggestions

    return error_dict
