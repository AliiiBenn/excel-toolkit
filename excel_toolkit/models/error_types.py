"""Error type definitions for operations.

This module defines Algebraic Data Types (ADTs) for structured error representation.
All error types are immutable dataclasses to ensure error values cannot be modified
after creation, making error handling more predictable and safer.

Error types are organized by category:
- ValidationError: Input validation errors
- FilterError: Filtering operation errors
- SortError: Sorting operation errors
- PivotError: Pivot table operation errors
- ParseError: Parsing errors (for aggregation specs)
- AggregationError: Aggregation operation errors
- CompareError: Comparison operation errors
"""

from dataclasses import field
from excel_toolkit.fp.immutable import immutable, dataclass
from typing import Any, Callable
from excel_toolkit.models.error_codes import ErrorCode


# =============================================================================
# Validation Errors
# =============================================================================

@dataclass
@immutable
class DangerousPatternError:
    """Condition contains dangerous code pattern.

    Attributes:
        pattern: The dangerous pattern that was detected
    """
    pattern: str
    ERROR_CODE: int = ErrorCode.DANGEROUS_PATTERN


@dataclass
@immutable
class ConditionTooLongError:
    """Condition exceeds maximum allowed length.

    Attributes:
        length: The actual length of the condition
        max_length: The maximum allowed length
    """
    length: int
    max_length: int
    ERROR_CODE: int = ErrorCode.CONDITION_TOO_LONG


@dataclass
@immutable
class UnbalancedParenthesesError:
    """Condition has unbalanced parentheses.

    Attributes:
        open_count: Number of opening parentheses
        close_count: Number of closing parentheses
    """
    open_count: int
    close_count: int
    ERROR_CODE: int = ErrorCode.UNBALANCED_PARENTHESES


@dataclass
@immutable
class UnbalancedBracketsError:
    """Condition has unbalanced brackets.

    Attributes:
        open_count: Number of opening brackets
        close_count: Number of closing brackets
    """
    open_count: int
    close_count: int
    ERROR_CODE: int = ErrorCode.UNBALANCED_BRACKETS


@dataclass
@immutable
class UnbalancedQuotesError:
    """Condition has unbalanced quotes.

    Attributes:
        quote_type: The type of quote (' or ")
        count: The number of quotes (should be even)
    """
    quote_type: str
    count: int
    ERROR_CODE: int = ErrorCode.UNBALANCED_QUOTES


@dataclass
@immutable
class InvalidFunctionError:
    """Invalid aggregation function name.

    Attributes:
        function: The invalid function name provided
        valid_functions: List of valid function names
    """
    function: str
    valid_functions: list[str]
    ERROR_CODE: int = ErrorCode.INVALID_FUNCTION


@dataclass
@immutable
class NoColumnsError:
    """No columns specified for an operation."""
    pass
    ERROR_CODE: int = ErrorCode.NO_COLUMNS


@dataclass
@immutable
class NoRowsError:
    """No row columns specified for pivot operation."""
    pass
    ERROR_CODE: int = ErrorCode.NO_ROWS


@dataclass
@immutable
class NoValuesError:
    """No value columns specified for pivot operation."""
    pass
    ERROR_CODE: int = ErrorCode.NO_VALUES


@dataclass
@immutable
class InvalidParameterError:
    """Invalid parameter provided."""

    parameter: str
    value: Any
    valid_values: list[str] | None = None
    ERROR_CODE: int = ErrorCode.INVALID_PARAMETER


@dataclass
@immutable
class ColumnNotFoundError:
    """Referenced column doesn't exist in DataFrame.

    Attributes:
        column: The column name that was not found
        available: List of available column names
    """
    column: str
    available: list[str]
    ERROR_CODE: int = ErrorCode.COLUMN_NOT_FOUND


@dataclass
@immutable
class ColumnsNotFoundError:
    """Multiple columns don't exist in DataFrame.

    Attributes:
        missing: List of column names that were not found
        available: List of available column names
    """
    missing: list[str]
    available: list[str]
    ERROR_CODE: int = ErrorCode.COLUMNS_NOT_FOUND


@dataclass
@immutable
class OverlappingColumnsError:
    """Group and aggregation columns overlap.

    Attributes:
        overlap: List of column names that appear in both groups
    """
    overlap: list[str]
    ERROR_CODE: int = ErrorCode.OVERLAPPING_COLUMNS


# =============================================================================
# Filter Errors
# =============================================================================

@dataclass
@immutable
class QueryFailedError:
    """Query execution failed.

    Attributes:
        message: The error message
        condition: The condition that caused the error
    """
    message: str
    condition: str
    ERROR_CODE: int = ErrorCode.QUERY_FAILED


@dataclass
@immutable
class ColumnMismatchError:
    """Type mismatch in comparison.

    Attributes:
        message: The error message
        condition: The condition that caused the error
    """
    message: str
    condition: str
    ERROR_CODE: int = ErrorCode.COLUMN_MISMATCH


# =============================================================================
# Sort Errors
# =============================================================================

@dataclass
@immutable
class NotComparableError:
    """Cannot sort mixed data types in column.

    Attributes:
        column: The column name
        message: The error message
    """
    column: str
    message: str
    ERROR_CODE: int = ErrorCode.NOT_COMPARABLE


@dataclass
@immutable
class SortFailedError:
    """Sorting failed.

    Attributes:
        message: The error message
    """
    message: str
    ERROR_CODE: int = ErrorCode.SORT_FAILED


# =============================================================================
# Pivot Errors
# =============================================================================

@dataclass
@immutable
class RowColumnsNotFoundError:
    """Row columns don't exist for pivot.

    Attributes:
        missing: List of missing column names
        available: List of available column names
    """
    missing: list[str]
    available: list[str]
    ERROR_CODE: int = ErrorCode.ROW_COLUMNS_NOT_FOUND


@dataclass
@immutable
class ColumnColumnsNotFoundError:
    """Column columns don't exist for pivot.

    Attributes:
        missing: List of missing column names
        available: List of available column names
    """
    missing: list[str]
    available: list[str]
    ERROR_CODE: int = ErrorCode.COLUMN_COLUMNS_NOT_FOUND


@dataclass
@immutable
class ValueColumnsNotFoundError:
    """Value columns don't exist for pivot.

    Attributes:
        missing: List of missing column names
        available: List of available column names
    """
    missing: list[str]
    available: list[str]
    ERROR_CODE: int = ErrorCode.VALUE_COLUMNS_NOT_FOUND


@dataclass
@immutable
class PivotFailedError:
    """Pivot table creation failed.

    Attributes:
        message: The error message
    """
    message: str
    ERROR_CODE: int = ErrorCode.PIVOT_FAILED


# =============================================================================
# Parse Errors
# =============================================================================

@dataclass
@immutable
class InvalidFormatError:
    """Invalid format for parsing.

    Attributes:
        spec: The specification that failed to parse
        expected_format: Description of expected format
    """
    spec: str
    expected_format: str
    ERROR_CODE: int = ErrorCode.INVALID_FORMAT


@dataclass
@immutable
class NoValidSpecsError:
    """No valid specifications found."""
    pass
    ERROR_CODE: int = ErrorCode.NO_VALID_SPECS


# =============================================================================
# Aggregation Errors
# =============================================================================

@dataclass
@immutable
class GroupColumnsNotFoundError:
    """Group columns don't exist.

    Attributes:
        missing: List of missing column names
        available: List of available column names
    """
    missing: list[str]
    available: list[str]
    ERROR_CODE: int = ErrorCode.GROUP_COLUMNS_NOT_FOUND


@dataclass
@immutable
class AggColumnsNotFoundError:
    """Aggregation columns don't exist.

    Attributes:
        missing: List of missing column names
        available: List of available column names
    """
    missing: list[str]
    available: list[str]
    ERROR_CODE: int = ErrorCode.AGG_COLUMNS_NOT_FOUND


@dataclass
@immutable
class AggregationFailedError:
    """Aggregation operation failed.

    Attributes:
        message: The error message
    """
    message: str
    ERROR_CODE: int = ErrorCode.AGGREGATION_FAILED


# =============================================================================
# Compare Errors
# =============================================================================

@dataclass
@immutable
class KeyColumnsNotFoundError:
    """Key columns don't exist in first DataFrame.

    Attributes:
        missing: List of missing column names
        available: List of available column names
    """
    missing: list[str]
    available: list[str]
    ERROR_CODE: int = ErrorCode.KEY_COLUMNS_NOT_FOUND


@dataclass
@immutable
class KeyColumnsNotFoundError2:
    """Key columns don't exist in second DataFrame.

    Attributes:
        missing: List of missing column names
        available: List of available column names
    """
    missing: list[str]
    available: list[str]
    ERROR_CODE: int = ErrorCode.KEY_COLUMNS_NOT_FOUND_2


@dataclass
@immutable
class ComparisonFailedError:
    """Comparison operation failed.

    Attributes:
        message: The error message
    """
    message: str
    ERROR_CODE: int = ErrorCode.COMPARISON_FAILED


# =============================================================================
# Result Types (Type Aliases)
# =============================================================================

# Validation errors can be any of the validation-specific errors
ValidationError = (
    DangerousPatternError |
    ConditionTooLongError |
    UnbalancedParenthesesError |
    UnbalancedBracketsError |
    UnbalancedQuotesError |
    InvalidFunctionError |
    NoColumnsError |
    NoRowsError |
    NoValuesError |
    ColumnNotFoundError |
    ColumnsNotFoundError |
    OverlappingColumnsError
)

# Filter operation errors
FilterError = (
    ColumnNotFoundError |
    QueryFailedError |
    ColumnMismatchError |
    ColumnsNotFoundError
)

# Sort operation errors
SortValidationError = NoColumnsError | ColumnNotFoundError
SortError = NotComparableError | SortFailedError

# Pivot operation errors
PivotValidationError = (
    InvalidFunctionError |
    NoRowsError |
    NoColumnsError |
    NoValuesError |
    RowColumnsNotFoundError |
    ColumnColumnsNotFoundError |
    ValueColumnsNotFoundError
)
PivotError = PivotFailedError

# Parse errors for aggregation specifications
ParseError = (
    InvalidFormatError |
    InvalidFunctionError |
    NoValidSpecsError
)

# Aggregation operation errors
AggregationValidationError = (
    GroupColumnsNotFoundError |
    AggColumnsNotFoundError |
    OverlappingColumnsError
)
AggregationError = AggregationFailedError

# Comparison operation errors
ComparisonValidationError = (
    KeyColumnsNotFoundError |
    KeyColumnsNotFoundError2
)
CompareError = ComparisonFailedError

# =============================================================================
# Phase 2: Support Operations Error Types
# =============================================================================

# Cleaning operation errors
@dataclass
@immutable
class CleaningError:
    """Generic cleaning operation failed."""

    message: str
    ERROR_CODE: int = ErrorCode.CLEANING_FAILED
@dataclass
@immutable
class InvalidFillStrategyError:
    """Invalid fill strategy specified."""

    strategy: str
    valid_strategies: list[str] = field(default_factory=lambda: [
        "forward", "backward", "mean", "median", "constant", "drop"
    ])
    ERROR_CODE: int = ErrorCode.INVALID_FILL_STRATEGY


@dataclass
@immutable
class FillFailedError:
    """Fill operation failed."""

    column: str
    reason: str
    ERROR_CODE: int = ErrorCode.FILL_FAILED


# Transforming operation errors
@dataclass
@immutable
class InvalidExpressionError:
    """Invalid expression provided."""

    expression: str
    reason: str
    ERROR_CODE: int = ErrorCode.INVALID_EXPRESSION


@dataclass
@immutable
class InvalidTypeError:
    """Invalid type specified for casting."""

    type_name: str
    valid_types: list[str] = field(default_factory=lambda: [
        "int", "float", "str", "bool", "datetime", "category"
    ])
    ERROR_CODE: int = ErrorCode.INVALID_TYPE


@dataclass
@immutable
class CastFailedError:
    """Casting operation failed."""

    column: str
    target_type: str
    reason: str
    ERROR_CODE: int = ErrorCode.CAST_FAILED


@dataclass
@immutable
class TransformingError:
    """Generic transforming operation failed."""

    message: str
    ERROR_CODE: int = ErrorCode.TRANSFORMING_FAILED


@dataclass
@immutable
class InvalidTransformationError:
    """Invalid transformation name."""

    transformation: str
    valid_transformations: list[str] = field(default_factory=lambda: [
        "log", "sqrt", "abs", "exp", "standardize", "normalize"
    ])
    ERROR_CODE: int = ErrorCode.INVALID_TRANSFORMATION


# Joining operation errors
@dataclass
@immutable
class InvalidJoinTypeError:
    """Invalid join type specified."""

    join_type: str
    valid_types: list[str] = field(default_factory=lambda: [
        "inner", "left", "right", "outer", "cross"
    ])
    ERROR_CODE: int = ErrorCode.INVALID_JOIN_TYPE


@dataclass
@immutable
class InvalidJoinParametersError:
    """Invalid combination of join parameters."""

    reason: str
    ERROR_CODE: int = ErrorCode.INVALID_JOIN_PARAMETERS


@dataclass
@immutable
class JoinColumnsNotFoundError:
    """Join columns not found in DataFrames."""

    missing_in_left: list[str] = field(default_factory=list)
    missing_in_right: list[str] = field(default_factory=list)
    ERROR_CODE: int = ErrorCode.JOIN_COLUMNS_NOT_FOUND


@dataclass
@immutable
class MergeColumnsNotFoundError:
    """Merge columns not found in all DataFrames."""

    missing: dict[int, list[str]] = field(default_factory=lambda: {})  # DataFrame index -> missing columns
    ERROR_CODE: int = ErrorCode.MERGE_COLUMNS_NOT_FOUND


@dataclass
@immutable
class InsufficientDataFramesError:
    """Less than 2 DataFrames provided for merge."""

    count: int
    ERROR_CODE: int = ErrorCode.INSUFFICIENT_DATAFRAMES


@dataclass
@immutable
class JoiningError:
    """Generic joining operation failed."""

    message: str
    ERROR_CODE: int = ErrorCode.JOINING_FAILED


# Validation operation errors
@dataclass
@immutable
class ValueOutOfRangeError:
    """Values outside specified range."""

    column: str
    min_value: Any
    max_value: Any
    violation_count: int
    ERROR_CODE: int = ErrorCode.VALUE_OUT_OF_RANGE


@dataclass
@immutable
class NullValueThresholdExceededError:
    """Null values exceed threshold."""

    column: str
    null_count: int
    null_percent: float
    threshold: float
    ERROR_CODE: int = ErrorCode.NULL_VALUE_THRESHOLD_EXCEEDED


@dataclass
@immutable
class UniquenessViolationError:
    """Duplicate values found."""

    columns: list[str]
    duplicate_count: int
    sample_duplicates: list = field(default_factory=list)
    ERROR_CODE: int = ErrorCode.UNIQUENESS_VIOLATION


@dataclass
@immutable
class InvalidRuleError:
    """Invalid validation rule."""

    rule_type: str
    reason: str
    ERROR_CODE: int = ErrorCode.INVALID_RULE


@dataclass
@immutable
class TypeMismatchError:
    """Column type doesn't match expected type."""

    column: str
    expected_type: str | list[str]
    actual_type: str
    ERROR_CODE: int = ErrorCode.TYPE_MISMATCH


# Validation result structure (not an error type, mutable)
class ValidationReport:
    """Report from validate_dataframe()."""

    def __init__(
        self,
        passed: int,
        failed: int,
        errors: list[dict] | None = None,
        warnings: list[dict] | None = None
    ):
        self.passed = passed
        self.failed = failed
        self.errors = errors or []
        self.warnings = warnings or []
