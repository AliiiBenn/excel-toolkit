# Error Codes Reference

This document provides a complete reference of all error codes used in excel-toolkit, designed for AI agents and programmatic error handling.

## Overview

Error codes are stable numeric identifiers that enable reliable error handling without depending on error type names or messages. They are organized by category with specific numeric ranges:

- **1xxx**: Validation errors
- **2xxx**: Filtering errors
- **3xxx**: Sorting errors
- **4xxx**: Pivoting errors
- **5xxx**: Parsing errors
- **6xxx**: Aggregation errors
- **7xxx**: Comparison errors
- **8xxx**: Cleaning errors
- **9xxx**: Transforming errors
- **10xxx**: Joining errors
- **11xxx**: Validation operation errors
- **12xxx**: File handler errors

## Using Error Codes

### Python Usage

```python
from excel_toolkit.models import ErrorCode, ColumnNotFoundError, error_to_dict

# Create an error
error = ColumnNotFoundError(column="Age", available=["Name", "Email"])

# Access error code directly
print(error.ERROR_CODE)  # 1011

# Use ErrorCode enum
print(ErrorCode.COLUMN_NOT_FOUND)  # 1011

# Serialize to dict (includes ERROR_CODE)
error_dict = error_to_dict(error)
print(error_dict["ERROR_CODE"])  # 1011

# Check error category programmatically
from excel_toolkit.models import get_error_category
category = get_error_category(ErrorCode.COLUMN_NOT_FOUND)
print(category)  # "VALIDATION"
```

### AI Agent Usage

AI agents can use error codes to:

1. **Identify error types programmatically** without parsing error messages
2. **Implement retry logic** based on error categories
3. **Provide automatic suggestions** using fuzzy matching
4. **Create error handling workflows** for specific error codes

```python
# Example: AI agent error handling
from excel_toolkit.models import ErrorCode, error_to_dict

error_dict = error_to_dict(error)
error_code = error_dict["ERROR_CODE"]

# Handle specific errors
match error_code:
    case ErrorCode.COLUMN_NOT_FOUND:
        # Check for suggestions
        if "suggestions" in error_dict:
            suggested_column = error_dict["suggestions"][0]["suggestions"][0]
            print(f"Did you mean '{suggested_column}'?")
    case ErrorCode.INVALID_FUNCTION:
        # Provide function name correction
        suggested = error_dict["suggestions"][0]["suggestions"][0]
        print(f"Did you mean '{suggested}'?")
    case _:
        # Generic error handling
        print(f"Error code: {error_code}")
```

## Error Codes by Category

### Validation Errors (1001-1013)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 1001 | `DANGEROUS_PATTERN` | `DangerousPatternError` | Condition contains dangerous code pattern |
| 1002 | `CONDITION_TOO_LONG` | `ConditionTooLongError` | Condition exceeds maximum allowed length |
| 1003 | `UNBALANCED_PARENTHESES` | `UnbalancedParenthesesError` | Condition has unbalanced parentheses |
| 1004 | `UNBALANCED_BRACKETS` | `UnbalancedBracketsError` | Condition has unbalanced brackets |
| 1005 | `UNBALANCED_QUOTES` | `UnbalancedQuotesError` | Condition has unbalanced quotes |
| 1006 | `INVALID_FUNCTION` | `InvalidFunctionError` | Invalid aggregation function name |
| 1007 | `NO_COLUMNS` | `NoColumnsError` | No columns specified for an operation |
| 1008 | `NO_ROWS` | `NoRowsError` | No row columns specified for pivot operation |
| 1009 | `NO_VALUES` | `NoValuesError` | No value columns specified for pivot operation |
| 1010 | `INVALID_PARAMETER` | `InvalidParameterError` | Invalid parameter provided |
| 1011 | `COLUMN_NOT_FOUND` | `ColumnNotFoundError` | Referenced column doesn't exist in DataFrame |
| 1012 | `COLUMNS_NOT_FOUND` | `ColumnsNotFoundError` | Multiple columns don't exist in DataFrame |
| 1013 | `OVERLAPPING_COLUMNS` | `OverlappingColumnsError` | Group and aggregation columns overlap |

**Example**:
```python
from excel_toolkit.models import ColumnNotFoundError, ErrorCode

error = ColumnNotFoundError(column="Agge", available=["Name", "Age", "Email"])
print(error.ERROR_CODE)  # 1011
print(ErrorCode.COLUMN_NOT_FOUND)  # 1011
```

### Filtering Errors (2001-2002)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 2001 | `QUERY_FAILED` | `QueryFailedError` | Query execution failed |
| 2002 | `COLUMN_MISMATCH` | `ColumnMismatchError` | Type mismatch in comparison |

### Sorting Errors (3001-3002)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 3001 | `NOT_COMPARABLE` | `NotComparableError` | Cannot sort mixed data types in column |
| 3002 | `SORT_FAILED` | `SortFailedError` | Sorting failed |

### Pivoting Errors (4001-4004)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 4001 | `ROW_COLUMNS_NOT_FOUND` | `RowColumnsNotFoundError` | Row columns don't exist for pivot |
| 4002 | `COLUMN_COLUMNS_NOT_FOUND` | `ColumnColumnsNotFoundError` | Column columns don't exist for pivot |
| 4003 | `VALUE_COLUMNS_NOT_FOUND` | `ValueColumnsNotFoundError` | Value columns don't exist for pivot |
| 4004 | `PIVOT_FAILED` | `PivotFailedError` | Pivot table creation failed |

### Parsing Errors (5001-5002)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 5001 | `INVALID_FORMAT` | `InvalidFormatError` | Invalid format for parsing |
| 5002 | `NO_VALID_SPECS` | `NoValidSpecsError` | No valid specifications found |

### Aggregation Errors (6001-6003)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 6001 | `GROUP_COLUMNS_NOT_FOUND` | `GroupColumnsNotFoundError` | Group columns don't exist |
| 6002 | `AGG_COLUMNS_NOT_FOUND` | `AggColumnsNotFoundError` | Aggregation columns don't exist |
| 6003 | `AGGREGATION_FAILED` | `AggregationFailedError` | Aggregation operation failed |

### Comparison Errors (7001-7003)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 7001 | `KEY_COLUMNS_NOT_FOUND` | `KeyColumnsNotFoundError` | Key columns don't exist in first DataFrame |
| 7002 | `KEY_COLUMNS_NOT_FOUND_2` | `KeyColumnsNotFoundError2` | Key columns don't exist in second DataFrame |
| 7003 | `COMPARISON_FAILED` | `ComparisonFailedError` | Comparison operation failed |

### Cleaning Errors (8001-8003)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 8001 | `CLEANING_FAILED` | `CleaningError` | Generic cleaning operation failed |
| 8002 | `INVALID_FILL_STRATEGY` | `InvalidFillStrategyError` | Invalid fill strategy specified |
| 8003 | `FILL_FAILED` | `FillFailedError` | Fill operation failed |

**Example with automatic suggestions**:
```python
from excel_toolkit.models import InvalidFillStrategyError, error_to_dict
import json

error = InvalidFillStrategyError(
    strategy="forwards",
    valid_strategies=["forward", "backward", "mean", "median"]
)

error_dict = error_to_dict(error)
print(json.dumps(error_dict, indent=2))
# {
#   "error_type": "InvalidFillStrategyError",
#   "ERROR_CODE": 8002,
#   "strategy": "forwards",
#   "valid_strategies": ["forward", "backward", "mean", "median"],
#   "suggestions": [
#     {
#       "field": "strategy",
#       "provided": "forwards",
#       "suggestions": ["forward"]
#     }
#   ]
# }
```

### Transforming Errors (9001-9005)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 9001 | `INVALID_EXPRESSION` | `InvalidExpressionError` | Invalid expression provided |
| 9002 | `INVALID_TYPE` | `InvalidTypeError` | Invalid type specified for casting |
| 9003 | `CAST_FAILED` | `CastFailedError` | Casting operation failed |
| 9004 | `TRANSFORMING_FAILED` | `TransformingError` | Generic transforming operation failed |
| 9005 | `INVALID_TRANSFORMATION` | `InvalidTransformationError` | Invalid transformation name |

### Joining Errors (10001-10006)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 10001 | `INVALID_JOIN_TYPE` | `InvalidJoinTypeError` | Invalid join type specified |
| 10002 | `INVALID_JOIN_PARAMETERS` | `InvalidJoinParametersError` | Invalid combination of join parameters |
| 10003 | `JOIN_COLUMNS_NOT_FOUND` | `JoinColumnsNotFoundError` | Join columns not found in DataFrames |
| 10004 | `MERGE_COLUMNS_NOT_FOUND` | `MergeColumnsNotFoundError` | Merge columns not found in all DataFrames |
| 10005 | `INSUFFICIENT_DATAFRAMES` | `InsufficientDataFramesError` | Less than 2 DataFrames provided for merge |
| 10006 | `JOINING_FAILED` | `JoiningError` | Generic joining operation failed |

### Validation Operation Errors (11001-11005)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 11001 | `VALUE_OUT_OF_RANGE` | `ValueOutOfRangeError` | Values outside specified range |
| 11002 | `NULL_VALUE_THRESHOLD_EXCEEDED` | `NullValueThresholdExceededError` | Null values exceed threshold |
| 11003 | `UNIQUENESS_VIOLATION` | `UniquenessViolationError` | Duplicate values found |
| 11004 | `INVALID_RULE` | `InvalidRuleError` | Invalid validation rule |
| 11005 | `TYPE_MISMATCH` | `TypeMismatchError` | Column type doesn't match expected type |

### File Handler Errors (12001-12006)

| Code | Constant Name | Error Type | Description |
|------|--------------|------------|-------------|
| 12001 | `FILE_NOT_FOUND` | - | File not found |
| 12002 | `FILE_ACCESS_ERROR` | - | File access error |
| 12003 | `UNSUPPORTED_FORMAT` | - | Unsupported file format |
| 12004 | `INVALID_FILE` | - | Invalid file |
| 12005 | `FILE_SIZE_ERROR` | - | File size error |
| 12006 | `ENCODING_ERROR` | - | Encoding error |

## Automatic Suggestions

Some error types include automatic suggestions using fuzzy matching to help correct typos:

### Supported Error Types

- `ColumnNotFoundError`: Suggests similar column names
- `ColumnsNotFoundError`: Suggests similar column names for each missing column
- `InvalidFunctionError`: Suggests similar function names
- `InvalidFillStrategyError`: Suggests similar fill strategies
- `InvalidTypeError`: Suggests similar type names
- `InvalidTransformationError`: Suggests similar transformations
- `InvalidJoinTypeError`: Suggests similar join types
- `InvalidParameterError`: Suggests similar parameter values

### Example Usage

```python
from excel_toolkit.models import ColumnNotFoundError, error_to_dict

# Typo in column name
error = ColumnNotFoundError(column="Aeg", available=["Name", "Age", "Email"])
error_dict = error_to_dict(error)

# Access suggestions
if "suggestions" in error_dict:
    for suggestion in error_dict["suggestions"]:
        print(f"Field: {suggestion['field']}")
        print(f"Provided: {suggestion['provided']}")
        print(f"Did you mean: {suggestion['suggestions']}?")

# Output:
# Field: column
# Provided: Aeg
# Did you mean: ['Age']?
```

## Error Categories

Errors can be categorized programmatically using `get_error_category`:

```python
from excel_toolkit.models import ErrorCode, get_error_category

# Get error category
category = get_error_category(ErrorCode.COLUMN_NOT_FOUND)
print(category)  # "VALIDATION"

category = get_error_category(ErrorCode.CLEANING_FAILED)
print(category)  # "CLEANING"
```

### Available Categories

- `VALIDATION`: Input validation errors (1xxx)
- `FILTERING`: Filtering operation errors (2xxx)
- `SORTING`: Sorting operation errors (3xxx)
- `PIVOTING`: Pivoting operation errors (4xxx)
- `PARSING`: Parsing errors (5xxx)
- `AGGREGATION`: Aggregation operation errors (6xxx)
- `COMPARISON`: Comparison operation errors (7xxx)
- `CLEANING`: Cleaning operation errors (8xxx)
- `TRANSFORMING`: Transforming operation errors (9xxx)
- `JOINING`: Joining operation errors (10xxx)
- `VALIDATION_OPERATION`: Validation operation errors (11xxx)
- `FILE_HANDLER`: File handler errors (12xxx)

## Best Practices for AI Agents

1. **Use error codes for programmatic handling**
   ```python
   if error_dict["ERROR_CODE"] == ErrorCode.COLUMN_NOT_FOUND:
       # Handle column not found
       pass
   ```

2. **Check for automatic suggestions**
   ```python
   if "suggestions" in error_dict:
       # Present suggestions to user or apply automatically
       pass
   ```

3. **Use error categories for retry logic**
   ```python
   category = get_error_category(error_code)
   if category == "VALIDATION":
       # Don't retry validation errors - they won't fix themselves
       pass
   elif category == "FILE_HANDLER":
       # Might retry file handler errors (temporal issues)
       pass
   ```

4. **Log error codes for debugging**
   ```python
   print(f"Error {error_dict['ERROR_CODE']}: {error_dict['error_type']}")
   ```

5. **Map error codes to user-friendly messages**
   ```python
   error_messages = {
       ErrorCode.COLUMN_NOT_FOUND: "The specified column doesn't exist",
       ErrorCode.INVALID_FUNCTION: "Invalid aggregation function",
       # ... more mappings
   }
   message = error_messages.get(error_code, "An error occurred")
   ```

## Stability Guarantee

Error codes are guaranteed to remain stable across versions. New error codes may be added, but existing codes will never be changed or removed. This ensures that programmatic error handling remains reliable over time.

## See Also

- [Error Handling Analysis](./issues/ERROR_HANDLING_ANALYSIS.md) - Detailed analysis of error handling quality
- [Source Code](../excel_toolkit/models/error_codes.py) - ErrorCode enum definition
- [Error Types](../excel_toolkit/models/error_types.py) - All error type definitions
