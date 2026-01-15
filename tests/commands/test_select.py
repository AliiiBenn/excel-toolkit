"""Unit tests for select command.

Tests for the select command that selects specific columns.
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
    """Create a sample data file for testing."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "age": [25, 30, 35, 28, 32],
            "city": ["Paris", "London", "Berlin", "Madrid", "Rome"],
            "salary": [50000, 60000, 70000, 55000, 65000],
            "email": ["alice@example.com", "bob@example.com", "charlie@example.com", "diana@example.com", "eve@example.com"],
        }
    )
    file_path = tmp_path / "data.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def file_with_nulls(tmp_path: Path) -> Path:
    """Create a file with null values."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", None, "Diana", "Eve"],
            "age": [25, 30, 35, 28, 32],
            "value": [100, 200, None, 400, 500],
        }
    )
    file_path = tmp_path / "nulls.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def empty_file(tmp_path: Path) -> Path:
    """Create an empty DataFrame file."""
    df = pd.DataFrame()
    file_path = tmp_path / "empty.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def csv_file(tmp_path: Path) -> Path:
    """Create a CSV file for testing."""
    df = pd.DataFrame(
        {
            "product": ["A", "B", "C"],
            "price": [10.99, 20.50, 15.75],
            "quantity": [100, 50, 75],
        }
    )
    file_path = tmp_path / "data.csv"
    df.to_csv(file_path, index=False)
    return file_path


# =============================================================================
# Select Command Tests
# =============================================================================


class TestSelectCommand:
    """Tests for the select command."""

    def test_select_single_column(self, sample_data_file: Path):
        """Test selecting a single column."""
        result = runner.invoke(app, ["select", str(sample_data_file), "--columns", "name"])

        assert result.exit_code == 0
        assert "Selected 1 of 6 columns" in result.stdout

    def test_select_multiple_columns(self, sample_data_file: Path):
        """Test selecting multiple columns."""
        result = runner.invoke(app, ["select", str(sample_data_file), "--columns", "id,name,age"])

        assert result.exit_code == 0
        assert "Selected 3 of 6 columns" in result.stdout

    def test_select_with_output(self, sample_data_file: Path, tmp_path: Path):
        """Test selecting with output file."""
        output_path = tmp_path / "selected.xlsx"
        result = runner.invoke(app, [
            "select", str(sample_data_file),
            "--columns", "id,name",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Written to:" in result.stdout
        assert output_path.exists()

    def test_select_exclude_columns(self, sample_data_file: Path):
        """Test excluding specific columns."""
        result = runner.invoke(app, [
            "select", str(sample_data_file),
            "--exclude", "salary,email"
        ])

        assert result.exit_code == 0
        assert "Selected 4 of 6 columns" in result.stdout
        assert "Excluded: salary,email" in result.stdout

    def test_select_only_numeric(self, sample_data_file: Path):
        """Test selecting only numeric columns."""
        result = runner.invoke(app, ["select", str(sample_data_file), "--only-numeric"])

        assert result.exit_code == 0
        assert "numeric columns only" in result.stdout

    def test_select_only_string(self, sample_data_file: Path):
        """Test selecting only string columns."""
        result = runner.invoke(app, ["select", str(sample_data_file), "--only-string"])

        assert result.exit_code == 0
        assert "string columns only" in result.stdout

    def test_select_only_datetime(self, sample_data_file: Path):
        """Test selecting only datetime columns."""
        result = runner.invoke(app, ["select", str(sample_data_file), "--only-datetime"])

        assert result.exit_code == 0
        # No datetime columns in sample data, so it should either pass with 0 or handle gracefully

    def test_select_only_non_empty(self, file_with_nulls: Path):
        """Test selecting only columns with no empty values."""
        result = runner.invoke(app, ["select", str(file_with_nulls), "--only-non-empty"])

        assert result.exit_code == 0
        assert "no empty values" in result.stdout

    def test_select_with_rename(self, sample_data_file: Path):
        """Test selecting with column renaming."""
        result = runner.invoke(app, [
            "select", str(sample_data_file),
            "--columns", "name->full_name,email->contact_email"
        ])

        assert result.exit_code == 0
        assert "Selected 2 of 6 columns" in result.stdout

    def test_select_dry_run(self, sample_data_file: Path):
        """Test dry-run mode."""
        result = runner.invoke(app, [
            "select", str(sample_data_file),
            "--columns", "id,name",
            "--dry-run"
        ])

        assert result.exit_code == 0
        assert "Preview" in result.stdout

    def test_select_csv_input(self, csv_file: Path):
        """Test selecting from CSV file."""
        result = runner.invoke(app, [
            "select", str(csv_file),
            "--columns", "product,price"
        ])

        assert result.exit_code == 0
        assert "Selected 2 of 3 columns" in result.stdout

    def test_select_specific_sheet(self, sample_data_file: Path):
        """Test selecting from specific sheet."""
        result = runner.invoke(app, [
            "select", str(sample_data_file),
            "--columns", "id,name",
            "--sheet", "Sheet1"
        ])

        assert result.exit_code == 0

    def test_select_invalid_column(self, sample_data_file: Path):
        """Test selecting non-existent column."""
        result = runner.invoke(app, [
            "select", str(sample_data_file),
            "--columns", "invalid_column"
        ])

        assert result.exit_code == 1

    def test_select_invalid_exclude_column(self, sample_data_file: Path):
        """Test excluding non-existent column."""
        result = runner.invoke(app, [
            "select", str(sample_data_file),
            "--exclude", "invalid_column"
        ])

        assert result.exit_code == 1

    def test_select_no_options(self, sample_data_file: Path):
        """Test select without specifying any option."""
        result = runner.invoke(app, ["select", str(sample_data_file)])

        assert result.exit_code == 1

    def test_select_empty_file(self, empty_file: Path):
        """Test select on empty file."""
        result = runner.invoke(app, [
            "select", str(empty_file),
            "--columns", "id"
        ])

        assert result.exit_code == 0
        assert "empty" in result.stdout.lower()

    def test_select_nonexistent_file(self):
        """Test select on non-existent file."""
        result = runner.invoke(app, [
            "select", "missing.xlsx",
            "--columns", "id"
        ])

        assert result.exit_code == 1

    def test_select_help(self):
        """Test select command help."""
        result = runner.invoke(app, ["select", "--help"])

        assert result.exit_code == 0
        assert "Select specific columns" in result.stdout
        assert "--columns" in result.stdout
