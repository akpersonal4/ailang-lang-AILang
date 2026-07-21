# AILang MCP Server

**Version:** 1.0.3  
**Status:** Complete — AI Tool Integration  
**Transport:** stdio (local only)

---

## Overview

The AILang MCP (Model Context Protocol) server exposes compiler capabilities directly to AI tools via a local stdio transport. This enables AI systems to:

- Query language rules and constraints
- Compile source code and receive diagnostics
- Get explanations for diagnostic codes
- Access standard library documentation
- Retrieve canonical code examples

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Tool (IDE/Agent)                   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              MCP Client                          │   │
│  │  • JSON-RPC 2.0 over stdio                       │   │
│  │  • Request/response protocol                      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 AILang MCP Server                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Server (server.py)                   │   │
│  │  • JSON-RPC 2.0 handler                           │   │
│  │  • Tool dispatch                                  │   │
│  │  • Error handling                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                           │                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Adapters                             │   │
│  │  • context_adapter.py    → get_language_context   │   │
│  │  • stdlib_adapter.py     → get_stdlib             │   │
│  │  • compiler_adapter.py   → compile_source         │   │
│  │  • diagnostics_adapter.py → explain_diagnostic    │   │
│  │  • examples_adapter.py   → get_examples           │   │
│  └─────────────────────────────────────────────────┘   │
│                           │                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Compiler Pipeline                    │   │
│  │  • Lexer → Parser → AST → Semantic → Type → IR   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## MCP Tools

### get_language_context

Returns AILang language context including rules, workflow, and diagnostics.

**Input:** None

**Output:**
```json
{
  "language": "AILang",
  "version": "1.0.3",
  "rules": {
    "no_loops": {
      "enabled": true,
      "description": "Use recursion only (while/for don't exist in AILang)"
    },
    ...
  },
  "workflow": ["fmt", "check", "build", "test", "run"],
  "diagnostics": {
    "SEM002": "Forward reference",
    ...
  },
  "stdlib": ["string", "math", "list", ...],
  "types": ["int", "float", "string", ...],
  "operators": {
    "arithmetic": ["+", "-", "*", "/", "%"],
    ...
  }
}
```

### get_stdlib

Returns standard library modules, functions, and signatures.

**Input:**
```json
{
  "module": "string"  // Optional: specific module to query
}
```

**Output:**
```json
{
  "modules": ["string", "math", "list", ...],
  "details": {
    "string": {
      "description": "String manipulation functions",
      "functions": {
        "concat": {
          "args": ["str", "str"],
          "returns": "str",
          "description": "Concatenate two strings"
        },
        ...
      }
    },
    ...
  }
}
```

### compile_source

Compiles AILang source code and returns diagnostics.

**Input:**
```json
{
  "source": "fn main() { return 0 }"
}
```

**Output:**
```json
{
  "success": true,
  "diagnostics": []
}
```

Or on error:
```json
{
  "success": false,
  "diagnostics": [
    {
      "code": "SEM002",
      "message": "Forward reference: function 'y' is called before it is defined",
      "line": 1,
      "column": 20,
      "severity": "error"
    }
  ]
}
```

### explain_diagnostic

Returns detailed explanation for a diagnostic code.

**Input:**
```json
{
  "code": "SEM002"
}
```

**Output:**
```json
{
  "code": "SEM002",
  "title": "Forward Reference",
  "description": "The code references a function that is defined later in the file.",
  "cause": "Function is called before it is defined.",
  "fix": "Move the function definition before its first use (bottom-up ordering).",
  "example": {
    "bad": "fn main() { let x = y(); return 0 }\nfn y() { return 42 }",
    "good": "fn y() { return 42 }\nfn main() { let x = y(); return 0 }"
  }
}
```

### get_examples

Returns canonical AILang code examples.

**Input:**
```json
{
  "category": "hello"  // Optional: hello, inventory, csv, json, recursion, file_io
}
```

**Output:**
```json
{
  "category": "hello",
  "title": "Hello World",
  "description": "Basic AILang program with functions and variables",
  "code": "fn greet(name) {\n    ...\n}"
}
```

## JSON-RPC 2.0 Protocol

The MCP server uses JSON-RPC 2.0 over stdio transport.

### Request Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_language_context",
    "arguments": {}
  }
}
```

### Response Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{...}"
      }
    ]
  }
}
```

### Error Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found: unknown_method"
  }
}
```

## Methods

| Method | Description |
|--------|-------------|
| `initialize` | Initialize the MCP server |
| `tools/list` | List available tools |
| `tools/call` | Call a specific tool |
| `ping` | Check server availability |

## Error Codes

| Code | Description |
|------|-------------|
| -32700 | Parse error |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32603 | Internal error |

## Security

- **Local only:** No network access, no HTTP, no cloud
- **No authentication:** Runs on stdio transport
- **No telemetry:** No data collection
- **Read-only:** Compiler queries only, no file system writes

## Integration

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

### Custom Integration

```python
import subprocess
import json

# Start MCP server
process = subprocess.Popen(
    ["ail", "mcp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)

# Send request
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "get_language_context",
        "arguments": {},
    },
}
process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()

# Read response
response = json.loads(process.stdout.readline())
```

## Testing

```bash
python -m pytest tests/test_mcp_server.py -v
```

## File Structure

```
tools/ail_mcp/
├── __init__.py
├── __main__.py
├── server.py
├── compiler_adapter.py
├── context_adapter.py
├── stdlib_adapter.py
├── diagnostics_adapter.py
├── examples_adapter.py
└── tests/
```
