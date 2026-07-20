# AILang VS Code Extension v1.1.0

**Release Date:** 2026-07-20
**Status:** Stable Release

---

## What's New

This is the first official stable release of the AILang VS Code extension.

### Language Server (LSP)

- **Real-time diagnostics** — errors and warnings appear as you type
- **Code formatting** — format entire document or selected range via LSP
- **Format on save** — automatic formatting when saving `.ail` files (configurable)
- **Hover documentation** — hover over any identifier to see type info and docs
- **Go to definition** — click any identifier to jump to its declaration
- **Document symbols** — browse functions, variables, and imports in the outline panel
- **Auto-completion** — keywords, stdlib modules, and user-defined functions
- **Signature help** — function parameter hints as you type

### Commands

| Command | Description |
|---------|-------------|
| `AILang: Build Current File` | Compile the active `.ail` file |
| `AILang: Run Current File` | Run the active `.ail` file |
| `AILang: Check Current File` | Pre-flight validation (forward references, missing imports) |
| `AILang: Show Version` | Display installed AILang version |
| `AILang: Format Document` | Format the active document |
| `AILang: Show Output Channel` | Show the extension output log |

### MCP Integration (AI-Assisted)

| Command | Description |
|---------|-------------|
| `AILang MCP: Start Server` | Start the MCP server for AI tools |
| `AILang MCP: Stop Server` | Stop the MCP server |
| `AILang MCP: Restart Server` | Restart the MCP server |
| `AILang MCP: Compile Current File` | Compile via MCP (shows detailed diagnostics) |
| `AILang MCP: Explain Diagnostic Under Cursor` | Get detailed explanation of the error under your cursor |
| `AILang MCP: Insert Code Example` | Insert a code example from the example library |

### Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `ailang.compilerPath` | `"ail"` | Path to the `ail` CLI executable |
| `ailang.formatOnSave` | `true` | Format files automatically on save |
| `ailang.enableDiagnostics` | `true` | Enable real-time error checking |
| `ailang.maxProblems` | `100` | Maximum diagnostics per file |
| `ailang.trace.server` | `"off"` | Log LSP communication (for debugging) |

### Syntax Highlighting

- Full TextMate grammar for AILang syntax
- Keywords, strings, numbers, comments, operators, stdlib modules
- 9 code snippets (`main`, `fn`, `if`, `ifelse`, `import`, `return`, `let`, `recur`, `comment`)
- Language configuration: bracket matching, auto-close, folding, indentation

---

## Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| VS Code | 1.84.0+ | Latest stable |
| Python | 3.11+ | 3.12+ |
| `ail` CLI | v1.0.0+ | v1.1.0+ |
| OS | Windows, macOS, Linux | Any |

---

## Installation

### From VSIX (recommended)

1. Download `vscode-ailang-1.1.0.vsix` from this release
2. In VS Code, run `Extensions: Install from VSIX...` from the Command Palette
3. Select the downloaded `.vsix` file
4. Reload VS Code when prompted

### From Source

```bash
git clone https://github.com/akpersonal4/ailang-lang-AILang.git
cd ailang-lang-AILang/extensions/vscode-ailang
npm install
npm run package
code --install-extension vscode-ailang-1.1.0.vsix
```

---

## Known Limitations

- **Single-file navigation** — Go to Definition, Find References, and Rename work within the current file only
- **Static completion** — Completion list is not context-sensitive (same list regardless of cursor position)
- **No semantic highlighting** — Syntax highlighting uses TextMate grammar only
- **No debugger** — Debugger integration planned for a future release

---

## What's Next

- **M84** — Official Documentation Website
- **M85** — Browser Playground
- **M86** — AI Agent SDK

---

## Links

- [Repository](https://github.com/akpersonal4/ailang-lang-AILang)
- [Language Specification](https://github.com/akpersonal4/ailang-lang-AILang/blob/main/docs/reference/LANGUAGE_SPEC.md)
- [Getting Started](https://github.com/akpersonal4/ailang-lang-AILang/blob/main/docs/reference/GETTING_STARTED.md)
- [Architecture](https://github.com/akpersonal4/ailang-lang-AILang/blob/main/docs/architecture/VSCODE_EXTENSION_ARCHITECTURE.md)

---

## License

Apache-2.0
