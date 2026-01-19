"""Stable error codes for programmatic error handling.

This module defines numeric error codes that provide stable identification
of error types across versions. These codes enable AI agents and programmatic
clients to handle errors reliably without depending on error type names or messages.

Error Code Ranges:
    1xxx: Validation errors
    2xxx: Filtering errors
    3xxx: Sorting errors
    4xxx: Pivoting errors
    5xxx: Parsing errors
    6xxx: Aggregation errors
    7xxx: Comparison errors
    8xxx: Cleaning errors
    9xxx: Transforming errors
    10xxx: Joining errors
    11xxx: Validation operation errors
    12xxx: File handler errors

Example:
    >>> from excel_toolkit.models.error_codes import ErrorCode
    >>> ErrorCode.COLUMN_NOT_FOUND
    1001
"""

from enum import IntEnum


class ErrorCode(IntEnum):
    """Stable numeric error codes for all error types.

    These codes are guaranteed to remain stable across versions.
    When adding new error types, use the next available code in the appropriate range.
    """

    # =========================================================================
    # Validation Errors (1xxx)
    # =========================================================================

    # Security and syntax validation
    DANGEROUS_PATTERN = 1001
    CONDITION_TOO_LONG = 1002
    UNBALANCED_PARENTHESES = 1003
    UNBALANCED_BRACKETS = 1004
    UNBALANCED_QUOTES = 1005

    # Function and parameter validation
    INVALID_FUNCTION = 1006
    NO_COLUMNS = 1007
    NO_ROWS = 1008
    NO_VALUES = 1009
    INVALID_PARAMETER = 1010

    # Column validation
    COLUMN_NOT_FOUND = 1011
    COLUMNS_NOT_FOUND = 1012
    OVERLAPPING_COLUMNS = 1013

    # =========================================================================
    # Filtering Errors (2xxx)
    # =========================================================================

    QUERY_FAILED = 2001
    COLUMN_MISMATCH = 2002

    # =========================================================================
    # Sorting Errors (3xxx)
    # =========================================================================

    NOT_COMPARABLE = 3001
    SORT_FAILED = 3002

    # =========================================================================
    # Pivoting Errors (4xxx)
    # =========================================================================

    ROW_COLUMNS_NOT_FOUND = 4001
    COLUMN_COLUMNS_NOT_FOUND = 4002
    VALUE_COLUMNS_NOT_FOUND = 4003
    PIVOT_FAILED = 4004

    # =========================================================================
    # Parsing Errors (5xxx)
    # =========================================================================

    INVALID_FORMAT = 5001
    NO_VALID_SPECS = 5002

    # =========================================================================
    # Aggregation Errors (6xxx)
    # =========================================================================

    GROUP_COLUMNS_NOT_FOUND = 6001
    AGG_COLUMNS_NOT_FOUND = 6002
    AGGREGATION_FAILED = 6003

    # =========================================================================
    # Comparison Errors (7xxx)
    # =========================================================================

    KEY_COLUMNS_NOT_FOUND = 7001
    KEY_COLUMNS_NOT_FOUND_2 = 7002
    COMPARISON_FAILED = 7003

    # =========================================================================
    # Cleaning Errors (8xxx)
    # =========================================================================

    CLEANING_FAILED = 8001
    INVALID_FILL_STRATEGY = 8002
    FILL_FAILED = 8003

    # =========================================================================
    # Transforming Errors (9xxx)
    # =========================================================================

    INVALID_EXPRESSION = 9001
    INVALID_TYPE = 9002
    CAST_FAILED = 9003
    TRANSFORMING_FAILED = 9004
    INVALID_TRANSFORMATION = 9005

    # =========================================================================
    # Joining Errors (10xxx)
    # =========================================================================

    INVALID_JOIN_TYPE = 10001
    INVALID_JOIN_PARAMETERS = 10002
    JOIN_COLUMNS_NOT_FOUND = 10003
    MERGE_COLUMNS_NOT_FOUND = 10004
    INSUFFICIENT_DATAFRAMES = 10005
    JOINING_FAILED = 10006

    # =========================================================================
    # Validation Operation Errors (11xxx)
    # =========================================================================

    VALUE_OUT_OF_RANGE = 11001
    NULL_VALUE_THRESHOLD_EXCEEDED = 11002
    UNIQUENESS_VIOLATION = 11003
    INVALID_RULE = 11004
    TYPE_MISMATCH = 11005

    # =========================================================================
    # File Handler Errors (12xxx)
    # =========================================================================

    FILE_NOT_FOUND = 12001
    FILE_ACCESS_ERROR = 12002
    UNSUPPORTED_FORMAT = 12003
    INVALID_FILE = 12004
    FILE_SIZE_ERROR = 12005
    ENCODING_ERROR = 12006


# =============================================================================
# Error Code Categories
# =============================================================================

VALIDATION_ERRORS = {
    ErrorCode.DANGEROUS_PATTERN,
    ErrorCode.CONDITION_TOO_LONG,
    ErrorCode.UNBALANCED_PARENTHESES,
    ErrorCode.UNBALANCED_BRACKETS,
    ErrorCode.UNBALANCED_QUOTES,
    ErrorCode.INVALID_FUNCTION,
    ErrorCode.NO_COLUMNS,
    ErrorCode.NO_ROWS,
    ErrorCode.NO_VALUES,
    ErrorCode.INVALID_PARAMETER,
    ErrorCode.COLUMN_NOT_FOUND,
    ErrorCode.COLUMNS_NOT_FOUND,
    ErrorCode.OVERLAPPING_COLUMNS,
}

FILTERING_ERRORS = {
    ErrorCode.QUERY_FAILED,
    ErrorCode.COLUMN_MISMATCH,
}

SORTING_ERRORS = {
    ErrorCode.NOT_COMPARABLE,
    ErrorCode.SORT_FAILED,
}

PIVOTING_ERRORS = {
    ErrorCode.ROW_COLUMNS_NOT_FOUND,
    ErrorCode.COLUMN_COLUMNS_NOT_FOUND,
    ErrorCode.VALUE_COLUMNS_NOT_FOUND,
    ErrorCode.PIVOT_FAILED,
}

PARSING_ERRORS = {
    ErrorCode.INVALID_FORMAT,
    ErrorCode.NO_VALID_SPECS,
}

AGGREGATION_ERRORS = {
    ErrorCode.GROUP_COLUMNS_NOT_FOUND,
    ErrorCode.AGG_COLUMNS_NOT_FOUND,
    ErrorCode.AGGREGATION_FAILED,
}

COMPARISON_ERRORS = {
    ErrorCode.KEY_COLUMNS_NOT_FOUND,
    ErrorCode.KEY_COLUMNS_NOT_FOUND_2,
    ErrorCode.COMPARISON_FAILED,
}

CLEANING_ERRORS = {
    ErrorCode.CLEANING_FAILED,
    ErrorCode.INVALID_FILL_STRATEGY,
    ErrorCode.FILL_FAILED,
}

TRANSFORMING_ERRORS = {
    ErrorCode.INVALID_EXPRESSION,
    ErrorCode.INVALID_TYPE,
    ErrorCode.CAST_FAILED,
    ErrorCode.TRANSFORMING_FAILED,
    ErrorCode.INVALID_TRANSFORMATION,
}

JOINING_ERRORS = {
    ErrorCode.INVALID_JOIN_TYPE,
    ErrorCode.INVALID_JOIN_PARAMETERS,
    ErrorCode.JOIN_COLUMNS_NOT_FOUND,
    ErrorCode.MERGE_COLUMNS_NOT_FOUND,
    ErrorCode.INSUFFICIENT_DATAFRAMES,
    ErrorCode.JOINING_FAILED,
}

VALIDATION_OPERATION_ERRORS = {
    ErrorCode.VALUE_OUT_OF_RANGE,
    ErrorCode.NULL_VALUE_THRESHOLD_EXCEEDED,
    ErrorCode.UNIQUENESS_VIOLATION,
    ErrorCode.INVALID_RULE,
    ErrorCode.TYPE_MISMATCH,
}

FILE_HANDLER_ERRORS = {
    ErrorCode.FILE_NOT_FOUND,
    ErrorCode.FILE_ACCESS_ERROR,
    ErrorCode.UNSUPPORTED_FORMAT,
    ErrorCode.INVALID_FILE,
    ErrorCode.FILE_SIZE_ERROR,
    ErrorCode.ENCODING_ERROR,
}


# =============================================================================
# Utility Functions
# =============================================================================

def get_error_category(code: ErrorCode) -> str | None:
    """Get the category name for an error code.

    Args:
        code: Error code to categorize

    Returns:
        Category name or None if not found

    Example:
        >>> get_error_category(ErrorCode.COLUMN_NOT_FOUND)
        'VALIDATION'
    """
    categories = {
        "VALIDATION": VALIDATION_ERRORS,
        "FILTERING": FILTERING_ERRORS,
        "SORTING": SORTING_ERRORS,
        "PIVOTING": PIVOTING_ERRORS,
        "PARSING": PARSING_ERRORS,
        "AGGREGATION": AGGREGATION_ERRORS,
        "COMPARISON": COMPARISON_ERRORS,
        "CLEANING": CLEANING_ERRORS,
        "TRANSFORMING": TRANSFORMING_ERRORS,
        "JOINING": JOINING_ERRORS,
        "VALIDATION_OPERATION": VALIDATION_OPERATION_ERRORS,
        "FILE_HANDLER": FILE_HANDLER_ERRORS,
    }

    for category, codes in categories.items():
        if code in codes:
            return category
    return None
