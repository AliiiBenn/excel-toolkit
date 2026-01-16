"""Unit tests for pivot command.

Tests for the pivot command that creates pivot table summaries.
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
def sales_data_for_pivot(tmp_path: Path) -> Path:
    """Create a sales data file for pivoting."""
    df = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03"],
            "product": ["A", "B", "A", "B", "A"],
            "region": ["North", "South", "North", "South", "West"],
            "sales": [100, 200, 150, 250, 180],
            "quantity": [10, 20, 15, 25, 18],
        }
    )
    file_path = tmp_path / "sales_pivot.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def multi_index_pivot_file(tmp_path: Path) -> Path:
    """Create a file suitable for multi-index pivoting."""
    df = pd.DataFrame(
        {
            "year": [2023, 2023, 2023, 2024, 2024, 2024, 2023, 2023, 2024],
            "quarter": ["Q1", "Q2", "Q3", "Q1", "Q2", "Q3", "Q1", "Q2", "Q1"],
            "product": ["A", "A", "A", "A", "A", "A", "B", "B", "B"],
            "revenue": [1000, 1500, 1200, 1800, 2000, 1700, 800, 900, 1100],
            "units": [100, 150, 120, 180, 200, 170, 80, 90, 110],
        }
    )
    file_path = tmp_path / "multi_pivot.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def empty_file_pivot(tmp_path: Path) -> Path:
    """Create an empty DataFrame file."""
    df = pd.DataFrame()
    file_path = tmp_path / "empty_pivot.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def csv_file_for_pivot(tmp_path: Path) -> Path:
    """Create a CSV file for pivoting."""
    df = pd.DataFrame(
        {
            "category": ["A", "B", "A", "C", "B", "A"],
            "month": ["Jan", "Jan", "Feb", "Jan", "Feb", "Jan"],
            "value": [10, 20, 15, 30, 25, 18],
        }
    )
    file_path = tmp_path / "pivot_data.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def file_with_nulls_pivot(tmp_path: Path) -> Path:
    """Create a file with null values for pivoting."""
    df = pd.DataFrame(
        {
            "region": ["North", "South", "North", None, "South", "North"],
            "product": ["A", "B", "A", "C", "B", "A"],
            "sales": [100, 200, 150, 300, 250, 180],
        }
    )
    file_path = tmp_path / "nulls_pivot.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


# =============================================================================
# Pivot Command Tests
# =============================================================================


class TestPivotCommand:
    """Tests for the pivot command."""

    def test_pivot_basic(self, sales_data_for_pivot: Path):
        """Test basic pivot table creation."""
        result = runner.invoke(
            app, ["pivot", str(sales_data_for_pivot), "--rows", "date", "--columns", "product", "--values", "sales"]
        )

        assert result.exit_code == 0
        assert "Rows: date" in result.stdout
        assert "Columns: product" in result.stdout
        assert "Values: sales" in result.stdout

    def test_pivot_sum_aggregation(self, sales_data_for_pivot: Path):
        """Test pivot with sum aggregation (default)."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "region",
                "--columns", "product",
                "--values", "sales",
                "--aggfunc", "sum",
            ],
        )

        assert result.exit_code == 0
        assert "Aggregation: sum" in result.stdout

    def test_pivot_mean_aggregation(self, sales_data_for_pivot: Path):
        """Test pivot with mean aggregation."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "product",
                "--columns", "region",
                "--values", "sales",
                "--aggfunc", "mean",
            ],
        )

        assert result.exit_code == 0
        assert "Aggregation: mean" in result.stdout

    def test_pivot_avg_synonym(self, sales_data_for_pivot: Path):
        """Test that avg is treated as mean."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "date",
                "--columns", "product",
                "--values", "sales",
                "--aggfunc", "avg",
            ],
        )

        assert result.exit_code == 0

    def test_pivot_count_aggregation(self, sales_data_for_pivot: Path):
        """Test count aggregation."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "region",
                "--columns", "product",
                "--values", "quantity",
                "--aggfunc", "count",
            ],
        )

        assert result.exit_code == 0

    def test_pivot_min_aggregation(self, sales_data_for_pivot: Path):
        """Test min aggregation."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "product",
                "--columns", "date",
                "--values", "sales",
                "--aggfunc", "min",
            ],
        )

        assert result.exit_code == 0

    def test_pivot_max_aggregation(self, sales_data_for_pivot: Path):
        """Test max aggregation."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "region",
                "--columns", "date",
                "--values", "quantity",
                "--aggfunc", "max",
            ],
        )

        assert result.exit_code == 0

    def test_pivot_median_aggregation(self, sales_data_for_pivot: Path):
        """Test median aggregation."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "product",
                "--columns", "region",
                "--values", "sales",
                "--aggfunc", "median",
            ],
        )

        assert result.exit_code == 0

    def test_pivot_multiple_rows(self, multi_index_pivot_file: Path):
        """Test pivoting with multiple row columns."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(multi_index_pivot_file),
                "--rows", "year,quarter",
                "--columns", "product",
                "--values", "revenue",
                "--aggfunc", "sum",
            ],
        )

        assert result.exit_code == 0
        assert "Rows: year, quarter" in result.stdout

    def test_pivot_multiple_columns(self, multi_index_pivot_file: Path):
        """Test pivoting with multiple column dimensions."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(multi_index_pivot_file),
                "--rows", "year",
                "--columns", "quarter,product",
                "--values", "revenue",
            ],
        )

        assert result.exit_code == 0
        assert "Columns: quarter, product" in result.stdout

    def test_pivot_multiple_values(self, sales_data_for_pivot: Path):
        """Test pivoting with multiple value columns."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "date",
                "--columns", "product",
                "--values", "sales,quantity",
            ],
        )

        assert result.exit_code == 0
        assert "Values: sales, quantity" in result.stdout

    def test_pivot_with_fill_value_zero(self, sales_data_for_pivot: Path):
        """Test pivot with fill value set to 0."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "region",
                "--columns", "product",
                "--values", "sales",
                "--fill", "0",
            ],
        )

        assert result.exit_code == 0
        assert "Fill value: 0" in result.stdout

    def test_pivot_with_output(self, sales_data_for_pivot: Path, tmp_path: Path):
        """Test pivot with output file."""
        output_path = tmp_path / "pivoted.xlsx"
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "region",
                "--columns", "product",
                "--values", "sales",
                "--output", str(output_path),
            ],
        )

        assert result.exit_code == 0
        assert "Written to:" in result.stdout
        assert output_path.exists()

    def test_pivot_dry_run(self, sales_data_for_pivot: Path):
        """Test dry-run mode."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "region",
                "--columns", "product",
                "--values", "sales",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Preview" in result.stdout

    def test_pivot_csv_input(self, csv_file_for_pivot: Path):
        """Test pivoting from CSV file."""
        result = runner.invoke(
            app,
            ["pivot", str(csv_file_for_pivot), "--rows", "category", "--columns", "month", "--values", "value"],
        )

        assert result.exit_code == 0

    def test_pivot_specific_sheet(self, sales_data_for_pivot: Path):
        """Test pivoting from specific sheet."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "date",
                "--columns", "product",
                "--values", "sales",
                "--sheet", "Sheet1",
            ],
        )

        assert result.exit_code == 0

    def test_pivot_invalid_row_column(self, sales_data_for_pivot: Path):
        """Test pivoting with non-existent row column."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "invalid_column",
                "--columns", "product",
                "--values", "sales",
            ],
        )

        assert result.exit_code == 1

    def test_pivot_invalid_column_column(self, sales_data_for_pivot: Path):
        """Test pivoting with non-existent column column."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "date",
                "--columns", "invalid_column",
                "--values", "sales",
            ],
        )

        assert result.exit_code == 1

    def test_pivot_invalid_value_column(self, sales_data_for_pivot: Path):
        """Test pivoting with non-existent value column."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "date",
                "--columns", "product",
                "--values", "invalid_column",
            ],
        )

        assert result.exit_code == 1

    def test_pivot_invalid_aggregation_function(self, sales_data_for_pivot: Path):
        """Test pivoting with invalid aggregation function."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(sales_data_for_pivot),
                "--rows", "date",
                "--columns", "product",
                "--values", "sales",
                "--aggfunc", "invalid",
            ],
        )

        assert result.exit_code == 1

    def test_pivot_missing_rows_parameter(self, sales_data_for_pivot: Path):
        """Test pivot without --rows parameter."""
        result = runner.invoke(
            app, ["pivot", str(sales_data_for_pivot), "--columns", "product", "--values", "sales"]
        )

        assert result.exit_code == 1

    def test_pivot_missing_columns_parameter(self, sales_data_for_pivot: Path):
        """Test pivot without --columns parameter."""
        result = runner.invoke(app, ["pivot", str(sales_data_for_pivot), "--rows", "date", "--values", "sales"])

        assert result.exit_code == 1

    def test_pivot_missing_values_parameter(self, sales_data_for_pivot: Path):
        """Test pivot without --values parameter."""
        result = runner.invoke(
            app, ["pivot", str(sales_data_for_pivot), "--rows", "date", "--columns", "product"]
        )

        assert result.exit_code == 1

    def test_pivot_empty_file(self, empty_file_pivot: Path):
        """Test pivot on empty file."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(empty_file_pivot),
                "--rows", "column",
                "--columns", "col2",
                "--values", "value",
            ],
        )

        assert result.exit_code == 0
        assert "empty" in result.stdout.lower()

    def test_pivot_nonexistent_file(self):
        """Test pivot on non-existent file."""
        result = runner.invoke(
            app, ["pivot", "missing.xlsx", "--rows", "date", "--columns", "product", "--values", "sales"]
        )

        assert result.exit_code == 1

    def test_pivot_help(self):
        """Test pivot command help."""
        result = runner.invoke(app, ["pivot", "--help"])

        assert result.exit_code == 0
        assert "Create pivot table" in result.stdout
        assert "--rows" in result.stdout
        assert "--columns" in result.stdout
        assert "--values" in result.stdout

    def test_pivot_with_nulls(self, file_with_nulls_pivot: Path):
        """Test pivoting with null values."""
        result = runner.invoke(
            app,
            [
                "pivot",
                str(file_with_nulls_pivot),
                "--rows", "region",
                "--columns", "product",
                "--values", "sales",
                "--fill", "0",
            ],
        )

        assert result.exit_code == 0
