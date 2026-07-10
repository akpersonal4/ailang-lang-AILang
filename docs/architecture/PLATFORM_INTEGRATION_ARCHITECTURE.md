# Platform Integration Architecture

**Defines the shared `ail_platform/` layer that consolidates duplicated project logic across all DX tools.**

---

## Table of Contents

1. [Motivation](#1-motivation)
2. [Platform Layer Overview](#2-platform-layer-overview)
3. [Shared Project Model](#3-shared-project-model)
4. [Workspace Model](#4-workspace-model)
5. [Manifest Handling](#5-manifest-handling)
6. [Report Schema](#6-report-schema)
7. [Diagnostics Model](#7-diagnostics-model)
8. [Symbol Services](#8-symbol-services)
9. [Event Model](#9-event-model)
10. [Extension Points](#10-extension-points)
11. [Migration Strategy](#11-migration-strategy)
12. [Testing Strategy](#12-testing-strategy)
13. [Backward Compatibility Guarantees](#13-backward-compatibility-guarantees)

---

## 1. Motivation

### 1.1 Current State

The project has 6 DX tools plus a Language Server. Over time, each tool independently solved the same problems, producing 6+ copies of the same logic:

| Pattern | Occurrences | Impact |
|---------|:-----------:|--------|
| `get_project_root()` | 6 copies (5 local + 1 shared but unused) | Changing root resolution requires touching 6 files |
| `read_file_safe()` | 3 variants (shared + 2 local) | Inconsistent error handling |
| CLI argument parsing | 4 ad-hoc implementations | Flag inconsistencies across tools |
| Report writing | 5 custom implementations | Each tool builds Markdown/JSON from scratch |
| Exit codes | 4 incompatible schemes | `exit 2` = "regression" in benchmark, "no files" in static_analyzer |
| Diagnostics conversion | 3 separate pathways | LSP → client, CLI → stderr, static analyzer → stdout parse |

### 1.2 Problem

Every duplicated pattern creates:
- **Maintenance burden** — changing a convention requires hunting all copies
- **Inconsistency** — tools behave differently with the same flags
- **Onboarding friction** — new tools must reimplement the same patterns
- **Bug surface** — each copy independently rots

### 1.3 Goal

A single `ail_platform/` package that provides canonical implementations for all cross-tool concerns. Existing tools import platform modules; new tools are built on them by default.

### 1.4 Non-Goals

- **Not a rewrite** — platform modules extract existing patterns; no new features
- **Not a framework** — tools remain independent executables; platform is a library
- **Not touching compiler core** — `compiler/` is frozen; platform wraps the compiler, doesn't modify it

---

## 2. Platform Layer Overview

### 2.1 Layers After Integration

```
┌──────────────────────────────────────────────────────────┐
│                    DX Tools (7 services)                   │
│  bench  doctor  context  static_analyzer  testgen  pkg  │
│                        LSP                                │
├──────────────────────────────────────────────────────────┤
│                    platform/ (shared)                      │
│  project  workspace  manifest  diagnostics               │
│  symbol_index  report_schema  configuration  events       │
├──────────────────────────────────────────────────────────┤
│                  tools/common/ (lightweight)               │
│  cli  filesystem  process  hashing                        │
├──────────────────────────────────────────────────────────┤
│                   compiler/ (language core)                │
│  lexer  parser  ast  semantic  diagnostics  lsp          │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Module Map

| Module | Responsibility | Source of Truth |
|--------|---------------|-----------------|
| `ail_platform/project.py` | Project root, app discovery, output dirs | Extracted from `tools/common/filesystem.py` + tool copies |
| `ail_platform/workspace.py` | Workspace model (root, apps, modules, config) | New; informed by LSP document model |
| `ail_platform/manifest.py` | `ail.toml` parse/validate/find/write | Extracted from `tools/ail_package_manager/manifest.py` |
| `ail_platform/diagnostics.py` | Diagnostic model, severity mapping, LSP conversion | Extracted from `compiler/lsp/features/diagnostics.py` + `compiler/diagnostics.py` |
| `ail_platform/symbol_index.py` | Cross-file symbol index, AST walk utilities | Extracted from LSP feature modules |
| `ail_platform/report_schema.py` | Standard report schema, JSON/MD generation | Extracted from `tools/common/reporting.py` + tool reporters |
| `ail_platform/configuration.py` | Tool configuration from `ail.toml [tools.<name>]` | New; schema-driven |
| `ail_platform/events.py` | Event bus for cross-tool communication | New; lightweight observer pattern |
| `ail_platform/__init__.py` | Version, exports | Canonical platform version |

### 2.3 Platform Dependency Rules

```
platform/
├── events.py          — No dependencies on other platform modules
├── project.py         — No dependencies on other platform modules
├── report_schema.py   — No dependencies on other platform modules
├── manifest.py        — No dependencies on other platform modules
├── diagnostics.py     — No dependencies on other platform modules
├── configuration.py   — Depends on: manifest
├── symbol_index.py    — Depends on: diagnostics (for symbol diagnostics)
├── workspace.py       — Depends on: project, manifest, configuration
```

---

## 3. Shared Project Model

### 3.1 Canonical Project Root

```python
# platform/project.py

from pathlib import Path


def get_project_root() -> Path:
    """Return the project root directory.

    Walks up from the platform package location (3 levels deep
    under the project root: platform/ → project root).
    Falls back to cwd-based discovery for non-standard layouts.
    """
    return Path(__file__).resolve().parent.parent.parent
```

All tools replace their local `get_project_root()` with `ail_platform.project.get_project_root()`.

### 3.2 App Discovery

```python
@dataclass
class AppInfo:
    name: str
    root: Path
    main_file: Path
    ail_files: list[Path]

def discover_apps(root: Path | None = None) -> list[AppInfo]:
    """Discover all AILang apps under root/apps/."""
```

Standardizes the pattern currently scattered across `tools.common.filesystem.discover_apps()` and tool-local copies.

### 3.3 Output Directory Resolution

```python
def ensure_output_dir(tool_name: str, root: Path | None = None,
                      override: Path | None = None) -> Path:
    """Return (and create) the output directory for a tool.

    Default: <project_root>/generated/<tool_name>/
    Override via --output-dir argument.
    """
```

### 3.4 Safe File Reading

```python
def read_file_safe(path: Path) -> str | None:
    """Read a file if it exists and is readable.

    Returns None (never raises) for:
    - Missing file
    - Binary content (UnicodeDecodeError)
    - Permission error (OSError)
    - Encoding error (LookupError)
    """
```

Canonicalizes 3 variants. Uses the most robust version (try/except for `UnicodeDecodeError, OSError`).

---

## 4. Workspace Model

### 4.1 Workspace State

```python
# platform/workspace.py

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Workspace:
    """Complete workspace state for a DX tool session."""
    root: Path
    apps: list[AppInfo] = field(default_factory=list)
    config: dict = field(default_factory=dict)
    tool_config: dict = field(default_factory=dict)

    @classmethod
    def from_root(cls, root: Path | None = None,
                  tool_name: str | None = None) -> "Workspace":
        """Discover workspace from a project root.

        1. Resolve root (get_project_root or cwd-based)
        2. Discover apps (apps/*/main.ail)
        3. Load ail.toml if present
        4. Extract tool-specific config if tool_name provided
        """
```

### 4.2 Usage Pattern

```python
# In any tool's __main__.py:
from platform.workspace import Workspace

def main() -> int:
    workspace = Workspace.from_root(tool_name="ail_benchmark")
    # workspace.root, workspace.apps, workspace.config
```

Replaces the pattern where each tool independently discovers root, apps, and config.

### 4.3 LSP Integration

The LSP's `LspServer` gets an optional workspace reference:

```python
# compiler/lsp/server.py — modified
from platform.workspace import Workspace

class LspServer:
    def __init__(self, workspace: Workspace | None = None):
        self.documents: dict[str, Document] = {}
        self.workspace = workspace  # Optional workspace context
```

When a workspace is available, the LSP uses it for:
- Cross-file reference resolution (future)
- Workspace symbol search
- `ail.toml`-based project configuration

---

## 5. Manifest Handling

### 5.1 Canonical Manifest Parser

Extracted and generalized from `tools/ail_package_manager/manifest.py`:

```python
# platform/manifest.py

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectManifest:
    name: str
    version: str
    description: str = ""
    authors: list[str] = field(default_factory=list)
    license: str = ""
    entry: str = "main.ail"
    language_version: str = ""
    dependencies: dict[str, str] = field(default_factory=dict)
    tools: dict[str, dict] = field(default_factory=dict)

def find_manifest(start_dir: Path | None = None) -> Path | None:
    """Walk up from start_dir (or cwd) looking for ail.toml."""
    ...

def parse_manifest(path: Path) -> ProjectManifest:
    """Parse and validate an ail.toml file."""
    ...

def write_manifest(manifest: ProjectManifest, path: Path) -> None:
    """Write a ProjectManifest to ail.toml."""
    ...
```

### 5.2 Tool Configuration from Manifest

```python
def get_tool_config(manifest: ProjectManifest,
                    tool_name: str) -> dict:
    """Extract tool-specific configuration from [tools.<tool_name>].

    Example ail.toml:
        [tools.ail_benchmark]
        suites = ["quick", "canonical"]
        repeat = 5
    """
```

### 5.3 Package Manager Uses Canonical Source

The package manager's `manifest.py` becomes a thin wrapper:

```python
# tools/ail_package_manager/manifest.py
# After migration:
from platform.manifest import (
    ProjectManifest, find_manifest, parse_manifest, write_manifest
)

# Package-manager-specific validation on top:
def validate_package_name(name: str) -> bool:
    """Package manager extends with kebab-case check."""
    ...
```

---

## 6. Report Schema

### 6.1 Standard Schema

```python
# platform/report_schema.py

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReportMetadata:
    tool: str
    version: str
    timestamp: str = ""  # Auto-filled on creation

    def __post_init__(self):
        if not self.timestamp:
            from datetime import datetime, timezone
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ReportSummary:
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0


@dataclass
class Report:
    metadata: ReportMetadata
    summary: ReportSummary
    payload: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        ...

    def to_markdown(self) -> str:
        """Generate standard Markdown report from metadata + summary."""
        ...
```

### 6.2 Standard Exit Codes

```python
# platform/report_schema.py

class ExitCode:
    SUCCESS = 0        # All operations completed without issues
    FAILURE = 1        # Items failed but tool completed
    REGRESSION = 2     # Performance regression (benchmark runner only)
    INTERNAL_ERROR = 3 # Tool cannot function (bad args, I/O error, no apps)
```

All tools migrate to `ExitCode.SUCCESS` etc. instead of hardcoded integers.

### 6.3 Writer Helpers

```python
def write_report(report: Report, output_dir: Path,
                 formats: set[str] = {"json", "markdown"}) -> dict[str, Path]:
    """Write report in specified formats.

    Returns: {"json": Path, "markdown": Path}
    Only includes formats that were requested.
    """
    ...
```

---

## 7. Diagnostics Model

### 7.1 Unified Diagnostic

```python
# platform/diagnostics.py

from dataclasses import dataclass
from enum import IntEnum


class Severity(IntEnum):
    ERROR = 1
    WARNING = 2
    INFO = 3
    HINT = 4

# Aligned with LSP DiagnosticSeverity:
# 1 = Error, 2 = Warning, 3 = Information, 4 = Hint


@dataclass
class DiagnosticPosition:
    line: int      # 0-based
    column: int    # 0-based


@dataclass
class DiagnosticRange:
    start: DiagnosticPosition
    end: DiagnosticPosition


@dataclass
class Diagnostic:
    range: DiagnosticRange
    severity: Severity
    message: str
    source: str = "ailang"
    code: str = ""
```

### 7.2 Compiler → Platform Conversion

```python
def from_compiler_diagnostic(
    compiler_diag: "compiler.diagnostics.Diagnostic"
) -> Diagnostic:
    """Convert compiler diagnostic to platform diagnostic.

    Maps:
        Severity.ERROR → Severity.ERROR (1)
        Severity.WARNING → Severity.WARNING (2)
        Severity.NOTE → Severity.INFO (3)
    Converts 1-based line/column to 0-based.
    """
    ...
```

### 7.3 LSP → Platform Conversion

```python
def to_lsp_diagnostic(diag: Diagnostic) -> dict:
    """Convert platform diagnostic to LSP JSON-RPC diagnostic dict.

    Used by compiler/lsp/features/diagnostics.py.
    """
    ...
```

---

## 8. Symbol Services

### 8.1 Symbol Index

```python
# platform/symbol_index.py

from dataclasses import dataclass, field
from enum import Enum, auto


class SymbolKind(Enum):
    FUNCTION = auto()
    VARIABLE = auto()
    PARAMETER = auto()
    MODULE = auto()


@dataclass
class Symbol:
    name: str
    kind: SymbolKind
    file_path: str
    line: int       # 0-based
    column: int     # 0-based


@dataclass
class SymbolIndex:
    """Cross-file symbol index for workspace-level queries."""
    symbols: dict[str, list[Symbol]] = field(default_factory=dict)

    def add_symbol(self, symbol: Symbol) -> None:
        ...

    def find(self, name: str) -> list[Symbol]:
        """Find all symbols with given name across files."""
        ...

    def find_in_file(self, name: str, file_path: str) -> list[Symbol]:
        """Find symbols with given name in a specific file."""
        ...
```

### 8.2 AST Walk Utilities

Consolidates utilities duplicated across LSP features (definition.py, hover.py, references.py, rename.py, signature_help.py):

```python
def walk_ast(node: ASTNode, callback: Callable[[ASTNode], None]) -> None:
    """Walk AST depth-first, calling callback at each node."""

def find_node_at_offset(node: ASTNode, offset: int) -> ASTNode | None:
    """Find the deepest AST node at a given character offset."""

def position_to_offset(text: str, line: int, column: int) -> int:
    """Convert 0-based line/column to character offset."""

def offset_to_position(text: str, offset: int) -> tuple[int, int]:
    """Convert character offset to 0-based (line, column)."""
```

### 8.3 LSP Feature Module Simplification

Before migration, 5 LSP feature modules define `_walk_ast()`, `_find_node_at_offset()`, and `_position_to_offset()` locally. After migration, they import from `ail_platform.symbol_index`.

---

## 9. Event Model

### 9.1 Lightweight Event Bus

```python
# platform/events.py

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class Event:
    type: str
    data: dict = field(default_factory=dict)


EventHandler = Callable[[Event], None]


class EventBus:
    """Simple publish-subscribe event bus.

    Enables loose coupling between tools without direct imports.
    """

    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def on(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to an event type."""
        self._handlers[event_type].append(handler)

    def emit(self, event: Event) -> None:
        """Emit an event, calling all registered handlers."""
        for handler in self._handlers[event.type]:
            handler(event)
```

### 9.2 Defined Events

| Event Type | Payload | Emitter | Consumers |
|------------|---------|---------|-----------|
| `workspace.loaded` | `{"root": "..."}` | Workspace loader | All tools |
| `project.analyzed` | `{"app_count": N}` | Static analyzer | Benchmark runner, test generator |
| `benchmark.completed` | `{"app": "...", "passed": bool}` | Benchmark runner | Repository doctor |
| `tests.generated` | `{"app": "...", "count": N}` | Test generator | Repository doctor |
| `diagnostics.updated` | `{"uri": "...", "count": N}` | LSP | IDE integration |

### 9.3 Usage Pattern

```python
# In any tool's main():
from platform.events import EventBus, Event

bus = EventBus()
bus.on("workspace.loaded", lambda e: print(f"Loaded {e.data['root']}"))
bus.emit(Event("workspace.loaded", {"root": str(root)}))
```

---

## 10. Extension Points

### 10.1 Platform Plugin System (Future)

The platform exposes these hooks for tool-specific customization:

```python
# platform/workspace.py — extension via subclassing
class CustomWorkspace(Workspace):
    def discover_apps(self) -> list[AppInfo]:
        # Override app discovery for custom layouts
        ...

# platform/report_schema.py — extension via Report subclass
class CustomReport(Report):
    def to_markdown(self) -> str:
        # Custom report template
        ...
```

### 10.2 Tool Registration

```python
# platform/registry.py (Future — post v0.4.x)
@dataclass
class ToolRegistration:
    name: str
    version: str
    description: str
    entry_point: str  # e.g., "tools.ail_benchmark.__main__:main"

_registry: dict[str, ToolRegistration] = {}

def register_tool(tool: ToolRegistration) -> None:
    """Register a tool with the platform."""
    _registry[tool.name] = tool
```

Not implemented in v0.4.x — reserved for future when tool discovery becomes dynamic.

### 10.3 Configuration-Driven Behavior

Tools declare their configuration schema in `ail.toml`:

```toml
[tools.ail_benchmark]
suites = ["quick", "canonical"]
repeat = 5
timeout = 120
memory = true
```

The platform loads this config and makes it available via `Workspace.tool_config`. Tools do not need to re-parse `ail.toml`.

---

## 11. Migration Strategy

### 11.1 Principles

| Principle | Rule |
|-----------|------|
| **Incremental** | One tool at a time, one module at a time. No big-bang rewrites. |
| **Backward compatible** | Existing function signatures preserved. Deprecation warnings instead of removal. |
| **Same behavior** | After migration, tool output is byte-identical to pre-migration output. |
| **Tests pass** | Every migration PR must pass all existing tests for the affected tool. |
| **Platform before migration** | `ail_platform/` must exist with working modules before any tool migration begins. |

### 11.2 Phase 1: Platform Creation

| Step | Action | Files |
|:----:|--------|-------|
| 1 | Create `ail_platform/` package | `ail_platform/__init__.py` |
| 2 | Implement `project.py` | `get_project_root()`, `discover_apps()`, `ensure_output_dir()`, `read_file_safe()` |
| 3 | Implement `manifest.py` | `ProjectManifest`, `find_manifest()`, `parse_manifest()`, `write_manifest()` |
| 4 | Implement `report_schema.py` | `Report`, `ReportMetadata`, `ReportSummary`, `ExitCode`, `write_report()` |
| 5 | Implement `diagnostics.py` | `Diagnostic`, `Severity`, `from_compiler_diagnostic()`, `to_lsp_diagnostic()` |
| 6 | Implement `symbol_index.py` | `SymbolIndex`, `Symbol`, `walk_ast()`, `find_node_at_offset()` |
| 7 | Implement `workspace.py` | `Workspace`, `from_root()` |
| 8 | Implement `configuration.py` | `get_tool_config()` |
| 9 | Implement `events.py` | `EventBus`, `Event` |

### 11.3 Phase 2: Package Manager Migration (Priority 1)

| Step | Action | Impact |
|:----:|--------|--------|
| 1 | Replace `get_project_root()` with `ail_platform.project.get_project_root()` | Single import change |
| 2 | Replace manifest module → import from `ail_platform.manifest` | Keep `validate_package_name()` as thin wrapper |
| 3 | Replace exit codes → `ExitCode.SUCCESS`, etc. | Constants change, values stay same |
| 4 | Update tests | Ensure byte-identical output |

### 11.4 Phase 3: Language Server Migration (Priority 2)

| Step | Action | Impact |
|:----:|--------|--------|
| 1 | Replace AST walk utilities → import from `ail_platform.symbol_index` | Remove 5 copies across feature modules |
| 2 | Replace diagnostics conversion → `from_compiler_diagnostic()` / `to_lsp_diagnostic()` | Single shared converter |
| 3 | Integrate `Workspace` (optional) | Non-breaking; workspace becomes available for future cross-file features |
| 4 | Update tests | Ensure functionality unchanged |

### 11.5 Phase 4: Remaining Tools (Priority 3–7)

Migration order:

| Priority | Tool | Key Changes |
|:--------:|------|-------------|
| 3 | Static Analyzer | `get_project_root()`, exit codes, report writing |
| 4 | Test Generator | Already uses `tools.common` heavily; migrate to platform, update `report_schema.py` usage |
| 5 | Benchmark Runner | `get_project_root()` (2 copies), CLI args, report writing, exit codes |
| 6 | Repository Doctor | `get_project_root()`, `read_file_safe()`, report writing |
| 7 | Context Generator | `get_project_root()`, `read_file_safe()`, report writing |

### 11.6 Migration Pattern for Each Tool

Each tool follows this checklist:

```markdown
## Tool Migration: <name>
- [ ] Replace `get_project_root()` → `from platform.project import get_project_root`
- [ ] Replace `read_file_safe()` → `from platform.project import read_file_safe`
- [ ] Replace CLI parser → use `tools.common.cli` (or extend it)
- [ ] Replace exit codes → `from platform.report_schema import ExitCode`
- [ ] Replace report writing → `from platform.report_schema import Report, write_report`
- [ ] Replace diagnostics → `from platform.diagnostics import from_compiler_diagnostic`
- [ ] Remove tool-local copies of extracted functions
- [ ] Run all existing tests → byte-identical output
- [ ] Update tool version (minor bump)
```

---

## 12. Testing Strategy

### 12.1 Platform Tests

| Test File | Scope | Pattern |
|-----------|-------|---------|
| `tests/platform_test.py` | Unit tests for all platform modules | In-process, no subprocess |
| `tests/platform_integration_test.py` | Cross-module integration (workspace + manifest + project) | Uses real ail.toml fixtures |

### 12.2 Test Matrix

| Module | Tests Required | Key Cases |
|--------|---------------|-----------|
| `project.py` | 6 | Root resolution, app discovery (empty, single, multi), `read_file_safe()` (missing, binary, encoding error), `ensure_output_dir()` |
| `manifest.py` | 8 | Parse valid/invalid ail.toml, find manifest (cwd, parent, not found), write manifest, tool config extraction |
| `report_schema.py` | 6 | JSON output, Markdown output, metadata auto-timestamp, exit code constants, missing fields |
| `diagnostics.py` | 5 | Compiler → platform conversion, LSP conversion, severity mapping, position conversion |
| `symbol_index.py` | 5 | Add/find symbols, cross-file lookup, AST walk utilities |
| `workspace.py` | 4 | `from_root()` with/without ail.toml, with/without apps, LSP integration |
| `configuration.py` | 3 | Tool config extraction from manifest, missing section, empty section |
| `events.py` | 4 | Subscribe/emit, multiple handlers, no handlers, event data |

### 12.3 Testing Tool Migrations

Each tool migration is verified by:

```python
def test_tool_output_unchanged_after_migration():
    """Tool produces byte-identical output after platform migration."""
    result_before = run_tool_pre_migration(args)
    result_after = run_tool_post_migration(args)
    assert result_before == result_after
    assert result_before.exit_code == result_after.exit_code
```

### 12.4 Continuous Integration

- Platform tests run on every PR that touches `ail_platform/`
- Full acceptance test suite runs on every PR that migrates a tool
- Performance benchmarks track platform module overhead (<1ms per call target)

---

## 13. Backward Compatibility Guarantees

### 13.1 Deprecation Policy

| Change Type | Deprecation Period | Mechanism |
|-------------|:------------------:|-----------|
| Function relocation | 1 minor version | Old location imports + re-exports from new location with `warnings.warn` |
| Function removal | 2 minor versions | Warning in first minor, removal in second |
| Signature change | 1 minor version | Deprecated signature accepted with warning |
| Exit code change | None (if values change) | Major version bump required |

### 13.2 What Stays the Same

- Tool CLI arguments and behavior (no user-facing changes)
- Report file names and JSON schemas
- Exit code values (integers — only the constant names change)
- `python -m tools.ail_<name>` invocation
- All existing test suites pass without modification

### 13.3 What Changes

- Internal imports (tools import from `ail_platform.` instead of local copies)
- Code organization (duplicated functions removed from tool directories)
- Version numbers (tool minor versions bumped on migration)

---

## Appendix A: File Map After Integration

```
platform/
├── __init__.py              — Version, exports
├── project.py               — get_project_root, discover_apps, ensure_output_dir
│                               read_file_safe, AppInfo
├── workspace.py             — Workspace dataclass, from_root()
├── manifest.py              — ProjectManifest, find_manifest, parse_manifest
│                               write_manifest, get_tool_config
├── diagnostics.py           — Diagnostic, Severity, DiagnosticPosition,
│                               DiagnosticRange, from_compiler_diagnostic,
│                               to_lsp_diagnostic
├── symbol_index.py          — SymbolIndex, Symbol, SymbolKind,
│                               walk_ast, find_node_at_offset,
│                               position_to_offset, offset_to_position
├── report_schema.py         — Report, ReportMetadata, ReportSummary,
│                               ExitCode, write_report
├── configuration.py         — ToolConfig, load_tool_config
└── events.py                — EventBus, Event, EventHandler
```

## Appendix B: Migration Timeline

| Phase | Scope | Estimated Effort | Dependencies |
|:-----:|-------|:----------------:|:------------:|
| 1 | Platform package creation | 2-3 days | None |
| 2 | Package Manager migration | 0.5 day | Phase 1 |
| 3 | Language Server migration | 1 day | Phase 1 |
| 4 | Static Analyzer migration | 0.5 day | Phase 1 |
| 5 | Test Generator migration | 0.5 day | Phase 1 |
| 6 | Benchmark Runner migration | 1 day | Phase 1 |
| 7 | Repository Doctor migration | 0.5 day | Phase 1 |
| 8 | Context Generator migration | 0.5 day | Phase 1 |

Total: ~7-8 days for all phases.

---

*This document is the architecture contract for platform integration. All migrations must follow this document before code changes begin.*

*Last updated: 2026-07-07*
