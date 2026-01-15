"""Unit tests for info command.

Tests for the info command that displays file metadata.
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner
import pandas as pd

from excel_toolkit.cli import app
from excel_toolkit.commands.info import (
    _get_file_type,
    _format_size,
    _delimiter_name,
)

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
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["Paris", "London", "Berlin"],
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
    df = pd.DataFrame({"product": ["A", "B", "C"], "price": [10.5, 20.0, 15.3], "stock": [100, 50, 75]})
    file_path = tmp_path / "test.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def csv_with_semicolon(tmp_path: Path) -> Path:
    """Create a CSV file with semicolon delimiter."""
    file_path = tmp_path / "semicolon.csv"
    file_path.write_text("product;price;stock\nA;10.5;100\nB;20.0;50", encoding="utf-8")
    return file_path


# =============================================================================
# Info Command Tests
# =============================================================================


class TestInfoCommand:
    """Tests for the info command."""

    def test_info_excel_file(self, sample_excel_file: Path):
        """Test info command on Excel file."""
        result = runner.invoke(app, ["info", str(sample_excel_file)])

        assert result.exit_code == 0
        assert "File: test.xlsx" in result.stdout
        assert "Type: Excel" in result.stdout
        assert "Size:" in result.stdout
        assert "Sheets" in result.stdout
        assert "Sheet1:" in result.stdout
        assert "3 rows" in result.stdout
        assert "3 columns" in result.stdout

    def test_info_multi_sheet_excel(self, multi_sheet_excel_file: Path):
        """Test info command on multi-sheet Excel file."""
        result = runner.invoke(app, ["info", str(multi_sheet_excel_file)])

        assert result.exit_code == 0
        assert "File: multi.xlsx" in result.stdout
        assert "Sheets (2):" in result.stdout
        assert "Data:" in result.stdout
        assert "Summary:" in result.stdout
        assert "3 rows" in result.stdout
        assert "2 rows" in result.stdout

    def test_info_csv_file(self, sample_csv_file: Path):
        """Test info command on CSV file."""
        result = runner.invoke(app, ["info", str(sample_csv_file)])

        assert result.exit_code == 0
        assert "File: test.csv" in result.stdout
        assert "Type: CSV" in result.stdout
        assert "Size:" in result.stdout
        assert "Encoding:" in result.stdout
        assert "Delimiter:" in result.stdout

    def test_info_csv_with_semicolon(self, csv_with_semicolon: Path):
        """Test info command detects semicolon delimiter."""
        result = runner.invoke(app, ["info", str(csv_with_semicolon)])

        assert result.exit_code == 0
        assert "Delimiter: semicolon" in result.stdout

    def test_info_nonexistent_file(self):
        """Test info command on non-existent file."""
        result = runner.invoke(app, ["info", "missing.xlsx"])

        assert result.exit_code == 1

    def test_info_unsupported_format(self, tmp_path: Path):
        """Test info command on unsupported format."""
        file_path = tmp_path / "data.json"
        file_path.write_text('{"key": "value"}')

        result = runner.invoke(app, ["info", str(file_path)])

        assert result.exit_code == 1
        assert "Supported formats" in result.stdout

    def test_info_verbose_excel(self, sample_excel_file: Path):
        """Test info command with verbose flag on Excel file."""
        result = runner.invoke(app, ["info", str(sample_excel_file), "--verbose"])

        assert result.exit_code == 0
        assert "File: test.xlsx" in result.stdout
        assert "Columns:" in result.stdout
        assert "name, age, city" in result.stdout

    def test_info_verbose_csv(self, sample_csv_file: Path):
        """Test info command with verbose flag on CSV file."""
        result = runner.invoke(app, ["info", str(sample_csv_file), "--verbose"])

        assert result.exit_code == 0
        assert "Rows:" in result.stdout
        assert "Columns:" in result.stdout
        assert "Column names:" in result.stdout

    def test_info_help(self):
        """Test info command help."""
        result = runner.invoke(app, ["info", "--help"])

        assert result.exit_code == 0
        assert "Display information about a data file" in result.stdout
        assert "file_path" in result.stdout
        assert "verbose" in result.stdout


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestHelperFunctions:
    """Tests for helper functions in info module."""

    def test_get_file_type_xlsx(self):
        """Test file type detection for .xlsx files."""
        assert "Excel" in _get_file_type(Path("data.xlsx"))

    def test_get_file_type_xls(self):
        """Test file type detection for .xls files."""
        assert "Excel" in _get_file_type(Path("data.xls"))

    def test_get_file_type_csv(self):
        """Test file type detection for .csv files."""
        assert _get_file_type(Path("data.csv")) == "CSV"

    def test_get_file_type_unknown(self):
        """Test file type detection for unknown formats."""
        assert _get_file_type(Path("data.json")) == "Unknown"

    def test_format_size_bytes(self):
        """Test size formatting for bytes."""
        assert "KB" in _format_size(512)
        assert "0.5" in _format_size(512)

    def test_format_size_kilobytes(self):
        """Test size formatting for kilobytes."""
        assert "KB" in _format_size(1024 * 5)
        assert "5.0" in _format_size(1024 * 5)

    def test_format_size_megabytes(self):
        """Test size formatting for megabytes."""
        assert "MB" in _format_size(1024 * 1024 * 2)
        assert "2.0" in _format_size(1024 * 1024 * 2)

    def test_delimiter_name_comma(self):
        """Test delimiter name for comma."""
        assert _delimiter_name(",") == "comma (,)"

    def test_delimiter_name_semicolon(self):
        """Test delimiter name for semicolon."""
        assert _delimiter_name(";") == "semicolon (;)"

    def test_delimiter_name_tab(self):
        """Test delimiter name for tab."""
        assert _delimiter_name("\t") == "tab"

    def test_delimiter_name_pipe(self):
        """Test delimiter name for pipe."""
        assert _delimiter_name("|") == "pipe (|)"

    def test_delimiter_name_unknown(self):
        """Test delimiter name for unknown delimiter."""
        assert _delimiter_name(":") == ":"
