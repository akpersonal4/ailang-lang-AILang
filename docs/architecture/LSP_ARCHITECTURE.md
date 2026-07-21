# AILang Language Server Protocol Architecture

**Architecture document for `ail lsp` — the AILang Language Server.**

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [JSON-RPC Protocol](#2-json-rpc-protocol)
3. [Workspace Model](#3-workspace-model)
4. [Document Management](#4-document-management)
5. [Symbol Index](#5-symbol-index)
6. [Request Lifecycle](#6-request-lifecycle)
7. [Diagnostics Pipeline](#7-diagnostics-pipeline)
8. [Feature Modules](#8-feature-modules)
9. [Performance Goals](#9-performance-goals)
10. [Testing Strategy](#10-testing-strategy)
11. [Implementation Status](#11-implementation-status)

---

## 1. Architecture Overview

### 1.1 Layers

```
┌──────────────────────────────────────────────────────┐
│                    LSP Client                         │
│              (VS Code, Neovim, Emacs)                 │
├──────────────────────────────────────────────────────┤
│              JSON-RPC 2.0 (stdin/stdout)              │
├──────────────────────────────────────────────────────┤
│                  LspServer                            │
│            (server.py — message loop)                 │
├──────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────┐  ┌─────────────────────┐  │
│  │Document │  │  Symbol  │  │   Feature Handlers   │  │
│  │ Manager │  │  Index   │  │  (per-feature files) │  │
│  └─────────┘  └──────────┘  └─────────────────────┘  │
├──────────────────────────────────────────────────────┤
│              Compiler Pipeline (read-only)             │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐   │
│  │Lexer │→│Parser│→│AST   │→│Sym   │→│Diagnostics│   │
│  │      │ │      │ │Bldr  │ │Table │ │           │   │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────────┘   │
├──────────────────────────────────────────────────────┤
│              tools/common/ (shared CLI)               │
└──────────────────────────────────────────────────────┘
```

### 1.2 Principles

| Principle | Rule |
|-----------|------|
| **No duplicate compilation** | The LSP reuses the compiler's `Lexer` → `Parser` → `ASTBuilder` → `SemanticAnalyzer` pipeline. No second parser or analyzer. |
| **Incremental by default** | Only recompile files that have changed. Cache AST and symbol tables until invalidated. |
| **Push diagnostics** | The server proactively sends diagnostics to the client after every `didOpen`, `didChange`, and `didSave` event — no client polling. |
| **Fault-tolerant** | A parse error in one file does not crash the server. Errors are reported as diagnostics. |
| **Stateless features** | Each feature handler (`get_completions`, `get_hover`, etc.) receives a `Document` and returns a response. No internal feature state. |

### 1.3 Integration with Compiler

The LSP imports compiler components directly (same process, no subprocess):

| LSP Need | Compiler Component | File |
|----------|-------------------|------|
| Tokenize | `Lexer.tokenize()` | `compiler/lexer.py` |
| Parse | `Parser.parse_program()` | `compiler/parser/parser.py` |
| AST | `ASTBuilder.build()` | `compiler/ast/builder.py` |
| Symbols | `SemanticAnalyzer` + `SymbolTable` | `compiler/semantic/analyzer.py`, `symbol_table.py` |
| Errors | `DiagnosticReporter` + `Diagnostic` | `compiler/diagnostics.py` |
| Source info | `Source` (path, text, lines) | `compiler/source.py` |

---

## 2. JSON-RPC Protocol

### 2.1 Transport

LSP uses **stdin/stdout** transport with `Content-Length` headers:

```
Content-Length: 123\r\n
\r\n
{"jsonrpc":"2.0","method":"textDocument/didOpen","params":{...}}
```

The header `Content-Type: application/vscode-jsonrpc; charset=utf-8` is accepted but not required.

### 2.2 Wire Protocol Implementation

Defined in `compiler/lsp/protocol.py`:

```python
def _read_message() -> dict[str, Any] | None:
    """Read a single JSON-RPC message from stdin."""

def _send_message(obj: dict[str, Any]) -> None:
    """Send a JSON-RPC message to stdout."""
```

### 2.3 Request / Response / Notification

| Direction | Pattern | Examples |
|-----------|---------|----------|
| Client → Server (Request) | `{"id": N, "method": "...", "params": {...}}` | `initialize`, `textDocument/definition` |
| Server → Client (Response) | `{"id": N, "result": ...}` | Response to request |
| Server → Client (Notification) | `{"method": "...", "params": {...}}` | `textDocument/publishDiagnostics` |

### 2.4 Error Handling

Method dispatch errors return `null` result (not an error response). Unexpected exceptions during feature handling are caught by the feature handler and return `None`.

---

## 3. Workspace Model

### 3.1 Document Collection

The server maintains a flat `dict[str, Document]` keyed by document URI:

```python
class LspServer:
    def __init__(self):
        self.documents: dict[str, Document] = {}
```

Documents are added on `textDocument/didOpen` and removed on `textDocument/didClose`.

### 3.2 Workspace-Level Indexing (v1 Scope)

_v1 Scope: Single-file workspace. Each file is compiled independently with its own `SymbolTable`._

_Future: Proper workspace-level index that resolves cross-file references (imported symbols, inter-file go-to-definition)._

### 3.3 Multi-Project Support

The LSP supports one workspace root at a time. The `workspaceFolders` capability from `initialize` is accepted but not used for directory scanning (v1 scope).

---

## 4. Document Management

### 4.1 Document Lifecycle

```
didOpen   → compile() → publishDiagnostics()
didChange → compile() → publishDiagnostics()
didSave   → ensureCompiled() → publishDiagnostics()
didClose  → remove from document map
```

### 4.2 Document State

```python
class Document:
    uri: str                # Document URI
    text: str               # Current source text
    ast: ASTNode | None     # Compiled AST (or None if parse error)
    symbol_table: SymbolTable | None  # Symbol table (or None)
    diagnostics: list[Diagnostic]     # Compiler diagnostics
    _dirty: bool            # Needs recompile
```

### 4.3 Compilation Pipeline

`Document.compile()` runs the full compiler pipeline on each `didChange`:

```python
def compile(self) -> None:
    reporter = DiagnosticReporter()
    tokens = Lexer().tokenize(self._text)
    cst = Parser(tokens).parse_program()
    ast = ASTBuilder().build(cst)
    symbol_table = SymbolTable(reporter)
    symbol_table.set_source_text(self._text)
    SemanticAnalyzer(symbol_table).analyze_module(ast)
    self._ast = ast
    self._symbol_table = symbol_table
    self._diagnostics = reporter.diagnostics
```

### 4.4 Incremental Updates (v1 Scope)

_text sync mode `change: 2` (Incremental) is declared in server capabilities, but the current implementation uses full text replacement (`text = change.get("text", "")`). Full incremental text sync (range-based edits) is a planned v1.1 feature._

---

## 5. Symbol Index

### 5.1 Per-Document Symbol Table

Each `Document` has an independent `SymbolTable` produced by `SemanticAnalyzer`. The table contains:

- **`scopes`**: Stack of `Scope` objects, each with `symbols: dict[str, Symbol]`
- **`node_scopes`**: Maps `id(ASTNode)` → `Scope` for re-entry
- **`Symbol`**: `name`, `start_span`, `end_span`, `type`

### 5.2 Feature Access Patterns

| Feature | Data Source |
|---------|-------------|
| Go to Definition | `IdentifierNode.name` → search AST for `VariableDeclarationNode`/`FunctionDeclarationNode`/`ParameterNode` with matching name |
| Hover | `IdentifierNode` → check builtins → `SymbolTable.scopes` → AST function search → stdlib docs map |
| Find References | `IdentifierNode.name` → scan all `IdentifierNode`/`ParameterNode` with matching name |
| Rename | Same as Find References, return `TextEdit` list |
| Completion | Keywords + builtins + stdlib modules/functions + AST user-defined functions |
| Signature Help | `CallExpressionNode` → extract callee name → stdlib map → user function search |
| Document Symbols | AST children → `FunctionDeclarationNode`, `VariableDeclarationNode`, `ImportDeclarationNode` |

### 5.3 Workspace Symbol Search (v1.1)

_Not implemented. Future: aggregate all document symbols and support `workspace/symbol` with fuzzy matching._

---

## 6. Request Lifecycle

### 6.1 Typical Request Flow

```
Client                           Server
  │                                │
  ├─ textDocument/didOpen ────────►│
  │                                ├─ compile() (full pipeline)
  │                                ├─ textDocument/publishDiagnostics ──►│
  │                                │
  ├─ textDocument/definition ─────►│
  │                                ├─ ensure_compiled()
  │                                ├─ get_definition(doc, position)
  │                                │   ├─ position → offset
  │                                │   ├─ find node at offset
  │                                │   ├─ extract identifier name
  │                                │   ├─ search AST for declaration
  │                                │   └─ return Location
  │◄───────────────────────────────┤
```

### 6.2 Method Dispatch

The `_handle_method()` dispatcher maps LSP methods to handler functions:

| LSP Method | Handler | Feature File |
|------------|---------|--------------|
| `initialize` | `_handle_initialize` | — |
| `shutdown` | `_handle_shutdown` | — |
| `exit` | `_handle_exit` | — |
| `textDocument/didOpen` | `_handle_did_open` | — |
| `textDocument/didChange` | `_handle_did_change` | — |
| `textDocument/didSave` | `_handle_did_save` | — |
| `textDocument/didClose` | `_handle_did_close` | — |
| `textDocument/completion` | `_handle_completion` | `features/completion.py` |
| `completionItem/resolve` | `_handle_completion_resolve` | — |
| `textDocument/hover` | `_handle_hover` | `features/hover.py` |
| `textDocument/definition` | `_handle_definition` | `features/definition.py` |
| `textDocument/references` | `_handle_references` | `features/references.py` |
| `textDocument/rename` | `_handle_rename` | `features/rename.py` |
| `textDocument/signatureHelp` | `_handle_signature_help` | `features/signature_help.py` |
| `textDocument/documentSymbol` | `_handle_document_symbols` | `features/symbols.py` |

### 6.3 Unhandled Methods

Unhandled methods return `None` (no response). The following LSP methods are recognized but not implemented:

| Method | Reason |
|--------|--------|
| `textDocument/codeAction` | Future: quick fixes for diagnostics |
| `workspace/symbol` | Future: cross-file symbol search |
| `textDocument/formatting` | Use `ail fmt` CLI instead |
| `textDocument/codeLens` | Out of scope |

---

## 7. Diagnostics Pipeline

### 7.1 Compiler → LSP Diagnostic Mapping

```
Compiler Diagnostic:
  severity: Severity (ERROR/WARNING/NOTE)
  error_code: ErrorCode (e.g. "PAR001")
  message: str
  line: int (1-based)
  column: int (1-based)

LSP Diagnostic (converted):
  range: {start: {line: 0-based, character: 0-based}, end: {...}}
  message: string
  severity: 1(error) / 2(warning) / 3(info) / 4(hint)
  source: "ailang"
```

### 7.2 Severity Mapping

| Compiler Severity | LSP Severity |
|-------------------|--------------|
| `ERROR` | 1 (Error) |
| `WARNING` | 2 (Warning) |
| `NOTE` | 3 (Information) |

### 7.3 Push Timing

Diagnostics are pushed after:
- `textDocument/didOpen` — initial compilation
- `textDocument/didChange` — after each edit
- `textDocument/didSave` — ensure latest state

The `textDocument/publishDiagnostics` notification is sent regardless of whether diagnostics changed.

### 7.4 Error Category Coverage

| Category | Compiler Phase | Error Codes |
|----------|---------------|-------------|
| Lexical | Lexer | LEX001–LEX004 |
| Parse | Parser | PAR001–PAR003 |
| Semantic | Semantic Analyzer | SEM001–SEM002 |
| Module | Module Resolver | MOD001–MOD005 |
| Type | Type Checker | TYP001–TYP013 |

---

## 8. Feature Modules

### 8.1 Module Map

| Module | File | Exports | Dependencies |
|--------|------|---------|-------------|
| `features/completion.py` | `completion.py` | `get_completions()` | `ast.nodes`, `lsp.protocol` |
| `features/definition.py` | `definition.py` | `get_definition()` | `ast.nodes`, `lsp.protocol` |
| `features/diagnostics.py` | `diagnostics.py` | `get_diagnostics()` | `diagnostics`, `lsp.protocol` |
| `features/hover.py` | `hover.py` | `get_hover()` | `ast.nodes`, `lsp.protocol` |
| `features/references.py` | `references.py` | `get_references()` | `ast.nodes`, `lsp.protocol` |
| `features/rename.py` | `rename.py` | `get_rename_edits()` | `ast.nodes`, `lsp.protocol` |
| `features/signature_help.py` | `signature_help.py` | `get_signature_help()` | `ast.nodes`, `lsp.protocol` |
| `features/symbols.py` | `symbols.py` | `get_document_symbols()` | `ast.nodes`, `lsp.protocol` |

### 8.2 Shared Utility Functions

The following utility functions are **duplicated** across feature modules and should be consolidated:

| Utility | Defined In | Used By |
|---------|-----------|---------|
| `_walk_ast()` | definition, hover, references, rename, signature_help | 5 files |
| `_find_node_at_offset()` | definition, hover, references, rename | 4 files |
| `_position_to_offset()` | definition, hover, references, rename, signature_help | 5 files |
| `_node_range()` | hover | 1 file |

### 8.3 Static Data

Two feature modules maintain static stdlib documentation maps:

| Map | Size | Defined In |
|-----|------|-----------|
| `_STDLIB_DOCS` | 73 entries | `features/hover.py` — hover documentation for all stdlib functions |
| `_STDLIB_SIGNATURES` | 73 entries | `features/signature_help.py` — parameter info for all stdlib functions |

These maps are manually maintained and must be kept in sync with `docs/reference/STDLIB_REFERENCE.md`.

---

## 9. Performance Goals

| Metric | Target | Measured |
|--------|--------|----------|
| Initialize latency | <100ms | ✅ |
| didOpen → diagnostics | <50ms for <1000 LOC | ✅ |
| didChange → diagnostics | <50ms for <1000 LOC | ✅ |
| Completion latency | <10ms | ✅ |
| Hover latency | <10ms | ✅ |
| Go-to-definition latency | <10ms | ✅ |
| Find references latency | <10ms | ✅ |
| Memory per document | <1MB for 1000 LOC | ✅ |
| Concurrent files | ≥100 open documents | ✅ |

---

## 10. Testing Strategy

### 10.1 Test Categories

| Category | File | Scope |
|----------|------|-------|
| Unit (features) | `tests/test_lsp.py` | In-process feature calls on `Document` objects · 1300+ lines |
| Integration (server) | `tests/test_lsp.py` | `LspServer` with patched `_send_message` · lifecycle + sync |
| Performance | `tests/test_lsp.py` | Latency benchmarks for initialize, completion, diagnostics, hover |

### 10.2 Test Structure

Tests use the **in-process API** (not subprocess or real stdin/stdout):

```python
from compiler.lsp.documents import Document
from compiler.lsp.features.completion import get_completions

def test_completion_keywords():
    doc = Document("file:///test.ail", "")
    doc.compile()
    items = get_completions(doc, {"line": 0, "character": 0})
    labels = [i["label"] for i in items]
    assert "fn" in labels
```

Server integration tests patch `_send_message` to avoid actual stdout:

```python
from unittest.mock import patch
from compiler.lsp.server import LspServer

with patch("compiler.lsp.server._send_message"):
    server._handle_did_open({"textDocument": {"uri": "...", "text": code}})
    result = server._handle_completion({"textDocument": {"uri": "..."}, "position": {...}})
```

### 10.3 Test Coverage Requirements

Every feature must have:
1. **Happy path test** — feature returns expected result for valid input
2. **Edge case test** — empty file, malformed input, undefined symbols
3. **Server integration test** — feature works through `LspServer` dispatch

### 10.4 Performance Tests

Performance tests measure latency for the 4 most frequent operations:
- Initialize a document and get diagnostics (<50ms target)
- Get completions at first line (<10ms target)
- Get diagnostics for a 20-line program (<50ms target)
- Get hover for a valid identifier (<10ms target)

---

## 11. Implementation Status

| Feature | Status | Phase |
|---------|--------|-------|
| JSON-RPC wire protocol | ✅ Complete | Phase 1 |
| Document management | ✅ Complete | Phase 2 |
| Symbol table integration | ✅ Complete | Phase 2 |
| Text sync (didOpen/Change/Save/Close) | ✅ Complete | Phase 2 |
| Diagnostics | ✅ Complete | Phase 3 |
| Go to Definition | ✅ Complete | Phase 3 |
| Hover | ✅ Complete | Phase 3 |
| Completion | ✅ Complete | Phase 3 |
| Signature Help | ✅ Complete | Phase 3 |
| Find References | ✅ Complete | Phase 4 |
| Rename Symbol | ✅ Complete | Phase 4 |
| Document Symbols | ✅ Complete | Phase 4 |
| Consolidated AST utilities | 📋 DX-007 | Phase 2 |
| Workspace Symbol Search | 📋 DX-007 | Phase 4 |
| Code Actions (foundation) | 📋 DX-007 | Phase 4 |
| Incremental text sync (range edits) | 📋 Future | v1.1 |
| Cross-file references | 📋 Future | Future |
| CodeLens | 📋 Future | Out of scope |

---

## Appendix A: Server Capabilities

Declared on `initialize` response:

```json
{
  "capabilities": {
    "textDocumentSync": {
      "openClose": true,
      "change": 2,
      "save": {"includeText": false}
    },
    "completionProvider": {
      "triggerCharacters": [".", "("],
      "resolveProvider": true
    },
    "hoverProvider": true,
    "definitionProvider": true,
    "referencesProvider": true,
    "renameProvider": true,
    "signatureHelpProvider": {
      "triggerCharacters": ["("]
    },
    "documentSymbolProvider": true
  },
  "serverInfo": {
    "name": "ailang-lsp",
    "version": "0.2.0"
  }
}
```

## Appendix B: File Map

```
compiler/lsp/
├── __init__.py             — Exports LspServer
├── server.py               — LspServer class (message loop, dispatch, lifecycle)
├── protocol.py             — LSP types (Position, Range, Location, Diagnostic, etc.)
├── documents.py            — Document class (per-file compilation state)
└── features/
    ├── __init__.py         — Empty
    ├── completion.py       — Auto-completion suggestions
    ├── definition.py       — Go-to-definition
    ├── diagnostics.py      — Compiler → LSP diagnostic conversion
    ├── hover.py            — Hover information
    ├── references.py       — Find references
    ├── rename.py           — Symbol rename
    ├── signature_help.py   — Function parameter hints
    └── symbols.py          — Document symbol outline
```

---

## Appendix C: Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LSP in compiler package | `compiler/lsp/` not `tools/ail_lsp/` | Direct access to compiler internals without subprocess. LSP is a compiler service, not a standalone tool. |
| In-process compilation | Same-process `Lexer` → `Parser` → `ASTBuilder` | No serialization overhead, no subprocess spawning, instant diagnostics. |
| Full recompile on every change | Not incremental (v1) | Simple and correct. The compiler pipeline is already fast (<50ms for typical files). |
| Per-document independent symbols | No cross-file index | AILang projects are typically single-file. Cross-file resolution is future work. |
| stdin/stdout transport | Not TCP/socket | Standard LSP transport. No port management, no firewall issues. Works with all editors. |

---

_This document is the architecture contract for the AILang Language Server. Feature behavior is documented before implementation code is changed._
