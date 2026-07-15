# AILang VS Code Extension

Syntax highlighting, snippets, bracket matching, language configuration, and LSP support for [AILang](https://github.com/akpersonal4/ailang-lang-AILang).

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

| Setting | Default | Description |
|---------|---------|-------------|
| `ailang.mcp.autoStart` | `true` | Automatically start MCP server on extension activation |
| `ailang.mcp.command` | `"ail"` | Command to launch the MCP server |
| `ailang.mcp.args` | `["mcp"]` | Arguments passed to the MCP server |
| `ailang.mcp.timeout` | `30000` | Timeout (ms) for MCP server initialization |
| `ailang.mcp.maxReconnectAttempts` | `3` | Max reconnect attempts after unexpected exit |

## Known Issues

- No semantic token coloring (uses TextMate grammar only)
- Multi-line comments not supported (language has none)

## Release Notes

### 0.3.0

- Added MCP server integration with automatic lifecycle management
- Added 7 commands for MCP server control and diagnostics
- Added status bar indicator and 5 configuration settings
- License changed to Apache-2.0

### 0.2.0

- Added code actions with TextEdit edits
- Fixed version synchronization and trailing comma issues

### 0.1.1

- Added `import as` alias syntax highlighting
- Added support for all 16 stdlib modules
- Refined snippets and added `let` and `comment` snippets

### 0.1.0

- Initial release: full syntax highlighting, snippets, language configuration

---

## Development

```bash
# Clone and navigate
git clone https://github.com/akpersonal4/ailang-lang-AILang.git
cd ailang/extensions/vscode-ailang

# Open in VS Code to develop
code .
```

Test highlighting by opening `.ail` files from `test-files/` and pressing `Ctrl+Shift+P` → "Developer: Inspect Editor Tokens and Scopes".
