# Benchmark Report — Markdown to HTML Converter

## Application Summary

| Attribute | Value |
|-----------|-------|
| Name | Markdown to HTML Converter |
| Purpose | Convert Markdown text to valid HTML supporting headings, paragraphs, bold, italic, inline code, code blocks, blockquotes, ordered/unordered lists, horizontal rules, links, images, and HTML escaping |
| Lines of Code | 518 |
| Functions | 38 |
| Modules Used | 5 (`list`, `map`, `string`, `file`, `convert`) |

## Development Metrics

| Metric | Result |
|--------|--------|
| First Compile | FAIL |
| Final Compile | PASS |
| First Runtime | FAIL |
| Final Runtime | PASS |
| Compiler Iterations | 4 |
| Runtime Iterations | 2 |
| Total Revisions | 6 |
| Development Time | ~40 min |

## Features Implemented

| Feature | Status | Evidence |
|---------|--------|----------|
| Headings (`#` to `######`) | ✅ | `<h1>Markdown Demo</h1>` |
| Paragraphs | ✅ | `<p>This is a <strong>paragraph</strong>...</p>` |
| Bold (`**text**`) | ✅ | `<strong>paragraph</strong>` |
| Italic (`*text*`) | ✅ | `<em>formatting</em>` |
| Bold-Italic (`***text***`) | ✅ | `<em><strong>bold-italic</strong></em>` |
| Inline Code (`` `code` ``) | ✅ | `<code>inline code</code>` |
| Code Blocks (` ``` `) | ✅ | `<pre>` with escaped HTML content |
| Blockquotes (`>`) | ✅ | `<blockquote>This is a blockquote.</blockquote>` |
| Ordered Lists (`1.`) | ✅ | `<ol><li>First item</li>...</ol>` |
| Unordered Lists (`-`) | ✅ | `<ul><li>Item one</li>...</ul>` |
| Horizontal Rules (`---`) | ✅ | `<hr/>` |
| Links (`[text](url)`) | ✅ | `<a href="https://ailang.ai">link to AILang</a>` |
| HTML Special Character Escaping | ✅ | `&quot;` in code blocks |

## Language Evaluation

| Category | Score (1–10) |
|----------|:---:|
| Documentation | 8 |
| Compiler Diagnostics | 5 |
| Standard Library | 5 |
| Ease of Development | 4 |
| AI Friendliness | 7 |

## Classified Issues

### Compiler Bug (0)
None found.

### Runtime Bug (0)
None found.

### Formatter Bug (1)
- **`ail fmt` reports spurious "Expected SEMICOLON" errors** on valid code. Confirmed reproducible on all four benchmark apps: `apps/library_management/main.ail`, `apps/note_taking/main.ail`, `apps/calendar_app/main.ail`, and `apps/markdown_parser/main.ail`. All four compile and run correctly with `ail run`.

### Documentation Gap (2)
1. **`string.concat` accepts exactly 2 arguments** — documented correctly in STDLIB_REFERENCE.md but the prevalence of multi-arg concatenation patterns in sample code (`process_inline_helper` at `main.ail:237–340`) leads to easy misuse. The error message `Function concat expected 2 arguments, got 3` is clear but this was tripped multiple times.
2. **No mention of string.find or string.index_of** — STDLIB_REFERENCE documents `string.contains` (boolean) but not a function that returns the position of a substring. The `find_substring` function at `main.ail:14` had to be implemented manually.

### Missing Standard Library Function (5)
1. **`string.find(text, pattern)`** — No function to find the index of a substring. Required for inline parsing (`find_substring` at `main.ail:14`).
2. **`string.split(text, delimiter)`** — No function to split a string by a delimiter. Required for line parsing (`split_lines` at `main.ail:29–39`).
3. **`string.replace(text, from, to)`** — No string replacement. HTML escaping and inline parsing would benefit.
4. **`list.sort(list, comparator)`** — Not needed for this benchmark, but noted from Calendar benchmark.
5. **`string.join(list, separator)`** — Not needed for this specific benchmark, but noted as a recurring gap.

### Language Limitation (4)
1. **No forward references** — All 4 compiler iterations in this benchmark were caused by forward reference issues. Functions must be defined in strict dependency order, which forced a complex 7-level file structure. In a 518-line file with 38 functions, this is a significant productivity cost.
2. **No loops (while/for)** — String parsing requires character-by-character recursion. The `find_substring` function at `main.ail:14` is O(n*m) recursive. The `process_inline_helper` at `main.ail:223–326` processes each character position with a recursive call. This makes parsing code verbose and hard to optimize.
3. **No string indexing (`s[i]`)** — Every character access requires `string.substring(text, i, i+1)`. The inline processor at `main.ail:334` uses this pattern extensively. This adds verbosity and makes code harder to read.
4. **No regex support** — Pattern matching for markdown requires manual character-by-character scanning with `find_substring` at `main.ail:14`.

### Poor Compiler Diagnostic (1)
1. **No source location in error messages** — Errors like `Undefined identifier: process_inline` do not include line numbers. In a 518-line file, finding the offending reference requires manual search.

## Repeated Implementation Patterns

1. **Recursive helper + wrapper** — Every list operation follows: helper(coll, i, params, acc) + wrapper(coll, params). This pattern appears in `split_lines`, `print_lines`, and by extension the state machine in `process_lines_with_state`.
2. **Character-by-character recursion** — String scanning follows: fn(text, i, result) returning when i >= len, else checking position i and recursing with i+1.
3. **Nested string.concat chains** — Building HTML tags requires deeply nested `string.concat` calls, as seen in `process_heading` at `main.ail:346–349`.

## Sample Output

The converter was tested with a markdown document containing all 13 feature types. The generated HTML was validated by inspection:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Markdown</title>
</head>
<body>
<h1>Markdown Demo</h1>
<p>This is a <strong>paragraph</strong> with <em>formatting</em> and
<code>inline code</code>.</p>
<h2>Headings</h2>
...
</body>
</html>
```
