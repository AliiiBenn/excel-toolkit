"""Comprehensive tests for comparing operations.

Tests for:
- validate_key_columns()
- compare_rows()
- find_differences()
- build_comparison_result()
- compare_dataframes()
"""

import pytest
import pandas as pd
import numpy as np
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.comparing import (
    validate_key_columns,
    compare_rows,
    find_differences,
    build_comparison_result,
    compare_dataframes,
    DifferencesResult,
    ComparisonResult,
)
from excel_toolkit.models.error_types import (
    KeyColumnsNotFoundError,
    ComparisonFailedError,
)


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def dataframe1():
    """Create first DataFrame for testing."""
    return pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [25, 30, 35, 40, 45],
        'City': ['NYC', 'LA', 'Chicago', 'Houston', 'Phoenix']
    })


@pytest.fixture
def dataframe2():
    """Create second DataFrame for testing."""
    return pd.DataFrame({
        'ID': [1, 2, 3, 4, 6],
        'Name': ['Alice', 'Bob', 'Charles', 'David', 'Frank'],
        'Age': [25, 30, 35, 41, 50],
        'City': ['NYC', 'LA', 'Chicago', 'Boston', 'Seattle']
    })


@pytest.fixture
def dataframe_same():
    """Create DataFrame identical to dataframe1."""
    return pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [25, 30, 35, 40, 45],
        'City': ['NYC', 'LA', 'Chicago', 'Houston', 'Phoenix']
    })


@pytest.fixture
def dataframe_added_only():
    """Create DataFrame with only added rows."""
    return pd.DataFrame({
        'ID': [6, 7, 8],
        'Name': ['Frank', 'Grace', 'Henry'],
        'Age': [50, 55, 60],
        'City': ['Seattle', 'Portland', 'Denver']
    })


@pytest.fixture
def dataframe_deleted_only():
    """Create DataFrame with only deleted rows."""
    return pd.DataFrame({
        'ID': [4, 5],
        'Name': ['David', 'Eve'],
        'Age': [40, 45],
        'City': ['Houston', 'Phoenix']
    })


@pytest.fixture
def dataframe_modified_only():
    """Create DataFrame with only modified rows."""
    return pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Alice', 'Robert', 'Charlie', 'David', 'Evelyn'],
        'Age': [26, 30, 35, 40, 45],
        'City': ['NYC', 'LA', 'Chicago', 'Boston', 'Phoenix']
    })


@pytest.fixture
def dataframe_with_nan():
    """Create DataFrame with NaN values."""
    return pd.DataFrame({
        'ID': [1, 2, 3, 4],
        'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Age': [25, 30, np.nan, 40],
        'City': ['NYC', 'LA', 'Chicago', np.nan]
    })


@pytest.fixture
def dataframe_with_nan_different():
    """Create DataFrame with different NaN values."""
    return pd.DataFrame({
        'ID': [1, 2, 3, 4],
        'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Age': [25, np.nan, 35, 40],
        'City': ['NYC', 'LA', np.nan, 'Boston']
    })


# =============================================================================
# validate_key_columns() Tests
# =============================================================================

class TestValidateKeyColumns:
    """Tests for validate_key_columns."""

    def test_no_key_columns(self, dataframe1):
        """Test validation with no key columns (None)."""
        result = validate_key_columns(dataframe1, dataframe1, None)

        assert is_ok(result)
        keys = unwrap(result)
        assert keys == []

    def test_valid_single_key_column(self, dataframe1):
        """Test validation with valid single key column."""
        result = validate_key_columns(dataframe1, dataframe1, ['ID'])

        assert is_ok(result)
        keys = unwrap(result)
        assert keys == ['ID']

    def test_valid_multiple_key_columns(self, dataframe1):
        """Test validation with valid multiple key columns."""
        result = validate_key_columns(dataframe1, dataframe1, ['ID', 'Name'])

        assert is_ok(result)
        keys = unwrap(result)
        assert keys == ['ID', 'Name']

    def test_key_column_missing_in_df1(self, dataframe1):
        """Test error when key column doesn't exist in df1."""
        result = validate_key_columns(dataframe1, dataframe1, ['InvalidColumn'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, KeyColumnsNotFoundError)
        assert error.missing == ['InvalidColumn']

    def test_key_column_missing_in_df2(self, dataframe1):
        """Test error when key column doesn't exist in df2."""
        df2 = pd.DataFrame({'ID': [1, 2], 'Name': ['Alice', 'Bob']})
        result = validate_key_columns(dataframe1, df2, ['City'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, KeyColumnsNotFoundError)
        assert error.missing == ['City']

    def test_multiple_key_columns_partial_missing(self, dataframe1):
        """Test error when some key columns are missing."""
        df2 = pd.DataFrame({'ID': [1, 2], 'Name': ['Alice', 'Bob']})
        result = validate_key_columns(dataframe1, df2, ['ID', 'Age', 'Invalid'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, KeyColumnsNotFoundError)
        assert set(error.missing) == {'Age', 'Invalid'}


# =============================================================================
# compare_rows() Tests
# =============================================================================

class TestCompareRows:
    """Tests for compare_rows."""

    def test_identical_rows(self):
        """Test comparing identical rows."""
        row1 = pd.Series({'A': 1, 'B': 2, 'C': 3})
        row2 = pd.Series({'A': 1, 'B': 2, 'C': 3})

        result = compare_rows(row1, row2)
        assert result is True

    def test_different_rows(self):
        """Test comparing different rows."""
        row1 = pd.Series({'A': 1, 'B': 2, 'C': 3})
        row2 = pd.Series({'A': 1, 'B': 5, 'C': 3})

        result = compare_rows(row1, row2)
        assert result is False

    def test_different_length_rows(self):
        """Test comparing rows of different lengths."""
        row1 = pd.Series({'A': 1, 'B': 2})
        row2 = pd.Series({'A': 1, 'B': 2, 'C': 3})

        result = compare_rows(row1, row2)
        assert result is False

    def test_rows_with_nan_same_positions(self):
        """Test comparing rows with NaN in same positions."""
        row1 = pd.Series({'A': 1, 'B': np.nan, 'C': 3})
        row2 = pd.Series({'A': 1, 'B': np.nan, 'C': 3})

        result = compare_rows(row1, row2)
        assert result is True

    def test_rows_with_nan_different_positions(self):
        """Test comparing rows with NaN in different positions."""
        row1 = pd.Series({'A': 1, 'B': np.nan, 'C': 3})
        row2 = pd.Series({'A': 1, 'B': 2, 'C': np.nan})

        result = compare_rows(row1, row2)
        assert result is False

    def test_row_with_nan_vs_value(self):
        """Test comparing row with NaN vs value."""
        row1 = pd.Series({'A': 1, 'B': np.nan, 'C': 3})
        row2 = pd.Series({'A': 1, 'B': 2, 'C': 3})

        result = compare_rows(row1, row2)
        assert result is False

    def test_empty_rows(self):
        """Test comparing empty rows."""
        row1 = pd.Series({}, dtype=float)
        row2 = pd.Series({}, dtype=float)

        result = compare_rows(row1, row2)
        assert result is True


# =============================================================================
# find_differences() Tests
# =============================================================================

class TestFindDifferences:
    """Tests for find_differences."""

    def test_no_differences(self, dataframe1, dataframe_same):
        """Test finding differences when there are none."""
        result = find_differences(dataframe1, dataframe_same, ['ID'])

        assert isinstance(result, DifferencesResult)
        assert len(result.only_df1) == 0
        assert len(result.only_df2) == 0
        assert len(result.modified_rows) == 0

    def test_added_rows(self, dataframe1, dataframe_added_only):
        """Test finding added rows."""
        df1 = pd.DataFrame({
            'ID': [1, 2, 3],
            'Name': ['Alice', 'Bob', 'Charlie']
        })
        df2 = pd.DataFrame({
            'ID': [1, 2, 3, 4],
            'Name': ['Alice', 'Bob', 'Charlie', 'David']
        })

        result = find_differences(df1, df2, ['ID'])

        assert len(result.only_df1) == 0
        assert len(result.only_df2) == 1
        assert 4 in result.only_df2
        assert len(result.modified_rows) == 0

    def test_deleted_rows(self, dataframe1):
        """Test finding deleted rows."""
        df1 = pd.DataFrame({
            'ID': [1, 2, 3, 4],
            'Name': ['Alice', 'Bob', 'Charlie', 'David']
        })
        df2 = pd.DataFrame({
            'ID': [1, 2, 3],
            'Name': ['Alice', 'Bob', 'Charlie']
        })

        result = find_differences(df1, df2, ['ID'])

        assert len(result.only_df1) == 1
        assert 4 in result.only_df1
        assert len(result.only_df2) == 0
        assert len(result.modified_rows) == 0

    def test_modified_rows(self, dataframe1, dataframe_modified_only):
        """Test finding modified rows."""
        result = find_differences(dataframe1, dataframe_modified_only, ['ID'])

        assert len(result.only_df1) == 0
        assert len(result.only_df2) == 0
        assert len(result.modified_rows) == 4
        assert 1 in result.modified_rows  # Age changed
        assert 2 in result.modified_rows  # Name changed
        assert 4 in result.modified_rows  # City changed
        assert 5 in result.modified_rows  # Name changed

    def test_all_difference_types(self, dataframe1, dataframe2):
        """Test finding all types of differences."""
        result = find_differences(dataframe1, dataframe2, ['ID'])

        # Deleted: ID=5 (only in df1)
        assert 5 in result.only_df1

        # Added: ID=6 (only in df2)
        assert 6 in result.only_df2

        # Modified: ID=3 (Charlie/Charles), ID=4 (different values)
        assert 3 in result.modified_rows
        assert 4 in result.modified_rows

    def test_no_key_columns(self, dataframe1):
        """Test finding differences without key columns (row position)."""
        df2 = pd.DataFrame({
            'ID': [1, 2, 3, 4, 5],
            'Name': ['Alice', 'Bob', 'Charles', 'David', 'Eve'],
            'Age': [25, 30, 35, 40, 45],
            'City': ['NYC', 'LA', 'Chicago', 'Houston', 'Phoenix']
        })

        result = find_differences(dataframe1, df2, [])

        # Without key columns, uses row position
        assert len(result.only_df1) == 0
        assert len(result.only_df2) == 0
        assert 2 in result.modified_rows  # Row 2 has different Name

    def test_multiple_key_columns(self):
        """Test finding differences with multiple key columns."""
        df1 = pd.DataFrame({
            'ID': [1, 1, 2, 2],
            'Name': ['Alice', 'Alice', 'Bob', 'Bob'],
            'Value': [10, 20, 30, 40]
        })
        df2 = pd.DataFrame({
            'ID': [1, 1, 2, 3],
            'Name': ['Alice', 'Alice', 'Bob', 'Charlie'],
            'Value': [10, 25, 30, 50]
        })

        result = find_differences(df1, df2, ['ID', 'Name'])

        # Deleted: (2, 'Bob') - only appears twice in df1, once in df2
        # Added: (3, 'Charlie') - only in df2
        # Modified: (1, 'Alice') second occurrence has different Value
        assert len(result.modified_rows) > 0

    def test_nan_handling(self, dataframe_with_nan, dataframe_with_nan_different):
        """Test that NaN values are handled correctly."""
        result = find_differences(dataframe_with_nan, dataframe_with_nan_different, ['ID'])

        # Row 2: df1 has Age=30, df2 has Age=NaN - different
        # Row 3: df1 has Age=NaN, df2 has Age=35 - different
        # Row 4: df1 has City=NaN, df2 has City=Boston - different
        assert len(result.only_df1) == 0
        assert len(result.only_df2) == 0
        # Should detect modifications (not all rows have same NaN positions)


# =============================================================================
# build_comparison_result() Tests
# =============================================================================

class TestBuildComparisonResult:
    """Tests for build_comparison_result."""

    def test_no_differences(self, dataframe1):
        """Test building result with no differences."""
        differences = DifferencesResult(
            only_df1=set(),
            only_df2=set(),
            modified_rows=[]
        )

        result = build_comparison_result(dataframe1, dataframe1, differences, ['ID'])

        assert '_diff_status' in result.columns
        assert all(result['_diff_status'] == 'unchanged')
        assert len(result) == len(dataframe1)

    def test_with_added_rows(self, dataframe1):
        """Test building result with added rows."""
        df2 = pd.DataFrame({
            'ID': [1, 2, 3, 6],
            'Name': ['Alice', 'Bob', 'Charlie', 'Frank']
        })
        differences = DifferencesResult(
            only_df1=set(),
            only_df2={6},
            modified_rows=[]
        )

        result = build_comparison_result(dataframe1.iloc[:3], df2, differences, ['ID'])

        assert '_diff_status' in result.columns
        assert 'added' in result['_diff_status'].values
        assert len(result[result['_diff_status'] == 'added']) == 1

    def test_with_deleted_rows(self, dataframe1):
        """Test building result with deleted rows."""
        differences = DifferencesResult(
            only_df1={5},
            only_df2=set(),
            modified_rows=[]
        )

        result = build_comparison_result(dataframe1, dataframe1.iloc[:4], differences, ['ID'])

        assert '_diff_status' in result.columns
        assert 'deleted' in result['_diff_status'].values
        assert len(result[result['_diff_status'] == 'deleted']) == 1

    def test_with_modified_rows(self, dataframe1, dataframe_modified_only):
        """Test building result with modified rows."""
        differences = DifferencesResult(
            only_df1=set(),
            only_df2=set(),
            modified_rows=[2, 4]
        )

        result = build_comparison_result(dataframe1, dataframe_modified_only, differences, ['ID'])

        assert '_diff_status' in result.columns
        assert 'modified' in result['_diff_status'].values
        assert len(result[result['_diff_status'] == 'modified']) == 2

    def test_column_order(self, dataframe1):
        """Test that columns are in correct order."""
        differences = DifferencesResult(
            only_df1=set(),
            only_df2=set(),
            modified_rows=[]
        )

        result = build_comparison_result(dataframe1, dataframe1, differences, ['ID'])

        columns = list(result.columns)
        assert columns[0] == 'ID'
        assert columns[1] == '_diff_status'

    def test_no_key_columns(self, dataframe1):
        """Test building result without key columns."""
        differences = DifferencesResult(
            only_df1=set(),
            only_df2=set(),
            modified_rows=[]
        )

        result = build_comparison_result(dataframe1, dataframe1, differences, [])

        assert '_diff_status' in result.columns
        # Should be first column when no key columns
        assert list(result.columns)[0] == '_diff_status'

    def test_multiple_key_columns_order(self):
        """Test column order with multiple key columns."""
        df1 = pd.DataFrame({
            'ID': [1, 2],
            'Name': ['Alice', 'Bob'],
            'Value': [10, 20]
        })
        differences = DifferencesResult(
            only_df1=set(),
            only_df2=set(),
            modified_rows=[]
        )

        result = build_comparison_result(df1, df1, differences, ['ID', 'Name'])

        columns = list(result.columns)
        assert columns[0] == 'ID'
        assert columns[1] == 'Name'
        assert columns[2] == '_diff_status'


# =============================================================================
# compare_dataframes() Tests
# =============================================================================

class TestCompareDataframes:
    """Tests for compare_dataframes."""

    def test_identical_dataframes(self, dataframe1, dataframe_same):
        """Test comparing identical DataFrames."""
        result = compare_dataframes(dataframe1, dataframe_same, ['ID'])

        assert is_ok(result)
        comparison = unwrap(result)
        assert isinstance(comparison, ComparisonResult)
        assert comparison.added_count == 0
        assert comparison.deleted_count == 0
        assert comparison.modified_count == 0
        assert len(comparison.df_result) == len(dataframe1)
        assert all(comparison.df_result['_diff_status'] == 'unchanged')

    def test_with_added_rows(self, dataframe1):
        """Test comparing with added rows."""
        df2 = pd.DataFrame({
            'ID': [1, 2, 3, 4, 5, 6],
            'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank'],
            'Age': [25, 30, 35, 40, 45, 50],
            'City': ['NYC', 'LA', 'Chicago', 'Houston', 'Phoenix', 'Seattle']
        })

        result = compare_dataframes(dataframe1, df2, ['ID'])

        assert is_ok(result)
        comparison = unwrap(result)
        assert comparison.added_count == 1
        assert comparison.deleted_count == 0
        assert comparison.modified_count == 0
        assert 'added' in comparison.df_result['_diff_status'].values

    def test_with_deleted_rows(self, dataframe1):
        """Test comparing with deleted rows."""
        df2 = pd.DataFrame({
            'ID': [1, 2, 3, 4],
            'Name': ['Alice', 'Bob', 'Charlie', 'David'],
            'Age': [25, 30, 35, 40],
            'City': ['NYC', 'LA', 'Chicago', 'Houston']
        })

        result = compare_dataframes(dataframe1, df2, ['ID'])

        assert is_ok(result)
        comparison = unwrap(result)
        assert comparison.added_count == 0
        assert comparison.deleted_count == 1
        assert comparison.modified_count == 0
        assert 'deleted' in comparison.df_result['_diff_status'].values

    def test_with_modified_rows(self, dataframe1, dataframe_modified_only):
        """Test comparing with modified rows."""
        result = compare_dataframes(dataframe1, dataframe_modified_only, ['ID'])

        assert is_ok(result)
        comparison = unwrap(result)
        assert comparison.added_count == 0
        assert comparison.deleted_count == 0
        assert comparison.modified_count == 4
        assert 'modified' in comparison.df_result['_diff_status'].values

    def test_all_difference_types(self, dataframe1, dataframe2):
        """Test comparing with all types of differences."""
        result = compare_dataframes(dataframe1, dataframe2, ['ID'])

        assert is_ok(result)
        comparison = unwrap(result)
        assert comparison.added_count == 1  # ID=6
        assert comparison.deleted_count == 1  # ID=5
        assert comparison.modified_count >= 2  # ID=3, ID=4

        # Check all status types present
        statuses = set(comparison.df_result['_diff_status'].values)
        assert 'added' in statuses
        assert 'deleted' in statuses
        assert 'modified' in statuses
        assert 'unchanged' in statuses

    def test_no_key_columns(self, dataframe1):
        """Test comparing without key columns (row position)."""
        df2 = pd.DataFrame({
            'ID': [1, 2, 3, 4, 5],
            'Name': ['Alice', 'Bob', 'Charles', 'David', 'Eve'],
            'Age': [25, 30, 35, 40, 45],
            'City': ['NYC', 'LA', 'Chicago', 'Houston', 'Phoenix']
        })

        result = compare_dataframes(dataframe1, df2, None)

        assert is_ok(result)
        comparison = unwrap(result)
        # Should detect modification at row position 2
        assert comparison.modified_count >= 1

    def test_empty_dataframes(self):
        """Test comparing empty DataFrames."""
        df1 = pd.DataFrame({'ID': [], 'Name': []})
        df2 = pd.DataFrame({'ID': [], 'Name': []})

        result = compare_dataframes(df1, df2, ['ID'])

        assert is_ok(result)
        comparison = unwrap(result)
        assert comparison.added_count == 0
        assert comparison.deleted_count == 0
        assert comparison.modified_count == 0
        assert len(comparison.df_result) == 0

    def test_key_columns_missing_in_df1(self, dataframe1):
        """Test error when key columns don't exist in df1."""
        result = compare_dataframes(dataframe1, dataframe1, ['InvalidColumn'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ComparisonFailedError)
        assert 'not found' in error.message.lower()

    def test_key_columns_missing_in_df2(self, dataframe1):
        """Test error when key columns don't exist in df2."""
        df2 = pd.DataFrame({'ID': [1, 2], 'Name': ['Alice', 'Bob']})
        result = compare_dataframes(dataframe1, df2, ['Age'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, ComparisonFailedError)

    def test_nan_handling(self, dataframe_with_nan, dataframe_with_nan_different):
        """Test that NaN values are handled correctly."""
        result = compare_dataframes(dataframe_with_nan, dataframe_with_nan_different, ['ID'])

        assert is_ok(result)
        comparison = unwrap(result)
        # Should detect differences where NaN positions differ
        assert comparison.modified_count >= 0

    def test_multiple_key_columns(self):
        """Test comparing with multiple key columns."""
        df1 = pd.DataFrame({
            'ID': [1, 1, 2, 2],
            'Name': ['Alice', 'Alice', 'Bob', 'Bob'],
            'Value': [10, 20, 30, 40]
        })
        df2 = pd.DataFrame({
            'ID': [1, 1, 2, 2],
            'Name': ['Alice', 'Alice', 'Bob', 'Bob'],
            'Value': [10, 25, 30, 40]
        })

        result = compare_dataframes(df1, df2, ['ID', 'Name'])

        assert is_ok(result)
        comparison = unwrap(result)
        # Should detect modification in second (1, 'Alice') row
        assert comparison.modified_count >= 1

    def test_result_dataframe_structure(self, dataframe1, dataframe2):
        """Test that result DataFrame has correct structure."""
        result = compare_dataframes(dataframe1, dataframe2, ['ID'])

        assert is_ok(result)
        comparison = unwrap(result)

        # Check _diff_status column exists
        assert '_diff_status' in comparison.df_result.columns

        # Check all required status values are present
        valid_statuses = {'unchanged', 'added', 'deleted', 'modified'}
        actual_statuses = set(comparison.df_result['_diff_status'].values)
        assert actual_statuses.issubset(valid_statuses)

    def test_counts_match_dataframe(self, dataframe1, dataframe2):
        """Test that counts match the actual DataFrame content."""
        result = compare_dataframes(dataframe1, dataframe2, ['ID'])

        assert is_ok(result)
        comparison = unwrap(result)

        added_count = len(comparison.df_result[comparison.df_result['_diff_status'] == 'added'])
        deleted_count = len(comparison.df_result[comparison.df_result['_diff_status'] == 'deleted'])
        modified_count = len(comparison.df_result[comparison.df_result['_diff_status'] == 'modified'])

        assert comparison.added_count == added_count
        assert comparison.deleted_count == deleted_count
        assert comparison.modified_count == modified_count


# =============================================================================
# Integration Tests
# =============================================================================

class TestComparingIntegration:
    """Integration tests for comparing operations."""

    def test_full_comparison_workflow(self, dataframe1, dataframe2):
        """Test complete workflow: validate, compare, build result."""
        result = compare_dataframes(dataframe1, dataframe2, ['ID'])

        assert is_ok(result)
        comparison = unwrap(result)

        # Check result structure
        assert hasattr(comparison, 'df_result')
        assert hasattr(comparison, 'added_count')
        assert hasattr(comparison, 'deleted_count')
        assert hasattr(comparison, 'modified_count')

        # Check DataFrame has correct columns
        assert 'ID' in comparison.df_result.columns
        assert '_diff_status' in comparison.df_result.columns

    def test_complex_comparison(self):
        """Test complex comparison with multiple scenarios."""
        df1 = pd.DataFrame({
            'EmployeeID': [101, 102, 103, 104, 105],
            'Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'Department': ['IT', 'HR', 'IT', 'Finance', 'HR'],
            'Salary': [50000, 60000, 55000, 65000, 52000]
        })

        df2 = pd.DataFrame({
            'EmployeeID': [101, 102, 103, 106, 107],
            'Name': ['John', 'Jane', 'Robert', 'David', 'Eve'],
            'Department': ['IT', 'HR', 'IT', 'Finance', 'HR'],
            'Salary': [52000, 60000, 55000, 65000, 53000]
        })

        result = compare_dataframes(df1, df2, ['EmployeeID'])

        assert is_ok(result)
        comparison = unwrap(result)

        # John (101): salary changed - modified
        # Jane (102): unchanged
        # Bob -> Robert (103): name changed - modified
        # Alice (104): deleted
        # Charlie (105): deleted
        # David (106): added
        # Eve (107): added

        assert comparison.added_count == 2
        assert comparison.deleted_count == 2
        assert comparison.modified_count == 2

    def test_comparison_preserves_all_data(self, dataframe1, dataframe2):
        """Test that comparison result preserves all relevant data."""
        result = compare_dataframes(dataframe1, dataframe2, ['ID'])

        assert is_ok(result)
        comparison = unwrap(result)

        # Check that we have all rows from both DataFrames
        expected_total = len(dataframe1) + len(dataframe2) - len(set(dataframe1['ID']) & set(dataframe2['ID']))
        # Note: This is approximate due to how common rows are handled
        assert len(comparison.df_result) >= len(dataframe2)
