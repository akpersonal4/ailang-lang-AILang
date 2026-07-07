# Diagnostic Quality Audit — AILang v0.1.3

## Scope

Every diagnostic emission site across the compiler (lexer, parser, semantic,
type checker, module resolver, LSP) was reviewed for message clarity, error
code consistency, severity correctness, and architectural coherence.

---

## Inventory

| Phase            | Error Codes          | Sites | Severity     |
|------------------|----------------------|-------|--------------|
| Lexer            | LEX001–LEX004         | 7     | ERROR        |
| Parser (tokens)  | PAR001                | 2     | ERROR        |
| Parser (parser)  | PAR001–PAR003         | 4     | ERROR        |
| Parser (stmts)   | PAR002                | 1     | ERROR        |
| Semantic         | SEM001–SEM002         | 2     | ERROR        |
| Semantic         | MOD002, MOD004         | 2     | WARN / ERROR |
| Type checker     | TYP001–TYP013         | 13    | ERROR        |
| Module resolver  | MOD001                | 1     | ERROR        |
| LSP              | LSP000                | 1     | ERROR        |

**Total: 33 diagnostic emission sites across 9 error code ranges.**

---

## Findings

### 1. Two competing error-code patterns (MEDIUM)

- **Pre-defined constants** in `compiler/diagnostics.py`: LEX001–LEX004,
  PAR001–PAR003, MOD001–MOD005. The canonical message string stored alongside
  the constant is **never used** as the actual diagnostic message — callers
  always pass their own message string.

- **Inline `ErrorCode(code, message)` construction**: SEM001–SEM002,
  TYP001–TYP013, LSP000. The same `ErrorCode` object is constructed at each
  report site with a different message. This means the error code *number* is
  the only stable identifier; the string message is duplicative and lives in
  the `ErrorCode` constructor.

**Recommendation:** Unify toward the inline-pattern (code number + message)
and remove unused canonical strings from `diagnostics.py`, OR move all
messages into `diagnostics.py` and reference them by constant.

---

### 2. PAR001 used as a catch-all default (LOW)

`TokenStream.report()` defaults to `code="PAR001"`, meaning any parse
diagnostic that doesn't explicitly pass a code gets PAR001. The actual
messages emitted are:
- `"Expected {kind.name}"`
- `"Expected expression"`
- `"Expected identifier"`
- `"Unexpected token in program"`

The canonical message `"Expected token"` from `diagnostics.py` is
**never emitted**.

---

### 3. PAR002 overloaded for two unrelated situations (MEDIUM)

PAR002 is used for:
1. `"Expected identifier in import path"` (`parser.py:135`)
2. `"Too many statements in block (infinite loop detected)"` (`statements.py:25`)

These are semantically unrelated — one is a syntax error in an import
statement, the other is a safety guard against infinite loops. They should
have distinct error codes.

---

### 4. MOD003 / MOD005 orphaned (LOW)

`MOD003_MODULE_NOT_FOUND` and `MOD005_INVALID_MODULE_PATH` are defined in
`diagnostics.py` but **never emitted** as diagnostics. The module resolver
raises `ModuleResolutionError` (a Python exception) instead, which is caught
and re-raised elsewhere. No diagnostic is ever constructed for these
conditions.

---

### 5. No Severity.NOTE emissions (LOW)

`Severity.NOTE` is defined in `diagnostics.py` and mapped in the LSP layer,
but no compiler phase ever creates a diagnostic with `Severity.NOTE`. All
29 report sites use `ERROR`; exactly 1 uses `WARNING` (MOD002 — duplicate
import).

---

### 6. Overall message quality

| Phase        | Quality | Notes |
|-------------|---------|-------|
| Lexer       | GOOD    | Messages include the unexpected character and context (e.g. `"Float literals not supported. Use integer division (22 / 7)"`) |
| Parser      | FAIR    | Messages are clear but lack source context (e.g. `"Expected expression"` doesn't say what was found instead) |
| Semantic    | GOOD    | Messages include the symbol name (`"Duplicate declaration: foo"`) |
| Type checker| GOOD    | Messages include types and operator info (`"Arithmetic operator '+' requires numeric types, got 'bool' and 'string'"`) |
| Module      | FAIR    | Exception-based rather than diagnostic-based — messages are only surfaced in a caught exception's `args[0]` |
| LSP         | GOOD    | Wraps unexpected Python exceptions for robustness |

---

## Recommendations

1. **Split PAR002** into two codes: one for import-path syntax, one for block
   iteration limit.
2. **Either** centralize all message strings in `diagnostics.py` (and reference
   them) **or** remove the unused canonical strings and stick to the inline
   pattern consistently.
3. **Emit MOD003 / MOD005 as diagnostics** from the module resolver instead of
   (or in addition to) raising exceptions.
4. **Consider** introducing `Severity.NOTE` in at least one place (e.g., unused
   import, inferred type info in hover).
