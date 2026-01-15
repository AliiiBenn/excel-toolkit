"""Unit tests for rename command.

Tests for the rename command that renames columns.
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
    """Create a sample data file."""
    df = pd.DataFrame(
        {
            "old_name": ["Alice", "Bob", "Charlie"],
            "first_name": ["Smith", "Jones", "Brown"],
            "id": [1, 2, 3],
            "value": [100, 200, 300],
        }
    )
    file_path = tmp_path / "data.xlsx"
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
def csv_file_for_rename(tmp_path: Path) -> Path:
    """Create a CSV file for renaming."""
    df = pd.DataFrame(
        {
            "col1": ["A", "B", "C"],
            "col2": [1, 2, 3],
        }
    )
    file_path = tmp_path / "rename.csv"
    df.to_csv(file_path, index=False)
    return file_path


# =============================================================================
# Rename Command Tests
# =============================================================================


class TestRenameCommand:
    """Tests for the rename command."""

    def test_rename_single_column(self, sample_data_file: Path):
        """Test renaming a single column."""
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "old_name:new_name"
        ])

        assert result.exit_code == 0
        assert "Renamed 1 column(s)" in result.stdout
        assert "old_name -> new_name" in result.stdout

    def test_rename_multiple_columns(self, sample_data_file: Path):
        """Test renaming multiple columns."""
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "old_name:new_name,first_name:fname"
        ])

        assert result.exit_code == 0
        assert "Renamed 2 column(s)" in result.stdout

    def test_rename_with_output(self, sample_data_file: Path, tmp_path: Path):
        """Test rename with output file."""
        output_path = tmp_path / "renamed.xlsx"
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "old_name:new_name",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Written to:" in result.stdout
        assert output_path.exists()

    def test_rename_dry_run(self, sample_data_file: Path):
        """Test dry-run mode."""
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "old_name:new_name",
            "--dry-run"
        ])

        assert result.exit_code == 0
        assert "Preview" in result.stdout

    def test_rename_csv_input(self, csv_file_for_rename: Path):
        """Test rename from CSV file."""
        result = runner.invoke(app, [
            "rename", str(csv_file_for_rename),
            "--mapping", "col1:column1,col2:column2"
        ])

        assert result.exit_code == 0
        assert "Renamed 2 column(s)" in result.stdout

    def test_rename_specific_sheet(self, sample_data_file: Path):
        """Test rename from specific sheet."""
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "old_name:new_name",
            "--sheet", "Sheet1"
        ])

        assert result.exit_code == 0

    def test_rename_invalid_old_column(self, sample_data_file: Path):
        """Test rename with non-existent old column."""
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "invalid_column:new_name"
        ])

        assert result.exit_code == 1

    def test_rename_no_mapping(self, sample_data_file: Path):
        """Test rename without specifying mapping."""
        result = runner.invoke(app, ["rename", str(sample_data_file)])

        # Typer returns exit code 2 for missing required parameter
        assert result.exit_code != 0

    def test_rename_invalid_format(self, sample_data_file: Path):
        """Test rename with invalid mapping format."""
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "invalid_format"
        ])

        assert result.exit_code == 1

    def test_rename_duplicate_old_column(self, sample_data_file: Path):
        """Test rename with duplicate old column names."""
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "old_name:new1,old_name:new2"
        ])

        assert result.exit_code == 1

    def test_rename_empty_name_in_mapping(self, sample_data_file: Path):
        """Test rename with empty name in mapping."""
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "old_name:,first_name:fname"
        ])

        assert result.exit_code == 1

    def test_rename_conflict_with_existing_column(self, sample_data_file: Path):
        """Test rename that conflicts with existing column."""
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "old_name:value"
        ])

        assert result.exit_code == 1

    def test_rename_empty_file(self, empty_file: Path):
        """Test rename on empty file."""
        result = runner.invoke(app, [
            "rename", str(empty_file),
            "--mapping", "col:new_col"
        ])

        assert result.exit_code == 0
        assert "empty" in result.stdout.lower()

    def test_rename_nonexistent_file(self):
        """Test rename on non-existent file."""
        result = runner.invoke(app, [
            "rename", "missing.xlsx",
            "--mapping", "old:new"
        ])

        assert result.exit_code == 1

    def test_rename_help(self):
        """Test rename command help."""
        result = runner.invoke(app, ["rename", "--help"])

        assert result.exit_code == 0
        assert "Rename columns" in result.stdout
        assert "--mapping" in result.stdout

    def test_rename_with_spaces_in_mapping(self, sample_data_file: Path):
        """Test rename with spaces in mapping."""
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "old_name : new_name , first_name : fname"
        ])

        assert result.exit_code == 0
        assert "Renamed 2 column(s)" in result.stdout

    def test_rename_preserve_data(self, sample_data_file: Path, tmp_path: Path):
        """Test that rename preserves data correctly."""
        output_path = tmp_path / "renamed.xlsx"
        result = runner.invoke(app, [
            "rename", str(sample_data_file),
            "--mapping", "old_name:name",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0

        # Verify the output has correct data
        df_output = pd.read_excel(output_path)
        assert "name" in df_output.columns
        assert "old_name" not in df_output.columns
        assert len(df_output) == 3  # All rows preserved
