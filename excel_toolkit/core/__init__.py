"""Core layer for file I/O operations.

This module provides the foundation for reading and writing data files.
It uses Result types for explicit error handling and supports multiple
file formats (Excel, CSV).

Example:
    >>> from excel_toolkit.core import HandlerFactory
    >>> from pathlib import Path
    >>> from excel_toolkit.fp import is_ok, unwrap
    >>>
    >>> factory = HandlerFactory()
    >>> result = factory.read_file(Path("data.xlsx"))
    >>>
    >>> if is_ok(result):
    ...     df = unwrap(result)
    ...     print(f"Read {len(df)} rows")
"""

# Public API - Handlers
from excel_toolkit.core.file_handlers import (
    ExcelHandler,
    CSVHandler,
    HandlerFactory,
)

# Public API - Exceptions
from excel_toolkit.core.exceptions import (
    FileHandlerError,
    FileNotFoundError,
    FileAccessError,
    UnsupportedFormatError,
    InvalidFileError,
    FileSizeError,
    EncodingError,
)

# Public API - Constants
from excel_toolkit.core.const import (
    SUPPORTED_READ_FORMATS,
    SUPPORTED_WRITE_FORMATS,
    DEFAULT_SHEET_NAME,
    DEFAULT_CSV_ENCODING,
    DEFAULT_CSV_DELIMITER,
    MAX_FILE_SIZE_MB,
    WARNING_FILE_SIZE_MB,
)

__all__ = [
    # Handlers
    "ExcelHandler",
    "CSVHandler",
    "HandlerFactory",
    # Exceptions
    "FileHandlerError",
    "FileNotFoundError",
    "FileAccessError",
    "UnsupportedFormatError",
    "InvalidFileError",
    "FileSizeError",
    "EncodingError",
    # Constants
    "SUPPORTED_READ_FORMATS",
    "SUPPORTED_WRITE_FORMATS",
    "DEFAULT_SHEET_NAME",
    "DEFAULT_CSV_ENCODING",
    "DEFAULT_CSV_DELIMITER",
    "MAX_FILE_SIZE_MB",
    "WARNING_FILE_SIZE_MB",
]
