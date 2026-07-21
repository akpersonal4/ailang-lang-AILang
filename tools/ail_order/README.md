# AILang Dependency Ordering Assistant (`ail order`)

## Overview

The `ail order` tool analyzes AILang source files to detect dependency ordering issues. It identifies forward reference violations (function called before definition), circular dependencies, unreachable functions, and duplicate declarations.

## Usage

```bash
# Analyze a single file
ail order file.ail

# Analyze a directory (generates reports)
ail order apps/mini_crm/

# Machine-readable JSON output
ail order --json file.ail

# Apply automatic reordering
ail order --fix file.ail

# Output reordered content to stdout
ail order --fix --stdout file.ail

# Quiet mode (suppress non-error output)
ail order --quiet file.ail
```

## Output Format

### Single File

```
Dependency Order Analysis: path/to/file.ail

L0:
  helper_a
  helper_b

L1:
  customer_search

L2:
  customer_reports

L3:
  main

Findings:
  [ERROR] (line 1) Forward reference: 'helper' called before definition
    Suggestion: Move 'helper' before 'main' or call order
  [WARNING] (line 10) Function 'unused_fn' is not reachable from main()
    Suggestion: Consider removing or adding a call path from main()
```

### Project Analysis

When analyzing a directory, Markdown and JSON reports are generated in `reports/`:

- `reports/DEPENDENCY_ORDERING_REPORT.md` — Human-readable analysis
- `reports/DEPENDENCY_ORDERING_REPORT.json` — Machine-readable for LSP/CI

## Detection Capabilities

| Finding | Severity | Description |
|---------|----------|-------------|
| Forward reference | ERROR | Function called before definition |
| Circular dependency | ERROR | Mutual recursion detected |
| Duplicate function | ERROR | Same function defined twice |
| Unreachable function | WARNING | Not reachable from main() |

## Integration

- **LSP Integration**: JSON output designed for language server consumption
- **CI Pipelines**: Exit code 0 for clean files, 1 if errors detected
- **AI Tooling**: Structured output enables automated fixes

## Architecture

```
tools/ail_order/
├── __init__.py     # Package exports
├── models.py       # Data models (FunctionInfo, FileAnalysis, etc.)
├── discovery.py    # Function/call extraction from source
├── graph.py        # Topological level computation, cycle detection
├── fixer.py        # Automatic reordering
├── reporter.py     # Markdown/JSON report generation
└── __main__.py     # CLI entry point
```

## Design Principles

- **No semantic changes**: Tool only analyzes, never modifies language behavior
- **Determinism preserved**: Output is stable across runs
- **Comments preserved**: Fix mode maintains all comments and formatting
- **Bottom-up ordering**: Recommends what order functions should be in