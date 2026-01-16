"""Data models and type definitions."""

# Export all error types
from excel_toolkit.models.error_types import (
    # Validation errors
    DangerousPatternError,
    ConditionTooLongError,
    UnbalancedParenthesesError,
    UnbalancedBracketsError,
    UnbalancedQuotesError,
    InvalidFunctionError,
    NoColumnsError,
    NoRowsError,
    NoValuesError,
    ColumnNotFoundError,
    ColumnsNotFoundError,
    OverlappingColumnsError,
    # Filter errors
    QueryFailedError,
    ColumnMismatchError,
    # Sort errors
    NotComparableError,
    SortFailedError,
    # Pivot errors
    RowColumnsNotFoundError,
    ColumnColumnsNotFoundError,
    ValueColumnsNotFoundError,
    PivotFailedError,
    # Parse errors
    InvalidFormatError,
    NoValidSpecsError,
    # Aggregation errors
    GroupColumnsNotFoundError,
    AggColumnsNotFoundError,
    AggregationFailedError,
    # Compare errors
    KeyColumnsNotFoundError,
    KeyColumnsNotFoundError2,
    ComparisonFailedError,
    # Type aliases
    ValidationError,
    FilterError,
    SortValidationError,
    SortError,
    PivotValidationError,
    PivotError,
    ParseError,
    AggregationValidationError,
    AggregationError,
    ComparisonValidationError,
    CompareError,
)

__all__ = [
    # Validation errors
    "DangerousPatternError",
    "ConditionTooLongError",
    "UnbalancedParenthesesError",
    "UnbalancedBracketsError",
    "UnbalancedQuotesError",
    "InvalidFunctionError",
    "NoColumnsError",
    "NoRowsError",
    "NoValuesError",
    "ColumnNotFoundError",
    "ColumnsNotFoundError",
    "OverlappingColumnsError",
    # Filter errors
    "QueryFailedError",
    "ColumnMismatchError",
    # Sort errors
    "NotComparableError",
    "SortFailedError",
    # Pivot errors
    "RowColumnsNotFoundError",
    "ColumnColumnsNotFoundError",
    "ValueColumnsNotFoundError",
    "PivotFailedError",
    # Parse errors
    "InvalidFormatError",
    "NoValidSpecsError",
    # Aggregation errors
    "GroupColumnsNotFoundError",
    "AggColumnsNotFoundError",
    "AggregationFailedError",
    # Compare errors
    "KeyColumnsNotFoundError",
    "KeyColumnsNotFoundError2",
    "ComparisonFailedError",
    # Type aliases
    "ValidationError",
    "FilterError",
    "SortValidationError",
    "SortError",
    "PivotValidationError",
    "PivotError",
    "ParseError",
    "AggregationValidationError",
    "AggregationError",
    "ComparisonValidationError",
    "CompareError",
]
