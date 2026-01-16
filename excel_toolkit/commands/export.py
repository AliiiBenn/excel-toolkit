"""Export command implementation.

Export data to various formats with customizable options.
"""

from pathlib import Path

import typer
import pandas as pd

from excel_toolkit.core import HandlerFactory
from excel_toolkit.fp import is_ok, is_err, unwrap, unwrap_err
from excel_toolkit.commands.common import read_data_file


def export(
    file_path: str = typer.Argument(..., help="Path to input file"),
    format: str = typer.Option(..., "--format", "-f", help="Output format: csv, json, parquet, tsv, html, markdown"),
    output: str = typer.Option(..., "--output", "-o", help="Output file path"),
    sheet: str | None = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel files"),
    delimiter: str = typer.Option(",", "--delimiter", "-d", help="Delimiter for CSV/TSV (default: ',' for CSV, '\\t' for TSV)"),
    orient: str = typer.Option("records", "--orient", help="Orientation for JSON (records, index, columns, values)"),
    index: bool = typer.Option(False, "--index", help="Include index in output"),
    float_format: str | None = typer.Option(None, "--float-format", help="Float format string (e.g., '%.2f')"),
    encoding: str = typer.Option("utf-8", "--encoding", "-e", help="Encoding for text formats"),
) -> None:
    """Export data to various formats with customizable options.

    Convert Excel or CSV files to different output formats including CSV, JSON, Parquet, TSV, HTML, and Markdown.

    Examples:
        xl export data.xlsx --format csv --output data.csv
        xl export data.xlsx --format json --orient records --output data.json
        xl export data.csv --format parquet --output data.parquet
        xl export data.xlsx --format html --output data.html
        xl export data.xlsx --format tsv --delimiter "\\t" --output data.tsv
    """
    # 1. Validate format
    valid_formats = ["csv", "json", "parquet", "tsv", "html", "markdown"]
    if format not in valid_formats:
        typer.echo(f"Error: Invalid format '{format}'", err=True)
        typer.echo(f"Valid formats: {', '.join(valid_formats)}")
        raise typer.Exit(1)

    # 2. Read file
    df = read_data_file(file_path, sheet)
    original_count = len(df)

    # 3. Handle empty file
    if df.empty:
        typer.echo("File is empty (no data rows)")
        raise typer.Exit(0)

    # 4. Export based on format
    output_path = Path(output)

    try:
        if format == "csv":
            # Use specified delimiter or default to comma
            sep = delimiter if format != "tsv" else "\t"
            df.to_csv(output_path, index=index, sep=sep, encoding=encoding, float_format=float_format)

        elif format == "tsv":
            # TSV is just CSV with tab delimiter
            df.to_csv(output_path, index=index, sep="\t", encoding=encoding, float_format=float_format)

        elif format == "json":
            # Validate orient parameter
            valid_orients = ["records", "index", "columns", "values"]
            if orient not in valid_orients:
                typer.echo(f"Error: Invalid orient '{orient}'", err=True)
                typer.echo(f"Valid orients: {', '.join(valid_orients)}")
                raise typer.Exit(1)

            df.to_json(output_path, orient=orient, index=index, force_ascii=False)

        elif format == "parquet":
            # Parquet requires pyarrow or fastparquet
            try:
                df.to_parquet(output_path, index=index)
            except ImportError:
                typer.echo("Error: Parquet export requires 'pyarrow' or 'fastparquet' package", err=True)
                typer.echo("Install with: pip install pyarrow", err=True)
                raise typer.Exit(1)

        elif format == "html":
            df.to_html(output_path, index=index)

        elif format == "markdown":
            with open(output_path, 'w', encoding=encoding) as f:
                f.write(df.to_markdown(index=index))

        # 5. Display summary
        typer.echo(f"Exported {original_count} rows to {output}")
        typer.echo(f"Format: {format}")

        if format in ["csv", "tsv"]:
            typer.echo(f"Delimiter: '{delimiter if format != 'tsv' else '\\t'}'")
            typer.echo(f"Encoding: {encoding}")
        elif format == "json":
            typer.echo(f"Orientation: {orient}")
        elif format == "parquet":
            typer.echo(f"Index included: {index}")

    except Exception as e:
        typer.echo(f"Error exporting to {format}: {str(e)}", err=True)
        raise typer.Exit(1)


# Create CLI app for this command
app = typer.Typer(help="Export data to various formats")

# Register the command
app.command()(export)
