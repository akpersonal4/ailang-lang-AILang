# Compatibility Matrix

AILang supports the following platforms, languages, and tools.

## Operating Systems

| Platform | Status | Notes |
|----------|--------|-------|
| Windows 10/11 | Supported | Primary development platform |
| Linux (Ubuntu 22.04+) | Supported | CI tested |
| Linux (Debian, Fedora) | Supported | Should work, community tested |
| macOS (Intel) | Supported | CI tested |
| macOS (Apple Silicon) | Supported | Native ARM64 |

## Python Versions

| Version | Status | Notes |
|---------|--------|-------|
| Python 3.11 | Supported | Minimum required version |
| Python 3.12 | Supported | Fully tested |
| Python 3.13 | Tested | Should work, not yet CI tested |

## IDE & Editor Support

| Tool | Status | Features |
|------|--------|----------|
| VS Code 1.84+ | Supported | Syntax highlighting, LSP (diagnostics, hover, completion, go-to-definition, find references, rename, signature help, symbols, code actions), MCP server integration, snippets |
| Cursor | Via MCP | Full MCP tool access (get_language_context, get_stdlib, compile_source, explain_diagnostic, get_examples) |
| Windsurf | Via MCP | Full MCP tool access |
| Claude Desktop | Via MCP | Full MCP tool access |
| GitHub Copilot | Via MCP | Full MCP tool access |
| OpenCode | Via MCP | Full MCP tool access |

## AI Tool Integration (MCP)

| Tool | Transport | Auto-Start | Status |
|------|-----------|------------|--------|
| Claude Code | stdio | Yes | Supported |
| Cursor | stdio | Yes | Supported |
| Windsurf | stdio | Yes | Supported |
| GitHub Copilot | stdio | Yes | Supported |
| OpenCode | stdio | Yes | Supported |
| Custom MCP clients | stdio | Manual | Supported (JSON-RPC 2.0) |

## Installation Methods

| Method | Command | Status |
|--------|---------|--------|
| PyPI | `pip install ailang-lang` | Supported |
| Source | `git clone` + `pip install -e .` | Supported |
| uv | `uv pip install ailang-lang` | Supported |
| VS Code Marketplace | Search "AILang" | Supported |
| VS Code .vsix | `code --install-extension` | Supported |

## Standard Library Modules (16)

All 16 modules are supported on all platforms:

`string`, `math`, `list`, `array`, `map`, `set`, `file`, `path`, `json`, `csv`, `time`, `random`, `environment`, `convert`, `io`, `system`
