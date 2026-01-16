"""Validate command implementation.

Validates data quality against various rules.
"""

from pathlib import Path
import typer

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.operations.validation import (
    validate_column_exists,
    validate_column_type,
    validate_value_range,
    validate_unique,
    check_null_values,
    validate_dataframe,
    ValidationReport,
)
from excel_toolkit.commands.common import read_data_file


def validate(
    file_path: str = typer.Argument(..., help="Path to input file"),
    columns: str | None = typer.Option(None, "--columns", "-c", help="Comma-separated columns to check"),
    types: str | None = typer.Option(None, "--types", "-t", help="Type checks (format: col:type,col:type)"),
    range: str | None = typer.Option(None, "--range", "-r", help="Range check (format: col:min:max)"),
    unique: str | None = typer.Option(None, "--unique", "-u", help="Check uniqueness of column(s)"),
    null_threshold: float | None = typer.Option(None, "--null-threshold", help="Max null percentage (0-1)"),
    min_value: float | None = typer.Option(None, "--min", help="Minimum value for range check"),
    max_value: float | None = typer.Option(None, "--max", help="Maximum value for range check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed validation info"),
    fail_fast: bool = typer.Option(False, "--fail-fast", help="Stop on first validation failure"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Validate data quality against various rules.

    Performs comprehensive validation checks:
    - Column existence: Verify columns exist
    - Type checking: Validate data types (int, float, str, bool, datetime, numeric)
    - Range validation: Ensure values within specified range
    - Uniqueness: Check for duplicate values
    - Null threshold: Verify null values don't exceed threshold

    Examples:
        xl validate data.xlsx --columns id,name,email
        xl validate data.csv --types "age:int,salary:float"
        xl validate data.xlsx --range "age:0:120"
        xl validate data.csv --unique id --null-threshold 0.1
        xl validate data.xlsx --columns id --types "id:int" --unique id --verbose
    """
    # 1. Read file
    df = read_data_file(file_path, sheet)

    # 2. Build validation rules
    rules = []

    # Column existence rule
    if columns:
        col_list = [c.strip() for c in columns.split(",")]
        rules.append({
            "type": "column_exists",
            "columns": col_list
        })

    # Type validation rule
    if types:
        type_dict = {}
        for spec in types.split(","):
            col, col_type = spec.split(":")
            type_dict[col.strip()] = col_type.strip()
        rules.append({
            "type": "column_type",
            "column_types": type_dict
        })

    # Range validation rule
    if range or (min_value is not None or max_value is not None):
        if range:
            # Parse range spec "col:min:max"
            col_name, min_val, max_val = range.split(":")
            range_col = col_name.strip()
            range_min = float(min_val)
            range_max = float(max_val)
        else:
            # Use --min and --max options (need a column)
            if not columns:
                typer.echo("Error: Must specify --columns with --min/--max", err=True)
                raise typer.Exit(1)
            range_col = columns.split(",")[0].strip()
            range_min = min_value
            range_max = max_value

        rules.append({
            "type": "value_range",
            "column": range_col,
            "min": range_min,
            "max": range_max
        })

    # Uniqueness rule
    if unique:
        unique_cols = [c.strip() for c in unique.split(",")]
        rules.append({
            "type": "unique",
            "columns": unique_cols
        })

    # Null threshold rule
    if null_threshold is not None:
        cols_to_check = [c.strip() for c in columns.split(",")] if columns else None
        rules.append({
            "type": "null_threshold",
            "columns": cols_to_check,
            "threshold": null_threshold
        })

    # If no rules specified, check all columns exist and have no nulls
    if not rules:
        typer.echo("No validation rules specified. Use --columns, --types, --range, --unique, or --null-threshold")
        typer.echo("Run 'xl validate --help' for examples")
        raise typer.Exit(0)

    # 3. Run validation
    result = validate_dataframe(df, rules)
    if is_err(result):
        error = unwrap_err(result)
        typer.echo(f"Validation error: {error}", err=True)
        raise typer.Exit(1)

    report: ValidationReport = unwrap(result)

    # 4. Display results
    _display_validation_report(report, verbose)

    # 5. Exit with error if failures
    if report.failed > 0 and fail_fast:
        raise typer.Exit(1)


def _display_validation_report(report: ValidationReport, verbose: bool) -> None:
    """Display validation report in user-friendly format.

    Args:
        report: Validation report from validate_dataframe
        verbose: Whether to show detailed warnings
    """
    # Summary
    typer.echo(f"✅ Passed: {report.passed}")
    if report.failed > 0:
        typer.echo(f"❌ Failed: {report.failed}", err=True)
    else:
        typer.echo("❌ Failed: 0")

    typer.echo("")

    # Errors
    if report.errors:
        typer.echo("Errors:", err=True)
        for i, error in enumerate(report.errors, 1):
            rule_num = error.get("rule", "?")
            error_type = error.get("type", "unknown")
            error_msg = error.get("error", str(error))
            typer.echo(f"  {i}. Rule #{rule_num} ({error_type}): {error_msg}", err=True)
        typer.echo("")

    # Warnings (only if verbose)
    if report.warnings and verbose:
        typer.echo("Warnings:")
        for i, warning in enumerate(report.warnings, 1):
            col = warning.get("column", "?")
            null_count = warning.get("null_count", 0)
            null_percent = warning.get("null_percent", 0.0)
            typer.echo(f"  {i}. Column '{col}': {null_count} nulls ({null_percent:.1%})")
        typer.echo("")


# Create CLI app for this command
app = typer.Typer(help="Validate data quality")

# Register the command
app.command()(validate)
