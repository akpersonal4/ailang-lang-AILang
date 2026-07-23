# CLI_CONSISTENCY_REPORT.md — M89E

**Milestone:** M89E — CLI Consistency  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## Issues Fixed

### Issue 1: Core commands don't support --help

**Root cause:** The 10 core commands (`run`, `build`, `fmt`, `test`, `new`, `check`, `rename`, `watch`, `lsp`, `mcp`) used a custom argument parser that treated `--help` as an unknown option, printing to stderr and exiting with code 1.

**Fix:** Added `--help`/`-h` detection at the start of each command's argument parsing. When detected, the command prints usage information to stdout and exits with code 0.

### Commands Fixed

| Command | Before | After |
|---------|--------|-------|
| `ail run --help` | Unknown option, exit 1 | Full help text, exit 0 |
| `ail build --help` | Unknown option, exit 1 | Full help text, exit 0 |
| `ail fmt --help` | Unknown option, exit 1 | Full help text, exit 0 |
| `ail test --help` | Unknown option, exit 1 | Full help text, exit 0 |
| `ail new --help` | Unknown option, exit 1 | Full help text, exit 0 |
| `ail check --help` | Unknown option, exit 1 | Full help text, exit 0 |
| `ail rename --help` | Unknown option, exit 1 | Full help text, exit 0 |
| `ail watch --help` | Unknown option, exit 1 | Full help text, exit 0 |
| `ail mcp --help` | Started server, no help | Full help text, exit 0 |
| `ail lsp --help` | No output | Full help text, exit 0 |

### Issue 2: MCP starts server instead of showing help

**Root cause:** `cmd_mcp` immediately delegated to the MCP server process without checking for help flags.

**Fix:** Added `--help`/`-h` check before delegation. Shows available MCP tools and usage.

## Help Output Consistency

All commands now follow the same pattern:
1. Description line
2. Blank line
3. `Usage:` section with concrete examples
4. Blank line
5. `Options:` section with flag descriptions
6. Exit code 0

## Verification

| Command | --help exit code | Output location |
|---------|:----------------:|:---------------:|
| ail run --help | 0 | stdout |
| ail build --help | 0 | stdout |
| ail fmt --help | 0 | stdout |
| ail test --help | 0 | stdout |
| ail new --help | 0 | stdout |
| ail check --help | 0 | stdout |
| ail rename --help | 0 | stdout |
| ail watch --help | 0 | stdout |
| ail mcp --help | 0 | stdout |
| ail lsp --help | 0 | stdout |
| ail doctor --help | 0 | stdout |
| ail heal --help | 0 | stdout |
| ail explain --help | 0 | stdout |

**Result: All 13 CLI commands now support --help consistently with exit code 0 and stdout output.**
