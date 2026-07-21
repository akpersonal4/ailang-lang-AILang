# AILang VS Code MCP Integration

**Version:** 0.3.0
**Status:** Complete — M72 Deliverable
**Milestone:** M72 — VS Code Marketplace + Automatic MCP

---

## Overview

The VS Code extension launches two independent server processes:

1. **LSP Server** (`ail lsp`) — Real-time editor features (diagnostics, completion, hover, go-to-definition)
2. **MCP Server** (`ail mcp`) — AI context queries, on-demand compilation, diagnostic explanations, examples

These servers do not communicate with each other. They serve different purposes and are managed independently.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    VS Code Extension                     │
│                    (extension.js)                        │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  LSP Client   │  │  MCP Client   │  │  Status Bar   │  │
│  │  (language-   │  │  (custom,     │  │  (robot icon) │  │
│  │   client)     │  │   NDJSON)     │  │               │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘  │
│         │                  │                             │
│  ┌──────┴───────┐  ┌──────┴───────┐                    │
│  │  MCP Manager  │  │  Logger       │                    │
│  │  (lifecycle)  │  │  (output)     │                    │
│  └──────────────┘  └──────────────┘                    │
└────────┬───────────────────┬────────────────────────────┘
         │                   │
         ▼                   ▼
┌─────────────────┐  ┌─────────────────┐
│  LSP Server      │  │  MCP Server      │
│  (ail lsp)       │  │  (ail mcp)       │
│                  │  │                  │
│  Diagnostics     │  │  5 MCP Tools     │
│  Completion      │  │  JSON-RPC 2.0    │
│  Hover           │  │  NDJSON          │
│  Definition      │  │  stdio           │
│  References      │  │                  │
│  Rename          │  │                  │
│  Code Actions    │  │                  │
└─────────────────┘  └─────────────────┘
```

---

## Communication Protocol

### LSP (existing)

Uses `Content-Length` framing over stdio, managed by `vscode-languageclient`.

### MCP (new)

Uses newline-delimited JSON (NDJSON) over stdio:

```
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"ailang-mcp","version":"1.0.4"}}}
```

Each message is a single JSON object followed by `\n`. The client buffers incoming data and splits on newlines to extract complete messages.

---

## File Map

```
extensions/vscode-ailang/
├── extension.js              — Entry point (LSP + MCP + commands)
├── package.json              — Manifest (settings, commands, activation)
├── src/
│   ├── mcp-client.js         — MCP JSON-RPC 2.0 client (NDJSON transport)
│   ├── mcp-manager.js        — Server lifecycle state machine
│   └── logger.js             — Output channel wrapper
├── syntaxes/
│   └── ailang.tmLanguage.json — TextMate grammar
├── snippets/
│   └── snippets.code-snippets — 9 code snippets
└── language-configuration.json — Bracket matching, folding, indent
```

---

## State Machine

```
stopped → starting → running
                    → reconnecting → running
                    → failed
starting → failed
reconnecting → failed (after max attempts)
```

State transitions emit `stateChange` events, updating the status bar.

---

## Commands

| Command | Description |
|---------|-------------|
| `ailang.mcp.start` | Start MCP server |
| `ailang.mcp.stop` | Stop MCP server |
| `ailang.mcp.restart` | Restart MCP server |
| `ailang.mcp.compile` | Compile active file via MCP |
| `ailang.mcp.explainDiagnostic` | Explain error under cursor |
| `ailang.mcp.insertExample` | Insert code example at cursor |
| `ailang.showOutput` | Show MCP output channel |

---

## Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ailang.mcp.autoStart` | `boolean` | `true` | Auto-start MCP on activation |
| `ailang.mcp.command` | `string` | `"ail"` | MCP server command |
| `ailang.mcp.args` | `string[]` | `["mcp"]` | MCP server arguments |
| `ailang.mcp.timeout` | `number` | `30000` | Init/call timeout (ms) |
| `ailang.mcp.maxReconnectAttempts` | `number` | `3` | Max reconnect retries |

---

## Reconnect Behavior

When the MCP server process exits unexpectedly:

1. Manager detects exit event from `MCPClient`
2. Enters `reconnecting` state
3. Waits with exponential backoff (1s, 2s, 4s, max 10s)
4. Spawns new process and re-initializes
5. Resets reconnect counter on success
6. Transitions to `failed` after max attempts

---

## Error Handling

| Error | Response |
|-------|----------|
| MCP server not installed | Warning message, status bar shows "Stopped" |
| MCP server crash | Auto-reconnect (up to max attempts) |
| Tool call timeout | Rejects promise, logs error |
| Invalid JSON-RPC response | Logs error, ignores message |
| Client disposed during call | Rejects pending with "Client disposed" |

---

## Testing

Tests are in `tests/test_vscode_mcp_integration.py`:

- **Protocol tests**: Server speaks correct JSON-RPC 2.0
- **Tool tests**: All 5 MCP tools return expected results
- **Client tests**: Node.js MCP client connects, initializes, calls tools
- **Manager tests**: Lifecycle state transitions work correctly
- **Config tests**: package.json has all required contributions

---

## Future Enhancements

| Enhancement | Status |
|-------------|--------|
| Compile-on-save via MCP | Deferred — LSP handles real-time diagnostics |
| Diagnostic code actions via MCP | Deferred — LSP already provides these |
| AI assistant integration | Separate step (Claude Desktop config) |
| Marketplace publication | Requires publisher account + `vsce` |
| TypeScript migration | Deferred — plain JS preserved |
