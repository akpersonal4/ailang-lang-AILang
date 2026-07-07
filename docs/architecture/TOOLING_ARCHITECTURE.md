# AILang Tooling Architecture

**Establishes the architecture contract for all DX tools (past, present, and future).**

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Tool Lifecycle](#2-tool-lifecycle)
3. [CLI Conventions](#3-cli-conventions)
4. [Exit Code Policy](#4-exit-code-policy)
5. [JSON Report Conventions](#5-json-report-conventions)
6. [Generated File Conventions](#6-generated-file-conventions)
7. [tools/common/ Responsibilities](#7-toolscommon-responsibilities)
8. [Shared Utilities](#8-shared-utilities)
9. [Discovery Patterns](#9-discovery-patterns)
10. [Plugin / Extension Points (Future)](#10-plugin--extension-points-future)
11. [Versioning Policy](#11-versioning-policy)
12. [Testing Strategy for DX Tools](#12-testing-strategy-for-dx-tools)

---

## 1. Architecture Overview

### 1.1 Layers

```
┌─────────────────────────────────────────────┐
│              Project Manifest                │
│          ail.toml (single source)            │
├─────────────────────────────────────────────┤
│  Tool A       Tool B       Tool C   ...      │  ← tools/ail_<name>/
│  __main__.py  __main__.py  __main__.py       │
├─────────────────────────────────────────────┤
│           tools/common/ shared lib           │  ← CLI, FS, process, report
├─────────────────────────────────────────────┤
│          compiler/ (language core)           │  ← frozen
└─────────────────────────────────────────────┘
```

### 1.2 Principles

| Principle | Rule |
|-----------|------|
| **Read-only by default** | Tools inspect, analyze, report. Never modify source files unless explicitly designed to (e.g., formatter, package manager `add`). |
| **Dual output** | Every tool produces both Markdown (human) and JSON (machine) output. |
| **Generated directory isolation** | All output goes under `generated/`. Never write into `apps/`, `tests/`, `stdlib/`, or `compiler/`. |
| **Fault-tolerant execution** | One failure does not abort the entire run. Results report per-item status. |
| **Specification-first** | Tool behavior is documented before implementation. CLI flags and output format are frozen before code is written. |
| **Common before custom** | Use `tools/common/` utilities before writing tool-specific code. Extend `common/` when you find a reusable pattern. |

---

## 2. Tool Lifecycle

Every DX tool follows this lifecycle:

```
1. DESIGN   → Architecture doc (this document as contract)
2. SPEC     → Tool-specific design doc (flags, behavior, output)
3. IMPLEMENT → tools/ail_<name>/__main__.py
4. TEST      → tests/dx_tool_NNN_acceptance_test.py
            → tests/dx_tool_NNN_regression_test.py
            → tests/dx_tool_NNN_ai_validation.py
5. DOC       → Update RELEASE docs, CHANGELOG, generated/PROJECT_CONTEXT.md
6. REVIEW    → Architecture review + acceptance tests pass
7. FREEZE    → Tool behavior is locked. Future changes require new DX number.
```

### 2.1 Directory Structure

```
tools/
├── ail_<name>/
│   ├── __init__.py          # (optional) Package marker
│   ├── __main__.py           # CLI entry point
│   ├── models.py             # (optional) Intermediate data models
│   ├── discovery.py          # (optional) File/app discovery
│   ├── runner.py             # (optional) Execution logic
│   ├── reporter.py           # (optional) Report generation (if complex)
│   └── DESIGN.md             # (optional) Tool-specific design doc
├── common/
│   ├── __init__.py
│   ├── cli.py
│   ├── filesystem.py
│   ├── hashing.py
│   ├── process.py
│   └── reporting.py
└── (legacy tools — no __init__.py, self-contained)
```

### 2.2 Entry Point Convention

Every tool's `__main__.py` must:

1. Define a `main() -> int` function
2. Call `raise SystemExit(main())` at module level when invoked directly
3. Accept `python -m tools.ail_<name>` invocation from project root

---

## 3. CLI Conventions

### 3.1 Parser Creation

All tools use `tools.common.cli.create_parser()` as the foundation:

```python
from tools.common.cli import create_parser, add_output_args, add_common_args

def main() -> int:
    parser = create_parser(
        prog="ail <toolname>",
        description="Short description of what the tool does",
    )
    add_output_args(parser)
    add_common_args(parser)
    # Tool-specific args follow
    parser.add_argument(...)
    args = parser.parse_args()
    ...
```

### 3.2 Standard Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--version` | flag | — | Show version and exit (from `create_parser`) |
| `--output-dir` | `Path` | `generated/<tool_name>/` | Report output directory |
| `--quiet` | flag | `False` | Suppress non-error output |
| `--verbose` | flag | `False` | Enable verbose/debug output |
| `--json-only` | flag | `False` | Suppress Markdown output |
| `--markdown-only` | flag | `False` | Suppress JSON output |

### 3.3 Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Tool directory | `tools/ail_<name>/` | `tools/ail_benchmark/` |
| Python module | `tools.ail_<name>` | `tools.ail_benchmark` |
| CLI invocation | `python -m tools.ail_<name>` | `python -m tools.ail_benchmark` |
| Report file (MD) | `<NAME>_REPORT.md` | `BENCHMARK_REPORT.md` |
| Report file (JSON) | `<NAME>_REPORT.json` | `BENCHMARK_REPORT.json` |
| Test file | `dx_tool_NNN_<type>_test.py` | `dx_tool_004_acceptance_test.py` |

### 3.4 Help Text

- `--help` output must use `argparse.RawDescriptionHelpFormatter`
- Description must be ≤80 characters
- Epilogue must not be set (keep default argparse behavior)

---

## 4. Exit Code Policy

All DX tools follow this unified exit code scheme:

| Code | Meaning | When |
|:----:|---------|------|
| `0` | Success | All operations completed without issues |
| `1` | Warning / Failure | One or more items failed but tool completed (e.g., build failure) |
| `2` | Regression | Performance regression detected (benchmark runner only) |
| `3` | Internal error | Tool configuration problem, invalid args, I/O error, no apps found |

### 4.1 Exit Code Rules

- Exit code `0` means the tool completed its work successfully, not necessarily that everything is "good" (e.g., a health check finding issues still exits `1`)
- Exit code `3` means the tool itself cannot function (missing input, bad args, I/O error)
- Exit codes ≥4 are reserved for future use

---

## 5. JSON Report Conventions

### 5.1 Top-Level Structure

Every JSON report must follow this structure:

```json
{
  "metadata": {
    "tool": "ail_<name>",
    "version": "<semver>",
    "timestamp": "<ISO-8601 datetime>"
  },
  "summary": {
    ...tool-specific summary...
  },
  ...tool-specific payload...
}
```

### 5.2 Summary Fields (Common)

Where applicable, summary must include:

| Field | Type | Description |
|-------|------|-------------|
| `total` | `int` | Total items processed |
| `passed` | `int` | Items that passed/succeeded |
| `failed` | `int` | Items that failed |
| `skipped` | `int` | Items that were skipped |

### 5.3 Timestamp Format

- Use `datetime.now(timezone.utc).isoformat()` (ISO-8601 with timezone)
- Example: `"2026-07-07T14:30:00.123456+00:00"`

### 5.4 Version Field

- Matches the tool's version, declared at the top of `__main__.py`
- Independent of the AILang compiler version
- Incremented when tool behavior changes

---

## 6. Generated File Conventions

### 6.1 Output Directory

- Default: `generated/<tool_name>/` (e.g., `generated/benchmarks/`, `generated/`)
- Overridable via `--output-dir`
- Created automatically if it does not exist

### 6.2 File Header

Every generated Markdown file must start with:

```markdown
# <Title>

_Auto-generated by `ail <toolname>` tool_
```

Every generated JSON file must include an `"auto_generated": true` field in metadata, or a comment at the top for non-JSON files.

### 6.3 No In-Place Modification

Generated files:
- Must NOT be committed to version control if they are ephemeral per-run reports
- SHOULD be committed if they are canonical reference outputs (e.g., benchmark baselines, snapshot comparisons)
- Must NEVER overwrite files outside `generated/` without explicit `--force` flag

### 6.4 `--force` Safety

When a tool writes outside `generated/`:
- Require explicit `--force` flag
- Print warning before overwriting
- Never overwrite files that have an `AUTO-GENERATED` or `DO NOT EDIT` header from another tool

---

## 7. tools/common/ Responsibilities

The `tools/common/` package is the shared infrastructure for all DX tools.

### 7.1 Ownership

- `tools/common/` is owned by the project, not by any single tool
- Adding a function to `common/` requires: (a) ≥2 tools would use it, OR (b) it codifies a project-wide convention
- Every function in `common/` must have a docstring and at least one test

### 7.2 Module Map

| Module | Responsibility | Exports |
|--------|---------------|---------|
| `cli.py` | Standard CLI conventions | `create_parser`, `add_output_args`, `add_common_args` |
| `filesystem.py` | Path resolution, file I/O, discovery | `get_project_root`, `read_file_safe`, `ensure_output_dir`, `discover_apps`, `list_py_files` |
| `process.py` | Subprocess execution | `run_subprocess`, `run_ail_build`, `run_ail_run` |
| `reporting.py` | Dual-format report writing | `write_json_report`, `write_markdown_report` |
| `hashing.py` | File content hashing | `hash_file` |

### 7.3 What Goes Where

| Need | Module |
|------|--------|
| Parse CLI args | `cli.py` |
| Find project root | `filesystem.py` |
| Find all `.ail` apps | `filesystem.py.discover_apps()` |
| Lists `.py` files | `filesystem.py.list_py_files()` |
| Read a file safely | `filesystem.py.read_file_safe()` |
| Run a subprocess | `process.py.run_subprocess()` |
| Build an `.ail` file | `process.py.run_ail_build()` |
| Run an `.ail` file | `process.py.run_ail_run()` |
| Write JSON report | `reporting.py.write_json_report()` |
| Write Markdown report | `reporting.py.write_markdown_report()` |
| SHA-256 hash a file | `hashing.py.hash_file()` |

### 7.4 Future Common Modules (Approved)

| Module | Trigger | Status |
|--------|---------|--------|
| `auth.py` | Package manager or registry requires API keys/credentials | Planned (DX-006) |
| `manifest.py` | Project manifest (ail.toml) reading/writing | Planned (DX-006) |
| `archive.py` | Package archive download/extraction | Planned (DX-006) |
| `network.py` | HTTP requests to registries | Planned (DX-006) |

---

## 8. Shared Utilities

### 8.1 Project Root Resolution

```python
def get_project_root() -> Path:
    """Return the project root directory (assumes tools/common/ is 3 levels deep)."""
    return Path(__file__).resolve().parent.parent.parent
```

This works from `tools/common/filesystem.py`. Tools that import from `tools.common` inherit this automatically. Standalone tools (legacy `ail_context`, `ail_doctor`, `ail_static_analyzer`) define their own `get_project_root()` — these should be migrated to use `tools.common.filesystem.get_project_root()`.

### 8.2 File Reading Safety

```python
def read_file_safe(path: Path) -> str | None:
    """Read a file if it exists and is readable. Returns None for binary/unreadable files."""
```

Returns `None` (never raises) for: missing file, binary content, permission error, encoding error.

### 8.3 Output Directory Creation

```python
def ensure_output_dir(path: Path) -> Path:
    """Ensure an output directory exists and return it."""
```

Creates parents as needed. Returns the path for chaining.

### 8.4 App Discovery

```python
def discover_apps(root: Path) -> list[Path]:
    """Discover all AILang app main files under root/apps/."""
```

Returns sorted list of `apps/*/main.ail` paths. Returns empty list if `apps/` doesn't exist.

```python
def list_py_files(root: Path) -> list[Path]:
    """Recursively list all .py files, excluding common noise dirs."""
```

Excludes: `.venv`, `.venv_test`, `.git`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `node_modules`, `__pycache__`.

### 8.5 Subprocess Execution

```python
@dataclass
class ProcessResult:
    stdout: str
    stderr: str
    exit_code: int

def run_subprocess(args: list[str], timeout: int | None = None, cwd: str | None = None) -> ProcessResult
```

Returns structured result. On timeout, returns `exit_code=-1` with `stderr="TIMEOUT after Ns"`.

### 8.6 AILang Build/Run Helpers

```python
def run_ail_build(filepath: str, timeout: int = 120) -> ProcessResult:
def run_ail_run(filepath: str, timeout: int = 120, args: list[str] | None = None) -> ProcessResult:
```

Convenience wrappers around `run_subprocess` that invoke `python -m compiler build/run <filepath>`.

### 8.7 Report Writing

```python
def write_json_report(data: Any, path: Path) -> Path:
    """Write JSON report. Returns path for chaining."""

def write_markdown_report(content: str, path: Path) -> Path:
    """Write Markdown report. Returns path for chaining."""
```

Both create parent directories and write UTF-8 content.

### 8.8 File Hashing

```python
def hash_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file's contents."""
```

Used for: duplicate detection, integrity verification, cache invalidation.

---

## 9. Discovery Patterns

### 9.1 App Discovery

```python
apps/                    # Standard app directory
├── app_name/            # One directory per app
│   ├── main.ail         # Entry point (primary target)
│   └── ...              # Supporting .ail files (imported by main)
```

`discover_apps()` finds `apps/*/main.ail`. For multi-file apps, import analysis is tool-specific.

### 9.2 Module Discovery

```
stdlib/                  # Standard library modules
├── string.ail
├── math.ail
└── ...
```

Module discovery follows the import system. Tools needing module analysis should parse `import` statements from `.ail` files.

### 9.3 Test Discovery

```
tests/                   # Test directory
├── generated/           # Auto-generated test files
├── dx_tool_NNN_*.py     # DX tool tests
└── *.py                 # Compiler/stdlib tests
```

Tools that discover tests (e.g., test generator) must:
- Distinguish generated from hand-written tests
- Not overwrite hand-written tests
- Report coverage gaps separately

---

## 10. Plugin / Extension Points (Future)

### 10.1 Not Yet Implemented

These extension points are **identified but not yet implemented**. They are documented here so that future tools do not accidentally create incompatible designs.

### 10.2 Pre/Post Hooks

Future tools may support lifecycle hooks:

```
ail build    → pre_build hook → build → post_build
ail install  → pre_install → install → post_install
```

Hook scripts would be declared in `ail.toml`:

```toml
[hooks]
pre_install = "scripts/pre_install.sh"
post_install = "scripts/post_install.sh"
```

### 10.3 Tool Composition

Tools may invoke other tools:

```
ail doctor --check benchmarks
    → internally calls ail benchmark --suite quick --quiet
```

When composing, invoke via `run_subprocess`, not direct Python imports.

### 10.4 Output Consumers

Any tool can consume another tool's JSON output:

```
ail static_analyzer --json-only
ail doctor --import-report generated/STATIC_ANALYZER_REPORT.json
```

This requires tools to publish their JSON schema. See §5.

---

## 11. Versioning Policy

### 11.1 Tool Version vs Compiler Version

| Component | Version Source | Update Cadence |
|-----------|---------------|----------------|
| AILang compiler | `pyproject.toml` | Per release |
| DX tools (individual) | Declared in `__main__.py` | Per tool change |
| `tools/common/` | Declared in `__init__.py` | Per `common/` change |

### 11.2 Version Compatibility

- A DX tool's major version must match the compiler's major version
- A DX tool's minor version is independent of the compiler's minor version
- `tools/common/` version is independent of both

---

## 12. Testing Strategy for DX Tools

### 12.1 Test Categories

Every DX tool must have three test files:

| File | Purpose | Pattern |
|------|---------|---------|
| `tests/dx_tool_NNN_acceptance_test.py` | Functional acceptance: tool runs, output exists, exit code correct | 8-12 tests |
| `tests/dx_tool_NNN_regression_test.py` | Edge cases, error handling, flag combinations | 4-8 tests |
| `tests/dx_tool_NNN_ai_validation.py` | AI-generated test scenarios | 3-5 tests |

### 12.2 Test Patterns

```python
class TestAcceptance:
    """Test that the tool runs and produces expected output."""

    def test_runs_successfully(self) -> None:
        """Tool exits 0 with valid input."""
        result = run_subprocess(["python", "-m", "tools.ail_<name>", "."])
        assert result.exit_code == 0

    def test_produces_json_output(self) -> None:
        """JSON report is created and valid."""
        run_subprocess(["python", "-m", "tools.ail_<name>", "."])
        report_path = get_project_root() / "generated" / "<NAME>_REPORT.json"
        assert report_path.exists()
        data = json.loads(report_path.read_text())
        assert "metadata" in data
        assert "summary" in data

    def test_produces_markdown_output(self) -> None:
        """Markdown report is created."""
        run_subprocess(["python", "-m", "tools.ail_<name>", "."])
        report_path = get_project_root() / "generated" / "<NAME>_REPORT.md"
        assert report_path.exists()
```

### 12.3 Test Independence

- Each test creates its own output or uses `--output-dir` to isolate
- Tests must not depend on the state left by a previous test
- Tests clean up generated output after each test class

---

## Appendix A: Current Tool Registry

| DX # | Tool | Status | Tests |
|:----:|------|--------|:-----:|
| DX-001 | `ail context` (legacy, self-contained) | ✅ Complete & Accepted | 9 acceptance + 6 AI validation |
| DX-002 | `ail doctor` (legacy, self-contained) | ✅ Complete & Accepted | 9 acceptance |
| DX-003 | `ail static_analyzer` (legacy, self-contained) | ✅ Complete & Accepted | 8 acceptance + 3 AI validation |
| DX-004 | `ail benchmark` (uses `tools/common/`) | ✅ Complete & Accepted | 11 acceptance + 4 regression + 4 AI |
| DX-005 | `ail testgen` (uses `tools/common/`) | ✅ Complete & Accepted | 9 acceptance + 4 regression + 4 AI |
| DX-006 | `ail pkg` (package manager) | 📋 Planned | — |

Legacy tools (DX-001 through DX-003) are self-contained with their own `get_project_root()` and `read_file_safe()`. They should be migrated to `tools/common/` when next modified.

## Appendix B: Reserved Tool Names

| Name | Purpose |
|------|---------|
| `ail init` | Initialize project manifest |
| `ail add` | Add a dependency |
| `ail remove` | Remove a dependency |
| `ail install` | Install all dependencies |
| `ail search` | Search package registry |
| `ail publish` | Publish a package |
| `ail update` | Update all dependencies |

---

*This document is the architecture contract for all AILang DX tools. Tools that violate these conventions should be updated to conform.*
