"""Filter command implementation.

Filters rows from data files based on conditions.
"""

from pathlib import Path
from typing import Any
import re

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory, ExcelHandler, CSVHandler
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err, ok, err
from excel_toolkit.fp._result import Result
from excel_toolkit.commands.common import (
    display_table,
    display_csv,
    display_json,
    format_file_info,
)


# Security: allowed patterns in conditions
ALLOWED_PATTERNS = [
    r"\w+\s*[=!<>]+\s*[\w'\"]+",  # Comparisons: x == 5, x > 3
    r"\w+\s+in\s+\[[^\]]+\]",  # in operator: x in [a, b, c]
    r"\w+\.isna\(\)",  # Null check: x.isna()
    r"\w+\.notna\(\)",  # Null check: x.notna()
    r"\w+\s+contains\s+['\"][^'\"]+['\"]",  # String contains
    r"\w+\s+startswith\s+['\"][^'\"]+['\"]",  # String starts with
    r"\w+\s+endswith\s+['\"][^'\"]+['\"]",  # String ends with
    r"\s+and\s+",  # Logical AND
    r"\s+or\s+",  # Logical OR
    r"\s+not\s+",  # Logical NOT
    r"\([^)]+\)",  # Parentheses for grouping
]

DANGEROUS_PATTERNS = [
    "import",
    "exec",
    "eval",
    "__",
    "open(",
    "file(",
    "os.",
    "sys.",
    "subprocess",
    "pickle",
]


def filter(
    file_path: str = typer.Argument(..., help="Path to input file"),
    condition: str = typer.Argument(..., help="Filter condition (e.g., 'age > 30')"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    rows: int | None = typer.Option(None, "--rows", "-n", help="Limit number of results"),
    columns: str | None = typer.Option(None, "--columns", "-c", help="Comma-separated columns to keep"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, csv, json)"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show preview without writing"),
) -> None:
    """Filter rows from a data file based on a condition.

    Uses pandas query syntax for conditions:
    - Numeric: age > 30, price >= 100
    - String: name == 'Alice', category in ['A', 'B']
    - Logical: age > 25 and city == 'Paris'
    - Null: value.isna(), value.notna()

    Examples:
        xl filter data.xlsx "age > 30"
        xl filter data.csv "price > 100" --output filtered.xlsx
        xl filter data.xlsx "city == 'Paris'" --columns name,age
        xl filter data.csv "status == 'active'" --dry-run
    """
    path = Path(file_path)
    factory = HandlerFactory()

    # Step 1: Validate file exists
    if not path.exists():
        typer.echo(f"File not found: {file_path}", err=True)
        raise typer.Exit(1)

    # Step 2: Validate condition for security
    validation_result = _validate_condition(condition)
    if is_err(validation_result):
        error = unwrap_err(validation_result)
        typer.echo(f"Invalid condition: {error}", err=True)
        raise typer.Exit(1)

    # Step 3: Get handler
    handler_result = factory.get_handler(path)
    if is_err(handler_result):
        error = unwrap_err(handler_result)
        typer.echo(f"{error}", err=True)
        raise typer.Exit(1)

    handler = unwrap(handler_result)

    # Step 4: Read file
    if isinstance(handler, ExcelHandler):
        sheet_name = sheet
        kwargs = {"sheet_name": sheet_name} if sheet_name else {}
        read_result = handler.read(path, **kwargs)
    elif isinstance(handler, CSVHandler):
        # Auto-detect encoding and delimiter
        encoding_result = handler.detect_encoding(path)
        encoding = unwrap(encoding_result) if is_ok(encoding_result) else "utf-8"

        delimiter_result = handler.detect_delimiter(path, encoding)
        delimiter = unwrap(delimiter_result) if is_ok(delimiter_result) else ","

        read_result = handler.read(path, encoding=encoding, delimiter=delimiter)
    else:
        typer.echo("Unsupported handler type", err=True)
        raise typer.Exit(1)

    if is_err(read_result):
        error = unwrap_err(read_result)
        typer.echo(f"Error reading file: {error}", err=True)
        raise typer.Exit(1)

    df = unwrap(read_result)
    original_count = len(df)

    # Step 5: Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # Step 6: Normalize condition
    normalized_condition = _normalize_condition(condition)

    # Step 7: Apply filter
    try:
        df_filtered = df.query(normalized_condition)
    except pd.errors.UndefinedVariableError as e:
        # Extract column name from error
        error_str = str(e)
        col_match = re.search(r"'([^']+)'", error_str)
        if col_match:
            col = col_match.group(1)
            typer.echo(f"Error: Column '{col}' not found", err=True)
            typer.echo(f"Available columns: {', '.join(df.columns)}")
        else:
            typer.echo(f"Error: {error_str}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        error_msg = str(e)
        if "could not convert" in error_msg:
            typer.echo("Error: Type mismatch in condition", err=True)
            typer.echo("Ensure numeric columns are compared with numbers", err=True)
            typer.echo("Ensure string columns are compared with strings in quotes", err=True)
        else:
            typer.echo(f"Error filtering data: {error_msg}", err=True)
        typer.echo(f"\nCondition: {condition}", err=True)
        raise typer.Exit(1)

    filtered_count = len(df_filtered)

    # Step 8: Select columns if specified
    if columns:
        try:
            col_list = [c.strip() for c in columns.split(",")]
            # Validate column names
            missing_cols = [c for c in col_list if c not in df_filtered.columns]
            if missing_cols:
                typer.echo(f"Error: Columns not found: {', '.join(missing_cols)}", err=True)
                typer.echo(f"Available columns: {', '.join(df_filtered.columns)}")
                raise typer.Exit(1)
            df_filtered = df_filtered[col_list]
        except Exception as e:
            typer.echo(f"Error selecting columns: {str(e)}", err=True)
            raise typer.Exit(1)

    # Step 9: Limit rows if specified
    if rows is not None:
        df_filtered = df_filtered.head(rows)

    # Step 10: Handle dry-run mode
    if dry_run:
        percentage = (filtered_count / original_count * 100) if original_count > 0 else 0
        typer.echo(f"Would filter {filtered_count} of {original_count} rows ({percentage:.1f}%)")
        typer.echo(f"Condition: {condition}")
        typer.echo("")
        if filtered_count > 0:
            preview_rows = min(5, filtered_count)
            typer.echo("Preview of first matches:")
            display_table(df_filtered.head(preview_rows))
        else:
            typer.echo("No rows match the condition")
        raise typer.Exit(0)

    # Step 11: Handle empty result
    if filtered_count == 0:
        typer.echo("No rows match the filter condition")
        typer.echo(f"Condition: {condition}")
        if output:
            # Still write empty file
            output_path = Path(output)
            write_result = factory.write_file(df_filtered, output_path)
            if is_err(write_result):
                error = unwrap_err(write_result)
                typer.echo(f"Error writing file: {error}", err=True)
                raise typer.Exit(1)
            typer.echo(f"Written to: {output}")
        raise typer.Exit(0)

    # Step 12: Display summary
    percentage = (filtered_count / original_count * 100) if original_count > 0 else 0
    typer.echo(f"Filtered {filtered_count} of {original_count} rows ({percentage:.1f}%)")
    typer.echo(f"Condition: {condition}")

    if filtered_count == original_count:
        typer.echo("Warning: All rows match the condition", err=True)

    typer.echo("")

    # Step 13: Write output or display
    if output:
        output_path = Path(output)
        write_result = factory.write_file(df_filtered, output_path)
        if is_err(write_result):
            error = unwrap_err(write_result)
            typer.echo(f"Error writing file: {error}", err=True)
            raise typer.Exit(1)
        typer.echo(f"Written to: {output}")
    else:
        # Display data
        if format == "table":
            display_table(df_filtered)
        elif format == "csv":
            display_csv(df_filtered)
        elif format == "json":
            display_json(df_filtered)
        else:
            typer.echo(f"Unknown format: {format}", err=True)
            typer.echo("Supported formats: table, csv, json")
            raise typer.Exit(1)


def _validate_condition(condition: str) -> Result[str, str]:
    """Validate filter condition for security and syntax.

    Args:
        condition: User-provided condition string

    Returns:
        Result[str, str] - Valid condition or error message
    """
    # Check for dangerous patterns
    condition_lower = condition.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern in condition_lower:
            return err(f"Unsafe pattern detected: {pattern}")

    # Check length
    if len(condition) > 1000:
        return err("Condition too long (max 1000 characters)")

    # Basic syntax validation
    # Check for balanced parentheses
    if condition.count("(") != condition.count(")"):
        return err("Unbalanced parentheses")

    # Check for balanced brackets
    if condition.count("[") != condition.count("]"):
        return err("Unbalanced brackets")

    # Check for balanced quotes
    single_quotes = condition.count("'")
    if single_quotes % 2 != 0:
        return err("Unbalanced single quotes")

    double_quotes = condition.count('"')
    if double_quotes % 2 != 0:
        return err("Unbalanced double quotes")

    return ok(condition)


def _normalize_condition(condition: str) -> str:
    """Normalize condition syntax for pandas.query().

    Handles special syntax and converts to pandas-compatible form.

    Args:
        condition: User-provided condition

    Returns:
        Normalized condition string
    """
    # Convert 'value is None' to 'value.isna()'
    condition = re.sub(r"(\w+)\s+is\s+None\b", r"\1.isna()", condition)
    condition = re.sub(r"(\w+)\s+is\s+not\s+None\b", r"\1.notna()", condition)

    # Convert 'value between X and Y' to 'value >= X and value <= Y'
    # Case insensitive
    pattern = r"(\w+)\s+between\s+([^ ]+)\s+and\s+([^ ]+)"
    replacement = r"\1 >= \2 and \1 <= \3"
    condition = re.sub(pattern, replacement, condition, flags=re.IGNORECASE)

    # Handle 'not in'
    condition = re.sub(r"(\w+)\s+not\s+in\s+", r"\1 not in ", condition, flags=re.IGNORECASE)

    return condition


# Create CLI app for this command
app = typer.Typer(help="Filter rows from data files")

# Register the command
app.command()(filter)
