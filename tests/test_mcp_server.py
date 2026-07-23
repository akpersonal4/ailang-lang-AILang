"""Tests for AILang MCP Server."""

import json
import subprocess
import sys


def run_mcp_command(request: dict) -> dict:
    """Run a MCP command and return the response."""
    request_json = json.dumps(request)
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_mcp"],
        input=request_json,
        capture_output=True,
        text=True,
    )
    # Parse the last line of stdout (the response)
    lines = result.stdout.strip().split("\n")
    for line in reversed(lines):
        if line.startswith("{"):
            return json.loads(line)
    return {}


def test_mcp_initialize():
    """Test MCP initialize method."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response
    assert response["result"]["serverInfo"]["name"] == "ailang-mcp"
    assert response["result"]["serverInfo"]["version"] == "1.1.3"


def test_mcp_tools_list():
    """Test MCP tools/list method."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 2
    assert "result" in response
    tools = response["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "get_language_context" in tool_names
    assert "get_stdlib" in tool_names
    assert "compile_source" in tool_names
    assert "explain_diagnostic" in tool_names
    assert "get_examples" in tool_names
    assert "get_document" in tool_names


def test_mcp_get_language_context():
    """Test get_language_context tool."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_language_context",
                "arguments": {},
            },
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 3
    assert "result" in response
    content = response["result"]["content"]
    assert len(content) == 1
    data = json.loads(content[0]["text"])
    assert data["language"] == "AILang"
    assert data["version"] == "1.1.3"
    assert "rules" in data
    assert "workflow" in data
    assert "diagnostics" in data
    assert "stdlib" in data
    assert "types" in data
    assert "operators" in data


def test_mcp_get_stdlib_all():
    """Test get_stdlib tool without module argument."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_stdlib",
                "arguments": {},
            },
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 4
    assert "result" in response
    content = response["result"]["content"]
    data = json.loads(content[0]["text"])
    assert "modules" in data
    assert "details" in data
    assert "string" in data["modules"]
    assert "math" in data["modules"]
    assert "list" in data["modules"]


def test_mcp_get_stdlib_module():
    """Test get_stdlib tool with module argument."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_stdlib",
                "arguments": {"module": "string"},
            },
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 5
    assert "result" in response
    content = response["result"]["content"]
    data = json.loads(content[0]["text"])
    assert data["module"] == "string"
    assert "functions" in data
    assert "concat" in data["functions"]
    assert "length" in data["functions"]


def test_mcp_compile_source_valid():
    """Test compile_source tool with valid source."""
    source = "fn main() { return 0 }"
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "compile_source",
                "arguments": {"source": source},
            },
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 6
    assert "result" in response
    content = response["result"]["content"]
    data = json.loads(content[0]["text"])
    assert data["success"] is True
    assert data["diagnostics"] == []


def test_mcp_compile_source_invalid():
    """Test compile_source tool with invalid source."""
    source = "fn main() { let x = y; return 0 }"
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "compile_source",
                "arguments": {"source": source},
            },
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 7
    assert "result" in response
    content = response["result"]["content"]
    data = json.loads(content[0]["text"])
    assert data["success"] is False
    assert len(data["diagnostics"]) > 0


def test_mcp_explain_diagnostic():
    """Test explain_diagnostic tool."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "explain_diagnostic",
                "arguments": {"code": "SEM002"},
            },
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 8
    assert "result" in response
    content = response["result"]["content"]
    data = json.loads(content[0]["text"])
    assert data["code"] == "SEM002"
    assert data["title"] == "Forward Reference"
    assert "description" in data
    assert "cause" in data
    assert "fix" in data
    assert "example" in data


def test_mcp_explain_diagnostic_unknown():
    """Test explain_diagnostic tool with unknown code."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "explain_diagnostic",
                "arguments": {"code": "UNKNOWN"},
            },
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 9
    assert "result" in response
    content = response["result"]["content"]
    data = json.loads(content[0]["text"])
    assert "error" in data
    assert "available_codes" in data


def test_mcp_get_examples_all():
    """Test get_examples tool without category argument."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "get_examples",
                "arguments": {},
            },
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 10
    assert "result" in response
    content = response["result"]["content"]
    data = json.loads(content[0]["text"])
    assert "categories" in data
    assert "examples" in data
    assert "hello" in data["categories"]
    assert "inventory" in data["categories"]


def test_mcp_get_examples_category():
    """Test get_examples tool with category argument."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": "get_examples",
                "arguments": {"category": "hello"},
            },
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 11
    assert "result" in response
    content = response["result"]["content"]
    data = json.loads(content[0]["text"])
    assert data["category"] == "hello"
    assert "title" in data
    assert "code" in data
    assert "fn main()" in data["code"]


def test_mcp_ping():
    """Test MCP ping method."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "ping",
            "params": {},
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 12
    assert "result" in response


def test_mcp_unknown_method():
    """Test MCP with unknown method."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "unknown_method",
            "params": {},
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 13
    assert "error" in response
    assert response["error"]["code"] == -32601


def test_mcp_unknown_tool():
    """Test MCP with unknown tool."""
    response = run_mcp_command(
        {
            "jsonrpc": "2.0",
            "id": 14,
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {},
            },
        }
    )
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 14
    assert "error" in response
    assert response["error"]["code"] == -32603
