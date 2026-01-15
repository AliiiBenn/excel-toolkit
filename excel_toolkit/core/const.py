"""Constants for file handlers.

This module defines supported file formats, default values, and limits
for file operations in the Excel CLI Toolkit.
"""

# Supported file formats
SUPPORTED_READ_FORMATS = {
    ".xlsx": "excel",
    ".xls": "excel",
    ".csv": "csv",
}

SUPPORTED_WRITE_FORMATS = {
    ".xlsx": "excel",
    ".csv": "csv",
}

# Default values
DEFAULT_SHEET_NAME = "Sheet1"
DEFAULT_CSV_ENCODING = "utf-8"
DEFAULT_CSV_DELIMITER = ","
DEFAULT_EXCEL_ENGINE = "openpyxl"

# File size limits (in megabytes)
MAX_FILE_SIZE_MB = 500
WARNING_FILE_SIZE_MB = 100

# Encoding detection order (most common first)
ENCODING_DETECTION_ORDER = [
    "utf-8",
    "utf-8-sig",
    "latin-1",
    "cp1252",
    "iso-8859-1",
]

# Delimiter detection candidates
DELIMITER_CANDIDATES = [",", ";", "\t", "|"]
