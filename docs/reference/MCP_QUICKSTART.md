# AILang MCP Quick Start

**Version:** 1.0.3

---

## What is MCP?

MCP (Model Context Protocol) is a standard for AI tools to interact with external systems. The AILang MCP server exposes compiler capabilities to AI tools via stdio transport.

## Quick Start

### 1. Start the MCP Server

```bash
ail mcp
```

Output:
```
AILang MCP Server v1.0.3
Transport: stdio
Ready.
```

### 2. Send a Request

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_language_context","arguments":{}}}' | ail mcp
```

### 3. Get Language Context

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"language\": \"AILang\",\n  \"version\": \"1.0.3\",\n  ...\n}"
      }
    ]
  }
}
```

## Available Tools

### get_language_context

Get AILang language rules, workflow, and diagnostics.

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_language_context","arguments":{}}}' | ail mcp
```

### get_stdlib

Get standard library modules and functions.

```bash
# All modules
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_stdlib","arguments":{}}}' | ail mcp

# Specific module
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_stdlib","arguments":{"module":"string"}}}' | ail mcp
```

### compile_source

Compile AILang source code.

```bash
# Valid source
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"compile_source","arguments":{"source":"fn main() { return 0 }"}}}' | ail mcp

# Invalid source (forward reference)
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"compile_source","arguments":{"source":"fn main() { let x = y(); return 0 }\nfn y() { return 42 }"}}}' | ail mcp
```

### explain_diagnostic

Get detailed explanation for a diagnostic code.

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"explain_diagnostic","arguments":{"code":"SEM002"}}}' | ail mcp
```

### get_examples

Get canonical AILang code examples.

```bash
# All examples
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_examples","arguments":{}}}' | ail mcp

# Specific category
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_examples","arguments":{"category":"hello"}}}' | ail mcp
```

## Integration with AI Tools

### Claude Code

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ailang": {
      "command": "ail",
      "args": ["mcp"]
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ailang": {
      "command": "ail",
      "args": ["mcp"]
    }
  }
}
```

## Example: AI Agent Workflow

1. **Connect to MCP server**
2. **Query language context** → `get_language_context`
3. **Query stdlib** → `get_stdlib`
4. **Generate code** based on rules and examples
5. **Compile code** → `compile_source`
6. **If errors** → `explain_diagnostic` to understand and fix
7. **Retry compilation** until successful

## Troubleshooting

### Server won't start

Check that AILang is installed:

```bash
ail --version
```

### No response

Ensure you're sending valid JSON-RPC 2.0 requests with a newline at the end.

### Unknown tool error

Check available tools:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | ail mcp
```
