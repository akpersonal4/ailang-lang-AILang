# Development Log — Markdown to HTML Converter

## Application

- Name: Markdown to HTML Converter
- Location: `apps/markdown_parser/main.ail`
- Lines of Code: 518
- Functions: 38
- Modules Used: 5 (`list`, `map`, `string`, `file`, `convert`)

---

## Iteration Log

### Iteration 1 — First Compile

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Undefined identifier: find_any_of_helper, split_lines_helper, escape_html_helper, process_inline_helper, count_heading_marks, is_all_digits, count_same_chars, is_only_hr_chars, get_heading_tag, create_initial_state, process_lines_with_state, close_open_tags, join_lines` |
| Cause | All helper functions were defined after their callers. AILang does not support forward references. |
| Fix | Restructured entire file into dependency-ordered levels (Level 0 → Level 1 → ... → Level 7) |
| Time | 5 min |
| Classification | Language Limitation |

### Iteration 2 — Second Compile

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Duplicate declaration: remaining, len, char` and `Undefined identifier: text, start, lines, trimmed, first, process_inline` |
| Cause | Edit operations to fix Iteration 1 left orphaned duplicate function bodies in the file (from `split_lines_helper`, `escape_html_helper`, `is_hr_line_valid`, `process_inline_helper`). The compiler saw two copies of function logic. |
| Fix | Manually removed orphaned code blocks from the file. |
| Time | 3 min |
| Classification | User Error |

### Iteration 3 — Third Compile

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Undefined identifier: process_inline` |
| Cause | `process_inline_helper` calls `process_inline()` for recursive inner content processing. `process_inline` is a 1-line wrapper defined after the helper. |
| Fix | Replaced all `process_inline(text)` calls inside `process_inline_helper` with `process_inline_helper(text, 0, "")` to avoid forward reference. |
| Time | 1 min |
| Classification | Language Limitation |

### Iteration 4 — Fourth Compile

| Field | Value |
|-------|-------|
| Status | **PASS** |
| Time | — |

### Iteration 5 — First Runtime

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Runtime error: Function concat expected 2 arguments, got 3` |
| Cause | Image rendering code: `string.concat(a, b, c)` — `string.concat` only accepts 2 arguments. The link rendering had the same issue. |
| Fix | Nested `string.concat` calls correctly: `string.concat(string.concat(a, b), c)` |
| Time | 1 min |
| Classification | User Error |

### Iteration 6 — Second Runtime

| Field | Value |
|-------|-------|
| Status | **PASS** |
| Notes | All 13 markdown features produce correct HTML output. |
| Time | — |

---

## Summary

| Metric | Value |
|--------|-------|
| Compiler Iterations | 4 |
| Runtime Iterations | 2 |
| Total Revisions | 6 |
| Total Development Time | ~40 min |
| First Compile | FAIL |
| Final Compile | PASS |
| First Runtime | FAIL |
| Final Runtime | PASS |
