# Excel Toolkit - Implementation Roadmap

**Last Updated:** 2026-01-16
**Status:** Phase 1 COMPLETE ✅ | Phase 2 COMPLETE ✅ | Phase 3 PENDING ⏸️

---

## Overview

This roadmap tracks the implementation of the operations layer for the Excel Toolkit. The operations layer separates business logic from CLI concerns, enabling:
- Unit testing without CLI dependencies
- Code reuse in pipelines and templates
- Import by external packages
- Clear separation of concerns

**Current Progress:**
- ✅ Phase 1: 100% complete (5/5 core operations)
- ✅ Phase 2: 100% complete (4/4 support operations)

---

## Phase 1: Core Operations (✅ COMPLETE)

**Status:** 5/5 operations implemented
**Completed:** 2026-01-16
**Priority:** CRITICAL

### ✅ Completed Operations

#### 1. Immutable Dataclass Decorator
**File:** `excel_toolkit/fp/immutable.py`
**Status:** ✅ Complete
**Tests:** 39 passing
**Commit:** `d740279`

Features:
- `@immutable` decorator for frozen dataclasses
- Must be applied AFTER `@dataclass` decorator
- Creates immutable data structures

#### 2. Error Type ADTs
**File:** `excel_toolkit/models/error_types.py`
**Status:** ✅ Complete
**Tests:** 39 passing
**Commit:** `d740279`

Error Types (20+):
- Validation Errors (12 types)
- Filter Errors (4 types)
- Sort Errors (2 types)
- Pivot Errors (4 types)
- Parse Errors (3 types)
- Aggregation Errors (3 types)
- Compare Errors (3 types)

#### 3. Filtering Operations
**File:** `excel_toolkit/operations/filtering.py`
**Status:** ✅ Complete
**Tests:** 46 passing
**Commit:** `3fabc0f`

Functions:
- `validate_condition()` - Security and syntax validation
- `normalize_condition()` - Transform user syntax to pandas
- `apply_filter()` - Apply filter with column selection and limits
- `_extract_column_name()` - Helper function

Features:
- Security validation against dangerous patterns (import, exec, eval, __, etc.)
- Syntax validation (balanced parentheses, brackets, quotes)
- Max condition length check (1000 characters)
- Normalization: "is None" → `.isna()`, "between X and Y" → ">= X and <= Y"
- Column selection after filtering
- Row limiting

#### 4. Sorting Operations
**File:** `excel_toolkit/operations/sorting.py`
**Status:** ✅ Complete
**Tests:** 23 passing
**Commit:** `6b3c2bb`

Functions:
- `validate_sort_columns()` - Column existence validation
- `sort_dataframe()` - Sort with multiple options

Features:
- Single and multi-column sorting
- Ascending and descending order
- NaN placement control (first/last)
- Row limiting
- Mixed type error detection

#### 5. Pivoting Operations
**File:** `excel_toolkit/operations/pivoting.py`
**Status:** ✅ Complete
**Tests:** 56 passing
**Commit:** `da246eb`

Functions:
- `validate_aggregation_function()` - Function validation and normalization
- `validate_pivot_columns()` - Column existence validation
- `parse_fill_value()` - Fill value parsing (None, 0, nan, int, float, string)
- `flatten_multiindex()` - MultiIndex flattening for columns and index
- `create_pivot_table()` - Create pivot tables

Features:
- 11 aggregation functions (sum, mean, avg→mean, count, min, max, median, std, var, first, last)
- Multiple rows, columns, and values
- Fill value handling
- MultiIndex flattening
- Column name generation

#### 6. Aggregating Operations
**File:** `excel_toolkit/operations/aggregating.py`
**Status:** ✅ Complete
**Tests:** 38 passing
**Commit:** `86848cb`

Functions:
- `parse_aggregation_specs()` - Parse "column:func1,func2" format
- `validate_aggregation_columns()` - Validate columns exist and don't overlap
- `aggregate_groups()` - Groupby and aggregation

Features:
- Smart parsing with stateful handling of functions
- Normalizes "avg" to "mean"
- Merges duplicate column specs
- 11 aggregation functions
- MultiIndex flattening with trailing underscore removal
- Empty group handling

#### 7. Comparing Operations
**File:** `excel_toolkit/operations/comparing.py`
**Status:** ✅ Complete
**Tests:** 44 passing
**Commit:** `318719a`

Functions:
- `validate_key_columns()` - Validate key columns exist in both DataFrames
- `compare_rows()` - Compare two rows for equality with NaN handling
- `find_differences()` - Find added, deleted, and modified rows
- `build_comparison_result()` - Build result DataFrame with status column
- `compare_dataframes()` - Main comparison function

Features:
- Key columns or row position comparison
- NaN equality handling (NaN == NaN is OK)
- MultiIndex support via dict conversion
- Comprehensive difference tracking
- Status column ("added", "deleted", "modified", "unchanged")
- Column ordering (keys, status, others)

---

### ✅ Phase 1 Summary

**All 5 core operations completed:**

1. ✅ Filtering Operations (46 tests, commit `3fabc0f`)
2. ✅ Sorting Operations (23 tests, commit `6b3c2bb`)
3. ✅ Pivoting Operations (56 tests, commit `da246eb`)
4. ✅ Aggregating Operations (38 tests, commit `86848cb`)
5. ✅ Comparing Operations (44 tests, commit `318719a`)

**Total Statistics:**
- 207 tests passing
- 5 core operations implemented
- 5 commits (atomic per operation)
- ~3,500 lines of production code
- ~3,000 lines of test code
- Zero CLI dependencies in operations
- All operations return Result types for explicit error handling
- Comprehensive error types with immutable dataclasses
- Full test coverage of all error paths

**Key Achievements:**
- ✅ Complete separation of business logic from CLI
- ✅ Unit testable without CLI dependencies
- ✅ Reusable in pipelines and templates
- ✅ Importable by external packages
- ✅ Type-safe error handling with Result types
- ✅ Immutable error data structures
- ✅ Comprehensive test coverage
- ✅ All operations follow consistent patterns

---

## Phase 2: Support Operations (✅ COMPLETE)

**Status:** 4/4 operations implemented
**Completed:** 2026-01-16
**Priority:** Medium

### ✅ Completed Operations

#### 1. Cleaning Operations
**File:** `excel_toolkit/operations/cleaning.py`
**Status:** ✅ Complete
**Tests:** 57 passing
**Commit:** `0048fbc`

Functions:
- `trim_whitespace()` - Trim whitespace from string columns
- `remove_duplicates()` - Remove duplicate rows
- `fill_missing_values()` - Fill missing values with various strategies
- `standardize_columns()` - Standardize column names
- `clean_dataframe()` - Apply multiple cleaning operations

Features:
- Multiple fill strategies (forward, backward, mean, median, constant, drop)
- Column name standardization (lower, upper, title, snake case)
- Special character removal option
- Support for dict-based strategies per column
- Handles NaN values appropriately

#### 2. Transforming Operations
**File:** `excel_toolkit/operations/transforming.py`
**Status:** ✅ Complete
**Tests:** 52 passing
**Commit:** `e3b5476`

Functions:
- `apply_expression()` - Apply pandas expressions to create/modify columns
- `cast_columns()` - Cast columns to specified types
- `transform_column()` - Apply mathematical transformations

Features:
- Expression validation with security checks (blocks dangerous patterns)
- Support for arithmetic, string concatenation, and method call expressions
- Type casting for int, float, str, bool, datetime, category
- 6 built-in mathematical transformations (log, sqrt, abs, exp, standardize, normalize)
- Custom callable transformation support
- Comprehensive error handling for edge cases

#### 3. Joining Operations
**File:** `excel_toolkit/operations/joining.py`
**Status:** ✅ Complete
**Tests:** 33 passing
**Commit:** `343a7a0`

Functions:
- `validate_join_columns()` - Validate join columns exist in DataFrames
- `join_dataframes()` - Join two DataFrames with various join types
- `merge_dataframes()` - Merge multiple DataFrames sequentially

Features:
- Support for all join types (inner, left, right, outer, cross)
- Column validation for join operations
- Left/right column specification for asymmetric joins
- Index-based joins
- Custom suffixes for overlapping columns
- Sequential merging of multiple DataFrames
- Special handling for cross joins and empty DataFrames

#### 4. Validation Operations
**File:** `excel_toolkit/operations/validation.py`
**Status:** ✅ Complete
**Tests:** 53 passing
**Commit:** `c310d53`

Functions:
- `validate_column_exists()` - Validate that columns exist in DataFrame
- `validate_column_type()` - Validate column data types
- `validate_value_range()` - Validate values are within range
- `check_null_values()` - Check null values with threshold enforcement
- `validate_unique()` - Validate uniqueness of columns or combinations
- `validate_dataframe()` - Apply multiple validation rules with comprehensive reporting

Features:
- Column existence validation (single or multiple columns)
- Type checking for int, float, str, bool, datetime, numeric
- Value range validation with min/max bounds and allow_equal option
- Null value detection with percentage thresholds
- Uniqueness validation with ignore_null option
- Rule-based validation supporting 5 rule types (column_exists, column_type, value_range, unique, null_threshold)
- ValidationReport with passed/failed counts and detailed error/warning lists
- Empty DataFrame handling
- Multiple column combination validation

### ✅ Phase 2 Summary

**All 4 support operations completed:**

1. ✅ Cleaning Operations (57 tests, commit `0048fbc`)
2. ✅ Transforming Operations (52 tests, commit `e3b5476`)
3. ✅ Joining Operations (33 tests, commit `343a7a0`)
4. ✅ Validation Operations (53 tests, commit `c310d53`)

**Total Statistics:**
- 195 tests passing
- 4 support operations implemented
- 4 commits (atomic per operation)
- ~2,000 lines of production code
- ~1,800 lines of test code
- Zero CLI dependencies in operations
- All operations return Result types for explicit error handling
- Comprehensive error types with immutable dataclasses
- Full test coverage of all error paths

**Key Achievements:**
- ✅ Complete separation of business logic from CLI
- ✅ Unit testable without CLI dependencies
- ✅ Reusable in pipelines and templates
- ✅ Importable by external packages
- ✅ Type-safe error handling with Result types
- ✅ Immutable error data structures
- ✅ Comprehensive test coverage
- ✅ All operations follow consistent patterns
- ✅ Security validation for expression evaluation
- ✅ Flexible fill strategies for missing data
- ✅ Support for all pandas join types
- ✅ Comprehensive validation rules

---

## Phase 3: Command Refactoring (Not Started)

**Status:** 0/23 command files
**Estimated:** 2-3 days
**Priority:** High

### Commands to Refactor

For each command file:
1. Remove business logic
2. Import from operations
3. Keep only CLI concerns
4. Update error handling to use Result types
5. Reduce to <100 lines each

**Commands Using Implemented Operations:**
- `commands/filter.py` → Use `operations/filtering.py`
- `commands/sort.py` → Use `operations/sorting.py`

**Commands Pending Operations Implementation:**
- `commands/pivot.py` → Use `operations/pivoting.py`
- `commands/aggregate.py` → Use `operations/aggregating.py`
- `commands/compare.py` → Use `operations/comparing.py`

**Other Commands to Refactor:**
- `commands/clean.py` → Use `operations/cleaning.py`
- `commands/dedupe.py` → Use `operations/cleaning.py`
- `commands/fill.py` → Use `operations/cleaning.py`
- `commands/strip.py` → Use `operations/cleaning.py`
- `commands/transform.py` → Use `operations/transforming.py`
- `commands/join.py` → Use `operations/joining.py`
- `commands/merge.py` → Use `operations/joining.py`
- `commands/append.py` → Use `operations/joining.py`
- `commands/validate.py` → Use `operations/validation.py`

---

## Phase 4: Testing Infrastructure (Partially Complete)

**Status:** Phase 1 & 2 tests complete (402 tests total)
**Estimated:** 1-2 days for integration tests
**Priority:** High

### Test Coverage Goals

**Unit Tests:**
- [x] Error types (39 tests)
- [x] Filtering operations (46 tests)
- [x] Sorting operations (23 tests)
- [x] Pivoting operations (56 tests)
- [x] Aggregating operations (38 tests)
- [x] Comparing operations (44 tests)
- [x] Cleaning operations (57 tests)
- [x] Transforming operations (52 tests)
- [x] Joining operations (33 tests)
- [x] Validation operations (53 tests)

**Total: 441 unit tests passing**

**Target:** >90% code coverage (Phase 1 & 2 complete)

**Integration Tests:**
- Command workflow tests
- File I/O tests
- Format conversion tests

**Test Fixtures:**
- Sample Excel files
- Sample CSV files
- Edge case files (empty, large files, special characters)

---

## Phase 5: Documentation (Not Started)

**Estimated:** 1 day
**Priority:** Medium

### Documentation Tasks

- [ ] Update API documentation
- [ ] Add architecture diagrams
- [ ] Create contribution guide (CONTRIBUTING.md)
- [ ] Document operations layer patterns
- [ ] Add usage examples for each operation
- [ ] Document Result type patterns

---

## Success Metrics

### Quantitative
- [x] 5 core operation modules created
- [x] 4 support operation modules created
- [x] 50+ functions implemented (60+ functions)
- [x] 400+ unit tests written (441 tests)
- [x] >90% test coverage
- [x] Zero CLI dependencies in operations
- [ ] All commands reduced to <100 lines

### Qualitative
- [x] Clear separation of concerns
- [x] Reusable business logic
- [x] Type-safe error handling
- [ ] Comprehensive documentation
- [x] All tests passing

---

## Dependencies

**Blockers:**
- None - operations can be implemented independently

**Recommended Order:**
1. Pivoting (most complex of remaining)
2. Aggregating (medium complexity)
3. Comparing (most complex overall)

**Can Be Done in Parallel:**
- Test writing alongside implementation
- Documentation alongside development

---

## Risks and Mitigations

### High Risk
- **Security in filtering** - ⚠️ Partially addressed
  - Risk: Code injection through pandas.eval()
  - Mitigation: Comprehensive validation implemented, needs review

### Medium Risk
- **Type handling in sorting** - ✅ Addressed
  - Risk: Mixed type columns cause crashes
  - Mitigation: Pre-validation and clear errors implemented

- **Memory usage in comparing** - ⚠️ Pending
  - Risk: Large DataFrames cause memory issues
  - Mitigation: Will need chunking/streaming (Phase 3)

### Low Risk
- **MultiIndex flattening** - ⚠️ Pending
  - Risk: Column name collisions
  - Mitigation: Thorough testing required

---

## Next Steps

### Immediate (Next Session)

1. **Begin Phase 3: Command Refactoring**
   - [ ] Update `commands/filter.py` to use `operations/filtering.py`
   - [ ] Update `commands/sort.py` to use `operations/sorting.py`
   - [ ] Update `commands/pivot.py` to use `operations/pivoting.py`
   - [ ] Update `commands/aggregate.py` to use `operations/aggregating.py`
   - [ ] Update `commands/compare.py` to use `operations/comparing.py`
   - [ ] Update `commands/clean.py` to use `operations/cleaning.py`
   - [ ] Update `commands/transform.py` to use `operations/transforming.py`
   - [ ] Update `commands/join.py` to use `operations/joining.py`
   - [ ] Update `commands/validate.py` to use `operations/validation.py`

2. **Run Integration Tests**
   - [ ] Verify all commands work with operations layer
   - [ ] Fix any broken tests

### Medium Term (Future Sessions)

1. **Complete Command Refactoring**
   - All commands using operations layer
   - Reduce all command files to <100 lines

2. **Documentation**
   - API documentation
   - Architecture updates
   - Contribution guide

---

## Implementation Guidelines

### Code Style
- Follow existing patterns in filtering.py and sorting.py
- Use Result types for all fallible operations
- Comprehensive type hints
- Detailed docstrings
- Handle all error cases

### Testing Requirements
- Test all success paths
- Test all error paths
- Test edge cases (empty, NaN, single row, etc.)
- Test integration between functions
- Use fixtures for test data

### Commit Strategy
- Atomic commits per operation module
- Commit tests with implementation
- Write clear commit messages
- No push until complete

---

## Resources

### Design Documents
- `docs/issues/ISSUE_001_OPERATIONS_LAYER.md` - Detailed issue analysis
- `docs/issues/PHASE_1_DETAILED_SPEC.md` - Complete Phase 1 specification
- `docs/issues/MAIN.md` - All issues analysis

### Code References
- `excel_toolkit/operations/filtering.py` - Example implementation
- `excel_toolkit/operations/sorting.py` - Example implementation
- `excel_toolkit/models/error_types.py` - All error types

### Test References
- `tests/unit/operations/test_filtering.py` - Example test suite
- `tests/unit/operations/test_sorting.py` - Example test suite

---

**Total Estimated Time for Phase 1 & 2 Completion:** 8-12 hours
**Actual Time Invested:** ~10 hours
**Status:** ✅ Phase 1 COMPLETE (5 operations, 207 tests)
**Status:** ✅ Phase 2 COMPLETE (4 operations, 195 tests)
**Total:** 9 operations, 441 tests, 9 atomic commits
