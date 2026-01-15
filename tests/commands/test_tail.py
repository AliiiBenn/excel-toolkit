"""Unit tests for tail command.

Tests for the tail command that displays the last N rows.
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
    """Create a sample data file with multiple rows."""
    df = pd.DataFrame(
        {
            "id": range(1, 21),
            "name": [f"Person{i}" for i in range(1, 21)],
            "value": [i * 10 for i in range(1, 21)],
        }
    )
    file_path = tmp_path / "data.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def csv_file_for_tail(tmp_path: Path) -> Path:
    """Create a CSV file for tail testing."""
    df = pd.DataFrame(
        {
            "product": ["A", "B", "C", "D", "E"],
            "price": [10, 20, 30, 40, 50],
        }
    )
    file_path = tmp_path / "tail.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def empty_file(tmp_path: Path) -> Path:
    """Create an empty DataFrame file."""
    df = pd.DataFrame()
    file_path = tmp_path / "empty.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


# =============================================================================
# Tail Command Tests
# =============================================================================


class TestTailCommand:
    """Tests for the tail command."""

    def test_tail_default_rows(self, sample_data_file: Path):
        """Test tail with default number of rows."""
        result = runner.invoke(app, ["tail", str(sample_data_file)])

        assert result.exit_code == 0

    def test_tail_custom_rows(self, sample_data_file: Path):
        """Test tail with custom number of rows."""
        result = runner.invoke(app, ["tail", str(sample_data_file), "--rows", "10"])

        assert result.exit_code == 0

    def test_tail_all_rows(self, sample_data_file: Path):
        """Test tail showing more rows than available."""
        result = runner.invoke(app, ["tail", str(sample_data_file), "--rows", "100"])

        assert result.exit_code == 0

    def test_tail_csv_input(self, csv_file_for_tail: Path):
        """Test tail from CSV file."""
        result = runner.invoke(app, ["tail", str(csv_file_for_tail)])

        assert result.exit_code == 0

    def test_tail_specific_sheet(self, sample_data_file: Path):
        """Test tail from specific sheet."""
        result = runner.invoke(app, [
            "tail", str(sample_data_file),
            "--sheet", "Sheet1"
        ])

        assert result.exit_code == 0

    def test_tail_show_columns(self, sample_data_file: Path):
        """Test tail showing column information."""
        result = runner.invoke(app, [
            "tail", str(sample_data_file),
            "--show-columns"
        ])

        assert result.exit_code == 0

    def test_tail_max_columns(self, sample_data_file: Path):
        """Test tail with limited columns."""
        result = runner.invoke(app, [
            "tail", str(sample_data_file),
            "--max-columns", "2"
        ])

        assert result.exit_code == 0

    def test_tail_format_csv(self, sample_data_file: Path):
        """Test tail with CSV output format."""
        result = runner.invoke(app, [
            "tail", str(sample_data_file),
            "--format", "csv"
        ])

        assert result.exit_code == 0

    def test_tail_format_json(self, sample_data_file: Path):
        """Test tail with JSON output format."""
        result = runner.invoke(app, [
            "tail", str(sample_data_file),
            "--format", "json"
        ])

        assert result.exit_code == 0

    def test_tail_invalid_format(self, sample_data_file: Path):
        """Test tail with invalid format."""
        result = runner.invoke(app, [
            "tail", str(sample_data_file),
            "--format", "invalid"
        ])

        assert result.exit_code == 1

    def test_tail_empty_file(self, empty_file: Path):
        """Test tail on empty file."""
        result = runner.invoke(app, ["tail", str(empty_file)])

        assert result.exit_code == 0
        assert "empty" in result.stdout.lower()

    def test_tail_nonexistent_file(self):
        """Test tail on non-existent file."""
        result = runner.invoke(app, ["tail", "missing.xlsx"])

        assert result.exit_code == 1

    def test_tail_help(self):
        """Test tail command help."""
        result = runner.invoke(app, ["tail", "--help"])

        assert result.exit_code == 0
        assert "last N rows" in result.stdout
        assert "--rows" in result.stdout
