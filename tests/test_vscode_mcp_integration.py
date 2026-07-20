"""Tests for AILang VS Code MCP Integration.

Tests the MCP client and manager against a real `ail mcp` server process.
Does not require VS Code — uses the Node.js modules directly.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_mcp_command(request: dict) -> dict:
    """Run a single MCP command synchronously via subprocess."""
    request_json = json.dumps(request)
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_mcp"],
        input=request_json,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    lines = result.stdout.strip().split("\n")
    for line in reversed(lines):
        if line.startswith("{"):
            return json.loads(line)
    return {}


# ---------------------------------------------------------------------------
# MCP Protocol Tests (via subprocess — validates server-side protocol)
# ---------------------------------------------------------------------------


class TestMCPProtocol:
    """Verify the MCP server speaks correct JSON-RPC 2.0 over NDJSON."""

    def test_initialize_returns_server_info(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {},
            }
        )
        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 1
        assert "result" in resp
        info = resp["result"]["serverInfo"]
        assert info["name"] == "ailang-mcp"
        assert "version" in info

    def test_initialize_declares_capabilities(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {},
            }
        )
        caps = resp["result"]["capabilities"]
        assert "tools" in caps

    def test_tools_list_returns_five_tools(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }
        )
        tools = resp["result"]["tools"]
        names = [t["name"] for t in tools]
        assert len(tools) == 6
        assert "get_language_context" in names
        assert "get_stdlib" in names
        assert "compile_source" in names
        assert "explain_diagnostic" in names
        assert "get_examples" in names
        assert "get_document" in names

    def test_tools_have_schemas(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }
        )
        for tool in resp["result"]["tools"]:
            assert "inputSchema" in tool
            assert "type" in tool["inputSchema"]

    def test_ping_returns_empty(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "ping",
                "params": {},
            }
        )
        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 3
        assert "result" in resp

    def test_unknown_method_returns_error(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "bogus_method",
                "params": {},
            }
        )
        assert "error" in resp
        assert resp["error"]["code"] == -32601


# ---------------------------------------------------------------------------
# MCP Tool Execution Tests (via subprocess)
# ---------------------------------------------------------------------------


class TestMCPTools:
    """Test each MCP tool via synchronous subprocess calls."""

    def test_get_language_context(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {"name": "get_language_context", "arguments": {}},
            }
        )
        data = json.loads(resp["result"]["content"][0]["text"])
        assert data["language"] == "AILang"
        assert "rules" in data
        assert "workflow" in data
        assert data["workflow"] == ["fmt", "check", "build", "test", "run"]

    def test_get_stdlib_all(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 11,
                "method": "tools/call",
                "params": {"name": "get_stdlib", "arguments": {}},
            }
        )
        data = json.loads(resp["result"]["content"][0]["text"])
        assert "modules" in data
        assert len(data["modules"]) >= 15

    def test_get_stdlib_specific_module(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 12,
                "method": "tools/call",
                "params": {"name": "get_stdlib", "arguments": {"module": "math"}},
            }
        )
        data = json.loads(resp["result"]["content"][0]["text"])
        assert data["module"] == "math"
        assert "add" in data["functions"]

    def test_compile_source_valid(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 13,
                "method": "tools/call",
                "params": {
                    "name": "compile_source",
                    "arguments": {"source": "fn main() { return 0 }"},
                },
            }
        )
        data = json.loads(resp["result"]["content"][0]["text"])
        assert data["success"] is True
        assert data["diagnostics"] == []

    def test_compile_source_invalid(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 14,
                "method": "tools/call",
                "params": {
                    "name": "compile_source",
                    "arguments": {"source": "fn main() { let x = y; return 0 }"},
                },
            }
        )
        data = json.loads(resp["result"]["content"][0]["text"])
        assert data["success"] is False
        assert len(data["diagnostics"]) > 0

    def test_explain_diagnostic_valid_code(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 15,
                "method": "tools/call",
                "params": {
                    "name": "explain_diagnostic",
                    "arguments": {"code": "SEM002"},
                },
            }
        )
        data = json.loads(resp["result"]["content"][0]["text"])
        assert data["code"] == "SEM002"
        assert data["title"] == "Forward Reference"
        assert "fix" in data

    def test_explain_diagnostic_unknown_code(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 16,
                "method": "tools/call",
                "params": {
                    "name": "explain_diagnostic",
                    "arguments": {"code": "BOGUS99"},
                },
            }
        )
        data = json.loads(resp["result"]["content"][0]["text"])
        assert "error" in data
        assert "available_codes" in data

    def test_get_examples_hello(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 17,
                "method": "tools/call",
                "params": {
                    "name": "get_examples",
                    "arguments": {"category": "hello"},
                },
            }
        )
        data = json.loads(resp["result"]["content"][0]["text"])
        assert data["category"] == "hello"
        assert "fn main()" in data["code"]

    def test_get_examples_all(self):
        resp = run_mcp_command(
            {
                "jsonrpc": "2.0",
                "id": 18,
                "method": "tools/call",
                "params": {"name": "get_examples", "arguments": {}},
            }
        )
        data = json.loads(resp["result"]["content"][0]["text"])
        assert "categories" in data
        assert len(data["categories"]) >= 6


# ---------------------------------------------------------------------------
# MCP Client Tests (via Node.js subprocess)
# ---------------------------------------------------------------------------


class TestMCPClient:
    """Test the Node.js MCP client by running a small Node script."""

    @staticmethod
    def _run_node(script: str) -> str:
        """Run a Node.js script and return stdout."""
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT / "extensions" / "vscode-ailang"),
            timeout=30,
        )
        return result.stdout + result.stderr

    @staticmethod
    def _py_path() -> str:
        """Return the Python executable path, escaped for JS string literals."""
        return sys.executable.replace("\\", "\\\\")

    @staticmethod
    def _root_path() -> str:
        """Return the project root path, escaped for JS string literals."""
        return str(PROJECT_ROOT).replace("\\", "\\\\")

    def test_client_imports(self):
        out = self._run_node(
            "const {MCPClient} = require('./src/mcp-client'); "
            "console.log('MCPClient loaded: ' + typeof MCPClient);"
        )
        assert "MCPClient loaded: function" in out

    def test_manager_imports(self):
        out = self._run_node(
            "const {MCPManager} = require('./src/mcp-manager'); "
            "console.log('MCPManager loaded: ' + typeof MCPManager);"
        )
        assert "MCPManager loaded: function" in out

    def test_logger_imports(self):
        out = self._run_node(
            "const {Logger} = require('./src/logger'); "
            "console.log('Logger loaded: ' + typeof Logger);"
        )
        assert "Logger loaded: function" in out

    def test_client_connects_and_initializes(self):
        py = self._py_path()
        root = self._root_path()
        script = (
            "const {MCPClient} = require('./src/mcp-client');"
            "const {spawn} = require('child_process');"
            "const log = {info:()=>{}, error:()=>{}, warn:()=>{}, debug:()=>{}};"
            "const child = spawn('" + py + "', ['-m', 'tools.ail_mcp'], {"
            "  stdio: ['pipe', 'pipe', 'pipe'], cwd: '" + root + "'"
            "});"
            "const client = new MCPClient(child, log);"
            "client.initialize(15000).then(r => {"
            "  console.log('server=' + r.serverInfo.name);"
            "  console.log('tools=' + r.tools.length);"
            "  client.dispose(); process.exit(0);"
            "}).catch(e => {"
            "  console.error('FAIL: ' + e.message);"
            "  client.dispose(); process.exit(1);"
            "});"
        )
        out = self._run_node(script)
        assert "server=ailang-mcp" in out
        assert "tools=6" in out

    def test_client_calls_tool(self):
        py = self._py_path()
        root = self._root_path()
        script = (
            "const {MCPClient} = require('./src/mcp-client');"
            "const {spawn} = require('child_process');"
            "const log = {info:()=>{}, error:()=>{}, warn:()=>{}, debug:()=>{}};"
            "const child = spawn('" + py + "', ['-m', 'tools.ail_mcp'], {"
            "  stdio: ['pipe', 'pipe', 'pipe'], cwd: '" + root + "'"
            "});"
            "const client = new MCPClient(child, log);"
            "client.initialize(15000).then(async () => {"
            "  const r = await client.callTool('get_examples', {category: 'hello'});"
            "  const d = JSON.parse(r.content[0].text);"
            "  console.log('category=' + d.category);"
            "  console.log('has_code=' + (d.code.indexOf('fn main') >= 0));"
            "  client.dispose(); process.exit(0);"
            "}).catch(e => {"
            "  console.error('FAIL: ' + e.message);"
            "  client.dispose(); process.exit(1);"
            "});"
        )
        out = self._run_node(script)
        assert "category=hello" in out
        assert "has_code=true" in out

    def test_client_not_initialized_error(self):
        py = self._py_path()
        root = self._root_path()
        script = (
            "const {MCPClient} = require('./src/mcp-client');"
            "const {spawn} = require('child_process');"
            "const log = {info:()=>{}, error:()=>{}, warn:()=>{}, debug:()=>{}};"
            "const child = spawn('" + py + "', ['-m', 'tools.ail_mcp'], {"
            "  stdio: ['pipe', 'pipe', 'pipe'], cwd: '" + root + "'"
            "});"
            "const client = new MCPClient(child, log);"
            "client.callTool('get_examples').then(() => {"
            "  console.log('FAIL: should have thrown');"
            "  client.dispose(); process.exit(1);"
            "}).catch(e => {"
            "  console.log('correct_error=' + e.message.includes('not initialized'));"
            "  client.dispose(); process.exit(0);"
            "});"
        )
        out = self._run_node(script)
        assert "correct_error=true" in out

    def test_manager_lifecycle(self):
        py = self._py_path()
        root = self._root_path()
        script = (
            "const {MCPManager} = require('./src/mcp-manager');"
            "const log = {info:()=>{}, error:()=>{}, warn:()=>{}, debug:()=>{}};"
            "const cfg = {command: '" + py + "', args: ['-m', 'tools.ail_mcp'],"
            "  timeout: 15000, maxReconnectAttempts: 1};"
            "const mgr = new MCPManager(log, cfg);"
            "mgr.start().then(async () => {"
            "  console.log('state=' + mgr.state);"
            "  console.log('tools=' + mgr.client.tools.length);"
            "  await mgr.stop();"
            "  console.log('stopped=' + (mgr.state === 'stopped'));"
            "  await mgr.dispose();"
            "  process.exit(0);"
            "}).catch(e => {"
            "  console.error('FAIL: ' + e.message);"
            "  mgr.dispose(); process.exit(1);"
            "});"
        )
        out = self._run_node(script)
        assert "state=running" in out
        assert "tools=6" in out
        assert "stopped=true" in out


# ---------------------------------------------------------------------------
# Configuration Tests
# ---------------------------------------------------------------------------


class TestMCPConfiguration:
    """Verify VS Code extension package.json contributes are correct."""

    def test_package_json_has_settings(self):
        pkg_path = PROJECT_ROOT / "extensions" / "vscode-ailang" / "package.json"
        pkg = json.loads(pkg_path.read_text())
        config = pkg["contributes"]["configuration"]["properties"]
        assert "ailang.mcp.autoStart" in config
        assert "ailang.mcp.command" in config
        assert "ailang.mcp.args" in config
        assert "ailang.mcp.timeout" in config
        assert "ailang.mcp.maxReconnectAttempts" in config

    def test_package_json_has_commands(self):
        pkg_path = PROJECT_ROOT / "extensions" / "vscode-ailang" / "package.json"
        pkg = json.loads(pkg_path.read_text())
        commands = [c["command"] for c in pkg["contributes"]["commands"]]
        assert "ailang.mcp.start" in commands
        assert "ailang.mcp.stop" in commands
        assert "ailang.mcp.restart" in commands
        assert "ailang.mcp.compile" in commands
        assert "ailang.mcp.explainDiagnostic" in commands
        assert "ailang.mcp.insertExample" in commands
        assert "ailang.showOutput" in commands

    def test_package_json_version(self):
        pkg_path = PROJECT_ROOT / "extensions" / "vscode-ailang" / "package.json"
        pkg = json.loads(pkg_path.read_text())
        assert pkg["version"] == "0.3.0"

    def test_package_json_activation_events(self):
        pkg_path = PROJECT_ROOT / "extensions" / "vscode-ailang" / "package.json"
        pkg = json.loads(pkg_path.read_text())
        assert "onLanguage:ailang" in pkg["activationEvents"]
