"""Unit tests for aggregate command.

Tests for the aggregate command that performs custom aggregations on grouped data.
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner
import pandas as pd

from excel_toolkit.cli import app

# Initialize CLI test runner
runner = CliRunner()


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sales_data_for_aggregate(tmp_path: Path) -> Path:
    """Create a sales data file for aggregation."""
    df = pd.DataFrame(
        {
            "region": ["North", "South", "North", "East", "South", "West", "North", "East"],
            "product": ["A", "B", "A", "C", "B", "A", "C", "A"],
            "amount": [100, 200, 150, 300, 250, 180, 220, 170],
            "quantity": [10, 20, 15, 30, 25, 18, 22, 17],
        }
    )
    file_path = tmp_path / "sales_agg.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def multi_column_agg_file(tmp_path: Path) -> Path:
    """Create a file suitable for multi-column aggregation."""
    df = pd.DataFrame(
        {
            "year": [2023, 2023, 2023, 2024, 2024, 2024],
            "quarter": ["Q1", "Q2", "Q3", "Q1", "Q2", "Q3"],
            "region": ["North", "South", "North", "South", "North", "South"],
            "sales": [1000, 1500, 1200, 1800, 2000, 1700],
            "profit": [200, 300, 250, 400, 450, 380],
        }
    )
    file_path = tmp_path / "multi_agg.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def empty_file_agg(tmp_path: Path) -> Path:
    """Create an empty DataFrame file."""
    df = pd.DataFrame()
    file_path = tmp_path / "empty_agg.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def csv_file_for_aggregate(tmp_path: Path) -> Path:
    """Create a CSV file for aggregation."""
    df = pd.DataFrame(
        {
            "category": ["A", "B", "A", "C", "B", "A"],
            "value": [10, 20, 15, 30, 25, 18],
        }
    )
    file_path = tmp_path / "agg_data.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def file_with_nulls_agg(tmp_path: Path) -> Path:
    """Create a file with null values for aggregation."""
    df = pd.DataFrame(
        {
            "group": ["A", "B", "A", None, "B", "A"],
            "value": [10, 20, 15, 25, 30, 18],
        }
    )
    file_path = tmp_path / "nulls_agg.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


# =============================================================================
# Aggregate Command Tests
# =============================================================================


class TestAggregateCommand:
    """Tests for the aggregate command."""

    def test_aggregate_single_function(self, sales_data_for_aggregate: Path):
        """Test aggregation with single function."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "amount:sum"]
        )

        assert result.exit_code == 0
        assert "Grouped by: region" in result.stdout
        assert "Aggregations: amount:sum" in result.stdout

    def test_aggregate_multiple_functions_same_column(self, sales_data_for_aggregate: Path):
        """Test aggregation with multiple functions on same column."""
        result = runner.invoke(
            app,
            [
                "aggregate",
                str(sales_data_for_aggregate),
                "--group", "region",
                "--functions", "amount:sum,amount:min,amount:max",
            ],
        )

        assert result.exit_code == 0
        assert "Aggregations: amount:sum,amount:min,amount:max" in result.stdout

    def test_aggregate_multiple_columns(self, sales_data_for_aggregate: Path):
        """Test aggregation with multiple columns."""
        result = runner.invoke(
            app,
            [
                "aggregate",
                str(sales_data_for_aggregate),
                "--group", "region",
                "--functions", "amount:sum,amount:mean,quantity:count",
            ],
        )

        assert result.exit_code == 0

    def test_aggregate_mean_function(self, sales_data_for_aggregate: Path):
        """Test mean aggregation."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "product", "--functions", "amount:mean"]
        )

        assert result.exit_code == 0

    def test_aggregate_avg_synonym(self, sales_data_for_aggregate: Path):
        """Test that avg is treated as mean."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "amount:avg"]
        )

        assert result.exit_code == 0

    def test_aggregate_count_function(self, sales_data_for_aggregate: Path):
        """Test count aggregation."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "product", "--functions", "amount:count"]
        )

        assert result.exit_code == 0

    def test_aggregate_min_function(self, sales_data_for_aggregate: Path):
        """Test min aggregation."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "amount:min"]
        )

        assert result.exit_code == 0

    def test_aggregate_max_function(self, sales_data_for_aggregate: Path):
        """Test max aggregation."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "amount:max"]
        )

        assert result.exit_code == 0

    def test_aggregate_median_function(self, sales_data_for_aggregate: Path):
        """Test median aggregation."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "product", "--functions", "amount:median"]
        )

        assert result.exit_code == 0

    def test_aggregate_std_function(self, sales_data_for_aggregate: Path):
        """Test standard deviation aggregation."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "amount:std"]
        )

        assert result.exit_code == 0

    def test_aggregate_var_function(self, sales_data_for_aggregate: Path):
        """Test variance aggregation."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "amount:var"]
        )

        assert result.exit_code == 0

    def test_aggregate_first_function(self, sales_data_for_aggregate: Path):
        """Test first aggregation."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "amount:first"]
        )

        assert result.exit_code == 0

    def test_aggregate_last_function(self, sales_data_for_aggregate: Path):
        """Test last aggregation."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "amount:last"]
        )

        assert result.exit_code == 0

    def test_aggregate_multiple_group_columns(self, multi_column_agg_file: Path):
        """Test aggregation with multiple group columns."""
        result = runner.invoke(
            app,
            [
                "aggregate",
                str(multi_column_agg_file),
                "--group", "year,quarter",
                "--functions", "sales:sum,profit:mean",
            ],
        )

        assert result.exit_code == 0
        assert "Grouped by: year, quarter" in result.stdout

    def test_aggregate_comprehensive(self, sales_data_for_aggregate: Path):
        """Test aggregation with all statistics."""
        result = runner.invoke(
            app,
            [
                "aggregate",
                str(sales_data_for_aggregate),
                "--group", "region",
                "--functions", "amount:sum,amount:mean,amount:min,amount:max,amount:median,amount:count",
            ],
        )

        assert result.exit_code == 0

    def test_aggregate_with_output(self, sales_data_for_aggregate: Path, tmp_path: Path):
        """Test aggregation with output file."""
        output_path = tmp_path / "aggregated.xlsx"
        result = runner.invoke(
            app,
            [
                "aggregate",
                str(sales_data_for_aggregate),
                "--group", "region",
                "--functions", "amount:sum",
                "--output", str(output_path),
            ],
        )

        assert result.exit_code == 0
        assert "Written to:" in result.stdout
        assert output_path.exists()

    def test_aggregate_dry_run(self, sales_data_for_aggregate: Path):
        """Test dry-run mode."""
        result = runner.invoke(
            app,
            [
                "aggregate",
                str(sales_data_for_aggregate),
                "--group", "region",
                "--functions", "amount:sum",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Preview" in result.stdout

    def test_aggregate_csv_input(self, csv_file_for_aggregate: Path):
        """Test aggregation from CSV file."""
        result = runner.invoke(
            app, ["aggregate", str(csv_file_for_aggregate), "--group", "category", "--functions", "value:sum"]
        )

        assert result.exit_code == 0

    def test_aggregate_specific_sheet(self, sales_data_for_aggregate: Path):
        """Test aggregation from specific sheet."""
        result = runner.invoke(
            app,
            [
                "aggregate",
                str(sales_data_for_aggregate),
                "--group", "region",
                "--functions", "amount:sum",
                "--sheet", "Sheet1",
            ],
        )

        assert result.exit_code == 0

    def test_aggregate_invalid_group_column(self, sales_data_for_aggregate: Path):
        """Test aggregation with non-existent group column."""
        result = runner.invoke(
            app,
            ["aggregate", str(sales_data_for_aggregate), "--group", "invalid_column", "--functions", "amount:sum"],
        )

        assert result.exit_code == 1

    def test_aggregate_invalid_aggregate_column(self, sales_data_for_aggregate: Path):
        """Test aggregation with non-existent aggregate column."""
        result = runner.invoke(
            app,
            ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "invalid_column:sum"],
        )

        assert result.exit_code == 1

    def test_aggregate_invalid_function(self, sales_data_for_aggregate: Path):
        """Test aggregation with invalid function."""
        result = runner.invoke(
            app,
            ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "amount:invalid_func"],
        )

        assert result.exit_code == 1

    def test_aggregate_missing_group_parameter(self, sales_data_for_aggregate: Path):
        """Test aggregate without --group parameter."""
        result = runner.invoke(app, ["aggregate", str(sales_data_for_aggregate), "--functions", "amount:sum"])

        assert result.exit_code == 1

    def test_aggregate_missing_functions_parameter(self, sales_data_for_aggregate: Path):
        """Test aggregate without --functions parameter."""
        result = runner.invoke(app, ["aggregate", str(sales_data_for_aggregate), "--group", "region"])

        assert result.exit_code == 1

    def test_aggregate_same_column_for_group_and_aggregate(self, sales_data_for_aggregate: Path):
        """Test that same column cannot be used for grouping and aggregation."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "region:sum"]
        )

        assert result.exit_code == 1

    def test_aggregate_empty_file(self, empty_file_agg: Path):
        """Test aggregate on empty file."""
        result = runner.invoke(
            app, ["aggregate", str(empty_file_agg), "--group", "column", "--functions", "value:sum"]
        )

        assert result.exit_code == 0
        assert "empty" in result.stdout.lower()

    def test_aggregate_nonexistent_file(self):
        """Test aggregate on non-existent file."""
        result = runner.invoke(app, ["aggregate", "missing.xlsx", "--group", "region", "--functions", "amount:sum"])

        assert result.exit_code == 1

    def test_aggregate_help(self):
        """Test aggregate command help."""
        result = runner.invoke(app, ["aggregate", "--help"])

        assert result.exit_code == 0
        assert "Perform custom aggregations" in result.stdout
        assert "--group" in result.stdout
        assert "--functions" in result.stdout

    def test_aggregate_invalid_format(self, sales_data_for_aggregate: Path):
        """Test invalid function format (missing colon)."""
        result = runner.invoke(
            app, ["aggregate", str(sales_data_for_aggregate), "--group", "region", "--functions", "amount"]
        )

        assert result.exit_code == 1

    def test_aggregate_duplicate_column(self, sales_data_for_aggregate: Path):
        """Test duplicate column in aggregations."""
        result = runner.invoke(
            app,
            [
                "aggregate",
                str(sales_data_for_aggregate),
                "--group", "region",
                "--functions", "amount:sum,amount:sum",
            ],
        )

        assert result.exit_code == 1

    def test_aggregate_with_nulls(self, file_with_nulls_agg: Path):
        """Test aggregation with null values."""
        result = runner.invoke(
            app, ["aggregate", str(file_with_nulls_agg), "--group", "group", "--functions", "value:sum"]
        )

        assert result.exit_code == 0
