"""Unit tests for count command.

Tests for the count command that counts occurrences of unique values.
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
def sample_data_file(tmp_path: Path) -> Path:
    """Create a sample data file with categorical values."""
    df = pd.DataFrame(
        {
            "id": range(1, 11),
            "category": ["A", "B", "A", "C", "B", "A", "C", "B", "A", "C"],
            "status": ["active", "inactive", "active", "active", "inactive", "active", "inactive", "active", "active", "inactive"],
            "value": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        }
    )
    file_path = tmp_path / "data.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def csv_file_for_count(tmp_path: Path) -> Path:
    """Create a CSV file for count testing."""
    df = pd.DataFrame(
        {
            "product": ["Apple", "Banana", "Apple", "Cherry", "Banana", "Apple"],
            "quantity": [5, 3, 7, 2, 4, 6],
        }
    )
    file_path = tmp_path / "count.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def multi_column_file(tmp_path: Path) -> Path:
    """Create file with multiple columns to count."""
    df = pd.DataFrame(
        {
            "region": ["North", "South", "North", "East", "South", "West", "North", "East"],
            "product": ["A", "B", "A", "C", "B", "A", "C", "B"],
            "sales": [100, 200, 150, 300, 250, 180, 220, 270],
        }
    )
    file_path = tmp_path / "multi.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def empty_file(tmp_path: Path) -> Path:
    """Create an empty DataFrame file."""
    df = pd.DataFrame()
    file_path = tmp_path / "empty.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


# =============================================================================
# Count Command Tests
# =============================================================================


class TestCountCommand:
    """Tests for the count command."""

    def test_count_single_column(self, sample_data_file: Path):
        """Test count on a single column."""
        result = runner.invoke(app, [
            "count", str(sample_data_file),
            "--columns", "category"
        ])

        assert result.exit_code == 0
        assert "Total rows:" in result.stdout
        assert "Columns: category" in result.stdout

    def test_count_multiple_columns(self, multi_column_file: Path):
        """Test count on multiple columns."""
        result = runner.invoke(app, [
            "count", str(multi_column_file),
            "--columns", "region,product"
        ])

        assert result.exit_code == 0
        assert "Columns: region, product" in result.stdout
        assert "column" in result.stdout.lower()

    def test_count_sort_by_count_descending(self, sample_data_file: Path):
        """Test count sorted by count (descending default)."""
        result = runner.invoke(app, [
            "count", str(sample_data_file),
            "--columns", "category",
            "--sort", "count"
        ])

        assert result.exit_code == 0
        assert "Sorted by: count (descending)" in result.stdout

    def test_count_sort_by_count_ascending(self, sample_data_file: Path):
        """Test count sorted by count (ascending)."""
        result = runner.invoke(app, [
            "count", str(sample_data_file),
            "--columns", "category",
            "--sort", "count",
            "--ascending"
        ])

        assert result.exit_code == 0
        assert "Sorted by: count (ascending)" in result.stdout

    def test_count_sort_by_name_descending(self, sample_data_file: Path):
        """Test count sorted by name (descending)."""
        result = runner.invoke(app, [
            "count", str(sample_data_file),
            "--columns", "category",
            "--sort", "name"
        ])

        assert result.exit_code == 0
        assert "Sorted by: name (descending)" in result.stdout

    def test_count_sort_by_name_ascending(self, sample_data_file: Path):
        """Test count sorted by name (ascending)."""
        result = runner.invoke(app, [
            "count", str(sample_data_file),
            "--columns", "category",
            "--sort", "name",
            "--ascending"
        ])

        assert result.exit_code == 0
        assert "Sorted by: name (ascending)" in result.stdout

    def test_count_no_sort(self, sample_data_file: Path):
        """Test count without sorting."""
        result = runner.invoke(app, [
            "count", str(sample_data_file),
            "--columns", "category",
            "--sort", "none"
        ])

        assert result.exit_code == 0
        assert "Sorted by: none" in result.stdout

    def test_count_with_output(self, sample_data_file: Path, tmp_path: Path):
        """Test count with output file."""
        output_path = tmp_path / "counts.xlsx"
        result = runner.invoke(app, [
            "count", str(sample_data_file),
            "--columns", "category",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Written to:" in result.stdout
        assert output_path.exists()

    def test_count_csv_input(self, csv_file_for_count: Path):
        """Test count from CSV file."""
        result = runner.invoke(app, [
            "count", str(csv_file_for_count),
            "--columns", "product"
        ])

        assert result.exit_code == 0
        assert "Total rows:" in result.stdout

    def test_count_specific_sheet(self, sample_data_file: Path):
        """Test count from specific sheet."""
        result = runner.invoke(app, [
            "count", str(sample_data_file),
            "--columns", "category",
            "--sheet", "Sheet1"
        ])

        assert result.exit_code == 0

    def test_count_invalid_sort(self, sample_data_file: Path):
        """Test count with invalid sort value."""
        result = runner.invoke(app, [
            "count", str(sample_data_file),
            "--columns", "category",
            "--sort", "invalid"
        ])

        assert result.exit_code == 1
        assert "Valid values" in result.stdout or "Invalid sort" in result.stdout

    def test_count_missing_column(self, sample_data_file: Path):
        """Test count with non-existent column."""
        result = runner.invoke(app, [
            "count", str(sample_data_file),
            "--columns", "invalid_column"
        ])

        assert result.exit_code == 1
        assert "Columns not found" in result.stdout or "Available columns" in result.stdout

    def test_count_partial_missing_columns(self, multi_column_file: Path):
        """Test count with some valid and some invalid columns."""
        result = runner.invoke(app, [
            "count", str(multi_column_file),
            "--columns", "region,invalid"
        ])

        assert result.exit_code == 1
        assert "Columns not found" in result.stdout or "Available columns" in result.stdout

    def test_count_empty_file(self, empty_file: Path):
        """Test count on empty file."""
        result = runner.invoke(app, [
            "count", str(empty_file),
            "--columns", "category"
        ])

        assert result.exit_code == 0
        assert "empty" in result.stdout.lower()

    def test_count_nonexistent_file(self):
        """Test count on non-existent file."""
        result = runner.invoke(app, [
            "count", "missing.xlsx",
            "--columns", "category"
        ])

        assert result.exit_code == 1
        assert "File not found" in result.stdout or "File not found" in result.stderr

    def test_count_help(self):
        """Test count command help."""
        result = runner.invoke(app, ["count", "--help"])

        assert result.exit_code == 0
        assert "Count occurrences" in result.stdout
        assert "--columns" in result.stdout
        assert "--sort" in result.stdout
