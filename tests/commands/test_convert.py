"""Unit tests for convert command.

Tests for the convert command that converts file formats.
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
def excel_file(tmp_path: Path) -> Path:
    """Create an Excel file for conversion."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [100, 200, 300],
        }
    )
    file_path = tmp_path / "data.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def csv_file(tmp_path: Path) -> Path:
    """Create a CSV file for conversion."""
    df = pd.DataFrame(
        {
            "product": ["A", "B", "C"],
            "price": [10.5, 20.0, 15.75],
        }
    )
    file_path = tmp_path / "data.csv"
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
# Convert Command Tests
# =============================================================================


class TestConvertCommand:
    """Tests for the convert command."""

    def test_convert_excel_to_csv(self, excel_file: Path, tmp_path: Path):
        """Test converting Excel to CSV."""
        output_path = tmp_path / "converted.csv"
        result = runner.invoke(app, [
            "convert", str(excel_file),
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Written to:" in result.stdout
        assert output_path.exists()

        # Verify output
        df = pd.read_csv(output_path)
        assert len(df) == 3

    def test_convert_csv_to_excel(self, csv_file: Path, tmp_path: Path):
        """Test converting CSV to Excel."""
        output_path = tmp_path / "converted.xlsx"
        result = runner.invoke(app, [
            "convert", str(csv_file),
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Written to:" in result.stdout
        assert output_path.exists()

        # Verify output
        df = pd.read_excel(output_path)
        assert len(df) == 3

    def test_convert_excel_to_json(self, excel_file: Path, tmp_path: Path):
        """Test converting Excel to JSON."""
        output_path = tmp_path / "converted.json"
        result = runner.invoke(app, [
            "convert", str(excel_file),
            "--output", str(output_path)
        ])

        # JSON not supported yet, should fail gracefully
        assert result.exit_code != 0

    def test_convert_csv_to_json(self, csv_file: Path, tmp_path: Path):
        """Test converting CSV to JSON."""
        output_path = tmp_path / "converted.json"
        result = runner.invoke(app, [
            "convert", str(csv_file),
            "--output", str(output_path)
        ])

        # JSON not supported yet, should fail gracefully
        assert result.exit_code != 0

    def test_convert_preserves_data(self, excel_file: Path, tmp_path: Path):
        """Test that conversion preserves data correctly."""
        output_path = tmp_path / "converted.csv"
        result = runner.invoke(app, [
            "convert", str(excel_file),
            "--output", str(output_path)
        ])

        assert result.exit_code == 0

        # Read both files and compare
        df_original = pd.read_excel(excel_file)
        df_converted = pd.read_csv(output_path)

        pd.testing.assert_frame_equal(df_original, df_converted)

    def test_convert_with_sheet_parameter(self, excel_file: Path, tmp_path: Path):
        """Test converting specific sheet."""
        output_path = tmp_path / "converted.csv"
        result = runner.invoke(app, [
            "convert", str(excel_file),
            "--output", str(output_path),
            "--sheet", "Sheet1"
        ])

        assert result.exit_code == 0

    def test_convert_unsupported_format(self, excel_file: Path, tmp_path: Path):
        """Test converting to unsupported format."""
        output_path = tmp_path / "converted.txt"
        result = runner.invoke(app, [
            "convert", str(excel_file),
            "--output", str(output_path)
        ])

        assert result.exit_code == 1

    def test_convert_nonexistent_file(self, tmp_path: Path):
        """Test converting non-existent file."""
        output_path = tmp_path / "output.xlsx"
        result = runner.invoke(app, [
            "convert", "missing.xlsx",
            "--output", str(output_path)
        ])

        assert result.exit_code == 1

    def test_convert_empty_file(self, empty_file: Path, tmp_path: Path):
        """Test converting empty file."""
        output_path = tmp_path / "output.csv"
        result = runner.invoke(app, [
            "convert", str(empty_file),
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        # Should show warning about empty file

    def test_convert_help(self):
        """Test convert command help."""
        result = runner.invoke(app, ["convert", "--help"])

        assert result.exit_code == 0
        assert "Convert between" in result.stdout
        assert "--output" in result.stdout

    def test_convert_displays_summary(self, excel_file: Path, tmp_path: Path):
        """Test that convert displays format summary."""
        output_path = tmp_path / "converted.csv"
        result = runner.invoke(app, [
            "convert", str(excel_file),
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Input format:" in result.stdout
        assert "Output format:" in result.stdout
        assert "Rows:" in result.stdout
        assert "Columns:" in result.stdout
