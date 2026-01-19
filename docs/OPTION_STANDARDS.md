# Excel Toolkit - Option Standards Reference

This document provides a comprehensive reference for option naming conventions across all xl commands.

## Standard Options Table

| Operation | Long Flag | Short Flag | Commands Using It |
|-----------|-----------|------------|-------------------|
| **Column Selection** | `--column` / `--columns` | `-c` | count, unique, select, stats, filter |
| **Group By** | `--by` | `-b` | group |
| **Limit Rows** | `--limit` | `-n` | head, filter, count |
| **Sort** | `--sort` | (none) | group, count, unique, sort |
| **Sort Order** | `--desc` / `--ascending` | `-d` / (none) | sort |
| **Output File** | `--output` | `-o` | all commands |
| **Sheet Name** | `--sheet` | `-s` | all Excel commands |
| **Format** | `--format` | `-f` | head, filter, stats, export |
| **Dry Run** | `--dry-run` | (none) | group, select, unique |

## Command-Specific Options

### `xl group`
```bash
--by, -b         Columns to group by
--aggregate, -a  Aggregations (column:func format)
--sort           Sort results (asc/desc)
--sort-column    Specific column to sort by
```

### `xl count`
```bash
--columns, -c    Columns to count
--sort           Sort by (count/name/none)
--ascending      Sort ascending
--limit, -n      Limit number of results
```

### `xl unique`
```bash
--columns, -c    Columns to get unique values from
--count          Show count of each value
```

### `xl select`
```bash
--columns, -c    Columns to select (comma-separated)
--exclude        Columns to exclude
--only-numeric    Select only numeric columns
```

### `xl sort`
```bash
--columns, -c    Column(s) to sort by
--desc, -d       Sort descending
--na-placement   Where to place NaN values
```

### `xl filter`
```bash
--columns, -c    Columns to keep after filtering
--rows, -n       Limit number of results
```

### `xl stats`
```bash
--column, -c     Specific column to analyze
--all-columns, -a Analyze all columns
```

### `xl extract` (New)
```bash
--column, -c     Datetime column to extract from
--parts, -p      Parts to extract (year,month,day,etc.)
--suffix         Suffix for new columns
```

### `xl calculate` (New)
```bash
--column, -c     Column to calculate on
--operation, -op Calculation (cumsum,growth,growth_pct,etc.)
```

## Usage Patterns by Task

### Task: Analyze a specific column
```bash
# Count occurrences
xl count data.xlsx -c "Category"

# Get unique values
xl unique data.xlsx -c "Category"

# Get statistics
xl stats data.xlsx -c "Sales"
```

### Task: Work with grouped data
```bash
# Group and aggregate
xl group sales.xlsx --by "Region" --aggregate "Sales:sum"

# Group with multiple aggregations
xl group sales.xlsx --by "Region" --aggregate "Sales:sum,mean,min,max"

# Group and sort
xl group sales.xlsx --by "Region" --aggregate "Sales:sum" --sort desc
```

### Task: Limit output
```bash
# First N rows
xl head data.xlsx -n 10

# Top N after counting
xl count data.xlsx -c "Category" --sort count -n 10

# Top N after grouping
xl group sales.xlsx --by "Product" --aggregate "Sales:sum" --sort desc
# Note: group doesn't have -n yet, use --limit or pipe to head
```

### Task: Date/time analysis
```bash
# Extract date components
xl extract sales.xlsx --column "Date" --parts "year,month,quarter"

# Calculate growth
xl calculate sales.xlsx --column "Revenue" --operation growth_pct
```

## Key Design Decisions

### Why `--by` for group instead of `-c`?
- `-c` is used for column selection in other commands
- Grouping is semantically different from selection
- `-b` (by) is the short flag, consistent with SQL GROUP BY

### Why `--columns` vs `--column`?
- Singular: When accepting ONE column (stats, extract, calculate)
- Plural: When accepting MULTIPLE columns (count, unique, select)
- Commands vary based on their primary use case

### Sort order inconsistency
- `xl sort` uses `--desc` / `--ascending` boolean flags
- Other commands use `--sort asc|desc`
- This is being standardized to `--sort [asc|desc]` format

### Sheet option `-s`
- Universally available across all Excel-reading commands
- No conflict with other short flags in context

## Migration Guide

### From inconsistent to consistent usage

#### Old way (still works):
```bash
xl group data.xlsx --by "Category" --aggregate "Sales:sum"
xl count data.xlsx --columns "Region"
xl sort data.xlsx --columns "Price" --desc
```

#### New consistent way:
```bash
# Use -b for group by (short for --by)
xl group data.xlsx -b "Category" -a "Sales:sum"

# Use -c for columns (where available)
xl count data.xlsx -c "Region"

# Sort uses --columns for column specification
xl sort data.xlsx -c "Price" -d
```

## Best Practices

### 1. Use short flags for interactive use
```bash
xl count sales.xlsx -c "Region" --sort count -n 10
```

### 2. Use long flags for scripts
```bash
xl count sales.xlsx --columns "Region" --sort count --limit 10
```

### 3. Quote column names with spaces
```bash
xl group sales.xlsx -b "Sales Region" -a "Revenue:sum"
```

### 4. Use column indexing for special characters
```bash
xl count sales.xlsx -c "3"  # Reference 3rd column by index
```

## Version History

- **v0.3.0**: Added `-b` short flag for `--by` in group
- **v0.3.0**: Added `-n` short flag for `--limit` in count
- **v0.3.0**: Documented option standards across all commands
- **v0.2.0**: Initial command implementations with various option names

## Future Standardization Plans

### Phase 1: Documentation (Current)
- ✅ Document all options in reference table
- ✅ Add usage patterns by task
- ✅ Provide migration guide

### Phase 2: Alias Addition (Planned)
- Add `-g` as additional alias for `--by` (group)
- Add `-c` alias for `--by` in group command
- Add deprecation warnings for old patterns

### Phase 3: Cleanup (Future)
- Remove deprecated flags after 2-3 version cycles
- Enforce consistent option naming in new commands
