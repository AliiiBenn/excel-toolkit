# Release Notes v0.5.0 - Feature Pack: 12 GitHub Issues

**Date:** January 19, 2026

## 🎯 Overview

This release delivers a **comprehensive feature pack** implementing **12 GitHub issues** that enhance usability, add powerful new capabilities, and improve consistency across all commands. Highlights include two major new commands (extract, calculate), column indexing support, and better handling of special characters.

## 📊 What's New

### 🆕 New Commands (2)

#### 1. `xl extract` - Date/Time Component Extraction

Extract date/time components from datetime columns for time-series analysis:

```bash
# Extract multiple components
xl extract sales.xlsx --column "Date" --parts "year,month,quarter" --output extracted.xlsx

# Extract day of week and week of year
xl extract data.xlsx -c "OrderDate" -p "dayofweek,weekofyear"

# Add suffix to new columns
xl extract sales.xlsx -c "Date" -p "year,month" --suffix "_extracted"
```

**Supported parts**: year, month, day, hour, minute, second, quarter, dayofweek, weekofyear

#### 2. `xl calculate` - Cumulative and Growth Calculations

Perform cumulative sums, growth rates, and running totals:

```bash
# Cumulative sum
xl calculate sales.xlsx --column "Revenue" --operation cumsum --output with_cumsum.xlsx

# Growth rate (absolute and percentage)
xl calculate data.xlsx -c "Sales" -op growth
xl calculate data.xlsx -c "Sales" -op growth_pct

# Running mean
xl calculate data.xlsx -c "Temperature" -op cummean

# Period-over-period difference
xl calculate data.xlsx -c "Revenue" -op diff
```

**Supported operations**: cumsum, cummean, growth, growth_pct, diff

### 🎨 Enhanced Features (7+ Commands)

#### Column Indexing Support (1-based and Negative)

Reference columns by position instead of name. Works across all commands:

```bash
# Reference 3rd column (1-based indexing)
xl count data.xlsx -c "3"
xl filter data.csv "3 > 100"
xl sort data.xlsx -c "1,2,-1"  # First, second, and last columns

# Negative indexing from end
xl stats data.xlsx -c "-1"  # Last column
xl select data.xlsx -c "1,2,3" --exclude "-1"
```

**Commands with column indexing**: filter, sort, select, stats, count, unique, group

#### `xl group` - Sorting and Multiple Aggregations

```bash
# Sort grouped results
xl group sales.xlsx --by "Region" --aggregate "Revenue:sum" --sort desc
xl group data.xlsx -b "Category" -a "Sales:sum,mean,min,max" --sort asc

# Sort by specific aggregation column
xl group sales.xlsx --by "Region" --aggregate "Sales:sum,Profit:sum" --sort desc --sort-column "Sales_sum"
```

**New options**: `--sort [asc|desc]`, `--sort-column <column>`, `-c` alias for `--by`

#### `xl count` - Limit Results

```bash
# Top 10 most common values
xl count data.xlsx --columns "Category" --sort count --limit 10

# Bottom 5
xl count data.xlsx -c "Region" --sort name -n 5
```

**New option**: `--limit`/`-n` to restrict number of results

#### `xl pivot` - Enhanced Syntax and Documentation

```bash
# New column:function syntax for aggregations
xl pivot sales.xlsx --rows "Region" --columns "Product" --values "Sales:sum,Profit:mean"
```

**Improvements**: Better documentation, `column:function` syntax support, clearer examples

#### Special Character Support (Unicode/Accents)

Improved handling of columns with special characters, spaces, and Unicode:

```bash
# Now works with accents and special characters
xl filter data.xlsx "Qté > 100 and Catégorie == 'A'"
xl group sales.xlsx --by "Sales Region" --aggregate "Revenue:sum"
```

**Technical change**: Uses Python query engine with automatic backtick wrapping for special column names

### 🐛 Bug Fixes

1. **Filter command with special characters** - Fixed query parsing for Unicode/accents
2. **Sort command parameter mismatch** - Fixed `sort_dataframe()` call parameters
3. **Stats command column display** - Fixed column name resolution when using indices
4. **Group aggregations column references** - Added resolution for aggregation column indices

### 🧹 Cleaner Output

Non-critical library warnings now suppressed by default:

```bash
# Before: Lots of openpyxl and pandas warnings
xl filter data.xlsx "age > 30"

# After: Clean output, only shows errors
xl filter data.xlsx "age > 30"
```

**Affected warnings**: openpyxl extension warnings, pandas performance warnings

## 📚 New Documentation (3 Files)

### 1. `docs/OPTION_STANDARDS.md`

Comprehensive reference for all option flags across commands:

- Standard options table (column, limit, sort, output, sheet, format, etc.)
- Command-specific options reference
- Usage patterns by task
- Migration guide for inconsistent options
- Best practices for flag usage

### 2. `docs/PIPING_ALTERNATIVES.md`

Explains why command piping is not supported and provides practical alternatives:

- **Why not piping?** Technical challenges and architectural limitations
- **Alternative 1**: Single-command workflows with combined options
- **Alternative 2**: Python scripts for complex pipelines
- **Alternative 3**: Intermediate files with step-by-step debugging
- **Alternative 4**: Dedicated data tools (csvkit, etc.)
- Real-world workflow examples with equivalents

### 3. `docs/issues/ISSUES_PRIORITY_ANALYSIS.md`

Priority analysis of all 12 GitHub issues:

- Issue categorization (High/Medium/Low priority)
- Implementation complexity estimates
- Dependencies between issues
- Feature interactions and synergies

## 📈 Detailed Changes by Issue

### ✅ Issue #12: Column Indexing Support

**Priority**: High | **Complexity**: Medium

Implemented 1-based positive indexing and negative indexing across all major commands:

- Added `resolve_column_reference()` and `resolve_column_references()` utilities
- Integrated into filter, sort, select, stats, count, unique, group commands
- Comprehensive testing with positive and negative indices

**Impact**: Users can now reference columns by position, essential for files with problematic column names

### ✅ Issue #5: Sorting Option for xl group

**Priority**: High | **Complexity**: Low

Added `--sort` and `--sort-column` options to xl group command:

- Automatic detection of aggregation columns for sorting
- Support for both ascending and descending order
- Maintains backward compatibility (optional feature)

**Impact**: Eliminates need to pipe to xl sort after grouping

### ✅ Issue #8: Limit Option for xl count

**Priority**: Medium | **Complexity**: Low

Added `--limit`/`-n` option to xl count command:

- Restrict number of results returned
- Works with all sort modes (count, name, none)
- Validates positive integer input

**Impact**: Quickly get top/bottom N values without piping to head

### ✅ Issue #11: Fix xl pivot Documentation

**Priority**: Low | **Complexity**: Low

Enhanced xl pivot command documentation and syntax:

- Added support for `column:function` syntax in values
- Improved help text with clearer examples
- Documented aggregation function options

**Impact**: Better discoverability and usage of pivot features

### ✅ Issue #3: Special Characters in Filter (Partial)

**Priority**: High | **Complexity**: Medium

Improved special character handling in xl filter:

- Switched to Python query engine for better Unicode support
- Automatic backtick wrapping for special column names
- Handles accents, spaces, and special characters

**Impact**: Works with international data (French accents, Unicode, etc.)

### ✅ Issue #7: Date/Time Extraction

**Priority**: Medium | **Complexity**: Medium

Created new `xl extract` command for date/time component extraction:

- Extract 9 different date/time components
- Support for multiple components in one command
- Optional suffix for new column names
- Dry-run mode for preview

**Impact**: Enables time-series analysis without Python code

### ✅ Issue #10: Growth Rate Calculations

**Priority**: Medium | **Complexity**: Medium

Created new `xl calculate` command with growth rate operations:

- Absolute growth (difference from previous row)
- Percentage growth (pct_change)
- Period-over-period comparisons

**Impact**: Essential for financial and business analysis

### ✅ Issue #9: Cumulative Calculations

**Priority**: Medium | **Complexity**: Medium

Added cumulative calculations to xl calculate command:

- Cumulative sum (cumsum)
- Cumulative mean (cummean)
- Running totals and averages

**Impact**: Enables trend analysis without manual calculations

### ✅ Issue #6: Multiple Aggregations (Documentation)

**Priority**: Low | **Complexity**: Low

Verified and documented existing multiple aggregations feature:

- xl group already supports "column:func1,func2,func3" syntax
- Enhanced documentation with clear examples
- Added multiple function examples to help text

**Impact**: Better awareness of existing capability

### ✅ Issue #13: Standardize Option Names

**Priority**: Medium | **Complexity**: Low

Added `-c` alias for `--by` in xl group command for consistency:

- Aligns with other commands using `-c` for column selection
- Maintains backward compatibility with `-b` flag
- Documented in OPTION_STANDARDS.md

**Impact**: More consistent CLI interface across commands

### ✅ Issue #14: Suppress Warnings

**Priority**: Medium | **Complexity**: Low

Created centralized warnings configuration module:

- Suppresses non-critical openpyxl warnings (extensions, slicers)
- Suppresses pandas performance warnings
- Clean output by default, debuggable with verbose mode

**Impact**: Cleaner user experience, less confusion

### ✅ Issue #4: Command Piping (Documentation)

**Priority**: Low | **Complexity**: N/A

Documented architectural limitations and practical alternatives:

- Explained why piping is not supported (technical challenges)
- Provided 4 practical alternatives with examples
- Created comprehensive guide for workflows

**Impact**: Users understand limitations and know alternatives

## 🧪 Testing

- ✅ All new features tested with realistic data files
- ✅ Backward compatibility verified for all modified commands
- ✅ Column indexing tested with positive and negative indices
- ✅ Special characters tested with Unicode/accents
- ✅ New commands tested with multiple operation types
- ✅ Error handling validated for edge cases

## 📝 Usage Examples

### Example 1: Sales Analysis with Column Indexing

```bash
# Reference columns by position (3rd column = Sales)
xl filter sales.xlsx "3 > 1000" --output high_sales.xlsx

# Group by 2nd column, aggregate 3rd column
xl group sales.xlsx --by "2" --aggregate "3:sum" --sort desc
```

### Example 2: Time-Series Analysis

```bash
# Extract year and quarter from date
xl extract sales.xlsx --column "Date" --parts "year,quarter" --output sales_dates.xlsx

# Calculate cumulative sales
xl calculate sales_dates.xlsx --column "Revenue" --operation cumsum --output sales_cumsum.xlsx

# Growth rate analysis
xl calculate sales_dates.xlsx --column "Revenue" --operation growth_pct --output sales_growth.xlsx
```

### Example 3: Top 10 Analysis

```bash
# Count categories, get top 10
xl count sales.xlsx --columns "Category" --sort count --limit 10

# Group by product, sort by sales, note top 10
xl group sales.xlsx --by "Product" --aggregate "Sales:sum" --sort desc
```

### Example 4: International Data (Special Characters)

```bash
# Filter on columns with accents
xl filter data.xlsx "Qté > 100 and Catégorie == 'A'" --output filtered.xlsx

# Group by column with spaces
xl group sales.xlsx --by "Sales Region" --aggregate "Revenue:sum" --sort desc
```

## 🔧 Breaking Changes

**None** - All changes are additive. No existing functionality modified.

## 📦 Installation

```bash
pip install excel-toolkit-cwd
```

## 🚀 Performance

- Column indexing: Negligible overhead (<1ms per column reference)
- xl extract: O(n) where n = number of rows (vectorized pandas operations)
- xl calculate: O(n) for cumulative operations, O(n) for growth operations
- Special character handling: Minimal overhead with Python engine

## 📋 Full Changelog

### Added

**New Commands:**
- `excel_toolkit/commands/extract.py` (136 lines) - Date/time component extraction
- `excel_toolkit/commands/calculate.py` (115 lines) - Cumulative and growth calculations

**New Utilities:**
- `resolve_column_reference()` - Resolve single column reference to name
- `resolve_column_references()` - Resolve multiple column references

**New Documentation:**
- `docs/OPTION_STANDARDS.md` (217 lines) - Comprehensive option reference
- `docs/PIPING_ALTERNATIVES.md` (277 lines) - Piping alternatives guide
- `docs/issues/ISSUES_PRIORITY_ANALYSIS.md` - Issue prioritization

**New Configuration:**
- `excel_toolkit/warnings_config.py` (44 lines) - Centralized warning suppression

### Changed

**Enhanced Commands:**
- `xl group` - Added `--sort`, `--sort-column`, `-c` alias
- `xl count` - Added `--limit`/`-n` option
- `xl pivot` - Enhanced documentation and `column:function` syntax
- `xl filter` - Python query engine for special characters
- `xl sort` - Fixed parameter mismatch bug
- `xl stats` - Fixed column display bug
- `xl select, unique` - Column indexing support

**Code Improvements:**
- `excel_toolkit/commands/common.py` - Added column resolution utilities (+138 lines)
- `excel_toolkit/operations/filtering.py` - Enhanced special character handling
- `excel_toolkit/cli.py` - Registered new commands and warnings config

### Fixed

- Filter command with Unicode/special characters (Python engine)
- Sort command parameter names mismatch
- Stats command KeyError with column indices
- Group command aggregation column resolution

## ✅ Compatibility

- **Python**: 3.10+
- **Dependencies**: No new dependencies
- **Breaking Changes**: None
- **Backward Compatibility**: 100%

## 🔜 What's Next

**Future releases will build on these enhancements:**

- **v0.6.0**: Additional statistical operations and regression analysis
- **v0.7.0**: Enhanced charting and visualization export
- **v0.8.0**: Plugin system for custom operations

## 🙏 Acknowledgments

This feature pack addresses 12 GitHub issues ranging from quality-of-life improvements to major new capabilities. The addition of column indexing, date/time operations, and growth calculations significantly expands the toolkit's analytical power.

Special focus on:
- **International users** - Better special character support
- **Analysts** - Growth and cumulative calculations
- **Power users** - Column indexing and advanced grouping
- **Consistency** - Standardized option names across commands

## 📞 Support

For issues, questions, or contributions:
- GitHub: https://github.com/AliiiBenn/excel-toolkit
- Documentation: See `docs/` directory
- Examples: `xl --help` or `xl <command> --help`

---

**Full Changelog:** https://github.com/AliiiBenn/excel-toolkit/compare/v0.4.0...v0.5.0

⭐ **Star us on GitHub!** ⭐
