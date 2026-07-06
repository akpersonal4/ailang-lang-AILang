# Benchmark Report — HTTP Request Parser

## Application Summary

| Attribute | Value |
|-----------|-------|
| Name | HTTP Request Parser |
| Purpose | Parse HTTP/1.1 request strings into structured AILang data — extract method, URI, query parameters, headers, and body |
| Lines of Code | 405 |
| Functions | 38 |
| Modules Used | 4 (`list`, `map`, `string`, `convert`) |

## Development Metrics

| Metric | Result |
|--------|--------|
| First Compile | FAIL |
| Final Compile | PASS |
| First Runtime | FAIL |
| Final Runtime | PASS |
| Compiler Iterations | 5 |
| Runtime Iterations | 2 |
| Total Revisions | 7 |
| Development Time | ~36 min |

## Features Implemented

| Feature | Status | Details |
|---------|--------|---------|
| Method extraction (GET, POST, PUT) | ✅ | Extracts from first space-delimited token |
| URI parsing with query string split | ✅ | Split on `?`, separate path and query_string |
| Query parameter parsing | ✅ | Split on `&` then `=`, stored in map |
| HTTP version extraction | ✅ | Third token from request line |
| Header parsing (key: value) | ✅ | Handles `: ` and `:` separators with `trim_cr` |
| Content-Length extraction | ✅ | Case-sensitive and lowercase fallback |
| Host, User-Agent, Content-Type fields | ✅ | Convenience accessors on parsed result |
| Body extraction by Content-Length | ✅ | Bytes-accumulating recursion with line tracking |
| CRLF line ending normalization | ✅ | `\r\n` → `\n` normalization before parsing |
| Empty body for GET requests | ✅ | Content-Length=0 returns empty body |

## Architecture — 7 Dependency Levels

```
Level 0: No-dependency utilities
├── find_substring(text, start, pattern)    — linear search for substring
├── is_empty_line(line)                     — whitespace-only line check
└── trim_cr(line)                           — strip trailing \r

Level 1: String splitting
├── split_string_helper(text, delim, start, result)  — recursive delimiter split
├── split_string(text, delim)                         — wrapper creating list
├── normalize_line_endings_helper(text, i, result)    — \r\n → \n
├── normalize_line_endings(text)                      — wrapper
└── split_lines(text)                                 — full line split

Level 2: Parsing primitives
├── parse_query_pairs(pairs, i, params)    — iterate &-split pairs, split on =
├── parse_query_string(qs)                 — split & → parse pairs → map
├── parse_request_line(line)               — split space → extract method/uri/version
└── parse_header_line(line)                — split on : → key/value map

Level 3: Header parsing
├── parse_headers_helper(lines, i, headers)  — iterate lines, parse until blank
└── parse_headers_from_lines(lines, start)   — wrapper

Level 4: Full request parsing
├── parse_http_request(text)                 — orchestrate all parsing stages
├── get_body_helper(lines, i, bytes, cl, result)  — accumulate body by Content-Length
├── get_body_from_lines(lines, start, cl)         — wrapper
└── get_content_length(headers)                   — extract numeric Content-Length

Level 5: Display
├── print_map_items(map, i, keys)            — print key:value pairs
├── print_map(map, label)                    — label + formatted map output
└── print_request(req)                       — full formatted request dump

Level 6: Sample data and entry point
├── print_lines(lines, i)                    — debug line printer
└── main()                                   — 4 sample requests + execution
```

## Sample Outputs

All 4 sample requests produce correct parsed output:

### Sample 1: Simple GET
```
=== Parsed HTTP Request ===
Method: GET
URI: /index.html
Query String:
HTTP Version: HTTP/1.1
Headers:
    Accept: text/html
    Host: example.com
    User-Agent: AILang/0.1
Content-Length: 0
Body: (empty)
```

### Sample 2: GET with Query
```
=== Parsed HTTP Request ===
Method: GET
URI: /search
Query String: q=ailang&page=1&lang=en
HTTP Version: HTTP/1.1
Query Parameters:
    q: ailang
    page: 1
    lang: en
Headers:
    Host: api.example.com
    User-Agent: curl/8.0
Content-Length: 0
Body: (empty)
```

### Sample 3: POST with JSON Body
```
=== Parsed HTTP Request ===
Method: POST
URI: /api/data
Query String:
HTTP Version: HTTP/1.1
Headers:
    Content-Type: application/json
    Content-Length: 29
    Host: api.example.com
Content-Length: 29
Body: {"name": "test", "value": 42}
```

### Sample 4: PUT Request
```
=== Parsed HTTP Request ===
Method: PUT
URI: /notes/1
Query String:
HTTP Version: HTTP/1.1
Headers:
    Content-Length: 25
    Content-Type: application/x-www-form-urlencoded
    Host: localhost:8080
Content-Length: 25
Body: title=Hello&content=World
```

## Language Evaluation

| Category | Score (1–10) |
|----------|:---:|
| Documentation | 8 |
| Compiler Diagnostics | 5 |
| Standard Library | 6 |
| Ease of Development | 4 |
| AI Friendliness | 6 |

## Classified Issues

### Compiler Bug (0)
None found.

### Runtime Bug (1)

| Attribute | Value |
|-----------|-------|
| **Title** | Variable scoping: `_set_local` uses `assign` instead of `define` |
| **Description** | `let` declarations leak to global scope because `_set_local` in `interpreter.py` uses `environment.assign()` (traverses parent scope chain) instead of `environment.define()` (creates local variable). When `split_string` does `let result = list.new()`, it overwrites the global `result` with a list. A subsequent call expecting `result` to be a map fails with `TypeError: list indices must be integers or slices, not str`. |
| **Root Cause** | `compiler/runtime/interpreter.py` — the `_set_local` method used `environment.assign()` for both `let` declarations and `=` reassignments. |
| **Fix** | Split into `_define_local` (uses `define()`, for `let`) and `_assign_local` (uses `assign()`, for `=`). `VariableDeclarationIR` → `_define_local`. `AssignmentIR` → `_assign_local`. |
| **Impact** | Affects ALL AILang programs that use `let` with the same variable name across different functions. This is a fundamental language implementation defect. |
| **Regressions** | None — all 512 existing tests pass after the fix. |

### Language Limitation (2)

| # | Issue | Impact |
|---|-------|--------|
| 1 | **No forward references** — all 5 compiler iterations were caused by forward reference errors. Functions must be ordered bottom-up (callees before callers). For a 405-line file with 38 functions and 7 dependency levels, this added significant structural overhead. | 5 compiler iterations, ~11 min wasted |
| 2 | **No loops (while/for)** — String scanning requires recursive helper functions for every iteration pattern. `find_substring` (lines 13–21) scans character-by-character with recursion. `split_string_helper` (lines 41–52) builds a list recursively. `get_body_helper` (lines 188–205) accumulates body lines recursively. | Verbose, harder to optimize |

### Missing Standard Library (0)
None found — `list`, `map`, `string`, and `convert` modules provided everything needed.

### Documentation Gap (0)
None found.

### Poor Compiler Diagnostic (0)
None found.

### User Error (1)

| # | Issue | Description |
|---|-------|-------------|
| 1 | **Orphaned duplicate code from edit tool** | Multiple edit passes left orphaned function bodies in the file. Required 3 cleanup passes to remove ~15 duplicate lines causing "Duplicate declaration" errors. |

## Solutions and Workarounds

| Problem | Workaround |
|---------|------------|
| No forward references | Organize functions into dependency levels (Level 0 → Level N) with utility functions first |
| No loops | Use recursive helper + wrapper pattern for all iteration |
| Variable scoping bug (runtime) | Fix applied to interpreter; all `let` bindings now correctly create local scope |
| Orphaned code from edits | Manual inspection and cleanup after each edit pass |

## Comparison with Previous Benchmarks

| Metric | B1 (Library) | B2 (Notes) | B3 (Calendar) | B4 (Markdown) | B5 (HTTP Parser) |
|--------|:---:|:---:|:---:|:---:|:---:|
| Lines | 943 | 346 | 492 | 518 | **405** |
| Functions | — | 39 | 59 | 38 | **38** |
| Modules | — | 4 | 4 | 5 | **4** |
| Compiler Iterations | — | 1 | 3 | 4 | **5** |
| Runtime Iterations | — | 1 | 1 | 2 | **2** |
| Compiler Bugs | 0 | 0 | 1 | 0 | **0** |
| Runtime Bugs | 0 | 1 | 0 | 0 | **1** |
| Language Limitations | 1 | 0 | 1 | 2 | **2** |
| User Errors | 0 | 0 | 0 | 1 | **1** |
| Dev Time (min) | — | — | — | ~40 | **~36** |

## Overall Assessment

**AILang is moderately suitable for text/string parsing tasks.** The core building blocks (string manipulation, maps, lists, recursion) are sufficient to implement an HTTP/1.1 request parser. However, the lack of loops and forward references adds significant overhead. The most impactful discovery in this benchmark was a **runtime bug in the interpreter's variable scoping** (`_set_local` using `assign` instead of `define`) — a fundamental language implementation defect that potentially affects all AILang programs. Fixing this required modifying the interpreter itself rather than the application code.

**Key takeaway:** Parsing real-world protocols like HTTP is feasible in AILang, but each parsing stage requires explicit recursive helpers, and developers must organize functions in strict bottom-up dependency order.
