# CSV ETL Pipeline — AI Usage Guide

## Overview

Demonstrates CSV parsing, field validation, and data transformation in AILang using `csv.parse_header` for structured row access.

## Key Patterns

### CSV Parsing with Header

`csv.parse_header` returns a list of maps where each map's keys are the CSV column names:

```
let rows = csv.parse_header(raw_content);
let first = list.get(rows, 0);
let name = map.get(first, "name");
```

### Validation Pattern

Validate each row recursively, collecting valid rows into an accumulator list.
Return `1` for valid, `0` for invalid (function return type defaults to `INT_TYPE`):

```
fn validate_row(row_data, row_index) {
    let name_val = map.get(row_data, "name");
    if (string.length(string.trim(name_val)) == 0) { return 0 }
    1
}

fn validate_rows_helper(rows, idx, acc) {
    if (idx >= list.len(rows)) { return acc }
    let row = list.get(rows, idx);
    if (validate_row(row, idx) == 1) {
        list.append(acc, row);
    }
    validate_rows_helper(rows, idx + 1, acc)
}
```

### Field Normalization

Chain `string.trim` and `string.lowercase` for normalization:

```
fn normalize_field(value) {
    let trimmed = string.trim(value);
    string.lowercase(trimmed)
}
```

### Transform to New Map

Always create a new map for transformed rows — never mutate the original:

```
fn transform_row(row) {
    let raw = map.get(row, "field");
    let clean = normalize(raw);
    let result = map.new();
    map.set(result, "field", clean);
    result
}
```

## AI Notes

- `csv.parse_header` handles delimiter detection and header extraction automatically
- Empty CSV fields parse as empty strings — check with `string.length(string.trim(val)) == 0`
- AILang functions default to `INT_TYPE` return — use `return 0`/`return 1`, not `return false`/`return true`
- `if` conditions must be `BOOL_TYPE` — use `if (validate_row(...) == 1)` not `if (is_valid)`
- Wrap arithmetic on stdlib results with `convert.to_int` to avoid TYP001
- `list.append` mutates in place and returns the modified list
