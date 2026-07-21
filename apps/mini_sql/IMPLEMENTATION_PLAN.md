# Mini SQL Engine — Implementation Plan

## Overview

Build a lightweight SQL query engine in AILang that parses and executes SQL queries against in-memory tables loaded from CSV files.

## Supported SQL Syntax

```sql
SELECT [DISTINCT] column1, column2, ...
FROM table.csv
[WHERE condition [AND/OR condition ...]]
[ORDER BY column [ASC|DESC]]
[LIMIT n]
```

### Condition expressions:
- `column = value`, `column != value`
- `column < value`, `column <= value`
- `column > value`, `column >= value`
- `condition AND condition`
- `condition OR condition`
- String literals: `'value'`
- Numeric literals: `42`

## Architecture

```
SQL text → Tokenizer → Token list → Parser → Query map
                                                      ↓
CSV file → Table Loader → Table map → Executor → Result rows → Display
```

## Data Structures (AILang maps + lists)

### Token
```ail
{"type": "KEYWORD", "value": "SELECT"}
{"type": "IDENTIFIER", "value": "name"}
{"type": "OPERATOR", "value": "="}
{"type": "STRING", "value": "Alice"}
{"type": "NUMBER", "value": 42}
{"type": "COMMA", "value": ","}
{"type": "STAR", "value": "*"}
{"type": "LPAREN", "value": "("}
{"type": "RPAREN", "value": ")"}
{"type": "EOF", "value": ""}
```

### Query
```ail
{
  "command": "SELECT",
  "columns": ["name", "age"],       // or ["*"]
  "table": "employees.csv",
  "distinct": false,
  "where": ,                        // condition tree or None
  "order_by": "name",
  "order_dir": "ASC",
  "limit": 10
}
```

### Condition node
```ail
{"op": "AND", "left": ..., "right": ...}
{"op": "=", "left": "column_name", "right": "value"}
{"op": ">", "left": "column_name", "right": 30}
```

### Table
```ail
{"columns": ["name", "age"], "rows": [row1, row2, ...]}
```

### Row
```ail
{"name": "Alice", "age": "30"}
```

## Implementation Order

| Step | Component | Description |
|------|-----------|-------------|
| 1 | String Utilities | `find_substring`, `split_string`, `trim`, `to_upper` |
| 2 | Tokenizer | Recursive tokenizer for SQL text |
| 3 | Parser | Recursive descent SQL parser |
| 4 | Table Loader | CSV loading via `csv.parse_header` and `file.read` |
| 5 | Executor | WHERE filter, ORDER BY, LIMIT, DISTINCT, COUNT, column projection |
| 6 | Display | Formatted tabular output |
| 7 | Main | CLI entry point, error handling |

## AILang Features Used

- `string`: `concat`, `contains`, `equals`, `length`, `starts_with`, `substring`, `trim`, `uppercase`, `lowercase`
- `list`: `new`, `append`, `get`, `len`, `contains`, `clear`
- `map`: `new`, `set`, `get`, `has`, `delete`, `keys`, `clear`
- `convert`: `to_int`, `to_string`
- `csv`: `parse_header`
- `file`: `read`, `exists`
- `io`: `write`, `writeln`
- `print` builtin
- Recursion for all iteration
- `if/else` for control flow
- Comparison operators: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Logical operators: `&&`, `||`, `!`
- Arithmetic: `+` (string concat), `-`, `<`, `>`

## Known Language Limitations

| Limitation | Impact |
|------------|--------|
| No loops | All iteration via recursion; higher LOC |
| No regex | String matching via `string.contains`, `starts_with`, `ends_with` |
| No `string.split()` | Custom `split_string` via `find_substring` recursion |
| No float literals | All numeric constants must be integers |
| No `while`/`for` | Recursion depth limited (~1200 frames) |
| No exception handling | Runtime errors propagate as Python exceptions |
