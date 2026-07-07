# AILang

**AI-first programming language — deterministic, specification-driven, and compiler-friendly.**

[![Tests](https://img.shields.io/badge/tests-772%20passing-brightgreen)](#)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](#)
[![Version](https://img.shields.io/badge/version-0.3.0-blue)](#)
[![License](https://img.shields.io/badge/license-MIT-green)](#)

AILang is an AI-first programming language designed to be deterministic, specification-first, and easy for both humans and AI systems to reason about. It features a complete compiler pipeline, a 16-module standard library, and has been validated through 772 tests, stress testing up to 10,000 LOC, and AI-generated program verification with 100% first-pass success.

## Quick Start

```bash
# Install
git clone https://github.com/anomalyco/ailang.git
cd ailang
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows
pip install -e .

# Run your first program
echo 'fn main() { print("Hello, AILang!"); return 0 }' > hello.ail
ail hello.ail
```

## Documentation

| Guide | Description |
|-------|-------------|
| [Installation](docs/INSTALLATION.md) | Setup for Windows, Linux, macOS |
| [Getting Started](docs/GETTING_STARTED.md) | Step-by-step introduction |
| [Language Tour](docs/LANGUAGE_TOUR.md) | Complete language feature tour |
| [Standard Library Reference](docs/STDLIB_REFERENCE.md) | All 16 modules documented |
| [Compiler Architecture](docs/COMPILER_ARCHITECTURE.md) | Pipeline and design |
| [Contributor Guide](docs/CONTRIBUTING.md) | How to contribute |
| [Testing Guide](docs/TESTING.md) | Test patterns and practices |
| [Documentation Index](docs/INDEX.md) | All documentation |
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
- **AI-friendly** — validated with 23 AI-generated programs at 100% first-pass success
- **Fast compile times** — 5000 LOC compiles in <2 seconds
- **Low memory usage** — 5000 LOC uses <11 MB peak memory
- **Complete test coverage** — 772 tests across all compiler stages

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
| [string](docs/STDLIB_REFERENCE.md#string) | `concat`, `equals`, `uppercase`, `lowercase`, `length`, `contains`, `starts_with`, `ends_with`, `trim`, `substring` |
| [math](docs/STDLIB_REFERENCE.md#math) | `add`, `sub`, `mul`, `div`, `abs`, `min`, `max` |
| [list](docs/STDLIB_REFERENCE.md#list) | `new`, `append`, `len`, `get`, `contains`, `remove`, `clear` |
| [array](docs/STDLIB_REFERENCE.md#array) | `new`, `push`, `len`, `get`, `contains`, `remove`, `clear` |
| [map](docs/STDLIB_REFERENCE.md#map) | `new`, `set`, `get`, `has`, `delete`, `keys`, `clear` |
| [set](docs/STDLIB_REFERENCE.md#set) | `new`, `add`, `contains`, `len`, `remove`, `clear` |
| [file](docs/STDLIB_REFERENCE.md#file) | `exists`, `read`, `write`, `append`, `remove` |
| [path](docs/STDLIB_REFERENCE.md#path) | `join`, `basename`, `dirname`, `extension`, `normalize` |
| [json](docs/STDLIB_REFERENCE.md#json) | `parse`, `stringify` |
| [csv](docs/STDLIB_REFERENCE.md#csv) | `parse`, `parse_header`, `stringify` |
| [time](docs/STDLIB_REFERENCE.md#time) | `now`, `timestamp`, `sleep`, `format` |
| [random](docs/STDLIB_REFERENCE.md#random) | `int`, `float`, `choice` |
| [environment](docs/STDLIB_REFERENCE.md#environment) | `get`, `cwd`, `args` |
| [convert](docs/STDLIB_REFERENCE.md#convert) | `to_string`, `to_int`, `to_bool`, `to_number` |
| [io](docs/STDLIB_REFERENCE.md#io) | `write`, `writeln`, `println` |
| [system](docs/STDLIB_REFERENCE.md#system) | `exit` |

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
