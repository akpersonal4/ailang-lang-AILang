# AILang Formatter Architecture

**Architecture document for `ail fmt` — the AILang canonical source code formatter.**

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Existing Implementation](#2-existing-implementation)
3. [Formatting Pipeline](#3-formatting-pipeline)
4. [Philosophy & Style Rules](#4-philosophy--style-rules)
5. [Current Limitations](#5-current-limitations)
6. [v0.5 Hardening Scope](#6-v05-hardening-scope)
7. [Future Roadmap](#7-future-roadmap)
8. [CLI Interface](#8-cli-interface)
9. [Integration with Platform](#9-integration-with-platform)
10. [Testing Strategy](#10-testing-strategy)
11. [Stability Verification](#11-stability-verification)

---

## 1. Architecture Overview

### 1.1 Layers

```
┌─────────────────────────────────────────────────────────┐
│                     CLI (ail fmt)                         │
│             compiler/cli/main.py:cmd_fmt()                │
├─────────────────────────────────────────────────────────┤
│                     Formatter Engine                       │
│                   compiler/formatter.py                     │
│              _Formatter class + public API                  │
├─────────────────────────────────────────────────────────┤
│                   Compiler Pipeline (read-only)             │
│     Lexer → Parser → CST → ASTBuilder → ProgramNode        │
├─────────────────────────────────────────────────────────┤
│              ail_platform/ (project, workspace)             │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Principles

| Principle | Rule |
|-----------|------|
| **Deterministic** | Same input always produces same output. No randomness, no system-dependent behavior. |
| **Idempotent** | Running the formatter twice on the same file produces zero changes. |
| **Semantic-preserving** | Formatted code produces identical compiler output to the original. No reordering of declarations. |
| **Specification-first** | Every formatting rule is part of the language specification, not a tool preference. |
| **Zero configuration** | Single canonical style. No configuration options in v0.5. |
| **Read-compare-write safety** | Original source is never lost on error (format in memory, fail before write). |

### 1.3 What the Formatter Is Not

| Not this | Reason |
|----------|--------|
| A linting tool | The formatter only rewrites formatting, not code structure |
| A refactoring tool | No AST transformations, no code reordering |
| A configurable formatter | Single canonical style only |
| An incremental formatter (v1) | Full-file reformat only |

---

## 2. Existing Implementation

### 2.1 Module

Single file: `compiler/formatter.py` (466 LOC).

### 2.2 Public API

```python
def format_source(source: str) -> str:
    """Parse and format an AILang source string.
    Returns the formatted source.
    Raises ValueError on parse errors.
    """

def format_check(source: str) -> bool:
    """Return True if source is already formatted."""
```

### 2.3 Internal Architecture

The `_Formatter` class (lines 111–466) walks the AST depth-first and emits formatted lines:

```python
class _Formatter:
    INDENT = "    "  # 4-space indentation

    def __init__(self, source: str, ast: ProgramNode):
        self.source_lines = source.split("\n")
        self._lines: list[str] = []       # Output buffer
        self._indent = 0                   # Current indentation level
        self._last_source_line: int = -1   # For comment placement
```

### 2.4 AST Nodes Handled

| Node Type | Formatter Method |
|-----------|-----------------|
| `ProgramNode` | `_format_program()` |
| `ImportDeclarationNode` | `_format_import_declaration()` |
| `FunctionDeclarationNode` | `_format_function_declaration()` |
| `VariableDeclarationNode` | `_format_variable_declaration()` |
| `ExpressionStatementNode` | `_format_expression_statement()` |
| `ReturnStatementNode` | `_format_return_statement()` |
| `IfStatementNode` | `_format_if_statement()` |
| `BinaryExpressionNode` | `_format_binary()` |
| `UnaryExpressionNode` | `_format_unary()` |
| `CallExpressionNode` | `_format_call()` |
| `MemberAccessNode` | `_format_member_access()` |
| `IdentifierNode` | (inline in `_format_expression()`) |
| `NumberLiteralNode` | (inline) |
| `StringLiteralNode` | (inline) |
| `BooleanLiteralNode` | (inline) |

### 2.5 Operator Precedence

Precedence table (line 424–439):

| Level | Operators |
|:-----:|-----------|
| 1 | `=` |
| 2 | `\|\|` |
| 3 | `&&` |
| 4 | `==`, `!=` |
| 5 | `<`, `>`, `<=`, `>=` |
| 6 | `+`, `-` |
| 7 | `*`, `/`, `%` |

Parentheses are inserted when a subexpression's precedence is lower than the parent's (`_format_expression` line 403–408).

### 2.6 Comment Preservation

Comments are preserved by scanning the original source lines (not the AST):

- **Block comments**: `_comments_between(start_line, end_line)` — extracts `//` lines between AST nodes
- **Inline comments**: `_inline_comment(source_line)` — extracts trailing `// text` from a source line
- **Trailing comments**: After the last AST node, remaining comment lines are emitted

### 2.7 Error Handling

The `_parse_to_ast()` function (lines 56–93):

1. Creates a `DiagnosticReporter`
2. Runs `Lexer.tokenize()` → `Parser.parse_program()` → CST
3. Filters out "Expected SEMICOLON" diagnostics (parser recovers fully)
4. Raises `ValueError` if any *other* syntax errors exist
5. Runs `ASTBuilder.build()` on the CST → `ProgramNode`
6. Catches `ValueError`, `AssertionError`, `IndexError`, `AttributeError` from the builder

---

## 3. Formatting Pipeline

### 3.1 End-to-End Flow

```
Source String
    │
    ▼
Lexer.tokenize() → Token stream
    │
    ▼
Parser.parse_program() → CST node
    │
    ▼
Diagnostic filter (SEMICOLON tolerance)
    │
    ▼
ASTBuilder.build() → ProgramNode
    │
    ▼
_Formatter(source, ast).format()
    │
    ├── _format_program() — top-level declarations
    │       └── _format_import_declaration()
    │       └── _format_function_declaration()
    │       └── _format_variable_declaration()
    │       └── _format_node() — generic dispatch
    │
    ├── _format_block_body() — inside { }
    │       └── _format_node() — per-statement
    │
    └── _format_expression() — recursive expression printer
            └── _format_binary()
            └── _format_unary()
            └── _format_call()
            └── _format_member_access()
    │
    ▼
Join lines with \n, ensure trailing newline
    │
    ▼
Formatted string
```

### 3.2 Parser Integration

The formatter reuses the same compiler pipeline as the build/run commands:

| Component | File | Formatter Usage |
|-----------|------|-----------------|
| `Lexer` | `compiler/lexer.py` | `Lexer(reporter).tokenize(source)` |
| `Parser` | `compiler/parser/parser.py` | `Parser(tokens, reporter).parse_program()` |
| `ASTBuilder` | `compiler/ast/builder.py` | `ASTBuilder().build(cst)` |

### 3.3 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| AST-based, not token-based | AST ensures the formatter works on valid parsed structures | Cannot format syntactically invalid code; token-based would risk producing semantically invalid output |
| Comment extraction from source text | Comments are not preserved in the AST; extracted by line scanning | AST nodes carry source spans, allowing precise comment-to-node association |
| Full parse on every format | Not incremental (v1) | Current file sizes (typically <1000 LOC) make incremental formatting unnecessary |
| In-process compilation | No subprocess | Instant formatting, no serialization overhead |
| Internal to compiler package | `compiler/formatter.py` not `tools/ail_fmt/` | Direct access to compiler AST, lexer, parser. Formatter is a compiler service. |

---

## 4. Philosophy & Style Rules

### 4.1 Canonical Style

The following rules define the **single canonical AILang formatting style**. Every rule is part of the language specification — changing one requires a language version bump.

#### 4.1.1 Indentation

| Rule | Detail |
|------|--------|
| Indent size | 4 spaces |
| Indent character | Space only (no tabs) |
| Scope bodies | Indented one level inside `{ }` |
| Empty body | Same line: `fn main() {}` |

#### 4.1.2 Braces

| Construct | Style |
|-----------|-------|
| Function body | `fn name(params) {` → body → `}` |
| If body | `if (cond) {` → body → `}` |
| Else body | `} else {` → body → `}` |
| Else if chain | `} else if (cond) {` → body → `}` |
| Empty block | `fn name() {}` (no space before `{}`) |

#### 4.1.3 Operators

| Construct | Rule | Example |
|-----------|------|---------|
| Binary operators | Space before and after | `a + b`, `x == y` |
| Unary operators | No space after operator | `-42`, `!true` |
| Parenthesized expressions | Spaces inside parens: no | `(a + b) * c` |

#### 4.1.4 Declarations

| Construct | Rule | Example |
|-----------|------|---------|
| Import | `import module;` or `import module as alias;` | `import string;` |
| Variable | `let name = value;` | `let x = 42;` |
| Function parameters | `, ` after each parameter | `fn add(a, b)` |
| Return | `return value;` | `return a + b;` |

#### 4.1.5 Spacing

| Context | Rule |
|---------|------|
| After semicolons | No trailing spaces |
| Between functions | One blank line |
| Between imports and functions | One blank line |
| After opening paren/bracket | No space |
| Before closing paren/bracket | No space |
| Before comma | No space |
| After comma | One space |

#### 4.1.6 Newlines

| Rule | Detail |
|------|--------|
| File ending | Always trailing newline (`\n`) |
| Blank lines between functions | Exactly 1 blank line |
| Multiple blank lines | Collapsed to single |
| Trailing whitespace | Removed |

#### 4.1.7 Comments

| Rule | Detail |
|------|--------|
| Line comment | `// text` — one space after `//` |
| Inline comment | `code;  // text` — two spaces before `//` |
| Comment placement | Preserved relative to surrounding code |
| Trailing comments | After last function, preserved at end of file |

### 4.2 Determinism Guarantees

- Same input string → same output string (byte-identical)
- No dependency on: system time, random seed, filesystem state, locale
- No dependency on: input path, file name, import order
- No dependency on: length of identifier names (formatting is name-agnostic)

### 4.3 Idempotency Guarantees

- `format_source(format_source(source)) == format_source(source)`
- Running `ail fmt` twice on a file produces zero changes
- `format_check(source)` returns `True` iff the source is already formatted

### 4.4 Semantic Preservation Guarantees

- The formatter never reorders declarations
- The formatter never removes or modifies code (only whitespace/formatting)
- Comments remain in the same relative position
- String literals are preserved verbatim (including internal whitespace)
- AST structure is unchanged after formatting

---

## 5. Current Limitations

### 5.1 Spurious SEMICOLON Error

**Evidence**: Reported in backlog (`DEVELOPMENT_STATUS.md` line 251):
> "`ail fmt` spurious SEMICOLON error (formatter unusable on valid code)"

**Root cause area**: The formatter filters "Expected SEMICOLON" diagnostics from the parser in the `_parse_to_ast()` function (line 76–79), but the AST builder's exception handler (line 87–89) reports ALL diagnostics (including filtered ones) when it catches an error:

```python
except (ValueError, AssertionError, IndexError, AttributeError) as e:
    msgs = [d.message for d in reporter.diagnostics]  # <-- includes SEMICOLON
    raise ValueError("Syntax errors: " + "; ".join(msgs)) from e
```

If the AST builder fails for any reason (even one unrelated to semicolons), the error message will include "Expected SEMICOLON" messages that were never relevant.

**Severity**: High — blocks formatter use on valid code in edge cases.

### 5.2 Missing `--diff` Mode

**Current behavior**: `ail fmt` writes changes in-place (file mode) or to stdout (stdin mode). There is no way to see what would change without actually modifying files.

**Required**: `ail fmt --diff` that shows a unified diff of formatting changes to stdout, exits 0 if already formatted, 1 if changes would be made.

### 5.3 No Project-Wide Formatting

**Current behavior**: Only single-file formatting. Must specify an explicit file argument.

**Required**: `ail fmt <project_dir>` to recursively find and format all `.ail` files in a project.

### 5.4 Missing Edge-Case Coverage

**Identified gaps** (from existing test file `test_formatter.py`, 302 lines, 27 tests):

| Gap | Details |
|-----|---------|
| Multi-module projects | No tests for formatting across multiple files |
| Large files | No stress tests for 1000+ LOC |
| Nested if-else chains | Limited coverage of `else if` chains past 3 levels |
| Complex expressions | Deeply nested parens, chained member access, mixed operators |
| All stdlib patterns | Module imports, chained calls with dots, multiple arguments |
| Unicode/UTF-8 | No tests for non-ASCII identifiers or string content |
| Edge cases | Empty file, only comments, only imports, trailing backslash |
| Error recovery | Partial formatting on parse error (v1) |

### 5.5 No LSP Integration

**Current behavior**: The LSP architecture document (`LSP_ARCHITECTURE.md` line 270) explicitly routes `textDocument/formatting` away:
> "`textDocument/formatting` | Use `ail fmt` CLI instead"

**Impact**: Editor users cannot format-on-save through the LSP. They must use a separate CLI command or editor task.

### 5.6 No Configuration Support

**Current behavior**: The formatter has no configuration. This is intentional (single canonical style).

**Risk**: Any request for configuration (indent size, brace style, semicolons) must be rejected per the governance process unless ≥2 independent benchmarks request it.

### 5.7 No Incremental Formatting

**Current behavior**: The formatter always parses and reformats the entire file.

**Impact**: On very large files (>5000 LOC, though none exist in the current ecosystem), full-file formatting would be noticeably slow.

---

## 6. v0.5 Hardening Scope

### 6.1 Deliverables

| # | Item | Type | Effort |
|:-:|------|------|:------:|
| 1 | SEMICOLON bug fix (with regression test) | Bug fix | Small |
| 2 | `--diff` mode | Feature | Small |
| 3 | Project directory formatting | Feature | Medium |
| 4 | Additional regression tests | Test | Medium |
| 5 | Benchmark application formatting verification | Test | Small |
| 6 | Standard library formatting verification | Test | Small |
| 7 | Formatter stability tests as release gate | Test | Small |

### 6.2 Exclusion: LSP Formatting

LSP `textDocument/formatting` is explicitly **excluded from v0.5**. Rationale:

- LSP formatting requires incremental text sync and range handling
- CLI formatting is a simpler, more testable surface
- LSP integration is deferred to a future version (see §7.2)
- Users can script `ail fmt` commands through editor tasks

### 6.3 Exclusion: Configuration

Configuration is **excluded from v0.5 and all future versions** unless ≥2 independent benchmark applications request it per `GOVERNANCE.md`.

---

## 7. Future Roadmap

### 7.1 v0.5 (Hardening)

| Priority | Feature | Gate |
|:--------:|---------|------|
| P0 | SEMICOLON bug fix | Regression test exists |
| P1 | `--diff` mode | Tested with known unformatted sources |
| P2 | Project formatting | Recursive `.ail` discovery |
| P3 | Test expansion | Edge cases, large files, error recovery |
| P4 | Stability verification | Release gate (§11) |

### 7.2 Future Versions

| Feature | Rationale | When |
|---------|-----------|------|
| LSP `textDocument/formatting` | Format-on-save in editors | After v0.5, when LSP can call format_source() in-process |
| Range formatting | Format selected code only | With LSP formatting |
| Incremental formatting | Optimize large file formatting | If any AILang file exceeds 5000 LOC |
| Formatter configuration | Community-requested style options | Only if ≥2 benchmarks request per GOVERNANCE.md |

### 7.3 Explicit Non-Goals

| Not planned | Reason |
|-------------|--------|
| Multiple style presets | Single canonical style is a core philosophy |
| Code transformation (auto-fix) | Formatter is not a linter |
| Import sorting | Would require semantic analysis of dependencies |
| Line wrapping / max line length | AILang programs are typically expression-oriented; wrapping would change semantics |

---

## 8. CLI Interface

### 8.1 Current Interface

```
Usage: ail fmt [--check] [--stdin] [<file>]
```

| Mode | Command | Behavior |
|------|---------|----------|
| In-place | `ail fmt file.ail` | Format file, overwrite |
| Check | `ail fmt --check file.ail` | Exit 0 if formatted, 1 if not |
| Stdin | `ail fmt --stdin` | Read from stdin, write formatted to stdout |
| Stdin + check | `ail fmt --check --stdin` | Exit 0 if stdin is formatted, 1 if not |

### 8.2 v0.5 Interface (Proposed)

```
Usage: ail fmt [--check] [--diff] [--stdin] [--quiet] [<file_or_dir>]
```

| Mode | Command | Behavior |
|------|---------|----------|
| In-place (file) | `ail fmt file.ail` | Format file, overwrite (current) |
| In-place (dir) | `ail fmt project/` | Format all `.ail` files recursively |
| Check | `ail fmt --check file.ail` | Exit 0 if formatted, 1 if not (current) |
| Diff | `ail fmt --diff file.ail` | Print unified diff to stdout, exit 0/1 |
| Stdin | `ail fmt --stdin` | Read from stdin, write formatted (current) |
| Quiet | `ail fmt --quiet file.ail` | Suppress "Formatted:" output, only exit code |

### 8.3 Exit Codes

| Code | Meaning | When |
|:----:|---------|------|
| `0` | Success | File formatted, or already formatted (--check), or no changes (--diff) |
| `1` | Failure | File would change (--check/--diff), or syntax error, or file not found |

### 8.4 Integration with Platform

The formatter CLI does not use `tools/common/` directly — it is a compiler subcommand (`compiler/cli/main.py`). It integrates with:

| Platform Module | Usage |
|-----------------|-------|
| `ail_platform.workspace.Workspace` | For project-level formatting, discover `.ail` files |
| `ail_platform.project.discover_apps` | Find benchmark applications for stability testing |
| `ail_platform.diagnostics` | Convert formatter errors to platform diagnostics (future) |

---

## 9. Integration with Platform

### 9.1 Current Integration

The formatter is a compiler-internal module (`compiler/formatter.py`). It does not import from `ail_platform/` or `tools/common/`.

### 9.2 v0.5 Integration Points

| Need | Platform Module | When |
|------|-----------------|------|
| Find `.ail` files in a directory | `ail_platform.workspace` (or `project.discover_apps`) | Project formatting feature |
| Report formatting results | `ail_platform.report_schema` | If structured reports are needed (deferred) |
| Convert formatter errors | `ail_platform.diagnostics` | LSP integration (deferred to future) |

### 9.3 Non-Integration

The formatter does **not** use `tools/common/cli.py` or `tools/common/process.py`. It is invoked through the compiler's own CLI (`compiler/cli/main.py`) which has its own argument parsing. This is consistent with the LSP (`compiler/lsp/`) which also lives inside the compiler package.

---

## 10. Testing Strategy

### 10.1 Test Categories

| Category | File | Scope | Count |
|----------|------|-------|:-----:|
| Formatter unit tests | `tests/test_formatter.py` | `format_source()` and `format_check()` with inline sources | 27 |
| CLI integration tests | `tests/test_cli.py` | `ail fmt` subcommand, exit codes, `--check`, `--stdin` | 7 |

### 10.2 v0.5 Test Expansion

| New Test | Purpose | Priority |
|----------|---------|:--------:|
| SEMICOLON regression test | Exact minimal repro of the SEMICOLON bug | P0 |
| `--diff` mode | Correct diff output for unformatted file | P1 |
| Project formatting | Recursive formatting produces correct output | P2 |
| Large file stress test | 1000+ LOC, no errors, idempotent | P3 |
| All edge cases | Empty file, only comments, only imports, etc. | P3 |
| Error cases | Invalid syntax, binary input, permission error | P3 |

### 10.3 Test Patterns

```python
def test_format_simple_function() -> None:
    source = "fn add(a,b){return a+b;}"
    expected = "fn add(a, b) {\n    return a + b;\n}\n"
    assert format_source(source) == expected

def test_idempotent() -> None:
    source = "fn add(a, b) {\n    return a + b;\n}\n"
    assert format_source(source) == source
```

### 10.4 CLI Test Patterns

```python
def test_fmt_check_formatted() -> None:
    """--check on formatted file exits 0."""
    result = run_subprocess(["python", "-m", "compiler", "fmt", "--check", file])
    assert result.exit_code == 0

def test_fmt_check_unformatted() -> None:
    """--check on unformatted file exits 1."""
    result = run_subprocess(["python", "-m", "compiler", "fmt", "--check", file])
    assert result.exit_code == 1
```

---

## 11. Stability Verification

### 11.1 Formatter Stability Tests (Release Gate)

Every benchmark application must satisfy the following two properties:

#### 11.1.1 Semantic Preservation

```
Original Source
    │
    ▼
Format via format_source()
    │
    ▼
Compile via ail build
    │
    ▼
Run via ail run
    │
    ▼
Same output as unformatted run
```

#### 11.1.2 Idempotency

```
Format via format_source()
    │
    ▼
Format via format_source()  (second pass)
    │
    ▼
Zero changes relative to first pass
```

### 11.2 Implementation

```python
def verify_benchmark(benchmark_dir: Path) -> bool:
    """Verify that a benchmark app survives formatting unchanged."""

    # 1. Run the original and capture output
    original_output = run_ail_run(benchmark_dir / "main.ail")

    # 2. Format all .ail files
    for ail_file in benchmark_dir.rglob("*.ail"):
        source = ail_file.read_text()
        formatted = format_source(source)
        ail_file.write_text(formatted)

    # 3. Build (must still compile)
    build_result = run_ail_build(benchmark_dir / "main.ail")
    assert build_result.exit_code == 0, f"Build failed after format: {benchmark_dir}"

    # 4. Run and compare
    formatted_output = run_ail_run(benchmark_dir / "main.ail")
    assert original_output == formatted_output

    # 5. Idempotency: format again, verify zero changes
    for ail_file in benchmark_dir.rglob("*.ail"):
        source = ail_file.read_text()
        assert format_check(source), f"Not idempotent: {ail_file}"
```

### 11.3 Release Gate Checklist

| # | Check | How |
|:-:|-------|-----|
| 1 | All formatter tests pass | `pytest tests/test_formatter.py` |
| 2 | All CLI tests pass | `pytest tests/test_cli.py` |
| 3 | Every benchmark app formats clean | `verify_benchmark()` for each app in `apps/` and `phase11/` |
| 4 | Standard library formats clean | `format_check()` on every `stdlib/*.ail` file |
| 5 | Double format yields zero changes | Idempotency check on every formatted file |
| 6 | Compiler output identical before/after | Semantic preservation check on every app |

---

## Appendix A: File Map

```
compiler/
├── cli/
│   └── main.py                 — cmd_fmt() CLI handler (lines 150–222)
├── formatter.py                — Formatter engine (466 LOC, ~200 statements)
│
tests/
├── test_formatter.py           — 27 formatter tests (302 lines)
├── test_cli.py                 — 7 CLI tests for ail fmt
│
docs/
└── architecture/
    └── FORMATTER_ARCHITECTURE.md  — This document
```

## Appendix B: Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Formatter in compiler package | `compiler/formatter.py` not `tools/ail_fmt/` | Direct access to compiler AST. Formatter is a compiler service, same pattern as LSP. |
| AST-based formatting | Not token-based | Guarantees output is syntactically valid. Token-based could produce invalid token sequences. |
| Full-file reformat | Not incremental | Simpler, correct, fast enough for current file sizes. |
| Source-text comment extraction | Not AST comments | Comments are not preserved in the compiler AST. Source text scanning is reliable given source spans on AST nodes. |
| Zero configuration | Intentional | Single canonical style is a language specification concern, not a user preference. |
| SEMICOLON tolerance | Parser recovers | Missing semicolons are the most common handwritten formatting issue. The parser produces valid CST without them. |

## Appendix C: Comparison with Ecosystem

| Feature | AILang Formatter | Prettier | Black | rustfmt |
|---------|:----------------:|:--------:|:-----:|:-------:|
| Configuration | None | Optional | Minimal | Optional |
| `--check` mode | ✅ | ✅ | `--check` | `--check` |
| `--diff` mode | 📋 v0.5 | ✅ | `--diff` | ✅ |
| Project formatting | 📋 v0.5 | ✅ | ✅ | ✅ |
| Stdin mode | ✅ | ✅ | `--stdin` | — |
| LSP integration | 📋 Future | ✅ | Via plugin | ✅ |
| Range formatting | 📋 Future | ✅ | `--line-ranges` | — |
| Idempotency guarantee | ✅ | ✅ | ✅ | ✅ |
| Comment preservation | ✅ | ✅ | ✅ | ✅ |

---

## Appendix D: Current Test Coverage

| Test | File | Verifies |
|------|------|----------|
| `test_format_simple_function` | test_formatter.py | Basic function |
| `test_format_multiple_functions` | test_formatter.py | Blank line between functions |
| `test_format_variable_declaration` | test_formatter.py | `let` formatting |
| `test_format_imports` | test_formatter.py | Import formatting |
| `test_format_import_with_alias` | test_formatter.py | `import as` |
| `test_spaces_around_binary_operators` | test_formatter.py | Operator spacing |
| `test_spaces_around_comparison_operators` | test_formatter.py | Comparison spacing |
| `test_spaces_around_logical_operators` | test_formatter.py | `&&`, `\|\|` spacing |
| `test_unary_operators` | test_formatter.py | Unary `-` and `!` |
| `test_if_statement` | test_formatter.py | If block |
| `test_if_else_statement` | test_formatter.py | If-else |
| `test_if_else_if_chain` | test_formatter.py | Else-if chain |
| `test_recursive_function` | test_formatter.py | Recursion |
| `test_member_access` | test_formatter.py | Stdlib calls |
| `test_chained_member_access` | test_formatter.py | Chained calls |
| `test_string_literals` | test_formatter.py | String escapes |
| `test_bool_literals` | test_formatter.py | `true`/`false` |
| `test_idempotent` | test_formatter.py | Double format |
| `test_format_check_formatted` | test_formatter.py | `format_check()` True |
| `test_format_check_unformatted` | test_formatter.py | `format_check()` False |
| `test_comments_preserved` | test_formatter.py | Inline + block comments |
| `test_comments_between_functions` | test_formatter.py | Comment placement |
| `test_invalid_syntax_raises` | test_formatter.py | Error on bad syntax |
| `test_empty_block` | test_formatter.py | `fn main() {}` |
| `test_no_trailing_whitespace` | test_formatter.py | Whitespace cleanup |
| `test_blank_lines_removed` | test_formatter.py | Blank line collapse |
| `test_nested_expressions` | test_formatter.py | Precedence parens |
| CLI `fmt` tests | test_cli.py | 7 integration tests |

---

_This document is the architecture contract for the AILang Formatter. All formatting rules documented here are part of the language specification. Behavior changes require a language version bump._

_Last updated: 2026-07-07_
