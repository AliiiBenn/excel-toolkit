"""Comprehensive tests for validation operations.

Tests for:
- validate_column_exists()
- validate_column_type()
- validate_value_range()
- check_null_values()
- validate_unique()
- validate_dataframe()
"""

import pytest
import pandas as pd
import numpy as np
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.validation import (
    validate_column_exists,
    validate_column_type,
    validate_value_range,
    check_null_values,
    validate_unique,
    validate_dataframe,
)
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
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    return pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [25, 30, 35, 40, 45],
        'Salary': [50000.0, 60000.0, 70000.0, 80000.0, 90000.0],
        'Active': [True, False, True, False, True],
        'JoinDate': pd.to_datetime(['2020-01-01', '2020-02-01', '2020-03-01', '2020-04-01', '2020-05-01'])
    })


@pytest.fixture
def dataframe_with_nulls():
    """Create DataFrame with null values."""
    return pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Alice', None, 'Charlie', 'David', None],
        'Age': [25, 30, None, 40, 45],
        'Salary': [50000.0, None, 70000.0, 80000.0, 90000.0]
    })


@pytest.fixture
def dataframe_with_duplicates():
    """Create DataFrame with duplicate values."""
    return pd.DataFrame({
        'ID': [1, 2, 1, 3, 2],
        'Name': ['Alice', 'Bob', 'Alice', 'Charlie', 'Bob']
    })


# =============================================================================
# validate_column_exists() Tests
# =============================================================================

class TestValidateColumnExists:
    """Tests for validate_column_exists."""

    def test_single_column_exists(self, sample_dataframe):
        """Test single column that exists."""
        result = validate_column_exists(sample_dataframe, 'ID')

        assert is_ok(result)

    def test_single_column_missing(self, sample_dataframe):
        """Test single column that doesn't exist."""
        result = validate_column_exists(sample_dataframe, 'NonExistent')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnNotFoundError)

    def test_multiple_columns_all_exist(self, sample_dataframe):
        """Test multiple columns that all exist."""
        result = validate_column_exists(sample_dataframe, ['ID', 'Name', 'Age'])

        assert is_ok(result)

    def test_multiple_columns_some_missing(self, sample_dataframe):
        """Test multiple columns with some missing."""
        result = validate_column_exists(sample_dataframe, ['ID', 'NonExistent', 'Age'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnNotFoundError)

    def test_multiple_columns_all_missing(self, sample_dataframe):
        """Test multiple columns that all don't exist."""
        result = validate_column_exists(sample_dataframe, ['NonExistent1', 'NonExistent2'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnNotFoundError)

    def test_empty_column_list(self, sample_dataframe):
        """Test with empty column list."""
        result = validate_column_exists(sample_dataframe, [])

        assert is_ok(result)

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        result = validate_column_exists(df, 'AnyColumn')

        assert is_err(result)


# =============================================================================
# validate_column_type() Tests
# =============================================================================

class TestValidateColumnType:
    """Tests for validate_column_type."""

    def test_single_column_type_match_int(self, sample_dataframe):
        """Test single column type match (int)."""
        result = validate_column_type(sample_dataframe, {'Age': 'int'})

        assert is_ok(result)

    def test_single_column_type_match_float(self, sample_dataframe):
        """Test single column type match (float)."""
        result = validate_column_type(sample_dataframe, {'Salary': 'float'})

        assert is_ok(result)

    def test_single_column_type_match_str(self, sample_dataframe):
        """Test single column type match (str)."""
        result = validate_column_type(sample_dataframe, {'Name': 'str'})

        assert is_ok(result)

    def test_single_column_type_match_bool(self, sample_dataframe):
        """Test single column type match (bool)."""
        result = validate_column_type(sample_dataframe, {'Active': 'bool'})

        assert is_ok(result)

    def test_single_column_type_match_datetime(self, sample_dataframe):
        """Test single column type match (datetime)."""
        result = validate_column_type(sample_dataframe, {'JoinDate': 'datetime'})

        assert is_ok(result)

    def test_single_column_type_mismatch(self, sample_dataframe):
        """Test single column type mismatch."""
        result = validate_column_type(sample_dataframe, {'Age': 'str'})

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, TypeMismatchError)

    def test_multiple_columns_all_match(self, sample_dataframe):
        """Test multiple columns that all match."""
        result = validate_column_type(sample_dataframe, {
            'Age': 'int',
            'Name': 'str',
            'Salary': 'float'
        })

        assert is_ok(result)

    def test_multiple_columns_some_mismatch(self, sample_dataframe):
        """Test multiple columns with some mismatches."""
        result = validate_column_type(sample_dataframe, {
            'Age': 'int',
            'Name': 'int'  # Should be str
        })

        assert is_err(result)

    def test_multiple_valid_types_list(self, sample_dataframe):
        """Test with list of valid types."""
        result = validate_column_type(sample_dataframe, {
            'Age': ['int', 'float'],
            'Salary': ['int', 'float']
        })

        assert is_ok(result)

    def test_column_not_found(self, sample_dataframe):
        """Test error when column doesn't exist."""
        result = validate_column_type(sample_dataframe, {'NonExistent': 'int'})

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnNotFoundError)

    def test_numeric_type_check_int(self, sample_dataframe):
        """Test numeric type check with int column."""
        result = validate_column_type(sample_dataframe, {'Age': 'numeric'})

        assert is_ok(result)

    def test_numeric_type_check_float(self, sample_dataframe):
        """Test numeric type check with float column."""
        result = validate_column_type(sample_dataframe, {'Salary': 'numeric'})

        assert is_ok(result)

    def test_empty_column_types_dict(self, sample_dataframe):
        """Test with empty column_types dict."""
        result = validate_column_type(sample_dataframe, {})

        assert is_ok(result)


# =============================================================================
# validate_value_range() Tests
# =============================================================================

class TestValidateValueRange:
    """Tests for validate_value_range."""

    def test_all_values_in_range(self, sample_dataframe):
        """Test all values within range."""
        result = validate_value_range(sample_dataframe, 'Age', min_value=20, max_value=50)

        assert is_ok(result)

    def test_some_values_below_minimum(self, sample_dataframe):
        """Test some values below minimum."""
        result = validate_value_range(sample_dataframe, 'Age', min_value=30, max_value=50)

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ValueOutOfRangeError)

    def test_some_values_above_maximum(self, sample_dataframe):
        """Test some values above maximum."""
        result = validate_value_range(sample_dataframe, 'Age', min_value=20, max_value=30)

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ValueOutOfRangeError)

    def test_values_on_boundary_allow_equal_true(self, sample_dataframe):
        """Test values on boundary with allow_equal=True."""
        result = validate_value_range(sample_dataframe, 'Age', min_value=25, max_value=45, allow_equal=True)

        assert is_ok(result)

    def test_values_on_boundary_allow_equal_false(self, sample_dataframe):
        """Test values on boundary with allow_equal=False."""
        result = validate_value_range(sample_dataframe, 'Age', min_value=25, max_value=45, allow_equal=False)

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ValueOutOfRangeError)

    def test_no_minimum_specified(self, sample_dataframe):
        """Test with no minimum specified."""
        result = validate_value_range(sample_dataframe, 'Age', max_value=50)

        assert is_ok(result)

    def test_no_maximum_specified(self, sample_dataframe):
        """Test with no maximum specified."""
        result = validate_value_range(sample_dataframe, 'Age', min_value=20)

        assert is_ok(result)

    def test_no_bounds_specified(self, sample_dataframe):
        """Test with no bounds specified."""
        result = validate_value_range(sample_dataframe, 'Age')

        assert is_ok(result)

    def test_column_not_found(self, sample_dataframe):
        """Test error when column doesn't exist."""
        result = validate_value_range(sample_dataframe, 'NonExistent', min_value=0, max_value=100)

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnNotFoundError)


# =============================================================================
# check_null_values() Tests
# =============================================================================

class TestCheckNullValues:
    """Tests for check_null_values."""

    def test_no_null_values(self, sample_dataframe):
        """Test DataFrame with no null values."""
        result = check_null_values(sample_dataframe)

        assert is_ok(result)
        report = unwrap(result)
        assert report.passed > 0
        assert report.failed == 0

    def test_null_values_no_threshold(self, dataframe_with_nulls):
        """Test null values without threshold."""
        result = check_null_values(dataframe_with_nulls)

        assert is_ok(result)
        report = unwrap(result)
        assert report.warnings is not None
        assert len(report.warnings) > 0

    def test_null_values_within_threshold(self, dataframe_with_nulls):
        """Test null values within acceptable threshold."""
        result = check_null_values(dataframe_with_nulls, threshold=0.5)

        assert is_ok(result)
        report = unwrap(result)
        assert report.failed == 0

    def test_null_values_exceed_threshold(self, dataframe_with_nulls):
        """Test null values exceed threshold."""
        result = check_null_values(dataframe_with_nulls, columns=['Name'], threshold=0.1)

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, NullValueThresholdExceededError)

    def test_check_specific_columns(self, dataframe_with_nulls):
        """Test checking specific columns."""
        result = check_null_values(dataframe_with_nulls, columns=['ID', 'Age'])

        assert is_ok(result)
        report = unwrap(result)
        # ID has no nulls, Age has 1 null
        assert report.passed >= 1

    def test_all_null_values(self):
        """Test DataFrame with all null values."""
        df = pd.DataFrame({'Column': [None, None, None]})
        result = check_null_values(df, threshold=0.5)

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, NullValueThresholdExceededError)

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        result = check_null_values(df)

        assert is_ok(result)


# =============================================================================
# validate_unique() Tests
# =============================================================================

class TestValidateUnique:
    """Tests for validate_unique."""

    def test_unique_single_column(self, sample_dataframe):
        """Test unique values in single column."""
        result = validate_unique(sample_dataframe, 'ID')

        assert is_ok(result)

    def test_duplicate_single_column(self, dataframe_with_duplicates):
        """Test duplicate values in single column."""
        result = validate_unique(dataframe_with_duplicates, 'ID')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, UniquenessViolationError)
        assert error.duplicate_count > 0

    def test_unique_multiple_columns(self, dataframe_with_duplicates):
        """Test that duplicate combinations are detected."""
        result = validate_unique(dataframe_with_duplicates, ['ID', 'Name'])

        # The fixture has duplicate (ID, Name) combinations:
        # (1, Alice) appears twice, (2, Bob) appears twice
        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, UniquenessViolationError)

    def test_duplicate_multiple_columns(self, dataframe_with_duplicates):
        """Test duplicate combination across multiple columns."""
        df = pd.DataFrame({
            'ID': [1, 1, 2],
            'Name': ['Alice', 'Alice', 'Bob']
        })
        result = validate_unique(df, ['ID', 'Name'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, UniquenessViolationError)

    def test_ignore_null_true(self):
        """Test with ignore_null=True."""
        df = pd.DataFrame({'ID': [1, 2, None, 2]})
        result = validate_unique(df, 'ID', ignore_null=True)

        assert is_err(result)
        error = unwrap_err(result)
        # After dropping null: [1, 2, 2]
        # duplicated(keep='first') marks only the second 2 as duplicate
        assert error.duplicate_count == 1

    def test_ignore_null_false(self):
        """Test with ignore_null=False."""
        df = pd.DataFrame({'ID': [1, 2, None, None]})
        result = validate_unique(df, 'ID', ignore_null=False)

        assert is_err(result)
        error = unwrap_err(result)
        # duplicated(keep='first') marks only the second None as duplicate
        assert error.duplicate_count == 1

    def test_column_not_found(self, sample_dataframe):
        """Test error when column doesn't exist."""
        result = validate_unique(sample_dataframe, 'NonExistent')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnNotFoundError)


# =============================================================================
# validate_dataframe() Tests
# =============================================================================

class TestValidateDataframe:
    """Tests for validate_dataframe."""

    def test_multiple_rules_all_pass(self, sample_dataframe):
        """Test multiple validation rules that all pass."""
        rules = [
            {"type": "column_exists", "columns": ["ID", "Name"]},
            {"type": "value_range", "column": "Age", "min": 20, "max": 50},
            {"type": "unique", "columns": ["ID"]}
        ]
        result = validate_dataframe(sample_dataframe, rules)

        assert is_ok(result)
        report = unwrap(result)
        assert report.failed == 0

    def test_multiple_rules_some_fail(self, sample_dataframe):
        """Test multiple validation rules with some failures."""
        rules = [
            {"type": "column_exists", "columns": ["ID", "NonExistent"]},
            {"type": "value_range", "column": "Age", "min": 20, "max": 50}
        ]
        result = validate_dataframe(sample_dataframe, rules)

        assert is_ok(result)
        report = unwrap(result)
        assert report.failed > 0
        assert report.errors is not None

    def test_rule_column_exists(self, sample_dataframe):
        """Test column_exists rule."""
        rules = [{"type": "column_exists", "columns": ["ID", "Name"]}]
        result = validate_dataframe(sample_dataframe, rules)

        assert is_ok(result)
        report = unwrap(result)
        assert report.passed >= 1

    def test_rule_column_type(self, sample_dataframe):
        """Test column_type rule."""
        rules = [{"type": "column_type", "column_types": {"Age": "int"}}]
        result = validate_dataframe(sample_dataframe, rules)

        assert is_ok(result)
        report = unwrap(result)
        assert report.passed >= 1

    def test_rule_value_range(self, sample_dataframe):
        """Test value_range rule."""
        rules = [{"type": "value_range", "column": "Age", "min": 20, "max": 50}]
        result = validate_dataframe(sample_dataframe, rules)

        assert is_ok(result)
        report = unwrap(result)
        assert report.passed >= 1

    def test_rule_unique(self, sample_dataframe):
        """Test unique rule."""
        rules = [{"type": "unique", "columns": ["ID"]}]
        result = validate_dataframe(sample_dataframe, rules)

        assert is_ok(result)
        report = unwrap(result)
        assert report.passed >= 1

    def test_rule_null_threshold(self, dataframe_with_nulls):
        """Test null_threshold rule."""
        rules = [{"type": "null_threshold", "columns": ["Name"], "threshold": 0.5}]
        result = validate_dataframe(dataframe_with_nulls, rules)

        assert is_ok(result)
        report = unwrap(result)
        assert report.failed == 0

    def test_invalid_rule_type(self, sample_dataframe):
        """Test error with invalid rule type."""
        rules = [{"type": "invalid_type"}]
        result = validate_dataframe(sample_dataframe, rules)

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InvalidRuleError)

    def test_empty_rules_list(self, sample_dataframe):
        """Test with empty rules list."""
        result = validate_dataframe(sample_dataframe, [])

        assert is_ok(result)
        report = unwrap(result)
        assert report.passed == 0
        assert report.failed == 0

    def test_mixed_pass_fail_rules(self, sample_dataframe):
        """Test mix of passing and failing rules."""
        rules = [
            {"type": "column_exists", "columns": ["ID"]},  # Pass
            {"type": "column_exists", "columns": ["NonExistent"]},  # Fail
            {"type": "value_range", "column": "Age", "min": 0, "max": 100}  # Pass
        ]
        result = validate_dataframe(sample_dataframe, rules)

        assert is_ok(result)
        report = unwrap(result)
        assert report.passed >= 1
        assert report.failed >= 1
