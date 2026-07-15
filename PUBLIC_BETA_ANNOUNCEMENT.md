# AILang Public Beta Announcement

**Version:** v1.0.5 | **Date:** July 15, 2026 | **Phase:** Public Beta

---

## What is AILang?

AILang is an **AI-first programming language** designed to be deterministic, specification-driven, and easy for both humans and AI systems to reason about.

Unlike traditional languages adapted for AI, AILang was built from the ground up with AI code generation as a primary use case. It features:

- **Deterministic compilation** — same source always produces same output
- **Simple, explicit syntax** — functions, variables, conditionals, recursion
- **No hidden behavior** — what you see is what you get
- **AI-native tooling** — MCP server exposes the compiler to AI tools

> AILang is not intended to replace Python, Java, or Go. It is designed specifically for deterministic business applications and AI-assisted development workflows.

## Who is AILang for?

- **AI-assisted developers** — Build business applications with AI coding assistants
- **Teams using AI tools** — Claude Code, Cursor, Windsurf, GitHub Copilot users
- **Business software developers** — CRUD apps, data processing, file operations
- **Anyone curious about AI-first language design**

## Installation

```bash
# Install from PyPI
pip install ailang-lang

# Run your first program
echo 'fn main() { print("Hello, AILang!"); return 0 }' > hello.ail
ail run hello.ail
```

## Key Features

### Compiler Pipeline
- Full lexer → parser → AST → IR → interpreter pipeline
- 894 tests passing across all stages
- Designed for fast compilation and low memory usage for business applications

### 16-Module Standard Library
`string`, `math`, `list`, `array`, `map`, `set`, `file`, `path`, `json`, `csv`, `time`, `random`, `environment`, `convert`, `io`, `system`

### AI-Native Tooling

**MCP Server** (`ail mcp`):
- 5 tools: `get_language_context`, `get_stdlib`, `compile_source`, `explain_diagnostic`, `get_examples`
- JSON-RPC 2.0 over stdio
- Works with Claude Code, Cursor, Windsurf, GitHub Copilot, OpenCode

**VS Code Extension** (v0.3.0):
- Syntax highlighting, snippets, bracket matching
- LSP: hover, completion, diagnostics, go-to-definition, find references, rename
- MCP server integration with auto-start
- Status bar indicator for MCP server state

### Developer Tools
- `ail fmt` — Deterministic formatter (one style, no config)
- `ail check` — Pre-flight ordering validation
- `ail doctor` — Repository health checker
- `ail benchmark` — Benchmark runner
- `ail testgen` — Test generator

## Reference Applications

8 canonical examples demonstrating real-world patterns:

| App | Description |
|-----|-------------|
| `todo` | Task management with CRUD operations |
| `expense` | Expense tracking and categorization |
| `inventory` | Full inventory system with auth, backup, CSV import |
| `employee` | Employee record management |
| `log_analyzer` | Log file processing and analysis |
| `csv_etl` | CSV extraction, transformation, loading |
| `json_transformer` | JSON data transformation |
| `invoice` | Invoice generation and management |

## Example Code

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

## Platform Support

| Platform | Status |
|----------|--------|
| Windows 10/11 | Supported |
| Linux (Ubuntu 22.04+) | Supported |
| macOS (Intel) | Supported |
| macOS (Apple Silicon) | Supported |
| Python 3.11+ | Required |

## AI Tool Integration

| Tool | Supported via MCP |
|------|:-----------------:|
| Claude Code | Yes |
| Cursor | Yes |
| Windsurf | Yes |
| GitHub Copilot | Yes |
| OpenCode | Yes |

## Known Limitations

- **Recursion only** — No `while`/`for` loops (by design; use recursion)
- **No nested functions** — All functions at top level
- **Forward references not allowed** — Callee must be defined before caller
- **Stdlib frozen** — Additions require evidence from ≥2 independent benchmarks
- **Language frozen** — No syntax changes without governance vote

## Documentation

- [Getting Started](https://github.com/akpersonal4/ailang-lang-AILang/blob/main/docs/reference/GETTING_STARTED.md) — Step-by-step introduction
- [Language Tour](https://github.com/akpersonal4/ailang-lang-AILang/blob/main/docs/reference/LANGUAGE_TOUR.md) — Complete feature tour
- [Language Specification](https://github.com/akpersonal4/ailang-lang-AILang/blob/main/docs/reference/LANGUAGE_SPEC.md) — Canonical grammar and semantics
- [Stdlib Reference](https://github.com/akpersonal4/ailang-lang-AILang/blob/main/docs/reference/STDLIB_REFERENCE.md) — All 16 modules documented
- [MCP Quickstart](https://github.com/akpersonal4/ailang-lang-AILang/blob/main/docs/reference/MCP_QUICKSTART.md) — AI tool integration
- [VS Code Extension](https://github.com/akpersonal4/ailang-lang-AILang/blob/main/extensions/vscode-ailang/README.md) — IDE setup and features

## Links

- **GitHub:** https://github.com/akpersonal4/ailang-lang-AILang
- **PyPI:** https://pypi.org/project/ailang-lang/1.0.5/
- **VS Code Marketplace:** Search "AILang"
- **Issues:** https://github.com/akpersonal4/ailang-lang-AILang/issues
- **Discussions:** https://github.com/akpersonal4/ailang-lang-AILang/discussions

## Feedback

We want your feedback! Please:

- **Report bugs:** [GitHub Issues](https://github.com/akpersonal4/ailang-lang-AILang/issues)
- **Ask questions:** [GitHub Discussions](https://github.com/akpersonal4/ailang-lang-AILang/discussions)
- **Share what you build:** Tag us or open a discussion

## What's Next

- **M75** — Feedback and telemetry collection
- **M76** — AI ergonomics study
- **M77** — Constraint validation
- **P2** — 90-Day Production Validation

## License

Apache License 2.0

---

**Thank you for trying AILang!** Your feedback helps us build a better AI-first development experience.
