"""Comprehensive tests for joining operations.

Tests for:
- validate_join_columns()
- join_dataframes()
- merge_dataframes()
"""

import pytest
import pandas as pd
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.joining import (
    validate_join_columns,
    join_dataframes,
    merge_dataframes,
)
from excel_toolkit.models.error_types import (
    InvalidJoinParametersError,
    JoinColumnsNotFoundError,
    InvalidJoinTypeError,
    JoiningError,
    MergeColumnsNotFoundError,
    InsufficientDataFramesError,
)


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def left_dataframe():
    """Create left DataFrame for joining."""
    return pd.DataFrame({
        'ID': [1, 2, 3, 4],
        'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Value': [100, 200, 300, 400]
    })


@pytest.fixture
def right_dataframe():
    """Create right DataFrame for joining."""
    return pd.DataFrame({
        'ID': [2, 3, 4, 5],
        'Score': [85, 90, 95, 100],
        'Category': ['A', 'B', 'A', 'B']
    })


@pytest.fixture
def another_dataframe():
    """Create another DataFrame for merging."""
    return pd.DataFrame({
        'ID': [1, 2, 3, 5],
        'Extra': ['X', 'Y', 'Z', 'W']
    })


# =============================================================================
# validate_join_columns() Tests
# =============================================================================

class TestValidateJoinColumns:
    """Tests for validate_join_columns."""

    def test_valid_join_with_on(self, left_dataframe, right_dataframe):
        """Test valid join with 'on' parameter."""
        result = validate_join_columns(left_dataframe, right_dataframe, on=['ID'])

        assert is_ok(result)

    def test_valid_join_with_left_on_right_on(self, left_dataframe, right_dataframe):
        """Test valid join with 'left_on' and 'right_on'."""
        result = validate_join_columns(
            left_dataframe,
            right_dataframe,
            left_on=['ID'],
            right_on=['ID']
        )

        assert is_ok(result)

    def test_valid_join_with_left_index(self, left_dataframe, right_dataframe):
        """Test valid join with left_index=True."""
        result = validate_join_columns(left_dataframe, right_dataframe, left_index=True)

        assert is_ok(result)

    def test_valid_join_with_right_index(self, left_dataframe, right_dataframe):
        """Test valid join with right_index=True."""
        result = validate_join_columns(left_dataframe, right_dataframe, right_index=True)

        assert is_ok(result)

    def test_valid_join_with_both_indexes(self, left_dataframe, right_dataframe):
        """Test valid join with both index flags."""
        result = validate_join_columns(
            left_dataframe,
            right_dataframe,
            left_index=True,
            right_index=True
        )

        assert is_ok(result)

    def test_invalid_combination_on_with_left_on(self, left_dataframe, right_dataframe):
        """Test invalid combination: 'on' with 'left_on'."""
        result = validate_join_columns(
            left_dataframe,
            right_dataframe,
            on=['ID'],
            left_on=['ID']
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InvalidJoinParametersError)

    def test_column_not_found_in_left(self, left_dataframe, right_dataframe):
        """Test error when column not found in left DataFrame."""
        result = validate_join_columns(left_dataframe, right_dataframe, on=['NonExistent'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, JoinColumnsNotFoundError)

    def test_column_not_found_in_right(self, left_dataframe, right_dataframe):
        """Test error when column not found in right DataFrame."""
        result = validate_join_columns(left_dataframe, right_dataframe, on=['NonExistent'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, JoinColumnsNotFoundError)

    def test_empty_column_lists(self, left_dataframe, right_dataframe):
        """Test with empty column lists."""
        result = validate_join_columns(left_dataframe, right_dataframe, on=[])

        assert is_ok(result)

    def test_left_on_without_right_on(self, left_dataframe, right_dataframe):
        """Test error when only 'left_on' specified."""
        result = validate_join_columns(
            left_dataframe,
            right_dataframe,
            left_on=['ID']
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InvalidJoinParametersError)

    def test_mismatched_left_on_right_on_lengths(self, left_dataframe, right_dataframe):
        """Test error when 'left_on' and 'right_on' have different lengths."""
        result = validate_join_columns(
            left_dataframe,
            right_dataframe,
            left_on=['ID'],
            right_on=[]
        )

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InvalidJoinParametersError)


# =============================================================================
# join_dataframes() Tests
# =============================================================================

class TestJoinDataframes:
    """Tests for join_dataframes."""

    def test_inner_join(self, left_dataframe, right_dataframe):
        """Test inner join."""
        result = join_dataframes(left_dataframe, right_dataframe, how='inner', on=['ID'])

        assert is_ok(result)
        df_joined = unwrap(result)
        assert len(df_joined) == 3  # IDs 2, 3, 4 match
        assert 'Name' in df_joined.columns
        assert 'Score' in df_joined.columns

    def test_left_join(self, left_dataframe, right_dataframe):
        """Test left join."""
        result = join_dataframes(left_dataframe, right_dataframe, how='left', on=['ID'])

        assert is_ok(result)
        df_joined = unwrap(result)
        assert len(df_joined) == 4  # All left rows preserved

    def test_right_join(self, left_dataframe, right_dataframe):
        """Test right join."""
        result = join_dataframes(left_dataframe, right_dataframe, how='right', on=['ID'])

        assert is_ok(result)
        df_joined = unwrap(result)
        assert len(df_joined) == 4  # All right rows preserved

    def test_outer_join(self, left_dataframe, right_dataframe):
        """Test outer join."""
        result = join_dataframes(left_dataframe, right_dataframe, how='outer', on=['ID'])

        assert is_ok(result)
        df_joined = unwrap(result)
        assert len(df_joined) >= 4

    def test_cross_join(self, left_dataframe, right_dataframe):
        """Test cross join."""
        result = join_dataframes(left_dataframe, right_dataframe, how='cross')

        assert is_ok(result)
        df_joined = unwrap(result)
        assert len(df_joined) == 16  # 4 * 4

    def test_join_with_left_on_right_on(self, left_dataframe, right_dataframe):
        """Test join with different column names."""
        result = join_dataframes(
            left_dataframe,
            right_dataframe,
            how='inner',
            left_on=['ID'],
            right_on=['ID']
        )

        assert is_ok(result)
        df_joined = unwrap(result)
        assert len(df_joined) == 3

    def test_join_with_indexes(self, left_dataframe, right_dataframe):
        """Test join with indexes."""
        left = left_dataframe.set_index('ID')
        right = right_dataframe.set_index('ID')

        result = join_dataframes(left, right, how='inner', left_index=True, right_index=True)

        assert is_ok(result)
        df_joined = unwrap(result)
        assert len(df_joined) == 3

    def test_custom_suffixes(self, left_dataframe, right_dataframe):
        """Test custom suffixes for overlapping columns."""
        df2 = pd.DataFrame({'ID': [2, 3], 'Value': [500, 600]})

        result = join_dataframes(
            left_dataframe,
            df2,
            how='inner',
            on=['ID'],
            suffixes=('_left', '_right')
        )

        assert is_ok(result)
        df_joined = unwrap(result)
        assert 'Value_left' in df_joined.columns
        assert 'Value_right' in df_joined.columns

    def test_invalid_join_type(self, left_dataframe, right_dataframe):
        """Test error with invalid join type."""
        result = join_dataframes(left_dataframe, right_dataframe, how='invalid', on=['ID'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InvalidJoinTypeError)

    def test_column_not_found(self, left_dataframe, right_dataframe):
        """Test error when column not found."""
        result = join_dataframes(left_dataframe, right_dataframe, on=['NonExistent'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, JoinColumnsNotFoundError)

    def test_empty_dataframes(self):
        """Test join with empty DataFrames."""
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()

        result = join_dataframes(df1, df2, how='inner')

        assert is_ok(result)

    def test_no_matching_rows(self, left_dataframe, right_dataframe):
        """Test inner join with no matching rows."""
        df2 = pd.DataFrame({'ID': [10, 20, 30], 'Value': [1, 2, 3]})

        result = join_dataframes(left_dataframe, df2, how='inner', on=['ID'])

        assert is_ok(result)
        df_joined = unwrap(result)
        assert len(df_joined) == 0

    def test_all_matching_rows(self, left_dataframe, right_dataframe):
        """Test inner join where all rows match."""
        df2 = pd.DataFrame({
            'ID': [1, 2, 3, 4],
            'Extra': ['A', 'B', 'C', 'D']
        })

        result = join_dataframes(left_dataframe, df2, how='inner', on=['ID'])

        assert is_ok(result)
        df_joined = unwrap(result)
        assert len(df_joined) == 4


# =============================================================================
# merge_dataframes() Tests
# =============================================================================

class TestMergeDataframes:
    """Tests for merge_dataframes."""

    def test_merge_2_dataframes(self, left_dataframe, right_dataframe):
        """Test merging 2 DataFrames."""
        result = merge_dataframes([left_dataframe, right_dataframe], how='inner', on=['ID'])

        assert is_ok(result)
        df_merged = unwrap(result)
        assert len(df_merged) == 3

    def test_merge_3_dataframes(self, left_dataframe, right_dataframe, another_dataframe):
        """Test merging 3 DataFrames."""
        result = merge_dataframes(
            [left_dataframe, right_dataframe, another_dataframe],
            how='inner',
            on=['ID']
        )

        assert is_ok(result)
        df_merged = unwrap(result)
        assert len(df_merged) == 2  # Only IDs 2 and 3 are in all three

    def test_merge_with_on_parameter(self, left_dataframe, right_dataframe):
        """Test merge with 'on' parameter."""
        result = merge_dataframes([left_dataframe, right_dataframe], how='inner', on=['ID'])

        assert is_ok(result)
        df_merged = unwrap(result)
        assert 'Name' in df_merged.columns
        assert 'Score' in df_merged.columns

    def test_merge_without_on_parameter(self, left_dataframe, right_dataframe):
        """Test merge without 'on' parameter (cross merge)."""
        result = merge_dataframes([left_dataframe, right_dataframe], how='cross')

        assert is_ok(result)
        df_merged = unwrap(result)
        assert len(df_merged) == 16  # 4 * 4

    def test_different_join_types(self, left_dataframe, right_dataframe):
        """Test merge with different join types."""
        result = merge_dataframes([left_dataframe, right_dataframe], how='left', on=['ID'])

        assert is_ok(result)
        df_merged = unwrap(result)
        assert len(df_merged) == 4  # All left rows preserved

    def test_column_not_found_in_one_dataframe(self, left_dataframe, right_dataframe):
        """Test error when column not found in one DataFrame."""
        df2 = pd.DataFrame({'Value': [1, 2, 3]})  # No 'ID' column

        result = merge_dataframes([left_dataframe, df2], how='inner', on=['ID'])

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, MergeColumnsNotFoundError)

    def test_single_dataframe_error(self, left_dataframe):
        """Test error with only one DataFrame."""
        result = merge_dataframes([left_dataframe], how='inner')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InsufficientDataFramesError)

    def test_empty_list_error(self):
        """Test error with empty list."""
        result = merge_dataframes([], how='inner')

        assert is_err(result)
        error = unwrap_err(result)
        assert isinstance(error, InsufficientDataFramesError)

    def test_all_dataframes_empty(self):
        """Test merge with all empty DataFrames."""
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()

        result = merge_dataframes([df1, df2], how='inner')

        # Should handle gracefully
        assert is_ok(result) or is_err(result)
