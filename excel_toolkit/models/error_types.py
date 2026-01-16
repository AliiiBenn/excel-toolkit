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


@dataclass
@immutable
class NoColumnsError:
    """No columns specified for an operation."""
    pass


@dataclass
@immutable
class NoRowsError:
    """No row columns specified for pivot operation."""
    pass


@dataclass
@immutable
class NoValuesError:
    """No value columns specified for pivot operation."""
    pass


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


@dataclass
@immutable
class OverlappingColumnsError:
    """Group and aggregation columns overlap.

    Attributes:
        overlap: List of column names that appear in both groups
    """
    overlap: list[str]


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


@dataclass
@immutable
class SortFailedError:
    """Sorting failed.

    Attributes:
        message: The error message
    """
    message: str


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


@dataclass
@immutable
class PivotFailedError:
    """Pivot table creation failed.

    Attributes:
        message: The error message
    """
    message: str


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


@dataclass
@immutable
class NoValidSpecsError:
    """No valid specifications found."""
    pass


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


@dataclass
@immutable
class AggregationFailedError:
    """Aggregation operation failed.

    Attributes:
        message: The error message
    """
    message: str


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


@dataclass
@immutable
class ComparisonFailedError:
    """Comparison operation failed.

    Attributes:
        message: The error message
    """
    message: str


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
class CleaningError(Error):
    """Base error for cleaning operations."""
    message: str


@dataclass
@immutable
class InvalidFillStrategyError(CleaningError):
    """Invalid fill strategy specified."""
    strategy: str
    valid_strategies: list[str] = field(default_factory=lambda: [
        "forward", "backward", "mean", "median", "constant", "drop"
    ])


@dataclass
@immutable
class FillFailedError(CleaningError):
    """Fill operation failed."""
    column: str
    reason: str


CleaningValidationError = (
    ColumnNotFoundError |
    InvalidParameterError
)

# Transforming operation errors
@dataclass
@immutable
class TransformError(Error):
    """Base error for transform operations."""
    message: str


@dataclass
@immutable
class InvalidExpressionError(TransformError):
    """Invalid expression provided."""
    expression: str
    reason: str


@dataclass
@immutable
class InvalidTypeError(TransformError):
    """Invalid type specified for casting."""
    type_name: str
    valid_types: list[str] = field(default_factory=lambda: [
        "int", "float", "str", "bool", "datetime", "category"
    ])


@dataclass
@immutable
class CastFailedError(TransformError):
    """Casting operation failed."""
    column: str
    target_type: str
    reason: str


@dataclass
@immutable
class InvalidTransformationError(TransformError):
    """Invalid transformation name."""
    transformation: str
    valid_transformations: list[str] = field(default_factory=lambda: [
        "log", "sqrt", "abs", "exp", "standardize", "normalize"
    ])


TransformValidationError = (
    ColumnNotFoundError |
    InvalidTypeError |
    InvalidTransformationError
)

# Joining operation errors
@dataclass
@immutable
class JoinError(Error):
    """Base error for join operations."""
    message: str


@dataclass
@immutable
class InvalidJoinTypeError(JoinError):
    """Invalid join type specified."""
    join_type: str
    valid_types: list[str] = field(default_factory=lambda: [
        "inner", "left", "right", "outer", "cross"
    ])


@dataclass
@immutable
class InvalidJoinParametersError(JoinError):
    """Invalid combination of join parameters."""
    reason: str


@dataclass
@immutable
class JoinColumnsNotFoundError(JoinError):
    """Join columns not found in DataFrames."""
    missing_in_left: list[str] = field(default_factory=list)
    missing_in_right: list[str] = field(default_factory=list)


@dataclass
@immutable
class MergeColumnsNotFoundError(JoinError):
    """Merge columns not found in all DataFrames."""
    missing: dict[int, list[str]] = field(default_factory dict)  # DataFrame index -> missing columns


@dataclass
@immutable
class InsufficientDataFramesError(JoinError):
    """Less than 2 DataFrames provided for merge."""
    count: int


JoinValidationError = (
    InvalidJoinParametersError |
    JoinColumnsNotFoundError
)

JoinOperationError = (
    InvalidJoinTypeError |
    JoinValidationError |
    JoinColumnsNotFoundError
)

# Validation operation errors
@dataclass
@immutable
class ValidationError(Error):
    """Base error for validation operations."""
    message: str


@dataclass
@immutable
class ValueOutOfRangeError(ValidationError):
    """Values outside specified range."""
    column: str
    min_value: Any
    max_value: Any
    violation_count: int


@dataclass
@immutable
class NullValueThresholdExceededError(ValidationError):
    """Null values exceed threshold."""
    column: str
    null_count: int
    null_percent: float
    threshold: float


@dataclass
@immutable
class UniquenessViolationError(ValidationError):
    """Duplicate values found."""
    columns: list[str]
    duplicate_count: int
    sample_duplicates: list = field(default_factory=list)


@dataclass
@immutable
class InvalidRuleError(ValidationError):
    """Invalid validation rule."""
    rule_type: str
    reason: str


@dataclass
@immutable
class TypeMismatchError(ValidationError):
    """Column type doesn't match expected type."""
    column: str
    expected_type: str | list[str]
    actual_type: str


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
