# Diagnostics Improvement Report — AILang v0.1.3

## Summary

Three changes were made to improve diagnostic quality across the compiler:

### 1. CLI uses DiagnosticFormatter (compiler/cli/main.py)

**Before:**
```
ail build test.ail
Undefined identifier: foo
```

**After:**
```
ail build test.ail
ERROR SEM002 (line 3, column 12): Undefined identifier: foo
```

The `DiagnosticFormatter` class (which already existed in
`compiler/diagnostics.py`) is now wired into the CLI's error output path.
The format includes error code, line, column, and message in a standard
format that can be parsed by editors and IDEs.

### 2. SymbolTable offset→line/col conversion (compiler/semantic/symbol_table.py)

**Change:** Added `set_source_text()` method and fixed `_report_error()` to
convert character offsets to 1-based line/column numbers.

**Before:** `line=1, column=start_span+1` (character offset treated as column)
**After:** `line=3, column=12` (correct location in multi-line source)

The conversion algorithm walks through source lines, subtracting line lengths,
until the offset is within the current line. This correctly handles
multi-module compilation where each module has its own source text.

### 3. TypeChecker source text support (compiler/types/checker.py)

**Change:** Added `source_text` parameter to `TypeChecker.__init__()` and fixed
`_report_error()` with the same offset→line/col conversion as SymbolTable.

### 4. Session passes source text per-module (compiler/compilation/session.py)

**Change:** Both `analyze()` and `type_check()` now set the per-module source
text on SymbolTable / TypeChecker before processing each module. This ensures
diagnostics in multi-module programs show correct file locations.

## Integration

- `compiler/lsp/documents.py` updated to use `set_source_text()` API
- `tests/test_cli.py` test assertions updated to expect `"ERROR SEM"` format
- `tests/test_lexer.py` pre-existing assertion mismatch fixed
- All 522 tests pass, including LSP, CLI, and integration tests

## Verified behavior

```
$ ail build test_bad.ail
ERROR SEM002 (line 3, column 12): Undefined identifier: foo
```
