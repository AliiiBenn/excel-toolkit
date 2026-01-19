# Command Piping - Status and Alternatives

## Status: Not Implemented (Architectural Limitation)

Command piping (`|`) is not currently supported due to significant architectural requirements. This document explains the limitation and provides practical alternatives.

## Why Piping is Not Supported

### Technical Challenges

1. **Excel Format Preservation**: xl commands read/write Excel format (.xlsx, .xls). Piping would require:
   - Keeping Excel format in memory between commands
   - Converting to intermediate formats (CSV, parquet, pickle)
   - Managing temporary files internally

2. **All Commands Need Modification**: Every command would need:
   - stdin/stdout handling
   - Format detection and conversion
   - Error handling for broken pipes
   - Backward compatibility maintenance

3. **Memory Concerns**: Large Excel files (100MB+) would:
   - Consume significant memory in pipelines
   - Risk OOM errors with multi-stage pipelines
   - Require sophisticated streaming/caching

4. **Type Information Loss**: Excel metadata (types, formats, formulas) can be lost in conversions

### Estimated Effort

- **Minimum**: 2-3 weeks of development
- **Full Implementation**: 1-2 months
- **Testing & Refinement**: Ongoing

## Practical Alternatives

### Alternative 1: Single-Command Workflow (Recommended)

Many "piped" workflows can be accomplished with single commands:

#### Instead of: filter → group → sort
```bash
# What you want:
xl filter data.xlsx "Circuit == 'GP'" | xl group --by "Product" --aggregate "Qty:sum" | xl sort --desc

# Do this instead (one command):
xl group data.xlsx --by "Circuit,Product" --aggregate "Qty:sum" --sort desc
```

#### Instead of: filter → head
```bash
# What you want:
xl filter data.xlsx "Sales > 1000" | xl head -n 10

# Do this instead:
xl filter data.xlsx "Sales > 1000" --rows 10
```

#### Instead of: filter → count → sort
```bash
# What you want:
xl filter data.xlsx "Circuit == 'GP'" | xl count --by "Product" --sort count -n 10

# Do this instead:
xl count data.xlsx --columns "Circuit,Product" --sort count --limit 10
# Then filter results manually or use xl select
```

### Alternative 2: Python Script (For Complex Pipelines)

For complex multi-step workflows, use Python directly:

```python
import pandas as pd

# Read Excel
df = pd.read_excel('data.xlsx', sheet_name='DONNEES')

# Pipeline
df = df[df['Circuit'] == 'GP']  # filter
result = df.groupby('Product')['Qty'].sum().reset_index()  # group
result = result.sort_values('Qty', ascending=False)  # sort
top_10 = result.head(10)  # limit

# Save or display
top_10.to_excel('output.xlsx', index=False)
print(top_10)
```

### Alternative 3: Intermediate Files (Current Workflow)

For complex workflows, use intermediate files:

```bash
# Step 1: Filter
xl filter data.xlsx "Circuit == 'GP'" --output step1_filtered.xlsx

# Step 2: Group
xl group step1_filtered.xlsx --by "Product" --aggregate "Qty:sum" --output step2_grouped.xlsx

# Step 3: Sort
xl sort step2_grouped.xlsx --by "Qty_sum" --order desc --output step3_sorted.xlsx

# Step 4: View top results
xl head step3_sorted.xlsx -n 10

# Cleanup (optional)
rm step1_filtered.xlsx step2_grouped.xlsx step3_sorted.xlsx
```

**Pros:**
- Works today with existing xl commands
- Easy to debug each step
- Can save intermediate results for inspection

**Cons:**
- More verbose
- Slower (multiple I/O operations)
- Requires cleanup

### Alternative 4: Use Dedicated Data Tools

For complex pipelines, consider tools designed for piping:

```bash
# Convert to CSV first, then use Unix tools
xl export data.xlsx --output data.csv
cat data.csv | csvgrep -c "Circuit == 'GP'" | csvstat --group-by "Product"
```

Or use Python/pandas directly (see Alternative 2).

## Common Pipeline Patterns and xl Equivalents

### Pattern 1: Filter → Group → Sort

**Desired Pipeline:**
```bash
xl filter data.xlsx "condition" | xl group --by "col" | xl sort --desc
```

**xl Equivalent:**
```bash
# Use xl group with --where option (if available) or pre-filter
xl group data.xlsx --by "col" --aggregate "value:sum" --sort desc
# Then manually inspect or filter results
```

### Pattern 2: Filter → Limit

**Desired Pipeline:**
```bash
xl filter data.xlsx "condition" | xl head -n 10
```

**xl Equivalent:**
```bash
xl filter data.xlsx "condition" --rows 10
```

### Pattern 3: Count → Sort → Limit

**Desired Pipeline:**
```bash
xl count data.xlsx --columns "Category" | xl sort --by count --desc | xl head -n 10
```

**xl Equivalent:**
```bash
xl count data.xlsx --columns "Category" --sort count --limit 10
```

## Feature Requests That Would Reduce Piping Need

The following features would make piping less necessary:

1. ✅ **Column filtering in group** (Issue #5 - COMPLETED)
   - `xl group ... --sort desc` eliminates need for separate sort step

2. ✅ **Limit in count** (Issue #8 - COMPLETED)
   - `xl count ... --limit 10` eliminates need for pipe to head

3. ✅ **Row filtering** (filter command --rows option)
   - `xl filter ... --rows 10` eliminates need for pipe to head

4. ✅ **Multiple aggregations** (Issue #6 - COMPLETED)
   - `xl group ... --aggregate "Sales:sum,mean,min,max"` eliminates multiple group steps

## When to Use Each Alternative

| Use Case | Best Approach | Why |
|----------|---------------|-----|
| Simple filter+limit | Use filter --rows | One command, fast |
| Multi-aggregation | Use group with multiple funcs | Already supported |
| Complex workflow | Use Python script | Full flexibility, no limits |
| Debugging workflow | Use intermediate files | Can inspect each step |
| Quick analysis | Use single-command options | Fastest, less typing |
| Production pipeline | Use Python script | Reliable, testable |

## Examples: Real-World Workflows

### Example 1: Top 10 Products by Sales (GP Circuit)

**With Piping (Not Supported):**
```bash
xl filter sales.xlsx "Circuit == 'GP'" | \
xl group --by "Product" --aggregate "Sales:sum" | \
xl sort --by "Sales_sum" --desc | \
xl head -n 10
```

**Recommended Approach:**
```bash
# Single command with sorting
xl group sales.xlsx --by "Product" --aggregate "Sales:sum" --sort desc
# Then manually note top 10, or use Python for exact top-N
```

**Python Alternative:**
```python
import pandas as pd
df = pd.read_excel('sales.xlsx')
result = df[df['Circuit'] == 'GP'].groupby('Product')['Sales'].sum()
result = result.sort_values(ascending=False).head(10)
print(result)
```

### Example 2: Filter → Transform → Export

**With Piping (Not Supported):**
```bash
xl filter data.xlsx "Sales > 1000" | \
xl transform --multiply "Sales:1.1" | \
xl export --output result.xlsx
```

**Recommended Approach:**
```bash
# Use intermediate files
xl filter data.xlsx "Sales > 1000" --output filtered.xlsx
xl transform filtered.xlsx --multiply "Sales:1.1" --output result.xlsx
rm filtered.xlsx
```

## Future Considerations

### Possible Implementation (If Demand Grows)

A minimal piping implementation could support:

1. **CSV-only pipelines**: Convert to CSV once, pipe through CSV-aware commands
2. **Memory-based mode**: Optional flag to keep data in memory (for small files)
3. **Explicit pipe syntax**: `xl chain` command to build pipelines declaratively

### Vote for This Feature

If piping is critical for your workflow, please:
1. Comment on Issue #4 with your use case
2. Upvote the issue on GitHub repository
3. Provide examples of workflows that require piping

## Conclusion

While command piping is not currently supported, xl toolkit provides powerful single-command alternatives that accomplish most common data analysis tasks efficiently.

For complex multi-step workflows, consider:
1. Using Python/pandas directly (maximum flexibility)
2. Intermediate files (easy to debug)
3. Combining multiple xl options in single commands

The trade-off between piping convenience and implementation complexity means this feature is unlikely to be implemented in the near term unless there is significant user demand.

## Related Documentation

- **OPTION_STANDARDS.md**: Consistent option naming across commands
- **README.md**: Getting started with xl toolkit
- **Issue #4**: Original feature request and discussion
