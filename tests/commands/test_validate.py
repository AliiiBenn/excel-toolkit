"""Unit tests for validate command.

Tests for the validate command that validates data against rules.
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner
import pandas as pd
import json

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
            "email": ["alice@example.com", "bob@example.com", "invalid-email", "diana@example.com", "eve@example.com"],
            "salary": [50000, 60000, 70000, 55000, 65000],
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
            "name": ["Alice", None, "Charlie", "Diana", None],
            "value": [100, 200, None, 400, 500],
        }
    )
    file_path = tmp_path / "nulls.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def file_with_out_of_range(tmp_path: Path) -> Path:
    """Create a file with values out of range."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "age": [25, 150, -5, 35, 200],  # Invalid ages
            "score": [85, 92, 105, 78, -10],  # Invalid scores
        }
    )
    file_path = tmp_path / "out_of_range.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def file_with_duplicates(tmp_path: Path) -> Path:
    """Create a file with duplicate values."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "email": ["alice@example.com", "bob@example.com", "alice@example.com", "diana@example.com", "bob@example.com"],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        }
    )
    file_path = tmp_path / "duplicates.xlsx"
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
def rules_file(tmp_path: Path) -> Path:
    """Create a validation rules file."""
    rules = {
        "age": {
            "type": "int",
            "min": 0,
            "max": 120
        },
        "email": {
            "pattern": "email"
        },
        "salary": {
            "type": "float",
            "min": 0
        }
    }
    file_path = tmp_path / "rules.json"
    with open(file_path, "w") as f:
        json.dump(rules, f)
    return file_path


# =============================================================================
# Validate Command Tests
# =============================================================================


class TestValidateCommand:
    """Tests for the validate command."""

    def test_validate_type_checking(self, sample_data_file: Path):
        """Test basic type validation."""
        result = runner.invoke(app, ["validate", str(sample_data_file), "--rules", "age:int"])

        assert result.exit_code == 0

    def test_validate_range_validation(self, file_with_out_of_range: Path):
        """Test range validation."""
        result = runner.invoke(app, ["validate", str(file_with_out_of_range), "--rules", "age:int:0-120"])

        assert result.exit_code == 1  # Should fail due to out of range values
        assert "Error" in result.stdout or "error" in result.stdout

    def test_validate_email_pattern(self, sample_data_file: Path):
        """Test email pattern validation."""
        result = runner.invoke(app, ["validate", str(sample_data_file), "--rules", "email:email"])

        assert result.exit_code == 1  # Should fail due to invalid email
        assert "pattern" in result.stdout.lower() or "email" in result.stdout.lower()

    def test_validate_required_field(self, file_with_nulls: Path):
        """Test required field validation."""
        result = runner.invoke(app, ["validate", str(file_with_nulls), "--rules", "name:str"])

        # Should pass but show warning for null values
        assert result.exit_code == 0

    def test_validate_unique_constraint(self, file_with_duplicates: Path):
        """Test uniqueness validation."""
        result = runner.invoke(app, ["validate", str(file_with_duplicates), "--rules", "email:unique"])

        assert result.exit_code == 1  # Should fail due to duplicates
        assert "duplicate" in result.stdout.lower()

    def test_validate_multiple_columns(self, sample_data_file: Path):
        """Test validation of multiple columns."""
        result = runner.invoke(app, [
            "validate", str(sample_data_file),
            "--rules", "age:int:0-100;email:email"
        ])

        assert result.exit_code == 1  # Should fail due to invalid email

    def test_validate_with_rules_file(self, sample_data_file: Path, rules_file: Path):
        """Test validation with rules file."""
        result = runner.invoke(app, [
            "validate", str(sample_data_file),
            "--rules-file", str(rules_file)
        ])

        assert result.exit_code == 1  # Should fail due to invalid email

    def test_validate_specific_columns(self, sample_data_file: Path):
        """Test validation of specific columns only."""
        result = runner.invoke(app, [
            "validate", str(sample_data_file),
            "--columns", "age",
            "--rules", "age:int:0-100"
        ])

        assert result.exit_code == 0

    def test_validate_wildcard(self, sample_data_file: Path):
        """Test validation with wildcard rule."""
        result = runner.invoke(app, [
            "validate", str(sample_data_file),
            "--rules", "*"
        ])

        # Should validate all columns with basic validation
        assert result.exit_code == 0

    def test_validate_with_output(self, sample_data_file: Path, tmp_path: Path):
        """Test validation with JSON report output."""
        output_path = tmp_path / "report.json"
        result = runner.invoke(app, [
            "validate", str(sample_data_file),
            "--rules", "age:int",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Report written to:" in result.stdout
        assert output_path.exists()

        # Verify report structure
        with open(output_path, "r") as f:
            report = json.load(f)
        assert "file" in report
        assert "total_errors" in report
        assert "total_warnings" in report

    def test_validate_fail_fast(self, file_with_out_of_range: Path):
        """Test fail-fast mode."""
        result = runner.invoke(app, [
            "validate", str(file_with_out_of_range),
            "--rules", "age:int:0-120;score:int:0-100",
            "--fail-fast"
        ])

        assert result.exit_code == 1

    def test_validate_empty_file(self, empty_file: Path):
        """Test validation on empty file."""
        result = runner.invoke(app, ["validate", str(empty_file), "--rules", "value:int"])

        assert result.exit_code == 0
        assert "empty" in result.stdout.lower()

    def test_validate_nonexistent_file(self):
        """Test validation on non-existent file."""
        result = runner.invoke(app, ["validate", "missing.xlsx", "--rules", "age:int"])

        assert result.exit_code == 1

    def test_validate_no_rules(self, sample_data_file: Path):
        """Test validation without specifying rules."""
        result = runner.invoke(app, ["validate", str(sample_data_file)])

        assert result.exit_code == 1

    def test_validate_both_rules_and_file(self, sample_data_file: Path, rules_file: Path):
        """Test that both --rules and --rules-file cannot be specified."""
        result = runner.invoke(app, [
            "validate", str(sample_data_file),
            "--rules", "age:int",
            "--rules-file", str(rules_file)
        ])

        assert result.exit_code == 1

    def test_validate_invalid_rules_file(self, sample_data_file: Path, tmp_path: Path):
        """Test with non-existent rules file."""
        result = runner.invoke(app, [
            "validate", str(sample_data_file),
            "--rules-file", "nonexistent.json"
        ])

        assert result.exit_code == 1

    def test_validate_invalid_column(self, sample_data_file: Path):
        """Test validation with non-existent column."""
        result = runner.invoke(app, [
            "validate", str(sample_data_file),
            "--columns", "nonexistent",
            "--rules", "nonexistent:int"
        ])

        assert result.exit_code == 1

    def test_validate_csv_input(self, tmp_path: Path):
        """Test validation of CSV file."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "age": [25, 30, 35]
        })
        file_path = tmp_path / "data.csv"
        df.to_csv(file_path, index=False)

        result = runner.invoke(app, ["validate", str(file_path), "--rules", "age:int"])

        assert result.exit_code == 0

    def test_validate_specific_sheet(self, sample_data_file: Path):
        """Test validation of specific sheet."""
        result = runner.invoke(app, [
            "validate", str(sample_data_file),
            "--rules", "age:int",
            "--sheet", "Sheet1"
        ])

        assert result.exit_code == 0

    def test_validate_all_warnings(self, file_with_nulls: Path):
        """Test validation with only warnings (no errors)."""
        result = runner.invoke(app, [
            "validate", str(file_with_nulls),
            "--rules", "value:int"
        ])

        # Should pass (exit code 0) but show warnings
        assert result.exit_code == 0
        assert "Warning" in result.stdout or "warning" in result.stdout

    def test_validate_help(self):
        """Test validate command help."""
        result = runner.invoke(app, ["validate", "--help"])

        assert result.exit_code == 0
        assert "Validate data" in result.stdout
        assert "--rules" in result.stdout
