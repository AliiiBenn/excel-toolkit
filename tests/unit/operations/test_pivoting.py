"""Comprehensive tests for pivoting operations.

Tests for:
- validate_aggregation_function()
- validate_pivot_columns()
- parse_fill_value()
- flatten_multiindex()
- create_pivot_table()
"""

import pytest
import pandas as pd
import numpy as np
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.pivoting import (
    validate_aggregation_function,
    validate_pivot_columns,
    parse_fill_value,
    flatten_multiindex,
    create_pivot_table,
    VALID_AGGREGATION_FUNCTIONS,
)
from excel_toolkit.models.error_types import (
    InvalidFunctionError,
    NoRowsError,
    NoColumnsError,
    NoValuesError,
    RowColumnsNotFoundError,
    ColumnColumnsNotFoundError,
    ValueColumnsNotFoundError,
    PivotFailedError,
)


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sales_dataframe():
    """Create a sales DataFrame for testing."""
    return pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02', '2024-01-03'],
        'Product': ['A', 'B', 'A', 'B', 'A'],
        'Region': ['North', 'North', 'South', 'South', 'North'],
        'Sales': [100, 150, 200, 250, 120],
        'Quantity': [10, 15, 20, 25, 12],
        'Profit': [20, 30, 40, 50, 24],
    })


@pytest.fixture
def simple_dataframe():
    """Create a simple DataFrame for testing."""
    return pd.DataFrame({
        'Category': ['A', 'B', 'A', 'B', 'C'],
        'Type': ['X', 'X', 'Y', 'Y', 'X'],
        'Value': [10, 20, 30, 40, 50],
    })


@pytest.fixture
def multiindex_result():
    """Create a DataFrame with MultiIndex columns."""
    arrays = [
        ['Sales', 'Sales', 'Profit', 'Profit'],
        ['sum', 'mean', 'sum', 'mean']
    ]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples)
    df = pd.DataFrame([[100, 50, 20, 10], [200, 100, 40, 20]], columns=index)
    df.index = ['A', 'B']
    return df


# =============================================================================
# validate_aggregation_function() Tests
# =============================================================================

class TestValidateAggregationFunction:
    """Tests for validate_aggregation_function."""

    def test_valid_sum(self):
        """Test valid sum function."""
        result = validate_aggregation_function("sum")
        assert is_ok(result)
        assert unwrap(result) == "sum"

    def test_valid_mean(self):
        """Test valid mean function."""
        result = validate_aggregation_function("mean")
        assert is_ok(result)
        assert unwrap(result) == "mean"

    def test_valid_avg_normalizes_to_mean(self):
        """Test avg is normalized to mean."""
        result = validate_aggregation_function("avg")
        assert is_ok(result)
        assert unwrap(result) == "mean"

    def test_valid_avg_uppercase(self):
        """Test AVG (uppercase) is normalized to mean."""
        result = validate_aggregation_function("AVG")
        assert is_ok(result)
        assert unwrap(result) == "mean"

    def test_valid_count(self):
        """Test valid count function."""
        result = validate_aggregation_function("count")
        assert is_ok(result)
        assert unwrap(result) == "count"

    def test_valid_min(self):
        """Test valid min function."""
        result = validate_aggregation_function("min")
        assert is_ok(result)
        assert unwrap(result) == "min"

    def test_valid_max(self):
        """Test valid max function."""
        result = validate_aggregation_function("max")
        assert is_ok(result)
        assert unwrap(result) == "max"

    def test_valid_median(self):
        """Test valid median function."""
        result = validate_aggregation_function("median")
        assert is_ok(result)
        assert unwrap(result) == "median"

    def test_valid_std(self):
        """Test valid std function."""
        result = validate_aggregation_function("std")
        assert is_ok(result)
        assert unwrap(result) == "std"

    def test_valid_var(self):
        """Test valid var function."""
        result = validate_aggregation_function("var")
        assert is_ok(result)
        assert unwrap(result) == "var"

    def test_valid_first(self):
        """Test valid first function."""
        result = validate_aggregation_function("first")
        assert is_ok(result)
        assert unwrap(result) == "first"

    def test_valid_last(self):
        """Test valid last function."""
        result = validate_aggregation_function("last")
        assert is_ok(result)
        assert unwrap(result) == "last"

    def test_invalid_function(self):
        """Test invalid function name."""
        result = validate_aggregation_function("invalid_func")

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InvalidFunctionError)
        assert error.function == "invalid_func"
        assert error.valid_functions == VALID_AGGREGATION_FUNCTIONS


# =============================================================================
# validate_pivot_columns() Tests
# =============================================================================

class TestValidatePivotColumns:
    """Tests for validate_pivot_columns."""

    def test_valid_columns(self, simple_dataframe):
        """Test validation with valid columns."""
        result = validate_pivot_columns(
            simple_dataframe,
            rows=['Category'],
            columns=['Type'],
            values=['Value']
        )
        assert is_ok(result)

    def test_valid_multiple_columns(self, sales_dataframe):
        """Test validation with multiple columns."""
        result = validate_pivot_columns(
            sales_dataframe,
            rows=['Date', 'Region'],
            columns=['Product'],
            values=['Sales', 'Quantity']
        )
        assert is_ok(result)

    def test_no_rows_error(self, simple_dataframe):
        """Test error when no row columns specified."""
        result = validate_pivot_columns(
            simple_dataframe,
            rows=[],
            columns=['Type'],
            values=['Value']
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, NoRowsError)

    def test_no_columns_error(self, simple_dataframe):
        """Test error when no column columns specified."""
        result = validate_pivot_columns(
            simple_dataframe,
            rows=['Category'],
            columns=[],
            values=['Value']
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, NoColumnsError)

    def test_no_values_error(self, simple_dataframe):
        """Test error when no value columns specified."""
        result = validate_pivot_columns(
            simple_dataframe,
            rows=['Category'],
            columns=['Type'],
            values=[]
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, NoValuesError)

    def test_invalid_row_columns(self, simple_dataframe):
        """Test error when row columns don't exist."""
        result = validate_pivot_columns(
            simple_dataframe,
            rows=['InvalidRow'],
            columns=['Type'],
            values=['Value']
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, RowColumnsNotFoundError)
        assert error.missing == ['InvalidRow']

    def test_invalid_column_columns(self, simple_dataframe):
        """Test error when column columns don't exist."""
        result = validate_pivot_columns(
            simple_dataframe,
            rows=['Category'],
            columns=['InvalidCol'],
            values=['Value']
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ColumnColumnsNotFoundError)
        assert error.missing == ['InvalidCol']

    def test_invalid_value_columns(self, simple_dataframe):
        """Test error when value columns don't exist."""
        result = validate_pivot_columns(
            simple_dataframe,
            rows=['Category'],
            columns=['Type'],
            values=['InvalidVal']
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ValueColumnsNotFoundError)
        assert error.missing == ['InvalidVal']

    def test_multiple_invalid_row_columns(self, simple_dataframe):
        """Test error with multiple invalid row columns."""
        result = validate_pivot_columns(
            simple_dataframe,
            rows=['Invalid1', 'Invalid2'],
            columns=['Type'],
            values=['Value']
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, RowColumnsNotFoundError)
        assert set(error.missing) == {'Invalid1', 'Invalid2'}


# =============================================================================
# parse_fill_value() Tests
# =============================================================================

class TestParseFillValue:
    """Tests for parse_fill_value."""

    def test_none_value(self):
        """Test parsing None."""
        result = parse_fill_value(None)
        assert result is None

    def test_string_none(self):
        """Test parsing 'none' string."""
        result = parse_fill_value("none")
        assert result is None

    def test_string_none_uppercase(self):
        """Test parsing 'NONE' string."""
        result = parse_fill_value("NONE")
        assert result is None

    def test_string_zero(self):
        """Test parsing '0' string."""
        result = parse_fill_value("0")
        assert result == 0

    def test_string_nan(self):
        """Test parsing 'nan' string."""
        result = parse_fill_value("nan")
        assert pd.isna(result)

    def test_string_nan_uppercase(self):
        """Test parsing 'NAN' string."""
        result = parse_fill_value("NAN")
        assert pd.isna(result)

    def test_integer_string(self):
        """Test parsing integer string."""
        result = parse_fill_value("123")
        assert result == 123
        assert isinstance(result, int)

    def test_negative_integer_string(self):
        """Test parsing negative integer string."""
        result = parse_fill_value("-456")
        assert result == -456
        assert isinstance(result, int)

    def test_float_string(self):
        """Test parsing float string."""
        result = parse_fill_value("123.45")
        assert result == 123.45
        assert isinstance(result, float)

    def test_negative_float_string(self):
        """Test parsing negative float string."""
        result = parse_fill_value("-789.12")
        assert result == -789.12
        assert isinstance(result, float)

    def test_non_numeric_string(self):
        """Test parsing non-numeric string."""
        result = parse_fill_value("text")
        assert result == "text"
        assert isinstance(result, str)

    def test_zero_float_string(self):
        """Test parsing '0.0' string."""
        result = parse_fill_value("0.0")
        assert result == 0.0


# =============================================================================
# flatten_multiindex() Tests
# =============================================================================

class TestFlattenMultiindex:
    """Tests for flatten_multiindex."""

    def test_flatten_multiindex_columns(self, multiindex_result):
        """Test flattening MultiIndex columns."""
        result = flatten_multiindex(multiindex_result)

        assert not isinstance(result.columns, pd.MultiIndex)
        assert 'Sales_sum' in result.columns
        assert 'Sales_mean' in result.columns
        assert 'Profit_sum' in result.columns
        assert 'Profit_mean' in result.columns

    def test_flatten_multiindex_index(self, multiindex_result):
        """Test flattening MultiIndex index."""
        # Create DataFrame with MultiIndex index
        df = pd.DataFrame({'Value': [1, 2, 3]})
        df.index = pd.MultiIndex.from_tuples([('A', 'X'), ('B', 'Y'), ('C', 'Z')])

        result = flatten_multiindex(df)

        assert not isinstance(result.index, pd.MultiIndex)
        # Index should be reset to regular column
        assert 'level_0' in result.columns or 'index' in result.columns

    def test_no_multiindex_columns(self, simple_dataframe):
        """Test DataFrame without MultiIndex columns."""
        result = flatten_multiindex(simple_dataframe)

        assert isinstance(result.columns, pd.Index)
        assert not isinstance(result.columns, pd.MultiIndex)
        # Index should be reset
        assert 'index' in result.columns or 'Category' in result.columns

    def test_reset_index(self, simple_dataframe):
        """Test that index is reset."""
        df = simple_dataframe.set_index('Category')
        result = flatten_multiindex(df)

        # Index should be reset, making Category a column again
        assert 'Category' in result.columns


# =============================================================================
# create_pivot_table() Tests
# =============================================================================

class TestCreatePivotTable:
    """Tests for create_pivot_table."""

    def test_simple_pivot(self, simple_dataframe):
        """Test creating a simple pivot table."""
        result = create_pivot_table(
            simple_dataframe,
            rows=['Category'],
            columns=['Type'],
            values=['Value']
        )

        assert is_ok(result)
        pivot = unwrap(result)
        assert len(pivot) > 0
        assert 'Category' in pivot.columns

    def test_pivot_with_sum(self, sales_dataframe):
        """Test pivot with sum aggregation."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Product'],
            columns=['Region'],
            values=['Sales'],
            aggfunc='sum'
        )

        assert is_ok(result)
        pivot = unwrap(result)
        # Should have sales aggregated by product and region
        assert len(pivot) == 2  # 2 products

    def test_pivot_with_mean(self, sales_dataframe):
        """Test pivot with mean aggregation."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Product'],
            columns=['Region'],
            values=['Sales'],
            aggfunc='mean'
        )

        assert is_ok(result)
        pivot = unwrap(result)
        assert len(pivot) == 2

    def test_pivot_with_avg_normalizes_to_mean(self, sales_dataframe):
        """Test that 'avg' is normalized to 'mean'."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Product'],
            columns=['Region'],
            values=['Sales'],
            aggfunc='avg'
        )

        assert is_ok(result)
        pivot = unwrap(result)
        assert len(pivot) == 2

    def test_pivot_with_count(self, sales_dataframe):
        """Test pivot with count aggregation."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Product'],
            columns=['Region'],
            values=['Sales'],
            aggfunc='count'
        )

        assert is_ok(result)
        pivot = unwrap(result)
        assert len(pivot) == 2

    def test_pivot_with_fill_value_none(self, sales_dataframe):
        """Test pivot with fill_value=None."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Product'],
            columns=['Region'],
            values=['Sales'],
            aggfunc='sum',
            fill_value=None
        )

        assert is_ok(result)
        pivot = unwrap(result)

    def test_pivot_with_fill_value_zero(self, sales_dataframe):
        """Test pivot with fill_value=0."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Product'],
            columns=['Region'],
            values=['Sales'],
            aggfunc='sum',
            fill_value=0
        )

        assert is_ok(result)
        pivot = unwrap(result)

    def test_pivot_multiple_rows(self, sales_dataframe):
        """Test pivot with multiple row columns."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Date', 'Product'],
            columns=['Region'],
            values=['Sales']
        )

        assert is_ok(result)
        pivot = unwrap(result)
        # When multiple rows are used, they get joined with '_' in the index
        # After flatten_multiindex, the index is reset and becomes a column
        assert 'index' in pivot.columns
        # Check that we have the expected number of rows
        assert len(pivot) == 5  # 5 combinations of Date and Product

    def test_pivot_multiple_values(self, sales_dataframe):
        """Test pivot with multiple value columns."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Product'],
            columns=['Region'],
            values=['Sales', 'Quantity']
        )

        assert is_ok(result)
        pivot = unwrap(result)
        # With multiple values and columns, the column names become Value_Column
        # Should have Sales_North, Sales_South, Quantity_North, Quantity_South
        assert 'Sales_North' in pivot.columns
        assert 'Quantity_North' in pivot.columns
        assert len(pivot) == 2  # 2 products

    def test_pivot_invalid_function(self, simple_dataframe):
        """Test pivot with invalid aggregation function."""
        result = create_pivot_table(
            simple_dataframe,
            rows=['Category'],
            columns=['Type'],
            values=['Value'],
            aggfunc='invalid'
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, PivotFailedError)
        assert "Invalid aggregation function" in error.message

    def test_pivot_missing_row_column(self, simple_dataframe):
        """Test pivot with missing row column."""
        result = create_pivot_table(
            simple_dataframe,
            rows=['InvalidRow'],
            columns=['Type'],
            values=['Value']
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, PivotFailedError)
        assert "not found" in error.message

    def test_pivot_missing_column_column(self, simple_dataframe):
        """Test pivot with missing column column."""
        result = create_pivot_table(
            simple_dataframe,
            rows=['Category'],
            columns=['InvalidCol'],
            values=['Value']
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, PivotFailedError)
        assert "not found" in error.message

    def test_pivot_missing_value_column(self, simple_dataframe):
        """Test pivot with missing value column."""
        result = create_pivot_table(
            simple_dataframe,
            rows=['Category'],
            columns=['Type'],
            values=['InvalidVal']
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, PivotFailedError)
        assert "not found" in error.message


# =============================================================================
# Integration Tests
# =============================================================================

class TestPivotingIntegration:
    """Integration tests for pivoting operations."""

    def test_full_pivot_workflow(self, sales_dataframe):
        """Test complete workflow: validate, parse, pivot."""
        rows = ['Product']
        cols = ['Region']
        vals = ['Sales']
        agg = 'sum'

        # Create pivot table directly (includes validation)
        result = create_pivot_table(
            sales_dataframe,
            rows=rows,
            columns=cols,
            values=vals,
            aggfunc=agg
        )

        assert is_ok(result)
        pivot = unwrap(result)
        assert len(pivot) > 0

    def test_complex_pivot_workflow(self, sales_dataframe):
        """Test complex pivot with multiple options."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Date', 'Region'],
            columns=['Product'],
            values=['Sales', 'Quantity', 'Profit'],
            aggfunc='sum',
            fill_value=0
        )

        assert is_ok(result)
        pivot = unwrap(result)
        assert len(pivot) > 0

    def test_pivot_with_median(self, sales_dataframe):
        """Test pivot with median aggregation."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Region'],
            columns=['Product'],
            values=['Sales'],
            aggfunc='median'
        )

        assert is_ok(result)
        pivot = unwrap(result)

    def test_pivot_with_std(self, sales_dataframe):
        """Test pivot with std aggregation."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Region'],
            columns=['Product'],
            values=['Sales'],
            aggfunc='std'
        )

        assert is_ok(result)
        pivot = unwrap(result)

    def test_pivot_with_variance(self, sales_dataframe):
        """Test pivot with var aggregation."""
        result = create_pivot_table(
            sales_dataframe,
            rows=['Region'],
            columns=['Product'],
            values=['Sales'],
            aggfunc='var'
        )

        assert is_ok(result)
        pivot = unwrap(result)
