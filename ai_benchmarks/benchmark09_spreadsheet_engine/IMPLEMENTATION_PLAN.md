# Benchmark 009 — Spreadsheet Formula Engine Implementation Plan

**Date:** 2026-07-05  
**Evaluator:** Independent Senior Software Engineer

---

## Architecture Overview

- **No AST construction**: Recursive descent parser (precedence climbing) evaluates formulas on the fly, avoiding mutual recursion.
- **Workbook storage**: List-of-maps with integer keys (proven fast in B8) — rows as list indices, columns as map keys.
- **Formula evaluation**: Single `eval_full(tokens, pos, workbook, min_prec)` function handles all precedence levels via direct recursion. Function argument parsing inlined.
- **Dependency graph**: Built by extracting CELL token references from each formula's token stream. DFS white/gray/black cycle detection. Topological sort for evaluation order.
- **No mutual recursion**: All evaluator functions call `eval_full` (the same function), never a sibling that calls back.

## Data Structures

| Structure | Representation |
|-----------|---------------|
| **Workbook** | `list` of rows; each row is a `map` with integer column keys. |
| **Cell value** | A number, a string, or an error map `{"error": "#CODE!"}`. Formula cells store a map `{"type": "formula", "text": "...", "value": <evaluated>}`. |
| **Token** | `{"type": "NUMBER"/"CELL"/"OPERATOR"/"COMPARISON"/"FUNCTION"/"LPAREN"/"RPAREN"/"COMMA"/"COLON", "value": ...}` |
| **Dependency graph** | Map from cell key `"row,col"` to list of cell keys it depends on. |
| **DFS state** | Map from cell key to `0` (white), `1` (gray), or `2` (black). |

## Operator Precedence

| Precedence | Operators | Associativity |
|-----------|-----------|---------------|
| 1 (lowest) | `==` `!=` `<` `>` `<=` `>=` | Left |
| 2 | `+` `-` | Left |
| 3 (highest) | `*` `/` | Left |

## Function Reference

All functions are pure integer arithmetic. Strings in cells evaluate to 0 in arithmetic contexts.

| Function | Signature | Behavior |
|----------|-----------|----------|
| `SUM` | `SUM(range)` | Sum of numeric values in range |
| `AVG` | `AVG(range)` | Integer average (truncated) |
| `MIN` | `MIN(range)` | Minimum value in range |
| `MAX` | `MAX(range)` | Maximum value in range |
| `COUNT` | `COUNT(range)` | Count of non-empty cells |
| `IF` | `IF(cond, t, f)` | Returns `t` if `cond != 0`, else `f` |

Comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`) produce `1` (true) or `0` (false).

## Function Hierarchy (dependency order)

```
Level 0: Leaf utilities
  is_digit_char(ch) → bool
  is_letter_char(ch) → bool
  find_first_digit(s, start) → int

Level 1: Tokenizer
  make_token(type, value) → token
  classify_word(word) → "CELL"/"FUNCTION"/"UNKNOWN"
  collect_digits(text, pos) → {value, pos}
  collect_word(text, pos) → {word, pos}
  tokenize(text) → [tokens]

Level 2: Formula Evaluator (single self-recursive function)
  make_error(msg) → error_map
  error_or_val(val) → val or error check
  cell_ref_to_row_col(ref) → {row, col} or error
  op_precedence(token) → int
  apply_binary_op(a, tok, b) → number or error
  expand_range(start_key, end_key) → [cell_keys]
  eval_full(tokens, pos, workbook, min_prec) → result_map
    Handles: NUMBER, CELL, FUNCTION (SUM/AVG/MIN/MAX/COUNT/IF),
             LPAREN subexpr, binary operators, comparisons.
    IF args: 3 comma-separated expressions (recurse eval_full).
    Range functions: CELL:CELL expanded inline (no recursion).
  evaluate_formula(formula_text, workbook) → number or error

Level 3: Dependency Graph
  extract_cell_refs(tokens) → [cell_keys]
  build_graph(workbook, rows, cols) → {graph_map, error_cells}
  dfs_visit(node, graph, state, order) → bool (cycle flag)
  topological_sort(graph, all_formula_cells) → ordered_cells

Level 4: Workbook Engine
  create_workbook(rows, cols) → workbook
  set_constant(workbook, row, col, val) → void
  set_formula(workbook, row, col, text) → void
  get_cell_value(workbook, row, col) → number/string/error
  recalc_all(workbook) → void (builds graph, topo-sort, evaluates)

Level 5: Display
  cell_key_to_string(key) → "A1" style string
  print_workbook(workbook, rows, cols) → void

Level 6: Test Harness
  assert_equal(actual, expected, label) → bool
  run_test_simple_arithmetic() → bool
  run_test_cell_reference() → bool
  run_test_chained_formulas() → bool
  run_test_function_sum() → bool
  run_test_function_avg_min_max_count() → bool
  run_test_function_if() → bool
  run_test_comparisons() → bool
  run_test_circular_dependency() → bool
  run_test_error_propagation() → bool
  run_test_nested_expressions() → bool
  run_all_tests() → void
```

## Ordering Strategy

All functions are defined in strict dependency order (callee before caller). The single `eval_full` function handles all expression parsing recursively without calling any other AILang-defined function that could call it back. Function argument parsing is inlined within `eval_full`.

## Error Handling

| Condition | Error Code |
|-----------|-----------|
| Parse error | `#PARSE!` |
| Division by zero | `#DIV/0!` |
| Invalid cell reference | `#REF!` |
| Circular dependency | `#CIRC!` |
| Invalid value in arithmetic | `#VALUE!` |

---

## Revision Plan

| Iteration | Goal |
|:---------:|------|
| R1 | First compile — get basic structure working (empty workbook, no formulas) |
| R2 | Tokenizer + basic number evaluation |
| R3 | Full formula evaluator with binary ops and functions |
| R4 | Dependency graph + cycle detection + recalc_all |
| R5 | Test harness with all test cases passing |
