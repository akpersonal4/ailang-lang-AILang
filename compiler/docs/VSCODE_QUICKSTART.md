# AILang VS Code Extension — Quick Start

## Installation

### From Source (Development)

```bash
# Install AILang
pip install ailang-lang

# Open the extension directory in VS Code
cd extensions/vscode-ailang
code .
```

In VS Code:
1. Press `Ctrl+Shift+B` to build the extension (or skip — no build step needed)
2. Press `F5` to launch the Extension Development Host
3. Open any `.ail` file

### From Marketplace (Future)

```
ext install ailang.vscode-ailang
```

## What Happens Automatically

When you open a `.ail` file:

1. **LSP server starts** — real-time diagnostics, completion, hover, go-to-definition
2. **MCP server starts** — AI context, tool access, example library
3. **Status bar updates** — shows `$(robot) AILang MCP: Running`
4. **No configuration required**

## Features

### Real-time Diagnostics

Errors and warnings appear as you type. No save required.

### AI Context

The MCP server provides language rules, stdlib documentation, and diagnostic explanations to AI tools.

### Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| `AILang MCP: Compile Current File` | — | Compile via MCP, show results |
| `AILang MCP: Explain Diagnostic Under Cursor` | — | Explain error with fix suggestions |
| `AILang MCP: Insert Code Example` | — | Pick category, insert at cursor |
| `AILang MCP: Start Server` | — | Start MCP server |
| `AILang MCP: Stop Server` | — | Stop MCP server |
| `AILang: Show Output Channel` | — | Show MCP logs |

### Example Insertion

1. Run `AILang MCP: Insert Code Example`
2. Pick a category: hello, inventory, csv, json, recursion, file_io
3. Code is inserted at cursor position

### Diagnostic Explanation

1. Place cursor on a diagnostic (red squiggle)
2. Run `AILang MCP: Explain Diagnostic Under Cursor`
3. See title, description, cause, fix, and code examples

## Configuration

All settings are under `ailang.mcp` in VS Code Settings (`Ctrl+,`):

| Setting | Default | Description |
|---------|---------|-------------|
| `ailang.mcp.autoStart` | `true` | Auto-start MCP on activation |
| `ailang.mcp.command` | `"ail"` | MCP server command |
| `ailang.mcp.args` | `["mcp"]` | MCP server arguments |
| `ailang.mcp.timeout` | `30000` | Timeout (ms) |
| `ailang.mcp.maxReconnectAttempts` | `3` | Max reconnect retries |

## Troubleshooting

### MCP server not starting

1. Ensure `ail` is on your PATH: `ail --version`
2. Check the output channel: `AILang: Show Output Channel`
3. Try starting manually: `ail mcp`

### No diagnostics

1. Check that the LSP server started (status bar)
2. Try reloading the window: `Developer: Reload Window`

### MCP status bar shows "Failed"

1. Open output channel for details
2. Run `AILang MCP: Restart Server`
3. Check `ail mcp` works in terminal
