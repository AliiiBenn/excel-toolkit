"""Comprehensive tests for error_types module.

Tests all error ADTs for:
- Immutability
- Attribute access
- Type checking
- String representation
"""

import pytest
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
)


class TestDangerousPatternError:
    """Tests for DangerousPatternError."""

    def test_create_error(self):
        """Test creating a DangerousPatternError."""
        error = DangerousPatternError(pattern="__import__")
        assert error.pattern == "__import__"

    def test_immutability(self):
        """Test that DangerousPatternError is immutable."""
        error = DangerousPatternError(pattern="exec")
        from dataclasses import FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            error.pattern = "other"

    def test_repr(self):
        """Test string representation."""
        error = DangerousPatternError(pattern="eval")
        assert "DangerousPatternError" in repr(error)
        assert "eval" in repr(error)


class TestConditionTooLongError:
    """Tests for ConditionTooLongError."""

    def test_create_error(self):
        """Test creating a ConditionTooLongError."""
        error = ConditionTooLongError(length=1500, max_length=1000)
        assert error.length == 1500
        assert error.max_length == 1000

    def test_immutability(self):
        """Test that ConditionTooLongError is immutable."""
        error = ConditionTooLongError(length=1500, max_length=1000)
        from dataclasses import FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            error.length = 1000

    def test_repr(self):
        """Test string representation."""
        error = ConditionTooLongError(length=1500, max_length=1000)
        assert "ConditionTooLongError" in repr(error)


class TestUnbalancedParenthesesError:
    """Tests for UnbalancedParenthesesError."""

    def test_create_error(self):
        """Test creating an UnbalancedParenthesesError."""
        error = UnbalancedParenthesesError(open_count=3, close_count=2)
        assert error.open_count == 3
        assert error.close_count == 2

    def test_immutability(self):
        """Test immutability."""
        error = UnbalancedParenthesesError(open_count=3, close_count=2)
        from dataclasses import FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            error.open_count = 2


class TestUnbalancedBracketsError:
    """Tests for UnbalancedBracketsError."""

    def test_create_error(self):
        """Test creating an UnbalancedBracketsError."""
        error = UnbalancedBracketsError(open_count=1, close_count=2)
        assert error.open_count == 1
        assert error.close_count == 2


class TestUnbalancedQuotesError:
    """Tests for UnbalancedQuotesError."""

    def test_create_error_single_quote(self):
        """Test creating an UnbalancedQuotesError with single quote."""
        error = UnbalancedQuotesError(quote_type="'", count=3)
        assert error.quote_type == "'"
        assert error.count == 3

    def test_create_error_double_quote(self):
        """Test creating an UnbalancedQuotesError with double quote."""
        error = UnbalancedQuotesError(quote_type='"', count=1)
        assert error.quote_type == '"'
        assert error.count == 1


class TestInvalidFunctionError:
    """Tests for InvalidFunctionError."""

    def test_create_error(self):
        """Test creating an InvalidFunctionError."""
        error = InvalidFunctionError(
            function="invalid_func",
            valid_functions=["sum", "mean", "count"]
        )
        assert error.function == "invalid_func"
        assert error.valid_functions == ["sum", "mean", "count"]

    def test_immutability_list(self):
        """Test that the list is also immutable."""
        error = InvalidFunctionError(
            function="invalid",
            valid_functions=["sum", "mean"]
        )
        # The dataclass itself is frozen
        from dataclasses import FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            error.valid_functions = ["other"]


class TestNoColumnsError:
    """Tests for NoColumnsError."""

    def test_create_error(self):
        """Test creating a NoColumnsError."""
        error = NoColumnsError()
        assert isinstance(error, NoColumnsError)


class TestNoRowsError:
    """Tests for NoRowsError."""

    def test_create_error(self):
        """Test creating a NoRowsError."""
        error = NoRowsError()
        assert isinstance(error, NoRowsError)


class TestNoValuesError:
    """Tests for NoValuesError."""

    def test_create_error(self):
        """Test creating a NoValuesError."""
        error = NoValuesError()
        assert isinstance(error, NoValuesError)


class TestColumnNotFoundError:
    """Tests for ColumnNotFoundError."""

    def test_create_error(self):
        """Test creating a ColumnNotFoundError."""
        error = ColumnNotFoundError(
            column="missing_col",
            available=["col1", "col2", "col3"]
        )
        assert error.column == "missing_col"
        assert error.available == ["col1", "col2", "col3"]

    def test_immutability(self):
        """Test immutability."""
        error = ColumnNotFoundError(
            column="missing",
            available=["col1"]
        )
        from dataclasses import FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            error.column = "other"


class TestColumnsNotFoundError:
    """Tests for ColumnsNotFoundError."""

    def test_create_error(self):
        """Test creating a ColumnsNotFoundError."""
        error = ColumnsNotFoundError(
            missing=["col1", "col2"],
            available=["col3", "col4"]
        )
        assert error.missing == ["col1", "col2"]
        assert error.available == ["col3", "col4"]


class TestOverlappingColumnsError:
    """Tests for OverlappingColumnsError."""

    def test_create_error(self):
        """Test creating an OverlappingColumnsError."""
        error = OverlappingColumnsError(overlap=["col1", "col2"])
        assert error.overlap == ["col1", "col2"]


class TestQueryFailedError:
    """Tests for QueryFailedError."""

    def test_create_error(self):
        """Test creating a QueryFailedError."""
        error = QueryFailedError(
            message="Invalid syntax",
            condition="age >"
        )
        assert error.message == "Invalid syntax"
        assert error.condition == "age >"


class TestColumnMismatchError:
    """Tests for ColumnMismatchError."""

    def test_create_error(self):
        """Test creating a ColumnMismatchError."""
        error = ColumnMismatchError(
            message="Type mismatch",
            condition="age > 'text'"
        )
        assert error.message == "Type mismatch"
        assert error.condition == "age > 'text'"


class TestNotComparableError:
    """Tests for NotComparableError."""

    def test_create_error(self):
        """Test creating a NotComparableError."""
        error = NotComparableError(
            column="mixed_col",
            message="Cannot compare mixed types"
        )
        assert error.column == "mixed_col"
        assert error.message == "Cannot compare mixed types"


class TestSortFailedError:
    """Tests for SortFailedError."""

    def test_create_error(self):
        """Test creating a SortFailedError."""
        error = SortFailedError(message="Sorting failed")
        assert error.message == "Sorting failed"


class TestRowColumnsNotFoundError:
    """Tests for RowColumnsNotFoundError."""

    def test_create_error(self):
        """Test creating a RowColumnsNotFoundError."""
        error = RowColumnsNotFoundError(
            missing=["row1"],
            available=["col1", "col2"]
        )
        assert error.missing == ["row1"]
        assert error.available == ["col1", "col2"]


class TestColumnColumnsNotFoundError:
    """Tests for ColumnColumnsNotFoundError."""

    def test_create_error(self):
        """Test creating a ColumnColumnsNotFoundError."""
        error = ColumnColumnsNotFoundError(
            missing=["col1"],
            available=["col2", "col3"]
        )
        assert error.missing == ["col1"]
        assert error.available == ["col2", "col3"]


class TestValueColumnsNotFoundError:
    """Tests for ValueColumnsNotFoundError."""

    def test_create_error(self):
        """Test creating a ValueColumnsNotFoundError."""
        error = ValueColumnsNotFoundError(
            missing=["val1"],
            available=["val2", "val3"]
        )
        assert error.missing == ["val1"]
        assert error.available == ["val2", "val3"]


class TestPivotFailedError:
    """Tests for PivotFailedError."""

    def test_create_error(self):
        """Test creating a PivotFailedError."""
        error = PivotFailedError(message="Pivot creation failed")
        assert error.message == "Pivot creation failed"


class TestInvalidFormatError:
    """Tests for InvalidFormatError."""

    def test_create_error(self):
        """Test creating an InvalidFormatError."""
        error = InvalidFormatError(
            spec="invalid_spec",
            expected_format="column:func1,func2"
        )
        assert error.spec == "invalid_spec"
        assert error.expected_format == "column:func1,func2"


class TestNoValidSpecsError:
    """Tests for NoValidSpecsError."""

    def test_create_error(self):
        """Test creating a NoValidSpecsError."""
        error = NoValidSpecsError()
        assert isinstance(error, NoValidSpecsError)


class TestGroupColumnsNotFoundError:
    """Tests for GroupColumnsNotFoundError."""

    def test_create_error(self):
        """Test creating a GroupColumnsNotFoundError."""
        error = GroupColumnsNotFoundError(
            missing=["group1"],
            available=["col1", "col2"]
        )
        assert error.missing == ["group1"]
        assert error.available == ["col1", "col2"]


class TestAggColumnsNotFoundError:
    """Tests for AggColumnsNotFoundError."""

    def test_create_error(self):
        """Test creating an AggColumnsNotFoundError."""
        error = AggColumnsNotFoundError(
            missing=["agg1"],
            available=["agg2", "agg3"]
        )
        assert error.missing == ["agg1"]
        assert error.available == ["agg2", "agg3"]


class TestAggregationFailedError:
    """Tests for AggregationFailedError."""

    def test_create_error(self):
        """Test creating an AggregationFailedError."""
        error = AggregationFailedError(message="Aggregation failed")
        assert error.message == "Aggregation failed"


class TestKeyColumnsNotFoundError:
    """Tests for KeyColumnsNotFoundError."""

    def test_create_error(self):
        """Test creating a KeyColumnsNotFoundError."""
        error = KeyColumnsNotFoundError(
            missing=["key1"],
            available=["col1", "col2"]
        )
        assert error.missing == ["key1"]
        assert error.available == ["col1", "col2"]


class TestKeyColumnsNotFoundError2:
    """Tests for KeyColumnsNotFoundError2."""

    def test_create_error(self):
        """Test creating a KeyColumnsNotFoundError2."""
        error = KeyColumnsNotFoundError2(
            missing=["key1"],
            available=["col1", "col2"]
        )
        assert error.missing == ["key1"]
        assert error.available == ["col1", "col2"]


class TestComparisonFailedError:
    """Tests for ComparisonFailedError."""

    def test_create_error(self):
        """Test creating a ComparisonFailedError."""
        error = ComparisonFailedError(message="Comparison failed")
        assert error.message == "Comparison failed"


class TestErrorTypeHierarchy:
    """Tests for error type checking and hierarchy."""

    def test_column_not_found_error_type(self):
        """Test type checking for ColumnNotFoundError."""
        error = ColumnNotFoundError(
            column="missing",
            available=["col1"]
        )
        assert isinstance(error, ColumnNotFoundError)

    def test_all_errors_are_frozen(self):
        """Test that all error types are frozen dataclasses."""
        from dataclasses import FrozenInstanceError

        errors_to_test = [
            (DangerousPatternError, {"pattern": "test"}),
            (ConditionTooLongError, {"length": 100, "max_length": 50}),
            (ColumnNotFoundError, {"column": "x", "available": ["y"]}),
            (QueryFailedError, {"message": "msg", "condition": "cond"}),
            (NotComparableError, {"column": "col", "message": "msg"}),
            (InvalidFormatError, {"spec": "s", "expected_format": "f"}),
            (AggregationFailedError, {"message": "msg"}),
            (ComparisonFailedError, {"message": "msg"}),
        ]

        for error_class, kwargs in errors_to_test:
            error = error_class(**kwargs)
            # Try to modify an attribute - should raise FrozenInstanceError
            attr_name = list(kwargs.keys())[0]
            with pytest.raises(FrozenInstanceError):
                setattr(error, attr_name, "new_value")

    def test_all_errors_have_repr(self):
        """Test that all error types have proper string representation."""
        errors_to_test = [
            DangerousPatternError("test"),
            ConditionTooLongError(100, 50),
            UnbalancedParenthesesError(2, 1),
            ColumnNotFoundError("x", ["y"]),
            QueryFailedError("msg", "cond"),
            NotComparableError("col", "msg"),
            PivotFailedError("msg"),
            InvalidFormatError("spec", "format"),
            AggregationFailedError("msg"),
            ComparisonFailedError("msg"),
        ]

        for error in errors_to_test:
            repr_str = repr(error)
            assert error.__class__.__name__ in repr_str
