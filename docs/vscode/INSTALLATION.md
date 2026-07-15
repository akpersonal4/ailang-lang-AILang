# VS Code Extension — Installation

## Prerequisites

- **VS Code** 1.84 or later
- **AILang** installed (`pip install ailang-lang`)
- `ail` command available in your `PATH`

---

## Install from VS Code Marketplace (Recommended)

Search for "AILang" in the Extensions view (`Ctrl+Shift+X`).

---

## Install from .vsix

The pre-built extension package is included in the repository.

### Windows

```bash
code --install-extension extensions/vscode-ailang/vscode-ailang-0.3.0.vsix
```

### macOS / Linux

```bash
code --install-extension extensions/vscode-ailang/vscode-ailang-0.3.0.vsix
```

### Manual install

1. Open VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
3. Type "Extensions: Install from VSIX..."
4. Navigate to `extensions/vscode-ailang/vscode-ailang-0.3.0.vsix`
5. Click "Install"

---

## Install from Source

```bash
cd extensions/vscode-ailang
npm install
vsce package
code --install-extension vscode-ailang-0.3.0.vsix
```

---

## Verify Installation

1. Open any `.ail` file in VS Code
2. You should see syntax highlighting (keywords in color, strings highlighted)
3. If the file has errors, red squiggly lines appear automatically
4. Press `Ctrl+Space` to see auto-completion suggestions
5. Hover over any function name to see its documentation
6. Check the status bar for MCP server status (green = running)

---

## Troubleshooting

### "ail: command not found"

The extension requires `ail` to be in your system `PATH`. Verify:

```bash
ail --version
```

If this fails, add AILang to your PATH:

```bash
pip install ailang-lang
# Ensure ~/.local/bin (Linux/macOS) or %LOCALAPPDATA%\Python\Scripts (Windows) is in PATH
```

### No syntax highlighting

Ensure the file extension is `.ail`. The extension activates automatically for `.ail` files.

### Diagnostics not appearing

The LSP server starts automatically when you open a `.ail` file. If diagnostics don't appear:

1. Check the VS Code output panel: `View > Output > AILang Language Server`
2. Restart the language server: `Ctrl+Shift+P` → "AILang: Restart Language Server"

### MCP server not starting

The MCP server auto-starts on extension activation. If it's not running:

1. Check the status bar for MCP status
2. Run `Ctrl+Shift+P` → "AILang MCP: Start Server"
3. Check output panel for errors
