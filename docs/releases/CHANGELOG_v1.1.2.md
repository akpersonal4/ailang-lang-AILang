# Changelog

## v1.1.2 — DX Stabilization Release (2026-07-22)

### Fixed

- **Package detection**: `ail doctor` now correctly detects PyPI, editable, source checkout, and uninstalled states using `importlib.metadata`. Previously showed "NOT INSTALLED" for valid PyPI installations.
- **Doctor mode separation**: `ail doctor` now shows Project Health by default. Repository diagnostics (orphan documents, broken links, archive candidates) only appear with `ail doctor --repo`.
- **Install recommendations**: All tools now recommend `pip install ailang-lang` for end users. Only source checkout users see `pip install -e .`.
- **Heal env_setup**: Updated to recommend `pip install ailang-lang` instead of `pip install -e .`.

### Added

- **`ail doctor --repo`**: Explicit repository health analysis mode for AILang contributors.
- **`ail heal map_safety`**: New topic covering `map.has` guard pattern before `map.get`.
- **`ail heal string_concat`**: New topic explaining the 2-argument limit for `string.concat`.
- **`ail heal <file.ail>`**: File analysis mode documented in usage output.
- **Package detection tests**: 6 new tests for installation method detection and recommendation logic.

### Changed

- **CLI help text**: Updated `doctor` description to "Check project health (use --repo for repository analysis)".
- **CLI help text**: Updated `heal` description to mention file analysis capability.
- **Doctor output format**: Project Health uses structured sections (Environment, Standard Library, Project, Summary).
- **Doctor output format**: Repository Health uses numbered sections with health score.
- **Heal topics**: Now 9 topics (was 7): added `map_safety` and `string_concat`.

---

## Previous Releases

### v1.1.1 — VS Code Extension Release (2026-07-20)
- VS Code Extension v1.1.0: syntax highlighting, LSP, MCP integration, formatting, 12 commands
- MCP Server v1.2.0: 6 tools, JSON-RPC 2.0 over stdio
- 1079 tests passing

### v1.1.0 — Public Beta (2026-07-20)
- Package naming, CLI commands, VS Code extension hardening
- Formatter, language server, package manager
- 66+ applications validated
