# Development Log — HTTP Request Parser

## Application

- Name: HTTP Request Parser
- Location: `apps/http_request_parser/main.ail`
- Lines of Code: 405
- Functions: 38
- Modules Used: 4 (`list`, `map`, `string`, `convert`)

---

## Iteration Log

### Iteration 1 — First Compile

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Undefined identifier: split_string_helper, normalize_line_endings_helper, parse_query_pairs, parse_request_line, parse_header_line, parse_headers_helper, parse_http_request, get_body_helper, get_content_length, get_body_from_lines, print_map_items, print_map, print_request, print_lines` |
| Cause | All helper and main functions were defined in natural top-down order (callers before callees). AILang does not support forward references — functions must appear in the file before any call site. |
| Fix | Restructured entire file into dependency-ordered levels (Level 0 → Level 1 → ... → Level 6) |
| Time | 5 min |
| Classification | Language Limitation |

### Iteration 2 — Second Compile

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Duplicate declaration: remaining, len, char` and `Undefined identifier: text, start, lines, trimmed, first, process_inline` |
| Cause | The edit tool left orphaned duplicate function bodies in the file from multiple edit passes. The compiler saw two copies of function logic with conflicting variable declarations, and some orphaned code referenced variables outside scope. |
| Fix | Manual cleanup pass: removed orphaned code blocks found after Level 1 functions. |
| Time | 3 min |
| Classification | User Error |

### Iteration 3 — Third Compile (Cleanup Pass 1)

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Duplicate declaration: remaining, len, char` still present |
| Cause | First cleanup pass missed some orphaned lines. An old copy of `normalize_line_endings_helper` body remained between `parse_query_pairs` and `get_body_helper`. |
| Fix | Second manual cleanup: identified and removed all remnants of old function bodies. |
| Time | 2 min |
| Classification | User Error |

### Iteration 4 — Fourth Compile (Cleanup Pass 2)

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Duplicate declaration: remaining` still present |
| Cause | A third orphaned fragment remained — a few lines of `split_string_helper` body were duplicated after the real `split_string` function. |
| Fix | Third manual cleanup: removed remaining duplicate lines. |
| Time | 1 min |
| Classification | User Error |

### Iteration 5 — Fifth Compile (Cleanup Pass 3)

| Field | Value |
|-------|-------|
| Status | **PASS** |
| Time | — |

### Iteration 6 — First Runtime

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `TypeError: list indices must be integers or slices, not str` thrown inside `map.set` during `parse_request_line` |
| Cause | Root cause: `_set_local` in `compiler/runtime/interpreter.py` used `environment.assign()` which traverses the parent scope chain, instead of `environment.define()` which creates a local variable. This caused all `let` declarations to leak to the global scope. When `split_string` did `let result = list.new()`, it overwrote the global `result` from the map stored during a previous function call. When `parse_request_line` later called `map.set(result, "method", ...)`, it tried to index a list with a string key, causing the `TypeError`. |
| Fix | Split `_set_local` into `_define_local` (uses `define` for `let` declarations) and `_assign_local` (uses `assign` for `=` reassignments). `VariableDeclarationIR` handler now calls `_define_local`; `AssignmentIR` handler calls `_assign_local`. |
| Time | 20 min (debugging) + 5 min (fix + verification) |
| Classification | Runtime Bug |

### Iteration 7 — Second Runtime (Verification)

| Field | Value |
|-------|-------|
| Status | **PASS** |
| Notes | All 4 sample requests parse correctly. All 512 existing tests pass with no regressions. Samples verified: |
| | Sample 1: Simple GET → method=GET, uri=/index.html, http_version=HTTP/1.1, 3 headers |
| | Sample 2: GET with query → uri=/search, qs=q=ailang&page=1&lang=en, 3 query params |
| | Sample 3: POST with JSON body → Content-Length=29, body={"name": "test", "value": 42} |
| | Sample 4: PUT request → Content-Length=25, body=title=Hello&content=World |
| Time | — |

---

## Summary

| Metric | Value |
|--------|-------|
| Compiler Iterations | 5 |
| Runtime Iterations | 2 |
| Total Revisions | 7 |
| Total Development Time | ~36 min |
| First Compile | FAIL |
| Final Compile | PASS |
| First Runtime | FAIL |
| Final Runtime | PASS |
