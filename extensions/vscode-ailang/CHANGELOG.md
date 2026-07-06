# Change Log

All notable changes to the AILang VS Code extension will be documented in this file.

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
