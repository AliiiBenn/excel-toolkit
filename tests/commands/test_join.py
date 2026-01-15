"""Unit tests for join command.

Tests for the join command that joins two datasets.
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
def left_file(tmp_path: Path) -> Path:
    """Create left file for joining."""
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4],
            "customer_name": ["Alice", "Bob", "Charlie", "Diana"],
            "email": ["alice@example.com", "bob@example.com", "charlie@example.com", "diana@example.com"],
        }
    )
    file_path = tmp_path / "left.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def right_file(tmp_path: Path) -> Path:
    """Create right file for joining."""
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 5],
            "order_id": [101, 102, 103, 104],
            "amount": [500, 300, 750, 200],
        }
    )
    file_path = tmp_path / "right.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def different_keys_file(tmp_path: Path) -> Path:
    """Create file with different key column name."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 5, 6],
            "product": ["A", "B", "C", "D"],
            "price": [10, 20, 30, 40],
        }
    )
    file_path = tmp_path / "different_keys.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def csv_left_file(tmp_path: Path) -> Path:
    """Create CSV left file for joining."""
    df = pd.DataFrame(
        {
            "user_id": [1, 2, 3],
            "username": ["alice", "bob", "charlie"],
        }
    )
    file_path = tmp_path / "left.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def csv_right_file(tmp_path: Path) -> Path:
    """Create CSV right file for joining."""
    df = pd.DataFrame(
        {
            "user_id": [1, 2, 4],
            "score": [85, 90, 75],
        }
    )
    file_path = tmp_path / "right.csv"
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
# Join Command Tests
# =============================================================================


class TestJoinCommand:
    """Tests for the join command."""

    def test_join_inner_default(self, left_file: Path, right_file: Path, tmp_path: Path):
        """Test inner join (default)."""
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file),
            "--on", "customer_id"
        ])

        assert result.exit_code == 0
        assert "Join type: inner" in result.stdout
        assert "Joined rows: 3" in result.stdout  # Only matching IDs

    def test_join_left(self, left_file: Path, right_file: Path, tmp_path: Path):
        """Test left join."""
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file),
            "--on", "customer_id",
            "--how", "left"
        ])

        assert result.exit_code == 0
        assert "Join type: left" in result.stdout
        assert "Joined rows: 4" in result.stdout  # All left rows

    def test_join_right(self, left_file: Path, right_file: Path, tmp_path: Path):
        """Test right join."""
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file),
            "--on", "customer_id",
            "--how", "right"
        ])

        assert result.exit_code == 0
        assert "Join type: right" in result.stdout
        assert "Joined rows: 4" in result.stdout  # All right rows

    def test_join_outer(self, left_file: Path, right_file: Path, tmp_path: Path):
        """Test outer join."""
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file),
            "--on", "customer_id",
            "--how", "outer"
        ])

        assert result.exit_code == 0
        assert "Join type: outer" in result.stdout
        assert "Joined rows: 5" in result.stdout  # All rows from both

    def test_join_with_different_keys(self, left_file: Path, different_keys_file: Path, tmp_path: Path):
        """Test joining with different column names."""
        result = runner.invoke(app, [
            "join", str(left_file), str(different_keys_file),
            "--left-on", "customer_id",
            "--right-on", "id"
        ])

        assert result.exit_code == 0
        assert "Left on: customer_id" in result.stdout
        assert "Right on: id" in result.stdout

    def test_join_with_output(self, left_file: Path, right_file: Path, tmp_path: Path):
        """Test join with output file."""
        output_path = tmp_path / "joined.xlsx"
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file),
            "--on", "customer_id",
            "--output", str(output_path)
        ])

        assert result.exit_code == 0
        assert "Written to:" in result.stdout
        assert output_path.exists()

    def test_join_csv_files(self, csv_left_file: Path, csv_right_file: Path, tmp_path: Path):
        """Test joining CSV files."""
        result = runner.invoke(app, [
            "join", str(csv_left_file), str(csv_right_file),
            "--on", "user_id"
        ])

        assert result.exit_code == 0
        assert "Joined rows:" in result.stdout

    def test_join_specific_sheets(self, left_file: Path, right_file: Path, tmp_path: Path):
        """Test joining specific sheets."""
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file),
            "--on", "customer_id",
            "--left-sheet", "Sheet1",
            "--right-sheet", "Sheet1"
        ])

        assert result.exit_code == 0

    def test_join_invalid_join_type(self, left_file: Path, right_file: Path):
        """Test join with invalid join type."""
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file),
            "--on", "customer_id",
            "--how", "invalid"
        ])

        assert result.exit_code == 1

    def test_join_no_join_columns(self, left_file: Path, right_file: Path):
        """Test join without specifying join columns."""
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file)
        ])

        assert result.exit_code == 1

    def test_join_on_with_left_on(self, left_file: Path, right_file: Path):
        """Test join with both --on and --left-on specified."""
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file),
            "--on", "customer_id",
            "--left-on", "id"
        ])

        assert result.exit_code == 1

    def test_join_incomplete_key_specification(self, left_file: Path, right_file: Path):
        """Test join with only --left-on specified."""
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file),
            "--left-on", "customer_id"
        ])

        assert result.exit_code == 1

    def test_join_invalid_column_left(self, left_file: Path, right_file: Path):
        """Test join with non-existent column in left file."""
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file),
            "--on", "invalid_column"
        ])

        assert result.exit_code == 1

    def test_join_invalid_column_right(self, left_file: Path, right_file: Path):
        """Test join with non-existent column in right file."""
        result = runner.invoke(app, [
            "join", str(left_file), str(right_file),
            "--left-on", "customer_id",
            "--right-on", "invalid_column"
        ])

        assert result.exit_code == 1

    def test_join_empty_left_file(self, empty_file: Path, right_file: Path):
        """Test join with empty left file."""
        result = runner.invoke(app, [
            "join", str(empty_file), str(right_file),
            "--on", "customer_id"
        ])

        assert result.exit_code == 0
        assert "empty" in result.stdout.lower()

    def test_join_nonexistent_left_file(self, right_file: Path):
        """Test join with non-existent left file."""
        result = runner.invoke(app, [
            "join", "missing.xlsx", str(right_file),
            "--on", "customer_id"
        ])

        assert result.exit_code == 1

    def test_join_nonexistent_right_file(self, left_file: Path):
        """Test join with non-existent right file."""
        result = runner.invoke(app, [
            "join", str(left_file), "missing.xlsx",
            "--on", "customer_id"
        ])

        assert result.exit_code == 1

    def test_join_help(self):
        """Test join command help."""
        result = runner.invoke(app, ["join", "--help"])

        assert result.exit_code == 0
        assert "Join two datasets" in result.stdout
        assert "--on" in result.stdout
        assert "--how" in result.stdout
