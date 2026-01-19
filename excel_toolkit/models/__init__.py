"""Data models and type definitions."""

# Export error codes
from excel_toolkit.models.error_codes import ErrorCode, get_error_category

# Export error utilities and serialization
from excel_toolkit.models.error_utils import (
    ErrorSerializable,
    error_to_dict,
    get_error_type_name,
    get_error_code_value,
)

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
    # Phase 2: Support operations
    CleaningError,
    InvalidFillStrategyError,
    FillFailedError,
    InvalidExpressionError,
    InvalidTypeError,
    CastFailedError,
    TransformingError,
    InvalidTransformationError,
    InvalidJoinTypeError,
    InvalidJoinParametersError,
    JoinColumnsNotFoundError,
    MergeColumnsNotFoundError,
    InsufficientDataFramesError,
    JoiningError,
    ValueOutOfRangeError,
    NullValueThresholdExceededError,
    UniquenessViolationError,
    InvalidRuleError,
    TypeMismatchError,
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
    # Phase 2 errors
    "CleaningError",
    "InvalidFillStrategyError",
    "FillFailedError",
    "InvalidExpressionError",
    "InvalidTypeError",
    "CastFailedError",
    "TransformingError",
    "InvalidTransformationError",
    "InvalidJoinTypeError",
    "InvalidJoinParametersError",
    "JoinColumnsNotFoundError",
    "MergeColumnsNotFoundError",
    "InsufficientDataFramesError",
    "JoiningError",
    "ValueOutOfRangeError",
    "NullValueThresholdExceededError",
    "UniquenessViolationError",
    "InvalidRuleError",
    "TypeMismatchError",
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
    # Error utilities
    "ErrorCode",
    "get_error_category",
    "ErrorSerializable",
    "error_to_dict",
    "get_error_type_name",
    "get_error_code_value",
]
