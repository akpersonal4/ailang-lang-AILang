# AILang VS Code Extension

Syntax highlighting, snippets, bracket matching, language configuration, and LSP support for [AILang](https://github.com/anomalyco/ailang).

## Features

### Language Server Protocol (LSP)

When the `ail` CLI is installed and on your PATH, the extension provides:
- **Hover** — Documentation for variables, functions, stdlib modules
- **Completion** — Keywords, builtins, stdlib modules, functions
- **Diagnostics** — Real-time error reporting (lexical, parse, semantic, type errors)
- **Go to Definition** — Jump to function and variable declarations
- **Find References** — Find all usages of a symbol
- **Rename Symbol** — Rename variables, functions, and parameters
- **Signature Help** — Function parameter hints
- **Document Symbols** — Outline view for functions and imports

### Syntax highlighting

Full TextMate grammar for `.ail` files covering:
- Keywords: `fn`, `let`, `if`, `else`, `return`, `import`, `as`
- Standard library modules: `string`, `math`, `list`, `array`, `map`, `set`, `json`, `csv`, `file`, `path`, `time`, `random`, `environment`, `convert`, `io`, `system`
- Built-in functions: `print`
- Strings (with escape sequences), numbers, booleans (`true`/`false`)
- Operators (arithmetic, comparison, logical, assignment)
- Line comments (`//`)
- Function declarations and module member access

### Snippets and Configuration

- **Snippets** — Type `fn`, `if`, `main`, etc. to generate common code patterns
- **Language configuration** — Auto-closing brackets, on-enter indentation, folding markers

## Installation

### From VS Code Marketplace (recommended)

Search for "AILang" in the Extensions view (`Ctrl+Shift+X`).

### From source

```bash
# From the AILang repository root
code --install-extension extensions/vscode-ailang
```

### Manual side-load

```bash
cd extensions/vscode-ailang
code --install-extension vscode-ailang-0.1.0.vsix
```

## Usage

Open any `.ail` file and the extension activates automatically. Start typing to see syntax highlighting, snippets, and auto-completions.

Example:

```ail
import string;
import math;

fn factorial(n) {
    if (n == 0) {
        return 1
    }
    return n * factorial(n - 1)
}

fn main() {
    let msg = string.uppercase("hello ailang");
    let result = factorial(5);
    print(msg, result);
    return 0
}
```

## Requirements

- VS Code 1.84.0 or higher

## Extension Settings

This extension has no configurable settings — it works out of the box.

## Known Issues

- No semantic token coloring (uses TextMate grammar only)
- Multi-line comments not supported (language has none)

## Release Notes

### 0.1.1

- Added `import as` alias syntax highlighting
- Added support for all 16 stdlib modules
- Refined snippets and added `let` and `comment` snippets
- Added test `.ail` files for all syntax categories

### 0.1.0

- Initial release: full syntax highlighting, snippets, language configuration

---

## Development

```bash
# Clone and navigate
git clone https://github.com/anomalyco/ailang.git
cd ailang/extensions/vscode-ailang

# Open in VS Code to develop
code .
```

Test highlighting by opening `.ail` files from `test-files/` and pressing `Ctrl+Shift+P` → "Developer: Inspect Editor Tokens and Scopes".
