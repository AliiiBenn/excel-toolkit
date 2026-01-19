"""Stats command implementation.

Computes statistical summaries for data files.
"""

from pathlib import Path
from typing import Any
import json

import typer
import pandas as pd
import numpy as np

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import (
    read_data_file,
    display_table,
    resolve_column_reference,
)


def stats(
    file_path: str = typer.Argument(..., help="Path to input file"),
    column: str | None = typer.Option(None, "--column", "-c", help="Specific column to analyze"),
    all_columns: bool = typer.Option(False, "--all-columns", "-a", help="Analyze all numeric columns"),
    percentiles: str = typer.Option("25,50,75", "--percentiles", "-p", help="Percentiles to compute (comma-separated)"),
    include: str = typer.Option("numeric", "--include", help="Column types to include (numeric, categorical, datetime, all)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json, csv)"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
) -> None:
    """Compute statistical summaries for a data file.

    Calculates descriptive statistics including mean, median, standard deviation,
    min, max, quartiles, and more for numeric columns.

    Column reference can be:
        - Column name: "salary"
        - Column index (1-based): "3"
        - Negative index: "-1" (last column)

    Examples:
        xl stats data.xlsx --column salary
        xl stats data.csv --all-columns
        xl stats data.xlsx --column age --format json
        xl stats data.csv --all-columns --percentiles 10,25,50,75,90,95,99
        xl stats data.xlsx --all-columns --include categorical
        xl stats data.xlsx --column "3" --output third-col-stats.xlsx
    """
    # 1. Parse percentiles
    try:
        percentile_list = [float(p.strip()) for p in percentiles.split(",")]
        if not all(0 <= p <= 100 for p in percentile_list):
            typer.echo("Error: Percentiles must be between 0 and 100", err=True)
            raise typer.Exit(1)
    except ValueError:
        typer.echo(f"Error: Invalid percentiles format: {percentiles}", err=True)
        typer.echo("Expected comma-separated values (e.g., 25,50,75)", err=True)
        raise typer.Exit(1)

    # 2. Parse include types
    include_types = [t.strip().lower() for t in include.split(",")]
    valid_types = {"numeric", "categorical", "datetime", "all"}
    invalid_types = [t for t in include_types if t not in valid_types]
    if invalid_types:
        typer.echo(f"Error: Invalid include types: {', '.join(invalid_types)}", err=True)
        typer.echo(f"Valid types: {', '.join(valid_types)}", err=True)
        raise typer.Exit(1)

    # 3. Read file
    df = read_data_file(file_path, sheet)

    # 4. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 5. Determine columns to analyze
    if column:
        # Resolve column reference (supports both name and index)
        resolved_column = resolve_column_reference(column, df)
        columns_to_analyze = [resolved_column]
        # Store the resolved column name for display
        column_for_display = resolved_column
    elif all_columns:
        columns_to_analyze = list(df.columns)
    else:
        # Default: all numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            typer.echo("No numeric columns found in file")
            typer.echo("Use --all-columns to analyze non-numeric columns")
            typer.echo("Use --include categorical to include categorical columns")
            raise typer.Exit(0)
        columns_to_analyze = numeric_cols

    # Step 8: Filter columns by type if specified (only for --all-columns or default mode)
    # Skip type filtering when --column is explicitly specified
    if not column and "all" not in include_types:
        filtered_cols = []
        for col in columns_to_analyze:
            col_type = _get_column_type(df[col])
            if col_type in include_types:
                filtered_cols.append(col)
        columns_to_analyze = filtered_cols

    if not columns_to_analyze:
        typer.echo("No columns match the specified type filters")
        raise typer.Exit(0)

    # Step 9: Compute statistics
    all_stats = {}
    for col in columns_to_analyze:
        col_type = _get_column_type(df[col])
        if col_type == "numeric":
            col_stats = _compute_numeric_stats(df[col], percentile_list)
        elif col_type == "categorical":
            col_stats = _compute_categorical_stats(df[col])
        elif col_type == "datetime":
            col_stats = _compute_datetime_stats(df[col])
        else:
            col_stats = {"error": "Unsupported column type"}

        all_stats[col] = col_stats

    # Step 10: Output results
    if output:
        output_path = Path(output)
        try:
            with open(output_path, "w") as f:
                if format == "json":
                    json.dump(all_stats, f, indent=2, default=str)
                else:
                    f.write(_format_stats_as_text(all_stats, format))
            typer.echo(f"Written to: {output}")
        except Exception as e:
            typer.echo(f"Error writing file: {str(e)}", err=True)
            raise typer.Exit(1)
    else:
        if format == "json":
            typer.echo(json.dumps(all_stats, indent=2, default=str))
        elif format == "csv":
            typer.echo(_format_stats_as_csv(all_stats))
        elif format == "table":
            if column and len(all_stats) == 1:
                # Single column, display detailed table
                _display_single_column_stats(column_for_display, all_stats[column_for_display])
            else:
                # Multiple columns, display summary table
                _display_multi_column_stats(all_stats)
        else:
            typer.echo(f"Unknown format: {format}", err=True)
            typer.echo("Supported formats: table, json, csv")
            raise typer.Exit(1)


def _get_column_type(series: pd.Series) -> str:
    """Determine the type of a column for statistics."""
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    else:
        return "categorical"


def _compute_numeric_stats(series: pd.Series, percentiles: list[float]) -> dict:
    """Compute statistics for a numeric column."""
    # Remove NaN values for calculations
    clean_series = series.dropna()

    if clean_series.empty:
        return {
            "count": 0,
            "missing": len(series),
            "error": "No valid numeric values"
        }

    stats_dict = {
        "count": len(clean_series),
        "missing": series.isna().sum(),
        "mean": clean_series.mean(),
        "median": clean_series.median(),
        "std": clean_series.std(),
        "min": clean_series.min(),
        "max": clean_series.max(),
        "range": clean_series.max() - clean_series.min(),
    }

    # Add percentiles
    for p in sorted(percentiles):
        stats_dict[f"p{int(p)}"] = clean_series.quantile(p / 100)

    # Add additional stats if we have enough data
    if len(clean_series) > 2:
        stats_dict["var"] = clean_series.var()
        stats_dict["skew"] = clean_series.skew()
        stats_dict["kurtosis"] = clean_series.kurtosis()

    # Add mode if it exists
    mode_result = clean_series.mode()
    if not mode_result.empty:
        stats_dict["mode"] = mode_result.iloc[0]

    return stats_dict


def _compute_categorical_stats(series: pd.Series) -> dict:
    """Compute statistics for a categorical column."""
    value_counts = series.value_counts()

    stats_dict = {
        "count": len(series),
        "missing": series.isna().sum(),
        "unique": len(value_counts),
    }

    if not value_counts.empty:
        stats_dict["top"] = value_counts.index[0]
        stats_dict["freq"] = value_counts.iloc[0]

    return stats_dict


def _compute_datetime_stats(series: pd.Series) -> dict:
    """Compute statistics for a datetime column."""
    clean_series = series.dropna()

    if clean_series.empty:
        return {
            "count": 0,
            "missing": len(series),
            "error": "No valid datetime values"
        }

    min_date = clean_series.min()
    max_date = clean_series.max()

    stats_dict = {
        "count": len(clean_series),
        "missing": series.isna().sum(),
        "min": min_date,
        "max": max_date,
        "range_days": (max_date - min_date).days,
    }

    return stats_dict


def _display_single_column_stats(column_name: str, stats: dict) -> None:
    """Display statistics for a single column in table format."""
    typer.echo(f"Statistics for column: {column_name}")
    typer.echo("")

    if "error" in stats:
        typer.echo(f"Error: {stats['error']}")
        return

    # Create rows for display
    rows = []
    for key, value in stats.items():
        if key == "error":
            continue
        # Format value
        if isinstance(value, float):
            formatted_value = f"{value:.2f}"
        elif isinstance(value, int):
            formatted_value = str(value)
        elif pd.isna(value):
            formatted_value = "NaN"
        else:
            formatted_value = str(value)

        rows.append([key.replace("_", " ").title(), formatted_value])

    # Display as table
    if rows:
        df_display = pd.DataFrame(rows, columns=["Statistic", "Value"])
        display_table(df_display, max_col_width=50)


def _display_multi_column_stats(all_stats: dict) -> None:
    """Display summary statistics for multiple columns."""
    typer.echo("Statistical Summary")
    typer.echo("")

    # Create a summary table
    rows = []
    for col, stats in all_stats.items():
        if "error" in stats:
            rows.append([col, "Error", stats.get("error", "")])
            continue

        if "mean" in stats:  # Numeric
            rows.append([
                col,
                f"{stats['count']}",
                f"{stats.get('mean', 0):.2f}",
                f"{stats.get('std', 0):.2f}",
                f"{stats.get('min', 0):.2f}",
                f"{stats.get('max', 0):.2f}"
            ])
        elif "unique" in stats:  # Categorical
            rows.append([
                col,
                f"{stats['count']}",
                f"{stats['unique']} unique",
                stats.get('top', 'N/A'),
                f"{stats.get('freq', 0)}"
            ])
        elif "min" in stats:  # Datetime
            rows.append([
                col,
                f"{stats['count']}",
                str(stats.get('min', '')),
                str(stats.get('max', '')),
                f"{stats.get('range_days', 0)} days"
            ])

    if rows:
        if any("mean" in all_stats[col] for col in all_stats if "error" not in all_stats[col]):
            # Numeric columns
            df_display = pd.DataFrame(
                rows,
                columns=["Column", "Count", "Mean", "Std", "Min", "Max"]
            )
        else:
            # Mixed types
            df_display = pd.DataFrame(rows)

        display_table(df_display, max_col_width=30)


def _format_stats_as_text(all_stats: dict, format: str) -> str:
    """Format statistics as text (for file output)."""
    if format == "csv":
        return _format_stats_as_csv(all_stats)

    lines = []
    for col, stats in all_stats.items():
        lines.append(f"Column: {col}")
        for key, value in stats.items():
            lines.append(f"  {key}: {value}")
        lines.append("")

    return "\n".join(lines)


def _format_stats_as_csv(all_stats: dict) -> str:
    """Format statistics as CSV."""
    lines = []

    # Header
    if all_stats:
        first_col = next(iter(all_stats.values()))
        headers = ["column"] + list(first_col.keys())
        lines.append(",".join(headers))

    # Rows
    for col, stats in all_stats.items():
        values = [col] + [str(stats.get(k, "")) for k in headers[1:]]
        lines.append(",".join(values))

    return "\n".join(lines)


# Create CLI app for this command
app = typer.Typer(help="Compute statistical summaries")

# Register the command
app.command()(stats)
