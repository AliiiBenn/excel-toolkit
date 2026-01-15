"""Unit tests for search command.

Tests for the search command that searches for patterns.
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
    """Create a sample data file with various values."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "status": ["active", "inactive", "ERROR", "active", "error"],
            "message": ["OK", "Warning", "ERROR: Failed", "OK", "Error: Invalid"],
        }
    )
    file_path = tmp_path / "data.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def csv_file_for_search(tmp_path: Path) -> Path:
    """Create a CSV file for searching."""
    df = pd.DataFrame(
        {
            "product": ["A", "B", "C", "D"],
            "category": ["Electronics", "Books", "Electronics", "Books"],
        }
    )
    file_path = tmp_path / "search.csv"
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
# Search Command Tests
# =============================================================================


class TestSearchCommand:
    """Tests for the search command."""

    def test_search_literal_pattern(self, sample_data_file: Path):
        """Test searching for literal pattern."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "ERROR"
        ])

        assert result.exit_code == 0
        assert "Matches found:" in result.stdout

    def test_search_in_specific_column(self, sample_data_file: Path):
        """Test searching in specific column."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "active",
            "--columns", "status"
        ])

        assert result.exit_code == 0
        assert "Columns: status" in result.stdout

    def test_search_multiple_columns(self, sample_data_file: Path):
        """Test searching in multiple columns."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "OK",
            "--columns", "status,message"
        ])

        assert result.exit_code == 0

    def test_search_case_sensitive(self, sample_data_file: Path):
        """Test case-sensitive search."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "ERROR",
            "--case-sensitive"
        ])

        assert result.exit_code == 0

    def test_search_case_insensitive_default(self, sample_data_file: Path):
        """Test case-insensitive search (default)."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "error"
        ])

        assert result.exit_code == 0
        # Should find both "ERROR" and "error"

    def test_search_regex_pattern(self, sample_data_file: Path):
        """Test searching with regex pattern."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "^A",
            "--regex",
            "--columns", "name"
        ])

        assert result.exit_code == 0
        # Should find "Alice"

    def test_search_regex_or_pattern(self, sample_data_file: Path):
        """Test regex with OR pattern."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "ERROR|error",
            "--regex"
        ])

        assert result.exit_code == 0

    def test_search_no_matches(self, sample_data_file: Path):
        """Test search with no matches."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "NOTFOUND"
        ])

        assert result.exit_code == 0
        assert "No matches found" in result.stdout

    def test_search_with_output(self, sample_data_file: Path, tmp_path: Path):
        """Test search with output file."""
        output_path = tmp_path / "search_results.xlsx"
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "OK",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Written to:" in result.stdout
        assert output_path.exists()

    def test_search_csv_input(self, csv_file_for_search: Path):
        """Test search from CSV file."""
        result = runner.invoke(app, [
            "search", str(csv_file_for_search),
            "--pattern", "Electronics"
        ])

        assert result.exit_code == 0
        assert "Matches found:" in result.stdout

    def test_search_specific_sheet(self, sample_data_file: Path):
        """Test search from specific sheet."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "OK",
            "--sheet", "Sheet1"
        ])

        assert result.exit_code == 0

    def test_search_invalid_column(self, sample_data_file: Path):
        """Test search with non-existent column."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "test",
            "--columns", "invalid_column"
        ])

        assert result.exit_code == 1

    def test_search_invalid_regex(self, sample_data_file: Path):
        """Test search with invalid regex."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "[invalid",
            "--regex"
        ])

        assert result.exit_code == 1

    def test_search_empty_file(self, empty_file: Path):
        """Test search on empty file."""
        result = runner.invoke(app, [
            "search", str(empty_file),
            "--pattern", "test"
        ])

        assert result.exit_code == 0
        assert "empty" in result.stdout.lower()

    def test_search_nonexistent_file(self):
        """Test search on non-existent file."""
        result = runner.invoke(app, [
            "search", "missing.xlsx",
            "--pattern", "test"
        ])

        assert result.exit_code == 1

    def test_search_help(self):
        """Test search command help."""
        result = runner.invoke(app, ["search", "--help"])

        assert result.exit_code == 0
        assert "Search for patterns" in result.stdout
        assert "--pattern" in result.stdout

    def test_search_default_all_columns(self, sample_data_file: Path):
        """Test that search defaults to all columns."""
        result = runner.invoke(app, [
            "search", str(sample_data_file),
            "--pattern", "ERROR"
        ])

        assert result.exit_code == 0
        assert "Columns: all columns" in result.stdout
