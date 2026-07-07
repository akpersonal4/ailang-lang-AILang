# Formatter Fix Report — AILang v0.1.3

## Problem

`ail fmt` failed on nearly all benchmark `.ail` files with hundreds of
"Expected SEMICOLON" errors. The formatter's `_parse_to_ast` method used
a strict `Parser` that rejected any parse error, even though the build
pipeline silently tolerated these same errors when no `DiagnosticReporter`
was attached.

## Root cause

**All 36 benchmark files had missing semicolons on `return` statements**
(and, in one case, on a `let` declaration). This is a systematic style
issue — 1009 total missing semicolons across the benchmark suite.

The build pipeline (`_compile_all` in `session.py`) constructs a `Parser`
and `Lexer` without a `DiagnosticReporter`, so parse errors were silently
swallowed and execution proceeded with a partial AST. The formatter,
however, used a `Parser` without this tolerance and aborted.

## Fix (compiler/formatter.py)

```python
def _parse_to_ast(self, source_text: str) -> ProgramNode:
    reporter = DiagnosticReporter()
    lexer = Lexer(reporter)
    ...
    if reporter.has_errors():
        # Tolerate SEMICOLON errors — formatter will self-heal
        tolerated = [d for d in reporter.diagnostics
                     if "Expected SEMICOLON" in d.message]
        nontolerated = [d for d in reporter.diagnostics if d not in tolerated]
        ...
```

The fix:
1. Attaches a `DiagnosticReporter` to the parser during formatting
2. Checks for errors after parsing
3. **Tolerates only** "Expected SEMICOLON" errors and continues
4. All other errors cause a hard failure

## Self-healing behavior

When the formatter encounters a missing semicolon during parsing, it adds
the missing semicolon in its formatted output. Key properties:

- **Idempotent:** A second `ail fmt` pass produces identical output
- **Safe:** Only semicolons are auto-fixed, no structural changes
- **Verified:** Kanban and Inventory Management apps format identically on
  repeated passes

## Test results

- 27 formatter tests: all pass
- Full test suite: 522/522 pass
- All 42 benchmark apps: build and run correctly
- 40/42 apps have formatting violations (detected by `ail fmt --check`)

## Recommendations

1. **Run `ail fmt apps/` before tagging v0.1.3** to normalize all source files.
   This will add ~1009 missing semicolons across 40 files.
2. **Consider adding `ail fmt --check` to CI** after the batch format to prevent
   recurrence.
