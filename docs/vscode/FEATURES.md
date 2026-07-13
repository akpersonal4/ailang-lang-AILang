# VS Code Extension — Features

## Overview

The AILang VS Code extension provides a complete editing experience through
TextMate syntax highlighting and a Language Server Protocol (LSP) backend.

---

## Syntax Highlighting

TextMate grammar covers all AILang language constructs:

| Construct | Color Scope | Example |
|-----------|-------------|---------|
| **Keywords** | `keyword.*` | `fn`, `let`, `if`, `else`, `return`, `import`, `as`, `for` |
| **Booleans** | `constant.language.boolean` | `true`, `false` |
| **Functions** | `entity.name.function` | `fn main()` — name highlighted |
| **Strings** | `string.quoted.double` | `"hello"` |
| **String escapes** | `constant.character.escape` | `\n`, `\t`, `\\` |
| **Numbers** | `constant.numeric` | `42`, `3.14` |
| **Comments** | `comment.line.double-slash` | `// this is a comment` |
| **Operators** | `keyword.operator.*` | `+`, `-`, `==`, `!=`, `&&`, `\|\|`, `!` |
| **Stdlib modules** | `support.module` | `string.`, `math.`, `io.` in imports and member access |
| **Builtins** | `support.function.builtin` | `print` |
| **Module paths** | `entity.name.type.module` | `import io;`, `import math.add;` |
| **Member access** | `variable.other.object/property` | `string.length(x)` |

---

## LSP Features

The extension includes a full Language Server that provides:

### Diagnostics (Errors & Warnings)

- Real-time error reporting as you type
- Lexical errors (unrecognized characters)
- Parse errors (missing semicolons, unmatched braces)
- Semantic errors (undefined identifiers, type mismatches)
- Module errors (missing imports, circular dependencies)
- Warning severity support

Click any diagnostic to jump to the exact `file:line:col` location.

### Go To Definition

- **Ctrl+Click** or **F12** on any identifier to jump to its declaration
- Works for: variables, functions, parameters
- Handles local scope correctly

### Hover Information

- Hover over any identifier to see:
  - Function signature with parameter names
  - Documentation from stdlib reference (73 functions covered)
  - Module origin for imports
  - Variable type information

### Auto-Completion

Triggered by `Ctrl+Space` or automatically after `.` and `(`:

| Category | Count | Examples |
|----------|:-----:|---------|
| Keywords | 9 | `fn`, `let`, `if`, `else`, `return`, `import`, `for`, `true`, `false` |
| Builtins | 1 | `print` |
| Stdlib modules | 16 | `string`, `math`, `list`, `map`, `file`, `json`, etc. |
| Stdlib functions | 73 | `string.concat`, `math.add`, `list.get`, `file.read`, etc. |
| User functions | dynamic | All `fn` declarations in the current file |

### Rename

- **F2** on any identifier to rename it workspace-wide
- All references updated simultaneously
- Safe — compiler verifies the rename produces valid code

### Find References

- **Shift+F12** to find all usages of a symbol
- Shows every occurrence in the current file

### Signature Help

- Automatically appears when calling a function
- Shows parameter names and documentation
- Covers all 73 stdlib functions and user-defined functions

### Document Symbols

- **Ctrl+Shift+O** to see the file outline
- Functions, variables, and imports listed with their kinds

### Workspace Symbols

- **Ctrl+T** to search for symbols across all open files

---

## Code Actions (Quick Fixes)

Hover over a diagnostic (red squiggly line) and click the lightbulb icon:

| Action | Trigger | What It Does |
|--------|---------|--------------|
| **Import stdlib module** | Undefined identifier error | Inserts `import <module>;` at the top of the file |
| **Remove unused variable** | Unused variable warning | Deletes the entire `let` line |

---

## Snippets

Type the prefix and press `Tab` to expand:

| Prefix | Expands To |
|--------|-----------|
| `main` | Full `fn main()` with import boilerplate |
| `fn` | Function declaration template |
| `if` | If statement with braces |
| `ifelse` | If/else block |
| `import` | Import statement with semicolon |
| `return` | Return statement |
| `recur` | Recursive function pattern |
| `let` | Variable declaration |
| `comment` | Block comment |

---

## Language Configuration

- **Bracket matching**: `{}`, `()`, `[]`
- **Auto-closing**: `{}` → `{|}`, `()` → `(|)`, `""` → `"|"`, `//` → `// |`
- **Comment toggling**: `Ctrl+/` toggles `//` line comments
- **Folding**: `#region` / `#endregion` markers
- **Word selection**: underscores and dots included in word boundaries

---

## Performance

The LSP server compiles files in-process using the full AILang compiler pipeline:

| Metric | Target |
|--------|--------|
| Diagnostics latency | <50ms for <1000 LOC |
| Completion latency | <20ms |
| Hover latency | <10ms |
| Go-to-definition | <10ms |
| Rename | <50ms |

Full recompilation occurs on every document change. This is acceptable because
the AILang compiler is fast (<50ms for typical files).
