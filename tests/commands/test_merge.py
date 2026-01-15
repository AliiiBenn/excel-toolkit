"""Unit tests for merge command.

Tests for the merge command that combines files vertically.
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
def file1(tmp_path: Path) -> Path:
    """Create first file for merging."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [100, 200, 300],
        }
    )
    file_path = tmp_path / "file1.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def file2(tmp_path: Path) -> Path:
    """Create second file for merging."""
    df = pd.DataFrame(
        {
            "id": [4, 5, 6],
            "name": ["Diana", "Eve", "Frank"],
            "value": [400, 500, 600],
        }
    )
    file_path = tmp_path / "file2.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def file3(tmp_path: Path) -> Path:
    """Create third file for merging."""
    df = pd.DataFrame(
        {
            "id": [7, 8],
            "name": ["Grace", "Henry"],
            "value": [700, 800],
        }
    )
    file_path = tmp_path / "file3.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def csv_file1(tmp_path: Path) -> Path:
    """Create CSV file for merging."""
    df = pd.DataFrame(
        {
            "product": ["A", "B"],
            "price": [10, 20],
        }
    )
    file_path = tmp_path / "csv1.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def csv_file2(tmp_path: Path) -> Path:
    """Create second CSV file for merging."""
    df = pd.DataFrame(
        {
            "product": ["C", "D"],
            "price": [30, 40],
        }
    )
    file_path = tmp_path / "csv2.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def mismatched_file(tmp_path: Path) -> Path:
    """Create file with different columns."""
    df = pd.DataFrame(
        {
            "id": [1, 2],
            "email": ["test@example.com", "user@example.com"],  # Different column
        }
    )
    file_path = tmp_path / "mismatched.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def empty_file(tmp_path: Path) -> Path:
    """Create an empty DataFrame file with same columns as other files."""
    df = pd.DataFrame(columns=["id", "name", "value"])
    file_path = tmp_path / "empty.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


# =============================================================================
# Merge Command Tests
# =============================================================================


class TestMergeCommand:
    """Tests for the merge command."""

    def test_merge_two_files(self, file1: Path, file2: Path, tmp_path: Path):
        """Test merging two files."""
        output_path = tmp_path / "merged.xlsx"
        result = runner.invoke(app, [
            "merge",
            "--files", f"{file1},{file2}",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Files merged: 2" in result.stdout
        assert "Total rows: 6" in result.stdout
        assert output_path.exists()

    def test_merge_three_files(self, file1: Path, file2: Path, file3: Path, tmp_path: Path):
        """Test merging three files."""
        output_path = tmp_path / "merged.xlsx"
        result = runner.invoke(app, [
            "merge",
            "--files", f"{file1},{file2},{file3}",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Files merged: 3" in result.stdout
        assert "Total rows: 8" in result.stdout

    def test_merge_csv_files(self, csv_file1: Path, csv_file2: Path, tmp_path: Path):
        """Test merging CSV files."""
        output_path = tmp_path / "merged.csv"
        result = runner.invoke(app, [
            "merge",
            "--files", f"{csv_file1},{csv_file2}",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert output_path.exists()

        # Verify output
        df = pd.read_csv(output_path)
        assert len(df) == 4

    def test_merge_with_ignore_index(self, file1: Path, file2: Path, tmp_path: Path):
        """Test merging with index reset."""
        output_path = tmp_path / "merged.xlsx"
        result = runner.invoke(app, [
            "merge",
            "--files", f"{file1},{file2}",
            "--output", str(output_path),
            "--ignore-index"
        ])

        assert result.exit_code == 0
        assert output_path.exists()

    def test_merge_column_mismatch(self, file1: Path, mismatched_file: Path, tmp_path: Path):
        """Test merging files with different columns."""
        output_path = tmp_path / "merged.xlsx"
        result = runner.invoke(app, [
            "merge",
            "--files", f"{file1},{mismatched_file}",
            "--output", str(output_path)
        ])

        assert result.exit_code == 1
        # Error message is displayed
        assert "Column" in result.stdout or "Column" in result.stderr

    def test_merge_with_sheet_parameter(self, file1: Path, file2: Path, tmp_path: Path):
        """Test merging specific sheet."""
        output_path = tmp_path / "merged.xlsx"
        result = runner.invoke(app, [
            "merge",
            "--files", f"{file1},{file2}",
            "--output", str(output_path),
            "--sheet", "Sheet1"
        ])

        assert result.exit_code == 0

    def test_merge_nonexistent_file(self, file1: Path, tmp_path: Path):
        """Test merging with non-existent file."""
        output_path = tmp_path / "merged.xlsx"
        result = runner.invoke(app, [
            "merge",
            "--files", f"{file1},missing.xlsx",
            "--output", str(output_path)
        ])

        assert result.exit_code == 1

    def test_merge_displays_summary(self, file1: Path, file2: Path, tmp_path: Path):
        """Test that merge displays detailed summary."""
        output_path = tmp_path / "merged.xlsx"
        result = runner.invoke(app, [
            "merge",
            "--files", f"{file1},{file2}",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "file1.xlsx: 3 rows" in result.stdout
        assert "file2.xlsx: 3 rows" in result.stdout

    def test_merge_help(self):
        """Test merge command help."""
        result = runner.invoke(app, ["merge", "--help"])

        assert result.exit_code == 0
        assert "Merge multiple files" in result.stdout
        assert "--output" in result.stdout

    def test_merge_empty_files(self, empty_file: Path, file1: Path, tmp_path: Path):
        """Test merging with empty file."""
        output_path = tmp_path / "merged.xlsx"
        result = runner.invoke(app, [
            "merge",
            "--files", f"{empty_file},{file1}",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0

    def test_merge_single_file(self, file1: Path, tmp_path: Path):
        """Test merging a single file (edge case)."""
        output_path = tmp_path / "merged.xlsx"
        result = runner.invoke(app, [
            "merge",
            "--files", str(file1),
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Files merged: 1" in result.stdout
