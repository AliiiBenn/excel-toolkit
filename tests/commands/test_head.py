"""Unit tests for head command.

Tests for the head command that displays the first N rows of data files.
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
def sample_excel_file(tmp_path: Path) -> Path:
    """Create a sample Excel file for testing."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "name": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
            "value": [10.5, 20.3, 30.1, 40.9, 50.7, 60.5, 70.3, 80.1, 90.9, 100.7],
        }
    )
    file_path = tmp_path / "test.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def multi_sheet_excel_file(tmp_path: Path) -> Path:
    """Create an Excel file with multiple sheets."""
    df1 = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    df2 = pd.DataFrame({"x": [10, 20], "y": [30, 40]})

    file_path = tmp_path / "multi.xlsx"
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df1.to_excel(writer, sheet_name="Data", index=False)
        df2.to_excel(writer, sheet_name="Summary", index=False)
    return file_path


@pytest.fixture
def sample_csv_file(tmp_path: Path) -> Path:
    """Create a sample CSV file for testing."""
    df = pd.DataFrame(
        {
            "product": ["A", "B", "C", "D", "E", "F", "G"],
            "price": [10.5, 20.0, 15.3, 25.0, 30.5, 40.0, 35.3],
            "stock": [100, 50, 75, 120, 90, 60, 80],
        }
    )
    file_path = tmp_path / "test.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def empty_file(tmp_path: Path) -> Path:
    """Create an empty DataFrame file."""
    df = pd.DataFrame()
    file_path = tmp_path / "empty.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def single_row_file(tmp_path: Path) -> Path:
    """Create a file with only one row."""
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
    file_path = tmp_path / "single.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def wide_dataframe_file(tmp_path: Path) -> Path:
    """Create a file with many columns."""
    df = pd.DataFrame({f"col_{i}": [1, 2, 3] for i in range(20)})
    file_path = tmp_path / "wide.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


# =============================================================================
# Head Command Tests
# =============================================================================


class TestHeadCommand:
    """Tests for the head command."""

    def test_head_default_5_rows(self, sample_excel_file: Path):
        """Test default shows 5 rows."""
        result = runner.invoke(app, ["head", str(sample_excel_file)])

        assert result.exit_code == 0
        assert "File: test.xlsx" in result.stdout
        assert "10 rows x 3 columns" in result.stdout
        # Should have table output
        assert "+" in result.stdout or "|" in result.stdout

    def test_head_custom_rows(self, sample_excel_file: Path):
        """Test custom number of rows."""
        result = runner.invoke(app, ["head", str(sample_excel_file), "--rows", "3"])

        assert result.exit_code == 0
        assert "Showing data (10 rows x 3 columns)" in result.stdout

    def test_head_specific_sheet(self, multi_sheet_excel_file: Path):
        """Test reading specific Excel sheet."""
        result = runner.invoke(app, ["head", str(multi_sheet_excel_file), "--sheet", "Summary"])

        assert result.exit_code == 0
        assert "Sheet: Summary" in result.stdout

    def test_head_with_column_types(self, sample_excel_file: Path):
        """Test showing column types."""
        result = runner.invoke(app, ["head", str(sample_excel_file), "--show-columns"])

        assert result.exit_code == 0
        assert "Columns:" in result.stdout
        assert "id (int64)" in result.stdout or "id (int" in result.stdout
        assert "name (object)" in result.stdout

    def test_head_max_columns(self, wide_dataframe_file: Path):
        """Test limiting columns displayed."""
        result = runner.invoke(app, ["head", str(wide_dataframe_file), "--max-columns", "5"])

        assert result.exit_code == 0

    def test_head_csv_format(self, sample_excel_file: Path):
        """Test CSV output format."""
        result = runner.invoke(app, ["head", str(sample_excel_file), "--format", "csv", "--rows", "3"])

        assert result.exit_code == 0
        # CSV output should have commas
        assert "," in result.stdout or "id,name,value" in result.stdout

    def test_head_json_format(self, sample_excel_file: Path):
        """Test JSON output format."""
        result = runner.invoke(app, ["head", str(sample_excel_file), "--format", "json", "--rows", "2"])

        assert result.exit_code == 0
        # JSON output should have brackets
        assert "[" in result.stdout or "{" in result.stdout

    def test_head_empty_file(self, empty_file: Path):
        """Test head on empty file."""
        result = runner.invoke(app, ["head", str(empty_file)])

        assert result.exit_code == 0
        assert "File is empty" in result.stdout

    def test_head_single_row(self, single_row_file: Path):
        """Test head when file has only 1 row."""
        result = runner.invoke(app, ["head", str(single_row_file)])

        assert result.exit_code == 0
        assert "Showing data (1 row" in result.stdout or "1 rows" in result.stdout

    def test_head_fewer_rows_than_requested(self, single_row_file: Path):
        """Test when requesting more rows than available."""
        result = runner.invoke(app, ["head", str(single_row_file), "--rows", "10"])

        assert result.exit_code == 0
        # Should still work, just show 1 row
        assert "1 row" in result.stdout or "1 rows" in result.stdout

    def test_head_csv_file(self, sample_csv_file: Path):
        """Test head on CSV file."""
        result = runner.invoke(app, ["head", str(sample_csv_file)])

        assert result.exit_code == 0
        assert "File: test.csv" in result.stdout

    def test_head_nonexistent_file(self):
        """Test head on non-existent file."""
        result = runner.invoke(app, ["head", "missing.xlsx"])

        assert result.exit_code == 1

    def test_head_invalid_format(self, sample_excel_file: Path):
        """Test head with invalid format."""
        result = runner.invoke(app, ["head", str(sample_excel_file), "--format", "xml"])

        assert result.exit_code == 1
        assert "Unknown format" in result.stdout or "Supported formats" in result.stdout

    def test_head_help(self):
        """Test head command help."""
        result = runner.invoke(app, ["head", "--help"])

        assert result.exit_code == 0
        assert "Display the first N rows" in result.stdout
        assert "rows" in result.stdout
        assert "sheet" in result.stdout
        assert "format" in result.stdout

    def test_head_combined_options(self, sample_excel_file: Path):
        """Test combining multiple options."""
        result = runner.invoke(
            app, ["head", str(sample_excel_file), "--rows", "3", "--show-columns", "--format", "table"]
        )

        assert result.exit_code == 0
        assert "Columns:" in result.stdout

    def test_head_wide_dataframe_no_limit(self, wide_dataframe_file: Path):
        """Test wide dataframe without column limit."""
        result = runner.invoke(app, ["head", str(wide_dataframe_file), "--rows", "2"])

        assert result.exit_code == 0
        assert "20 columns" in result.stdout
