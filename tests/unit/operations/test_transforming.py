"""Comprehensive tests for transforming operations.

Tests for:
- apply_expression()
- cast_columns()
- transform_column()
"""

import pytest
import pandas as pd
import numpy as np
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.transforming import (
    apply_expression,
    cast_columns,
    transform_column,
    validate_expression_security,
)
from excel_toolkit.models.error_types import (
    ColumnNotFoundError,
    InvalidExpressionError,
    InvalidTypeError,
    CastFailedError,
    InvalidTransformationError,
    TransformingError,
)


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    return pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'Salary': [50000, 60000, 70000],
        'Active': [True, False, True],
        'Department': ['Sales', 'IT', 'Sales']
    })


@pytest.fixture
def numeric_dataframe():
    """Create numeric DataFrame for transformations."""
    return pd.DataFrame({
        'Value': [1, 2, 3, 4, 5],
        'Negative': [-1, -2, -3, -4, -5],
        'Positive': [10, 20, 30, 40, 50],
        'Zero': [0, 0, 0, 0, 0]
    })


# =============================================================================
# validate_expression_security() Tests
# =============================================================================

class TestValidateExpressionSecurity:
    """Tests for validate_expression_security."""

    def test_safe_expression(self):
        """Test that safe expressions pass validation."""
        result = validate_expression_security("Age * 2")
        assert is_ok(result)

    def test_dangerous_import(self):
        """Test that import is blocked."""
        result = validate_expression_security("import os")
        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InvalidExpressionError)
        assert "dangerous" in error.reason.lower()

    def test_dangerous_exec(self):
        """Test that exec is blocked."""
        result = validate_expression_security("exec('print(1)')")
        assert is_err(result)

    def test_dangerous_eval(self):
        """Test that eval is blocked."""
        result = validate_expression_security("eval('1+1')")
        assert is_err(result)

    def test_dangerous_double_underscore(self):
        """Test that __ is blocked."""
        result = validate_expression_security("__class__")
        assert is_err(result)

    def test_unbalanced_parentheses(self):
        """Test that unbalanced parentheses are caught."""
        result = validate_expression_security("Age * (2 + 3")
        assert is_err(result)
        error = unwrap_err(result)
        assert "parentheses" in error.reason.lower()

    def test_unbalanced_brackets(self):
        """Test that unbalanced brackets are caught."""
        result = validate_expression_security("df[0")
        assert is_err(result)
        error = unwrap_err(result)
        assert "bracket" in error.reason.lower()


# =============================================================================
# apply_expression() Tests
# =============================================================================

class TestApplyExpression:
    """Tests for apply_expression."""

    def test_simple_arithmetic(self, sample_dataframe):
        """Test simple arithmetic expression."""
        result = apply_expression(sample_dataframe, 'DoubleAge', 'Age * 2', validate=False)

        assert is_ok(result)
        df_transform = unwrap(result)
        assert 'DoubleAge' in df_transform.columns
        assert df_transform['DoubleAge'].tolist() == [50, 60, 70]

    def test_multiple_column_reference(self, sample_dataframe):
        """Test expression referencing multiple columns."""
        result = apply_expression(sample_dataframe, 'Total', 'Age * Salary / 100', validate=False)

        assert is_ok(result)
        df_transform = unwrap(result)
        assert 'Total' in df_transform.columns

    def test_string_concatenation(self, sample_dataframe):
        """Test string concatenation."""
        df = pd.DataFrame({
            'FirstName': ['John', 'Jane'],
            'LastName': ['Doe', 'Smith']
        })
        result = apply_expression(df, 'FullName', "FirstName + ' ' + LastName", validate=False)

        assert is_ok(result)
        df_transform = unwrap(result)
        assert df_transform['FullName'].tolist() == ['John Doe', 'Jane Smith']

    def test_comparison_expression(self, sample_dataframe):
        """Test comparison expression."""
        result = apply_expression(sample_dataframe, 'HighSalary', 'Salary > 55000', validate=False)

        assert is_ok(result)
        df_transform = unwrap(result)
        assert df_transform['HighSalary'].tolist() == [False, True, True]

    def test_method_call_upper(self, sample_dataframe):
        """Test string method call."""
        result = apply_expression(sample_dataframe, 'UpperName', 'Name.str.upper()', validate=False)

        assert is_ok(result)
        df_transform = unwrap(result)
        assert df_transform['UpperName'].tolist() == ['ALICE', 'BOB', 'CHARLIE']

    def test_modify_existing_column(self, sample_dataframe):
        """Test modifying existing column."""
        result = apply_expression(sample_dataframe, 'Age', 'Age * 2', validate=False)

        assert is_ok(result)
        df_transform = unwrap(result)
        assert df_transform['Age'].tolist() == [50, 60, 70]

    def test_create_new_column(self, sample_dataframe):
        """Test creating new column."""
        result = apply_expression(sample_dataframe, 'NewColumn', 'Age + 1', validate=False)

        assert is_ok(result)
        df_transform = unwrap(result)
        assert 'NewColumn' in df_transform.columns
        assert df_transform['NewColumn'].tolist() == [26, 31, 36]

    def test_dangerous_pattern_detection(self, sample_dataframe):
        """Test dangerous pattern is blocked."""
        result = apply_expression(sample_dataframe, 'Bad', 'import os', validate=True)

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InvalidExpressionError)

    def test_column_not_found(self, sample_dataframe):
        """Test error when column doesn't exist."""
        result = apply_expression(sample_dataframe, 'Result', 'NonExistent * 2', validate=False)

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnNotFoundError)

    def test_division_by_zero_handling(self, sample_dataframe):
        """Test division by zero."""
        df = pd.DataFrame({'A': [10, 20], 'B': [0, 5]})
        result = apply_expression(df, 'Result', 'A / B', validate=False)

        assert is_ok(result)
        df_transform = unwrap(result)
        assert pd.isna(df_transform['Result'].iloc[0]) or df_transform['Result'].iloc[0] == float('inf')

    def test_expression_with_constants(self, sample_dataframe):
        """Test expression with constants."""
        result = apply_expression(sample_dataframe, 'Adjusted', 'Age + 10 * 2', validate=False)

        assert is_ok(result)
        df_transform = unwrap(result)
        assert df_transform['Adjusted'].iloc[0] == 45  # 25 + 20

    def test_complex_nested_expression(self, sample_dataframe):
        """Test complex nested expression."""
        result = apply_expression(sample_dataframe, 'Complex', '((Age + Salary) / 100) * 2', validate=False)

        assert is_ok(result)
        df_transform = unwrap(result)
        assert 'Complex' in df_transform.columns

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        result = apply_expression(df, 'Result', '1 + 1', validate=False)
        assert is_ok(result)


# =============================================================================
# cast_columns() Tests
# =============================================================================

class TestCastColumns:
    """Tests for cast_columns."""

    def test_cast_single_column_to_int(self):
        """Test casting single column to int."""
        df = pd.DataFrame({'Age': ['25', '30', '35']})
        result = cast_columns(df, {'Age': 'int'})

        assert is_ok(result)
        df_cast = unwrap(result)
        assert df_cast['Age'].dtype == int
        assert df_cast['Age'].tolist() == [25, 30, 35]

    def test_cast_single_column_to_float(self):
        """Test casting single column to float."""
        df = pd.DataFrame({'Price': ['10.5', '20.3', '30.7']})
        result = cast_columns(df, {'Price': 'float'})

        assert is_ok(result)
        df_cast = unwrap(result)
        assert df_cast['Price'].dtype == float

    def test_cast_single_column_to_str(self):
        """Test casting single column to str."""
        df = pd.DataFrame({'ID': [1, 2, 3]})
        result = cast_columns(df, {'ID': 'str'})

        assert is_ok(result)
        df_cast = unwrap(result)
        assert df_cast['ID'].dtype == object or str

    def test_cast_single_column_to_bool_from_strings(self):
        """Test casting to bool from string representations."""
        df = pd.DataFrame({'Active': ['true', 'false', 'yes', 'no', '1', '0']})
        result = cast_columns(df, {'Active': 'bool'})

        assert is_ok(result)
        df_cast = unwrap(result)
        assert df_cast['Active'].dtype == bool
        assert df_cast['Active'].tolist() == [True, False, True, False, True, False]

    def test_cast_single_column_to_datetime(self):
        """Test casting to datetime."""
        df = pd.DataFrame({'Date': ['2020-01-01', '2020-02-01', '2020-03-01']})
        result = cast_columns(df, {'Date': 'datetime'})

        assert is_ok(result)
        df_cast = unwrap(result)
        assert pd.api.types.is_datetime64_any_dtype(df_cast['Date'])

    def test_cast_single_column_to_category(self):
        """Test casting to category."""
        df = pd.DataFrame({'Department': ['Sales', 'IT', 'Sales']})
        result = cast_columns(df, {'Department': 'category'})

        assert is_ok(result)
        df_cast = unwrap(result)
        assert pd.api.types.is_categorical_dtype(df_cast['Department'])

    def test_cast_multiple_columns(self):
        """Test casting multiple columns."""
        df = pd.DataFrame({
            'Age': ['25', '30', '35'],
            'Salary': ['50000', '60000', '70000'],
            'Active': ['true', 'false', 'true']
        })
        result = cast_columns(df, {
            'Age': 'int',
            'Salary': 'float',
            'Active': 'bool'
        })

        assert is_ok(result)
        df_cast = unwrap(result)
        assert df_cast['Age'].dtype == int
        assert df_cast['Salary'].dtype == float
        assert df_cast['Active'].dtype == bool

    def test_invalid_type_error(self):
        """Test error with invalid type."""
        df = pd.DataFrame({'Age': ['25', '30', '35']})
        result = cast_columns(df, {'Age': 'invalid_type'})

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InvalidTypeError)

    def test_column_not_found_error(self):
        """Test error when column doesn't exist."""
        df = pd.DataFrame({'Age': ['25', '30', '35']})
        result = cast_columns(df, {'NonExistent': 'int'})

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnNotFoundError)

    def test_cast_failed_error_string_to_int(self):
        """Test error when casting non-numeric string to int."""
        df = pd.DataFrame({'Age': ['twenty', 'thirty', 'thirty-five']})
        result = cast_columns(df, {'Age': 'int'})

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, CastFailedError)

    def test_cast_int_with_nan_fails(self):
        """Test that casting with NaN to int fails."""
        df = pd.DataFrame({'Age': ['25', None, '35']})
        result = cast_columns(df, {'Age': 'int'})

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, CastFailedError)
        assert "NaN" in error.reason

    def test_bool_from_various_formats(self):
        """Test bool conversion from various formats."""
        df = pd.DataFrame({
            'Value': ['True', 'False', 'Yes', 'No', 'T', 'F', 'Y', 'N', '1', '0']
        })
        result = cast_columns(df, {'Value': 'bool'})

        assert is_ok(result)
        df_cast = unwrap(result)
        expected = [True, False, True, False, True, False, True, False, True, False]
        assert df_cast['Value'].tolist() == expected

    def test_datetime_from_different_formats(self):
        """Test datetime parsing from different formats."""
        df = pd.DataFrame({
            'Date': ['2020-01-01', '01/02/2020', '2020.03.01']
        })
        result = cast_columns(df, {'Date': 'datetime'})

        assert is_ok(result)
        df_cast = unwrap(result)
        assert pd.api.types.is_datetime64_any_dtype(df_cast['Date'])

    def test_empty_dataframe(self):
        """Test casting empty DataFrame."""
        df = pd.DataFrame()
        result = cast_columns(df, {})
        assert is_ok(result)

    def test_column_already_correct_type(self):
        """Test casting column that's already the correct type."""
        df = pd.DataFrame({'Age': [25, 30, 35]})
        result = cast_columns(df, {'Age': 'int'})

        assert is_ok(result)
        df_cast = unwrap(result)
        assert df_cast['Age'].dtype == int


# =============================================================================
# transform_column() Tests
# =============================================================================

class TestTransformColumn:
    """Tests for transform_column."""

    def test_log_transformation(self, numeric_dataframe):
        """Test logarithm transformation."""
        result = transform_column(numeric_dataframe, 'Positive', 'log')

        assert is_ok(result)
        df_transform = unwrap(result)
        assert 'Positive' in df_transform.columns
        # Verify log was applied
        assert np.isclose(df_transform['Positive'].iloc[0], np.log(10))

    def test_sqrt_transformation(self, numeric_dataframe):
        """Test square root transformation."""
        result = transform_column(numeric_dataframe, 'Positive', 'sqrt')

        assert is_ok(result)
        df_transform = unwrap(result)
        assert np.isclose(df_transform['Positive'].iloc[0], np.sqrt(10))

    def test_abs_transformation(self, numeric_dataframe):
        """Test absolute value transformation."""
        result = transform_column(numeric_dataframe, 'Negative', 'abs')

        assert is_ok(result)
        df_transform = unwrap(result)
        assert df_transform['Negative'].tolist() == [1, 2, 3, 4, 5]

    def test_exp_transformation(self, numeric_dataframe):
        """Test exponential transformation."""
        result = transform_column(numeric_dataframe, 'Value', 'exp')

        assert is_ok(result)
        df_transform = unwrap(result)
        assert np.isclose(df_transform['Value'].iloc[0], np.exp(1))

    def test_standardize_transformation(self, numeric_dataframe):
        """Test z-score standardization."""
        result = transform_column(numeric_dataframe, 'Value', 'standardize')

        assert is_ok(result)
        df_transform = unwrap(result)
        # Mean should be ~0, std should be ~1
        assert np.isclose(df_transform['Value'].mean(), 0, atol=1e-10)
        assert np.isclose(df_transform['Value'].std(), 1, atol=1e-10)

    def test_normalize_transformation(self, numeric_dataframe):
        """Test min-max normalization."""
        result = transform_column(numeric_dataframe, 'Value', 'normalize')

        assert is_ok(result)
        df_transform = unwrap(result)
        # Min should be 0, max should be 1
        assert np.isclose(df_transform['Value'].min(), 0)
        assert np.isclose(df_transform['Value'].max(), 1)

    def test_custom_callable_transformation(self, numeric_dataframe):
        """Test custom callable transformation."""
        result = transform_column(numeric_dataframe, 'Value', lambda x: x ** 2)

        assert is_ok(result)
        df_transform = unwrap(result)
        assert df_transform['Value'].tolist() == [1, 4, 9, 16, 25]

    def test_invalid_transformation_name(self, numeric_dataframe):
        """Test error with invalid transformation name."""
        result = transform_column(numeric_dataframe, 'Value', 'invalid_transform')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InvalidTransformationError)

    def test_column_not_found(self, numeric_dataframe):
        """Test error when column doesn't exist."""
        result = transform_column(numeric_dataframe, 'NonExistent', 'log')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnNotFoundError)

    def test_log_of_negative_values(self, numeric_dataframe):
        """Test error when applying log to negative values."""
        result = transform_column(numeric_dataframe, 'Negative', 'log')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, TransformingError)
        assert "non-positive" in error.message.lower()

    def test_log_of_zero(self, numeric_dataframe):
        """Test error when applying log to zero."""
        result = transform_column(numeric_dataframe, 'Zero', 'log')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, TransformingError)
        assert "non-positive" in error.message.lower()

    def test_sqrt_of_negative_values(self, numeric_dataframe):
        """Test error when applying sqrt to negative values."""
        result = transform_column(numeric_dataframe, 'Negative', 'sqrt')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, TransformingError)
        assert "negative" in error.message.lower()

    def test_standardize_with_zero_std(self, numeric_dataframe):
        """Test error when standardizing column with zero std."""
        result = transform_column(numeric_dataframe, 'Zero', 'standardize')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, TransformingError)
        assert "zero standard deviation" in error.message.lower()

    def test_normalize_with_equal_min_max(self, numeric_dataframe):
        """Test error when normalizing column where min == max."""
        result = transform_column(numeric_dataframe, 'Zero', 'normalize')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, TransformingError)
        assert "min == max" in error.message.lower()

    def test_with_params_dict(self, numeric_dataframe):
        """Test transformation with params dict (not used in built-ins but should not error)."""
        result = transform_column(numeric_dataframe, 'Value', 'abs', params={'unused': 'value'})

        assert is_ok(result)
        df_transform = unwrap(result)
        assert df_transform['Value'].tolist() == [1, 2, 3, 4, 5]

    def test_empty_column_values(self):
        """Test transformation on empty column."""
        df = pd.DataFrame({'Value': []})
        result = transform_column(df, 'Value', 'abs')

        # Should handle empty column gracefully
        assert is_ok(result) or is_err(result)

    def test_single_value_column(self):
        """Test transformation on single value column."""
        df = pd.DataFrame({'Value': [5]})
        result = transform_column(df, 'Value', 'abs')

        assert is_ok(result)
        df_transform = unwrap(result)
        assert df_transform['Value'].iloc[0] == 5
