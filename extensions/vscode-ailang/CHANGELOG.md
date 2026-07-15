# Change Log

All notable changes to the AILang VS Code extension will be documented in this file.

## [0.3.0] - 2026-07-15

### Added
- MCP server integration with automatic lifecycle management
- 7 commands: Start/Stop/Restart MCP Server, Compile, Explain, Insert Example, Show Output
- Status bar indicator for MCP server state (running/stopped/reconnecting/failed)
- 5 configuration settings: autoStart, command, args, timeout, maxReconnectAttempts
- NDJSON transport for MCP communication
- Reconnection with exponential backoff

### Changed
- License changed from MIT to Apache-2.0
- Repository URL standardized to `akpersonal4/ailang-lang-AILang`
- Added keywords for marketplace discoverability

## [0.2.0] - 2026-07-13

### Added
- Code actions with actual TextEdit edits (import stdlib module, remove unused variable)
- `for` keyword syntax highlighting and completion (experimental)
- Icon field in package.json for marketplace display
- Updated description to reflect LSP capabilities

### Fixed
- Version synchronization: package.json, LSP serverInfo, .vsix all aligned at 0.2.0
- Trailing comma in package.json that caused strict JSON parse errors
- Code actions now generate WorkspaceEdit operations instead of title-only suggestions

### Changed
- Description updated: "syntax highlighting, LSP diagnostics, go-to-definition, hover, rename, snippets"

## [0.1.1] - 2026-07-05

### Added
- `import as` alias syntax highlighting (`import math as m;`)
- All 16 stdlib modules recognized: `string`, `math`, `list`, `array`, `map`, `set`, `json`, `csv`, `file`, `path`, `time`, `random`, `environment`, `convert`, `io`, `system`
- `let` snippet for variable declarations
- `comment` snippet for single-line comments
- 12 comprehensive test `.ail` files covering keywords, operators, strings, numbers, comments, imports, member access, function calls, nested expressions, stdlib usage, control flow, and snippets

### Fixed
- String escape sequences now properly highlighted
- Import statement scope matching improved

## [0.1.0] - 2026-07-05

### Added
- TextMate grammar with full syntax highlighting for `.ail` files
- Language configuration: auto-closing brackets, surrounding pairs, auto-indentation, comment toggling, folding markers
- 9 snippets: `main`, `fn`, `if`, `ifelse`, `import`, `return`, `recur`
- File icon references for Dark+ and Light+ themes
