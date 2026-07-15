# AILang

**AI-first programming language — deterministic, specification-driven, and compiler-friendly.**

[![Tests](https://img.shields.io/badge/tests-931%20passing-brightgreen)](#)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](#)
[![Version](https://img.shields.io/badge/version-1.0.3-blue)](#)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](#)

AILang is an AI-first programming language designed to be deterministic, specification-first, and easy for both humans and AI systems to reason about. It features a complete compiler pipeline, a 16-module standard library, and has been validated through 931 tests, stress testing up to 10,000 LOC, and AI-generated program verification with 100% first-pass success.

## AI Agent Setup

For AI-assisted development, run this first:

```bash
# Get machine-readable language context
ail context --json

# Read the documentation (installed with the package)
cat $(python -c "import compiler; import os; print(os.path.join(os.path.dirname(compiler.__file__), 'docs', 'AGENTS.md'))")
```

**Document hierarchy:**
1. `AILANG_DEVELOPMENT_PLAYBOOK.md` — coding patterns and conventions
2. `LANGUAGE_SPEC.md` — canonical language definition (authoritative)
3. `AGENTS.md` — AI operational rules (derived from spec)
4. `STDLIB_REFERENCE.md` — library API documentation

> If `AGENTS.md` conflicts with `LANGUAGE_SPEC.md`, the spec wins.

## Quick Start

```bash
# Install from PyPI
pip install ailang-lang

# Run your first program
echo 'fn main() { print("Hello, AILang!"); return 0 }' > hello.ail
ail hello.ail
```

Or install from source:

```bash
git clone https://github.com/akpersonal4/ailang-lang-AILang.git
cd ailang-lang-AILang
pip install -e .

# Run your first program
echo 'fn main() { print("Hello, AILang!"); return 0 }' > hello.ail
ail hello.ail
```

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/reference/GETTING_STARTED.md) | Step-by-step introduction |
| [Language Tour](docs/reference/LANGUAGE_TOUR.md) | Complete language feature tour |
| [Standard Library Reference](docs/reference/STDLIB_REFERENCE.md) | All 16 modules documented |
| [MCP Quick Start](docs/reference/MCP_QUICKSTART.md) | AI tool integration via MCP |
| [Compiler Architecture](docs/reference/COMPILER_ARCHITECTURE.md) | Pipeline and design |
| [Contributor Guide](docs/governance/CONTRIBUTING.md) | How to contribute |
| [Testing Guide](docs/reference/TESTING.md) | Test patterns and practices |
| [Quick Start](docs/QUICKSTART.md) | 5-minute setup guide |
| [VS Code Extension](extensions/vscode-ailang/README.md) | AILang VS Code extension |

## VS Code Extension

Install the AILang extension for syntax highlighting, snippets, bracket matching, and more:
```bash
code --install-extension extensions/vscode-ailang
```

Or package and install from the VS Code Marketplace: `extensions/vscode-ailang/`.

## Features

- **Simple, explicit syntax** — functions, variables, conditionals, recursion
- **Deterministic compilation** — same source always produces same output
- **16-module Standard Library** — string, math, collections, file I/O, JSON, CSV, time, random, environment, conversion
- **AI-native tooling** — `ail mcp` exposes compiler to AI tools via Model Context Protocol
- **AI-friendly** — validated with 23 AI-generated programs at 100% first-pass success
- **Fast compile times** — 5000 LOC compiles in <2 seconds
- **Low memory usage** — 5000 LOC uses <11 MB peak memory
- **Complete test coverage** — 931 tests across all compiler stages

## Example

```ail
import string;
import math;
import list;

fn process(items) {
    let first = list.get(items, 0);
    return string.uppercase(first)
}

fn main() {
    let items = list.new();
    list.append(items, "hello");
    list.append(items, "world");
    let r = process(items);
    let s = math.add(1, 2);
    print(r, s);
    return 0
}
```

## Standard Library

| Module | Operations |
|--------|-----------|
| [string](docs/reference/STDLIB_REFERENCE.md#string) | `concat`, `equals`, `uppercase`, `lowercase`, `length`, `contains`, `starts_with`, `ends_with`, `trim`, `substring`, `find`, `find_from`, `split`, `join`, `from_int`, `from_bool` |
| [math](docs/reference/STDLIB_REFERENCE.md#math) | `add`, `sub`, `mul`, `div`, `abs`, `min`, `max` |
| [list](docs/reference/STDLIB_REFERENCE.md#list) | `new`, `append`, `len`, `get`, `contains`, `remove`, `clear`, `sum`, `find_by_key`, `filter_by_key`, `filter_by_contains`, `collect_key`, `group_by_key`, `sum_by_key`, `take`, `skip`, `search_by_name`, `exists_by_key`, `sort`, `sort_by_key`, `copy` |
| [array](docs/reference/STDLIB_REFERENCE.md#array) | `new`, `push`, `len`, `get`, `contains`, `remove`, `clear` |
| [map](docs/reference/STDLIB_REFERENCE.md#map) | `new`, `set`, `get`, `has`, `delete`, `keys`, `clear`, `values`, `get_or_default`, `safe_get` |
| [set](docs/reference/STDLIB_REFERENCE.md#set) | `new`, `add`, `contains`, `len`, `remove`, `clear` |
| [file](docs/reference/STDLIB_REFERENCE.md#file) | `exists`, `read`, `write`, `append`, `remove`, `listdir` |
| [path](docs/reference/STDLIB_REFERENCE.md#path) | `join`, `basename`, `dirname`, `extension`, `normalize` |
| [json](docs/reference/STDLIB_REFERENCE.md#json) | `parse`, `stringify` |
| [csv](docs/reference/STDLIB_REFERENCE.md#csv) | `parse`, `parse_header`, `stringify` |
| [time](docs/reference/STDLIB_REFERENCE.md#time) | `now`, `timestamp`, `sleep`, `format` |
| [random](docs/reference/STDLIB_REFERENCE.md#random) | `int`, `float`, `choice` |
| [environment](docs/reference/STDLIB_REFERENCE.md#environment) | `get`, `cwd`, `args` |
| [convert](docs/reference/STDLIB_REFERENCE.md#convert) | `to_string`, `to_int`, `to_bool`, `to_number` |
| [io](docs/reference/STDLIB_REFERENCE.md#io) | `write`, `writeln`, `println` |
| [system](docs/reference/STDLIB_REFERENCE.md#system) | `exit` |

## Project Status

| Metric | Value |
|--------|-------|
| Python version | 3.11+ |
| Compiler LOC | ~3,950 (39 Python files) |
| Stdlib modules | 16 |
| Tests | **772 passing** |
| Example programs | 55+ |
| Application programs | 43+ |
| DX Tools | ail context, ail doctor, ail static_analyzer, ail benchmark, ail testgen |
| Quality gates | black, ruff, mypy all clean |
| Validation | Deterministic, AI-verified, stress-tested |

## Formatter

AILang includes a deterministic source code formatter. One style only — no configuration.

```bash
# Format a file in-place
ail fmt hello.ail

# Check if a file is formatted (exit 0 = yes, 1 = no)
ail fmt --check hello.ail

# Read from stdin, write formatted to stdout
cat hello.ail | ail fmt --stdin
```

Formatting rules:
- **4-space indentation**
- **Opening brace on same line** (`fn foo() {`, `if (cond) {`)
- **`} else {` on one line**
- **Spaces around all binary operators** (`a + b`, `x == y`, `a && b`)
- **Space after `,`** in parameter/argument lists
- **Single blank line between function declarations**
- **Trailing whitespace removed**
- **Newline at EOF**
- **Comments preserved** — inline and standalone comments are retained

Formatting is idempotent: formatting an already-formatted file produces no changes.

## Development

```bash
# Install development tools
pip install pytest black ruff mypy

# Run all quality gates
python -m pytest
black --check .
ruff check .
mypy
```

## License

This project is licensed under the MIT License.
