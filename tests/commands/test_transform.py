"""Unit tests for transform command.

Tests for the transform command that applies transformations to columns.
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
def numeric_data_file(tmp_path: Path) -> Path:
    """Create a file with numeric data."""
    df = pd.DataFrame(
        {
            "price": [10.0, 20.0, 30.0, 40.0, 50.0],
            "quantity": [1, 2, 3, 4, 5],
            "discount": [0.1, 0.15, 0.2, 0.25, 0.3],
        }
    )
    file_path = tmp_path / "numeric.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def string_data_file(tmp_path: Path) -> Path:
    """Create a file with string data."""
    df = pd.DataFrame(
        {
            "name": ["alice smith", "bob jones", "charlie brown"],
            "email": ["ALICE@EXAMPLE.COM", "BOB@EXAMPLE.COM", "CHARLIE@EXAMPLE.COM"],
            "description": ["  Item A  ", "  Item B  ", "  Item C  "],
        }
    )
    file_path = tmp_path / "strings.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def mixed_data_file(tmp_path: Path) -> Path:
    """Create a file with mixed data types."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "value": [100, 200, 300],
            "text": ["A", "B", "C"],
        }
    )
    file_path = tmp_path / "mixed.xlsx"
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
def csv_file_for_transform(tmp_path: Path) -> Path:
    """Create a CSV file for transformation."""
    df = pd.DataFrame(
        {
            "amount": [10, 20, 30],
            "rate": [0.5, 0.6, 0.7],
        }
    )
    file_path = tmp_path / "transform.csv"
    df.to_csv(file_path, index=False)
    return file_path


# =============================================================================
# Transform Command Tests
# =============================================================================


class TestTransformCommand:
    """Tests for the transform command."""

    # Math operations
    def test_transform_multiply(self, numeric_data_file: Path):
        """Test multiply operation."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price",
            "--multiply", "1.1"
        ])

        assert result.exit_code == 0
        assert "Operation: multiply 1.1" in result.stdout

    def test_transform_add(self, numeric_data_file: Path):
        """Test add operation."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price",
            "--add", "10"
        ])

        assert result.exit_code == 0
        assert "Operation: add 10.0" in result.stdout

    def test_transform_subtract(self, numeric_data_file: Path):
        """Test subtract operation."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price",
            "--subtract", "5"
        ])

        assert result.exit_code == 0
        assert "Operation: subtract 5.0" in result.stdout

    def test_transform_divide(self, numeric_data_file: Path):
        """Test divide operation."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price",
            "--divide", "2"
        ])

        assert result.exit_code == 0
        assert "Operation: divide 2.0" in result.stdout

    def test_transform_power(self, numeric_data_file: Path):
        """Test power operation."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "quantity",
            "--power", "2"
        ])

        assert result.exit_code == 0
        assert "Operation: power 2.0" in result.stdout

    def test_transform_mod(self, numeric_data_file: Path):
        """Test modulo operation."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "quantity",
            "--mod", "3"
        ])

        assert result.exit_code == 0
        assert "Operation: mod 3.0" in result.stdout

    # String operations
    def test_transform_uppercase(self, string_data_file: Path):
        """Test uppercase operation."""
        result = runner.invoke(app, [
            "transform", str(string_data_file),
            "--columns", "name",
            "--operation", "uppercase"
        ])

        assert result.exit_code == 0
        assert "Operation: uppercase" in result.stdout

    def test_transform_lowercase(self, string_data_file: Path):
        """Test lowercase operation."""
        result = runner.invoke(app, [
            "transform", str(string_data_file),
            "--columns", "email",
            "--operation", "lowercase"
        ])

        assert result.exit_code == 0
        assert "Operation: lowercase" in result.stdout

    def test_transform_titlecase(self, string_data_file: Path):
        """Test titlecase operation."""
        result = runner.invoke(app, [
            "transform", str(string_data_file),
            "--columns", "name",
            "--operation", "titlecase"
        ])

        assert result.exit_code == 0
        assert "Operation: titlecase" in result.stdout

    def test_transform_strip(self, string_data_file: Path):
        """Test strip operation."""
        result = runner.invoke(app, [
            "transform", str(string_data_file),
            "--columns", "description",
            "--operation", "strip"
        ])

        assert result.exit_code == 0
        assert "Operation: strip" in result.stdout

    def test_transform_length(self, string_data_file: Path):
        """Test length operation."""
        result = runner.invoke(app, [
            "transform", str(string_data_file),
            "--columns", "name",
            "--operation", "length"
        ])

        assert result.exit_code == 0
        assert "Operation: length" in result.stdout

    def test_transform_replace(self, string_data_file: Path):
        """Test replace operation."""
        result = runner.invoke(app, [
            "transform", str(string_data_file),
            "--columns", "name",
            "--operation", "replace",
            "--replace", "Smith,Jones"
        ])

        assert result.exit_code == 0

    def test_transform_multiple_columns(self, numeric_data_file: Path):
        """Test transforming multiple columns."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price,quantity",
            "--multiply", "2"
        ])

        assert result.exit_code == 0
        assert "Transformed 2 column(s)" in result.stdout

    def test_transform_with_output(self, numeric_data_file: Path, tmp_path: Path):
        """Test transform with output file."""
        output_path = tmp_path / "transformed.xlsx"
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price",
            "--multiply", "1.1",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Written to:" in result.stdout
        assert output_path.exists()

    def test_transform_dry_run(self, numeric_data_file: Path):
        """Test dry-run mode."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price",
            "--multiply", "1.1",
            "--dry-run"
        ])

        assert result.exit_code == 0
        assert "Preview" in result.stdout

    def test_transform_csv_input(self, csv_file_for_transform: Path):
        """Test transform from CSV file."""
        result = runner.invoke(app, [
            "transform", str(csv_file_for_transform),
            "--columns", "amount",
            "--multiply", "2"
        ])

        assert result.exit_code == 0

    def test_transform_specific_sheet(self, numeric_data_file: Path):
        """Test transform from specific sheet."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price",
            "--multiply", "1.1",
            "--sheet", "Sheet1"
        ])

        assert result.exit_code == 0

    def test_transform_invalid_column(self, numeric_data_file: Path):
        """Test transform with non-existent column."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "invalid_column",
            "--multiply", "2"
        ])

        assert result.exit_code == 1

    def test_transform_no_transformation(self, numeric_data_file: Path):
        """Test transform without specifying any transformation."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price"
        ])

        assert result.exit_code == 1

    def test_transform_math_and_string_conflict(self, numeric_data_file: Path):
        """Test that math and string operations cannot be combined."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price",
            "--multiply", "2",
            "--operation", "uppercase"
        ])

        assert result.exit_code == 1

    def test_transform_multiple_math_operations(self, numeric_data_file: Path):
        """Test that multiple math operations cannot be combined."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price",
            "--multiply", "2",
            "--add", "10"
        ])

        assert result.exit_code == 1

    def test_transform_invalid_numeric_value(self, numeric_data_file: Path):
        """Test transform with invalid numeric value."""
        result = runner.invoke(app, [
            "transform", str(numeric_data_file),
            "--columns", "price",
            "--multiply", "invalid"
        ])

        assert result.exit_code == 1

    def test_transform_invalid_operation(self, string_data_file: Path):
        """Test transform with invalid string operation."""
        result = runner.invoke(app, [
            "transform", str(string_data_file),
            "--columns", "name",
            "--operation", "invalid"
        ])

        assert result.exit_code == 1

    def test_transform_replace_without_pattern(self, string_data_file: Path):
        """Test replace operation without pattern."""
        result = runner.invoke(app, [
            "transform", str(string_data_file),
            "--columns", "name",
            "--operation", "replace"
        ])

        assert result.exit_code == 1

    def test_transform_empty_file(self, empty_file: Path):
        """Test transform on empty file."""
        result = runner.invoke(app, [
            "transform", str(empty_file),
            "--columns", "price",
            "--multiply", "2"
        ])

        assert result.exit_code == 0
        assert "empty" in result.stdout.lower()

    def test_transform_nonexistent_file(self):
        """Test transform on non-existent file."""
        result = runner.invoke(app, [
            "transform", "missing.xlsx",
            "--columns", "price",
            "--multiply", "2"
        ])

        assert result.exit_code == 1

    def test_transform_help(self):
        """Test transform command help."""
        result = runner.invoke(app, ["transform", "--help"])

        assert result.exit_code == 0
        assert "Apply transformations" in result.stdout
        assert "--multiply" in result.stdout
        assert "--operation" in result.stdout

    def test_transform_non_numeric_column_with_math(self, mixed_data_file: Path):
        """Test math operation on non-numeric column."""
        result = runner.invoke(app, [
            "transform", str(mixed_data_file),
            "--columns", "text",
            "--multiply", "2"
        ])

        assert result.exit_code == 0  # Should succeed with warning
