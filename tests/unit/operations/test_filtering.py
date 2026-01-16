"""Comprehensive tests for filtering operations.

Tests for:
- validate_condition()
- normalize_condition()
- apply_filter()
- _extract_column_name()
"""

import pytest
import pandas as pd
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.filtering import (
    validate_condition,
    normalize_condition,
    apply_filter,
    _extract_column_name,
    MAX_CONDITION_LENGTH,
)
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
)


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'city': ['Paris', 'London', 'Paris', 'Berlin', 'London'],
        'salary': [50000, 60000, 70000, 55000, 65000],
        'active': [True, False, True, True, False],
    })


# =============================================================================
# validate_condition() Tests
# =============================================================================

class TestValidateCondition:
    """Tests for validate_condition function."""

    def test_valid_numeric_comparison(self):
        """Test validation of valid numeric comparison."""
        result = validate_condition("age > 30")
        assert is_ok(result)
        assert unwrap(result) == "age > 30"

    def test_valid_string_comparison(self):
        """Test validation of valid string comparison."""
        result = validate_condition("name == 'Alice'")
        assert is_ok(result)

    def test_valid_logical_and(self):
        """Test validation of valid AND condition."""
        result = validate_condition("age > 25 and city == 'Paris'")
        assert is_ok(result)

    def test_valid_logical_or(self):
        """Test validation of valid OR condition."""
        result = validate_condition("age > 35 or city == 'London'")
        assert is_ok(result)

    def test_valid_in_operator(self):
        """Test validation of valid in operator."""
        result = validate_condition("city in ['Paris', 'London']")
        assert is_ok(result)

    def test_valid_isna(self):
        """Test validation of valid isna check."""
        result = validate_condition("value.isna()")
        assert is_ok(result)

    def test_valid_notna(self):
        """Test validation of valid notna check."""
        result = validate_condition("value.notna()")
        assert is_ok(result)

    def test_dangerous_pattern_import(self):
        """Test rejection of dangerous import pattern."""
        result = validate_condition("age > __import__('os').system('rm -rf /')")

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, DangerousPatternError)
        assert error.pattern == "import"

    def test_dangerous_pattern_exec(self):
        """Test rejection of dangerous exec pattern."""
        result = validate_condition("name == 'test' or exec('print(1)')")

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, DangerousPatternError)

    def test_dangerous_pattern_eval(self):
        """Test rejection of dangerous eval pattern."""
        result = validate_condition("age > eval('1+1')")

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, DangerousPatternError)

    def test_dangerous_pattern_double_underscore(self):
        """Test rejection of dangerous __ pattern."""
        result = validate_condition("age > __class__")

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, DangerousPatternError)

    def test_condition_too_long(self):
        """Test rejection of condition exceeding max length."""
        long_condition = "age > " + "1" * (MAX_CONDITION_LENGTH + 1)
        result = validate_condition(long_condition)

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ConditionTooLongError)
        assert error.length > MAX_CONDITION_LENGTH
        assert error.max_length == MAX_CONDITION_LENGTH

    def test_unbalanced_parentheses_open(self):
        """Test rejection of unbalanced parentheses (more open)."""
        result = validate_condition("age > (30 and city == 'Paris'")

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, UnbalancedParenthesesError)
        assert error.open_count > error.close_count

    def test_unbalanced_parentheses_close(self):
        """Test rejection of unbalanced parentheses (more close)."""
        result = validate_condition("age > 30 and city == 'Paris')")

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, UnbalancedParenthesesError)
        assert error.close_count > error.open_count

    def test_unbalanced_brackets_open(self):
        """Test rejection of unbalanced brackets (more open)."""
        result = validate_condition("city in ['Paris', 'London'")

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, UnbalancedBracketsError)

    def test_unbalanced_brackets_close(self):
        """Test rejection of unbalanced brackets (more close)."""
        result = validate_condition("city in 'Paris', 'London']")

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, UnbalancedBracketsError)

    def test_unbalanced_single_quotes(self):
        """Test rejection of unbalanced single quotes."""
        result = validate_condition("name == 'Alice")

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, UnbalancedQuotesError)
        assert error.quote_type == "'"
        assert error.count % 2 != 0

    def test_unbalanced_double_quotes(self):
        """Test rejection of unbalanced double quotes."""
        result = validate_condition('name == "Alice')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, UnbalancedQuotesError)
        assert error.quote_type == '"'

    def test_balanced_quotes(self):
        """Test acceptance of balanced quotes."""
        result = validate_condition("name == 'Alice' and city == \"Paris\"")
        assert is_ok(result)


# =============================================================================
# normalize_condition() Tests
# =============================================================================

class TestNormalizeCondition:
    """Tests for normalize_condition function."""

    def test_normalize_is_none(self):
        """Test normalization of 'is None' to .isna()."""
        result = normalize_condition("age is None")
        assert result == "age.isna()"

    def test_normalize_is_not_none(self):
        """Test normalization of 'is not None' to .notna()."""
        result = normalize_condition("age is not None")
        assert result == "age.notna()"

    def test_normalize_between_lowercase(self):
        """Test normalization of 'between' (lowercase)."""
        result = normalize_condition("price between 10 and 100")
        assert result == "price >= 10 and price <= 100"

    def test_normalize_between_uppercase(self):
        """Test normalization of 'BETWEEN' (uppercase)."""
        result = normalize_condition("price BETWEEN 10 AND 100")
        assert result == "price >= 10 and price <= 100"

    def test_normalize_between_mixed_case(self):
        """Test normalization of 'Between' (mixed case)."""
        result = normalize_condition("price Between 10 And 100")
        assert result == "price >= 10 and price <= 100"

    def test_normalize_not_in_lowercase(self):
        """Test normalization of 'not in' (lowercase)."""
        result = normalize_condition("id not in [1, 2, 3]")
        assert result == "id not in [1, 2, 3]"

    def test_normalize_not_in_uppercase(self):
        """Test normalization of 'NOT IN' (uppercase)."""
        result = normalize_condition("id NOT IN [1, 2, 3]")
        assert result == "id not in [1, 2, 3]"

    def test_normalize_multiple_transformations(self):
        """Test normalization with multiple transformations."""
        result = normalize_condition("age is None or salary between 100 and 200")
        assert "age.isna()" in result
        assert "salary >= 100 and salary <= 200" in result


# =============================================================================
# _extract_column_name() Tests
# =============================================================================

class TestExtractColumnName:
    """Tests for _extract_column_name helper function."""

    def test_extract_column_from_error(self):
        """Test extraction of column name from pandas error."""
        error_msg = "name 'invalid_column' is not defined"
        result = _extract_column_name(error_msg)
        assert result == "invalid_column"

    def test_extract_no_match(self):
        """Test extraction when no column name found."""
        error_msg = "Some random error message"
        result = _extract_column_name(error_msg)
        assert result == "unknown"

    def test_extract_multiple_matches(self):
        """Test extraction returns first match."""
        error_msg = "name 'col1' is not defined and 'col2' too"
        result = _extract_column_name(error_msg)
        assert result == "col1"


# =============================================================================
# apply_filter() Tests
# =============================================================================

class TestApplyFilter:
    """Tests for apply_filter function."""

    def test_filter_numeric_greater_than(self, sample_dataframe):
        """Test filtering with numeric > comparison."""
        result = apply_filter(sample_dataframe, "age > 30")

        assert is_ok(result)
        df_filtered = unwrap(result)
        assert len(df_filtered) == 2  # Charlie (35) and Eve (32)
        assert all(df_filtered['age'] > 30)

    def test_filter_numeric_less_than(self, sample_dataframe):
        """Test filtering with numeric < comparison."""
        result = apply_filter(sample_dataframe, "age < 30")

        assert is_ok(result)
        df_filtered = unwrap(result)
        assert len(df_filtered) == 2  # Alice (25) and David (28)
        assert df_filtered.iloc[0]['name'] == 'Alice'

    def test_filter_string_equality(self, sample_dataframe):
        """Test filtering with string == comparison."""
        result = apply_filter(sample_dataframe, "city == 'Paris'")

        assert is_ok(result)
        df_filtered = unwrap(result)
        assert len(df_filtered) == 2
        assert all(df_filtered['city'] == 'Paris')

    def test_filter_with_and(self, sample_dataframe):
        """Test filtering with AND logic."""
        result = apply_filter(sample_dataframe, "age > 25 and city == 'Paris'")

        assert is_ok(result)
        df_filtered = unwrap(result)
        # Only Charlie (35, Paris) qualifies (Alice has age 25 which is not > 25)
        assert len(df_filtered) == 1
        assert df_filtered.iloc[0]['name'] == 'Charlie'
        assert all(df_filtered['age'] > 25)
        assert all(df_filtered['city'] == 'Paris')

    def test_filter_with_or(self, sample_dataframe):
        """Test filtering with OR logic."""
        result = apply_filter(sample_dataframe, "age > 35 or city == 'London'")

        assert is_ok(result)
        df_filtered = unwrap(result)
        assert len(df_filtered) == 2  # Bob (London) and Eve (London)

    def test_filter_with_columns(self, sample_dataframe):
        """Test filtering with column selection."""
        result = apply_filter(
            sample_dataframe,
            "age > 30",
            columns=["name", "age"]
        )

        assert is_ok(result)
        df_filtered = unwrap(result)
        assert list(df_filtered.columns) == ["name", "age"]
        assert len(df_filtered) == 2  # Charlie and Eve

    def test_filter_with_columns_all_missing(self, sample_dataframe):
        """Test filtering with all selected columns missing."""
        result = apply_filter(
            sample_dataframe,
            "age > 30",
            columns=["missing1", "missing2"]
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnsNotFoundError)
        assert "missing1" in error.missing
        assert "missing2" in error.missing

    def test_filter_with_columns_partial_missing(self, sample_dataframe):
        """Test filtering with some selected columns missing."""
        result = apply_filter(
            sample_dataframe,
            "age > 30",
            columns=["name", "missing", "age"]
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnsNotFoundError)
        assert error.missing == ["missing"]

    def test_filter_with_limit(self, sample_dataframe):
        """Test filtering with row limit."""
        result = apply_filter(
            sample_dataframe,
            "age > 25",
            limit=2
        )

        assert is_ok(result)
        df_filtered = unwrap(result)
        assert len(df_filtered) == 2

    def test_filter_invalid_column(self, sample_dataframe):
        """Test filtering with non-existent column."""
        result = apply_filter(sample_dataframe, "invalid_column > 30")

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnNotFoundError)
        assert error.column == "invalid_column"
        assert "age" in error.available

    def test_filter_empty_result(self, sample_dataframe):
        """Test filtering that returns no rows."""
        result = apply_filter(sample_dataframe, "age > 100")

        assert is_ok(result)
        df_filtered = unwrap(result)
        assert len(df_filtered) == 0

    def test_filter_all_rows_match(self, sample_dataframe):
        """Test filtering where all rows match."""
        result = apply_filter(sample_dataframe, "age > 0")

        assert is_ok(result)
        df_filtered = unwrap(result)
        assert len(df_filtered) == len(sample_dataframe)

    def test_filter_with_columns_and_limit(self, sample_dataframe):
        """Test filtering with both column selection and limit."""
        result = apply_filter(
            sample_dataframe,
            "age > 25",
            columns=["name", "city"],
            limit=3
        )

        assert is_ok(result)
        df_filtered = unwrap(result)
        assert len(df_filtered) == 3
        assert list(df_filtered.columns) == ["name", "city"]


# =============================================================================
# Integration Tests
# =============================================================================

class TestFilteringIntegration:
    """Integration tests for filtering operations."""

    def test_full_validation_and_filter_workflow(self, sample_dataframe):
        """Test complete workflow: validate, normalize, filter."""
        condition = "age > 30 and city == 'Paris'"

        # Step 1: Validate
        validation_result = validate_condition(condition)
        assert is_ok(validation_result)

        # Step 2: Normalize
        normalized = normalize_condition(condition)

        # Step 3: Filter
        filter_result = apply_filter(sample_dataframe, normalized)
        assert is_ok(filter_result)

        df_filtered = unwrap(filter_result)
        assert len(df_filtered) == 1
        assert df_filtered.iloc[0]['name'] == 'Charlie'

    def test_condition_with_none_filtering(self):
        """Test filtering with None values."""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, None, 35],
        })

        # Normalize 'age is None'
        normalized = normalize_condition("age is None")

        result = apply_filter(df, normalized)
        assert is_ok(result)

        df_filtered = unwrap(result)
        assert len(df_filtered) == 1
        assert pd.isna(df_filtered.iloc[0]['age'])

    def test_complex_filter_workflow(self, sample_dataframe):
        """Test complex filtering with column selection and limit."""
        condition = "(age > 30 or salary < 60000) and city != 'Berlin'"

        # Validate
        validation_result = validate_condition(condition)
        assert is_ok(validation_result)

        # Filter with column selection and limit
        result = apply_filter(
            sample_dataframe,
            condition,
            columns=["name", "age", "salary"],
            limit=2
        )

        assert is_ok(result)
        df_filtered = unwrap(result)
        assert len(df_filtered) <= 2
        assert list(df_filtered.columns) == ["name", "age", "salary"]
