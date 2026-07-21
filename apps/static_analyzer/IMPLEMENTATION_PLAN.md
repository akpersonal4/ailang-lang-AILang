# Implementation Plan — AILang Static Code Analyzer

## Benchmark: #013
## Date: 2026-07-06

---

## Architecture

The analyzer is a single AILang module (`main.ail`) that reads source files via the `file` stdlib, performs line-level static analysis, and emits formatted reports via `print()`.

No AST introspection is available — all analysis is pattern-matching on source lines.

## Data Model

```
analysis_result = {
  "file_results": [{
    "path": str,
    "source_stats": { "total_lines", "blank_lines", "comment_lines", "code_lines" },
    "functions": { "list": [{ "name", "line", "length", "params", "branches", "fanout" }],
                   "total", "avg_length", "longest_name", "longest_length", "duplicates" },
    "variables": { "per_fn": { fn_name: count }, "total", "duplicates" },
    "calls": { "counts": { callee: count }, "total", "unused", "recursive", "unreachable" },
    "modules": { "imports": [str], "total", "duplicates" },
    "complexity": { "max_depth", "high_branch", "large_funcs", "high_fanout" },
    "documentation": { "documented", "undocumented" }
  }],
  "aggregate": merged stats across files
}
```

## Parsing Strategy

No parser available — text-level pattern matching on each line:

| Pattern | Detection | Extracted |
|---------|-----------|-----------|
| Blank line | `string.length(stripped) == 0` | — |
| Comment line | starts with `//` | — |
| `fn name(params)` | starts with `fn ` | function name |
| `import module;` | starts with `import ` | module path |
| `let name = value` | starts with `let ` | variable name |
| `name(args)` | scan for `(` + backtrack to identifier | function name |

Call detection: scan each line for `(`, then backtrack to find identifier start. Skip AILang keywords (`fn`, `let`, `if`, `else`, `return`, `import`, `as`, `true`, `false`).

## Function Dependency Graph

```
Level 0:  find_substring, is_digit, is_letter, is_ident, is_keyword
Level 1:  find_ident_start, extract_call_name_at, split_string, join_strings, list_copy
Level 2:  strip_comment, is_blank_line, is_comment_line, is_fn_def, is_import, is_let,
          extract_fn_name, extract_import_path, extract_var_name
Level 3:  find_fn_defs, find_imports, find_let_decls, detect_duplicates,
          count_fn_lines, count_if_branches, count_calls_in_file, find_unused_fns,
          find_unreachable_fns
Level 4:  compute_source_stats, compute_fn_stats, compute_var_stats,
          compute_call_stats, compute_module_stats, compute_complexity,
          build_call_graph, compute_max_depth
Level 5:  format_report, generate_dep_tree, analyze_file, aggregate_results
Level 6:  main()
```

## Estimated LOC: 520–580
## Estimated Functions: 44–48

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Forward reference error | Medium | High | Strict bottom-up ordering, Level 0→6 |
| `find_substring` O(n²) on long lines | Medium | Low | Lines typically <200 chars |
| Call detection false positives | High | Medium | Filter keywords; limitation of text analysis |
| Recursion depth on large files | Low | Medium | Each file analyzed independently |
| No `list.sort` for ordered reports | Certain | Medium | Implement selection sort (~12 LOC) |
| `string.concat` 3-arg misuse | Low | High | Use `+` for all concatenations |
| Undefined stdlib assumption | Low | Medium | Stdlib audit: only documented APIs used |
| Map key mismatch | Medium | Medium | Single consistent key naming convention |

## Stdlib Audit

| Function | Needed | Status |
|----------|--------|--------|
| `string.length` | Yes | ✅ Stdlib |
| `string.substring` | Yes | ✅ Stdlib |
| `string.equals` | Yes | ✅ Stdlib |
| `string.contains` | Yes | ✅ Stdlib |
| `string.starts_with` | Yes | ✅ Stdlib |
| `string.trim` | Yes | ✅ Stdlib |
| `string.concat` | No | Use `+` operator instead |
| `string.split` | Yes | ❌ Write custom (pattern: `split_string`) |
| `string.find` | Yes | ❌ Write custom (pattern: `find_substring`) |
| `string.contains` | Yes | ✅ Stdlib |
| `list.new` | Yes | ✅ Stdlib |
| `list.append` | Yes | ✅ Stdlib |
| `list.get` | Yes | ✅ Stdlib |
| `list.len` | Yes | ✅ Stdlib |
| `list.contains` | Yes | ✅ Stdlib |
| `list.copy` | Yes | ❌ Write custom `list_copy` |
| `list.remove` | Maybe | ✅ Stdlib |
| `map.new` | Yes | ✅ Stdlib |
| `map.set` | Yes | ✅ Stdlib |
| `map.get` | Yes | ✅ Stdlib (guard with `map.has`) |
| `map.has` | Yes | ✅ Stdlib |
| `map.keys` | Yes | ✅ Stdlib |
| `file.exists` | Yes | ✅ Stdlib |
| `file.read` | Yes | ✅ Stdlib |
| `convert.to_string` | Yes | ✅ Stdlib |
| `environment.args` | Yes | ✅ Stdlib |
| `system.exit` | Yes | ✅ Stdlib |