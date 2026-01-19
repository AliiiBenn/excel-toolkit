# Error Handling Analysis

**Date:** 2025-01-19
**Component:** Error Management System
**Target Audience:** AI Agents using Excel Toolkit
**Purpose:** Analysis of error handling quality and recommendations for improvement

---

## Overview

This document provides a comprehensive analysis of the error handling system in Excel Toolkit, with specific focus on its suitability for AI agents that require explicit, structured, and predictable error information.

**Key Findings:**
- The project uses a **functional Result type approach** (Either/Success-Failure) instead of traditional exceptions
- **40+ specific error types** are well-organized and hierarchical
- **Overall Score: 8.2/10** - Excellent for CLI tools, with room for improvement for AI agents

---

## Architecture Summary

### Error Type System

The project implements two parallel error handling systems:

#### 1. Core File Handler Exceptions (`excel_toolkit/core/exceptions.py`)

```python
FileHandlerError (base)
├── FileNotFoundError
├── FileAccessError
├── UnsupportedFormatError
├── InvalidFileError
├── FileSizeError
└── EncodingError
```

#### 2. Operation-Specific Error Types (`excel_toolkit/models/error_types.py`)

Algebraic Data Types (ADTs) for structured error representation:

```python
ValidationError = (
    DangerousPatternError |
    ConditionTooLongError |
    UnbalancedParenthesesError |
    ColumnNotFoundError |
    # ... 10+ more validation errors
)

FilterError = ColumnNotFoundError | QueryFailedError | ColumnMismatchError
SortError = NotComparableError | SortFailedError
PivotError = PivotFailedError
AggregationError = AggregationFailedError
```

### Result Type Implementation

The functional programming module (`excel_toolkit/fp/`) provides a zero-dependency Result type:

```python
from excel_toolkit.fp import ok, err, is_ok, is_err, unwrap, unwrap_err

# All fallible operations return Result[T, E]
def read_file(path: Path) -> Result[pd.DataFrame, FileHandlerError]:
    if not path.exists():
        return err(FileNotFoundError(f"File not found: {path}"))
    # ... validation and read logic
    return ok(dataframe)

# Usage in commands
result = read_file(path)
if is_err(result):
    error = unwrap_err(result)
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(1)
value = unwrap(result)
```

---

## Strengths

### 1. Rich Context in Error Types

Each error type includes structured context that enables AI agents to understand and react to errors:

```python
# excel_toolkit/models/error_types.py:135-144
@dataclass
@immutable
class ColumnNotFoundError:
    """Referenced column doesn't exist in DataFrame.

    Attributes:
        column: The column name that was not found
        available: List of available column names
    """
    column: str
    available: list[str]
```

**Result for AI Agents:**
```
"Error filtering data: Column 'Age' not found. Available: ['Name', 'Email', 'City']"
```

The agent can immediately:
1. Understand what's missing (`Age`)
2. See available alternatives
3. Correct the error without additional queries

### 2. Built-in Security

Input validation detects dangerous code patterns:

```python
# excel_toolkit/operations/filtering.py:47-58
DANGEROUS_PATTERNS = [
    "import", "exec", "eval", "__", "open(",
    "file(", "os.", "sys.", "subprocess", "pickle"
]
```

**For AI Agents:** Protection against code injection → Increased robustness.

### 3. Immutable Error Types

All error types use `@immutable` decorator:

```python
@dataclass
@immutable
class ConditionTooLongError:
    length: int
    max_length: int
```

This ensures error values cannot be modified after creation, making error handling more predictable.

### 4. Explicit Error Handling

The functional API forces explicit error handling:

```python
# excel_toolkit/commands/filter.py:72-76
result = apply_filter(df, normalized, columns=col_list, limit=rows)
if is_err(result):
    error = unwrap_err(result)
    typer.echo(f"Error filtering data: {error}", err=True)
    raise typer.Exit(1)
```

**Benefits:**
- Impossible to forget error handling
- Clear and predictable flow
- Static typing with `Result[T, E]`

### 5. Comprehensive Error Coverage

Error types cover all failure scenarios with specific variants:

- **15+ Validation errors** (security, syntax, column existence)
- **Filter errors** (column mismatch, query failed)
- **Sort errors** (not comparable, sort failed)
- **Pivot errors** (row/column/value columns not found)
- **Aggregation errors** (group columns, aggregation columns)
- **Comparison errors** (key columns not found)
- **Cleaning errors** (invalid fill strategy, fill failed)
- **Transforming errors** (invalid expression, cast failed)
- **Joining errors** (invalid join type, columns not found)
- **Validation errors** (value out of range, null threshold exceeded, uniqueness violation)

---

## Areas for Improvement for AI Agents

### 1. Missing Numeric Error Codes

**Current:** Errors are identified by class name strings

```python
# excel_toolkit/commands/common.py:283-284
if "ColumnNotFoundError" in error_type:
    typer.echo(f"Error: {error_msg}", err=True)
```

**Problems for AI Agents:**
- String-based parsing → fragile
- Difficult to create automatic mappings
- No stable versioning

**Recommendation:** Add `error_code` field (numeric or enum):

```python
from enum import IntEnum

class ErrorCode(IntEnum):
    COLUMN_NOT_FOUND = 1001
    COLUMN_MISMATCH = 1002
    QUERY_FAILED = 1003
    # ...

@dataclass
@immutable
class ColumnNotFoundError:
    error_code: int = ErrorCode.COLUMN_NOT_FOUND
    column: str
    available: list[str]
```

**Benefits:**
- Stable identification across versions
- Easy programmatic handling
- Internationalization support

### 2. Unstructured Message Format

**Current:** Messages are formatted strings

```python
# excel_toolkit/core/file_handlers.py:91
return err(FileNotFoundError(f"File not found: {path}"))
```

**Problems:**
- AI agents must **parse** strings to extract information
- Format not stable over time
- Difficult to localize

**Recommendation:** Separate error type from display message:

```python
# Option 1: Structured messages (JSON-compatible)
@dataclass
@immutable
class ColumnNotFoundError:
    column: str
    available: list[str]

    def to_dict(self) -> dict:
        return {
            "error_type": "ColumnNotFoundError",
            "error_code": 1001,
            "column": self.column,
            "available": self.available,
            "suggestion": self._get_suggestion()
        }

    def _get_suggestion(self) -> str | None:
        from difflib import get_close_matches
        matches = get_close_matches(self.column, self.available, n=1, cutoff=0.6)
        return f"Did you mean: '{matches[0]}'?" if matches else None

# Option 2: Separate formatters
def format_error(error: Error) -> str:
    """Format error for human-readable output."""
    if isinstance(error, ColumnNotFoundError):
        return f"Column '{error.column}' not found. Available: {error.available}"
    # ...
```

### 3. Inconsistency in `handle_operation_error`

**Location:** `excel_toolkit/commands/common.py:267-313`

```python
def handle_operation_error(error: Exception) -> None:
    error_type = type(error).__name__
    error_msg = str(error)

    # String-based matching
    if "ColumnNotFoundError" in error_type:
        typer.echo(f"Error: {error_msg}", err=True)
    elif "TypeMismatchError" in error_type:
        typer.echo(f"Type mismatch: {error_msg}", err=True)
    # ... more string checks
```

**Problems:**
- Depends on **class names** (fragile to refactoring)
- No modern **pattern matching** (Python 3.10+)
- Duplicated logic

**Recommendation:** Use `match/case` (Python 3.10+):

```python
def handle_operation_error(error: Exception) -> None:
    """Handle operation errors with structured pattern matching."""
    match error:
        case ColumnNotFoundError(column, available):
            typer.echo(
                f"Column '{column}' not found. Available: {available}",
                err=True
            )
        case TypeMismatchError(column, expected, actual):
            typer.echo(
                f"Type mismatch in '{column}': expected {expected}, got {actual}",
                err=True
            )
        case ValueOutOfRangeError(column, min_value, max_value, violation_count):
            typer.echo(
                f"{violation_count} values in '{column}' outside range [{min_value}, {max_value}]",
                err=True
            )
        case _:
            # Fallback for unknown errors
            typer.echo(f"Error: {error}", err=True)

    raise typer.Exit(1)
```

### 4. Generic Errors Lack Specificity

Some errors don't provide enough context:

```python
# excel_toolkit/models/error_types.py:461-465
@dataclass
@immutable
class CleaningError:
    """Generic cleaning operation failed."""
    message: str  # ← Too generic
```

**Problem:** AI agents cannot **react programmatically** to this error.

**Recommendation:** Split into specific types:

```python
# Instead of generic CleaningError
CleaningError = (
    InvalidFillStrategyError |
    FillFailedError |
    MissingColumnError |
    DuplicateColumnError |
    InvalidValueHandling
)

@dataclass
@immutable
class FillFailedError:
    """Fill operation failed for specific column."""
    column: str
    strategy: str
    reason: str  # Specific reason (e.g., "Cannot compute mean of string column")
    suggestion: str | None = None
```

### 5. No Automatic Suggestions

Errors indicate what's wrong, but **not how to fix**:

```python
# Current
"Column 'Age' not found. Available: ['Name', 'Email']"

# Better for AI agents
"Column 'Age' not found. Available: ['Name', 'Email']. Did you mean: 'Name'?"
```

**Recommendation:** Add intelligence to error types:

```python
@dataclass
@immutable
class ColumnNotFoundError:
    column: str
    available: list[str]

    @property
    def suggestion(self) -> str | None:
        """Suggest closest matching column name."""
        from difflib import get_close_matches
        matches = get_close_matches(self.column, self.available, n=1, cutoff=0.6)
        return matches[0] if matches else None

    def __str__(self) -> str:
        base = f"Column '{self.column}' not found. Available: {self.available}"
        if self.suggestion:
            base += f". Did you mean: '{self.suggestion}'?"
        return base
```

### 6. Silent Validation Loses Detail

In `check_null_values` (`excel_toolkit/operations/validation.py:284-290`):

```python
existence_check = validate_column_exists(df, columns)
if is_err(existence_check):
    # For validation, return ok() with error in report
    return ok(ValidationReport(
        passed=0,
        failed=1,
        errors=[{"error": "Column not found"}],  # ← Lost detail
        warnings=[]
    ))
```

**Problem:** Original error (with column name) is lost.

**Recommendation:** Preserve original error details:

```python
if is_err(existence_check):
    error = unwrap_err(existence_check)
    return ok(ValidationReport(
        passed=0,
        failed=1,
        errors=[{
            "error_type": "ColumnNotFoundError",
            "column": error.column,
            "available": error.available,
            "message": str(error)
        }],
        warnings=[]
    ))
```

---

## Quality Scores (For AI Agents)

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Explicitness** | 8/10 | Result types excellent, but some messages are strings |
| **Context** | 9/10 | Most errors include their context |
| **Predictability** | 9/10 | Very consistent type system |
| **Actionability** | 7/10 | Descriptive errors but lacks suggestions |
| **Stability** | 6/10 | Depends on class names and formatted strings |
| **Security** | 10/10 | Danger validation built-in |

**Overall Score: 8.2/10**

Excellent for a CLI tool, with specific improvements possible for AI agents.

---

## Priority Recommendations

### High Priority

1. **Add Stable Error Codes**
   - Implement `ErrorCode` enum
   - Add `error_code` field to all error types
   - Document codes in reference table

2. **Implement `to_dict()` Serialization**
   - Add JSON-serialization to all error types
   - Separate structured data from display messages
   - Enable machine-readable error output

3. **Use `match/case` Pattern Matching**
   - Refactor `handle_operation_error` to use Python 3.10+ match/case
   - Remove string-based type checking
   - Improve maintainability

### Medium Priority

4. **Add Automatic Suggestions**
   - Implement fuzzy matching for column names
   - Suggest corrections for common mistakes
   - Provide "Did you mean...?" hints

5. **Split Generic Errors**
   - Break down `CleaningError`, `TransformingError`, etc.
   - Create specific, actionable error types
   - Maintain error specificity

### Low Priority

6. **Create Error Reference Documentation**
   - Document all error types in central location
   - Include error codes, causes, and solutions
   - Add examples for each error type

7. **Add Error Recovery Hints**
   - Include retry suggestions where applicable
   - Document which errors are retryable
   - Provide recovery strategies

---

## Implementation Example

### Enhanced Error Type with All Recommendations

```python
from enum import IntEnum
from dataclasses import dataclass
from excel_toolkit.fp.immutable import immutable

class ErrorCode(IntEnum):
    """Stable error codes for programmatic handling."""
    COLUMN_NOT_FOUND = 1001
    COLUMN_MISMATCH = 1002
    QUERY_FAILED = 1003

@dataclass
@immutable
class ColumnNotFoundError:
    """Referenced column doesn't exist in DataFrame.

    Attributes:
        error_code: Stable numeric error code
        column: The column name that was not found
        available: List of available column names
    """
    error_code: int = ErrorCode.COLUMN_NOT_FOUND
    column: str
    available: list[str]

    @property
    def suggestion(self) -> str | None:
        """Suggest closest matching column name."""
        from difflib import get_close_matches
        matches = get_close_matches(
            self.column,
            self.available,
            n=1,
            cutoff=0.6
        )
        return matches[0] if matches else None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "error_type": "ColumnNotFoundError",
            "error_code": self.error_code,
            "column": self.column,
            "available": self.available,
            "suggestion": self.suggestion
        }

    def __str__(self) -> str:
        """Human-readable error message."""
        base = f"Column '{self.column}' not found. Available: {self.available}"
        if self.suggestion:
            base += f". Did you mean: '{self.suggestion}'?"
        return base
```

### Usage in Commands

```python
from excel_toolkit.fp import is_err, unwrap_err

result = apply_filter(df, condition)
if is_err(result):
    error = unwrap_err(result)

    # For AI agents: structured output
    if structured_output:
        typer.echo(json.dumps(error.to_dict(), indent=2), err=True)

    # For humans: readable message
    else:
        typer.echo(f"Error: {error}", err=True)

    raise typer.Exit(error.error_code)
```

---

## Conclusion

The Excel Toolkit's error handling system is **well-architected** with:
- Strong functional programming foundation
- Comprehensive error type coverage
- Good context inclusion in errors

With the recommended improvements, it would become **exceptional for AI agents** by adding:
- Stable error codes for programmatic handling
- JSON-serializable error structures
- Automatic suggestions and corrections
- More specific error types

The current system is already production-ready for CLI usage. The proposed enhancements would make it ideal for AI agent integration without breaking existing functionality.
