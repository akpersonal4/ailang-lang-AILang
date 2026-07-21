# M83A — VS Code Extension Architecture

**Status:** Implementation Complete (M83A–M83C)
**Version:** 1.1.1
**Date:** 2026-07-20
**Depends On:** M81 (formatting baseline), M82 (onboarding documentation)

---

## 1. Goals

### Target Users

| User | Primary Need | Frequency |
|------|-------------|-----------|
| AILang developers (human) | Write, navigate, format, debug AILang code | Daily |
| AI coding assistants | Language context, diagnostics, examples | Per session |
| New learners | Syntax highlighting, hover docs, error explanations | First week |

### Supported Workflows

1. **Write** — Author AILang files with syntax highlighting, auto-completion, and snippets
2. **Navigate** — Go to definition, find references, browse document symbols
3. **Format** — Automatic or manual code formatting with the canonical formatter
4. **Diagnose** — Real-time error highlighting with explanations and quick fixes
5. **Understand** — Hover over identifiers to see types, signatures, and documentation
6. **Manage** — Project discovery, dependency visualization, package management

### Non-Goals (for this architecture)

- TypeScript implementation details (out of scope — see Explicitly Out of Scope)
- Extension packaging and marketplace publishing (out of scope)
- UI assets, icons, theme support (out of scope)
- Debugger implementation (Phase 3, not MVP)
- Multi-language support (AILang only)

---

## 2. Extension Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          VS Code                                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Extension Host                         │   │
│  │                                                          │   │
│  │  ┌──────────────┐    ┌──────────────┐                   │   │
│  │  │  Extension    │    │  Extension   │                   │   │
│  │  │  (activation, │    │  Settings    │                   │   │
│  │  │   lifecycle)  │    │  (ailang.*)  │                   │   │
│  │  └──────┬───────┘    └──────────────┘                   │   │
│  │         │                                                │   │
│  │         ├──────────────────────────────────┐             │   │
│  │         │                                  │             │   │
│  │  ┌──────▼───────┐                  ┌───────▼──────┐     │   │
│  │  │  Language     │                  │  MCP Client  │     │   │
│  │  │  Client       │                  │  (JSON-RPC)  │     │   │
│  │  │  (LSP 3.17)  │                  │              │     │   │
│  │  └──────┬───────┘                  └───────┬──────┘     │   │
│  │         │                                  │             │   │
│  └─────────┼──────────────────────────────────┼─────────────┘   │
│            │ stdin/stdout                     │ stdin/stdout     │
│            │ Content-Length JSON-RPC          │ NDJSON           │
│            │                                  │                  │
│  ┌─────────▼─────────┐              ┌─────────▼────────┐       │
│  │  `ail lsp`         │              │  `ail mcp`        │       │
│  │  (Python process)  │              │  (Python process) │       │
│  │                    │              │                   │       │
│  │  ┌──────────────┐ │              │  ┌─────────────┐ │       │
│  │  │ LSP Server    │ │              │  │ MCP Server   │ │       │
│  │  │ (16 methods)  │ │              │  │ (6 tools)    │ │       │
│  │  └──────┬───────┘ │              │  └─────────────┘ │       │
│  │         │          │              │                   │       │
│  │  ┌──────▼───────┐ │              └───────────────────┘       │
│  │  │  Compiler     │ │                                         │
│  │  │  Pipeline     │ │                                         │
│  │  │  (Lexer →     │ │                                         │
│  │  │   Parser →    │ │                                         │
│  │  │   AST →       │ │                                         │
│  │  │   Semantic →  │ │                                         │
│  │  │   TypeCheck)  │ │                                         │
│  │  └──────────────┘ │                                         │
│  └────────────────────┘                                         │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow: User Types Code

```
User types in editor
    │
    ▼
VS Code sends textDocument/didChange (Content-Length JSON-RPC)
    │
    ▼
`ail lsp` receives change, updates Document state
    │
    ▼
Document.compile() runs full pipeline (Lexer → Parser → AST → Semantic → TypeCheck)
    │
    ▼
LSP server publishes textDocument/publishDiagnostics
    │
    ▼
VS Code displays red/yellow squiggles in editor
```

### Data Flow: User Hovers Over Identifier

```
User hovers over identifier
    │
    ▼
VS Code sends textDocument/hover (Content-Length JSON-RPC)
    │
    ▼
`ail lsp` finds AST node at cursor position
    │
    ▼
LSP server returns Hover with markdown content + range
    │
    ▼
VS Code shows hover popup with formatted documentation
```

### Two-Server Design

The extension spawns two independent server processes:

| Server | Transport | Purpose | Lifecycle |
|--------|-----------|---------|-----------|
| `ail lsp` | Content-Length JSON-RPC | IDE intelligence (diagnostics, hover, completion, navigation) | Long-lived, one per workspace |
| `ail mcp` | NDJSON JSON-RPC | AI-assisted tools (compile, explain, examples) | On-demand, started by user command |

**Rationale:** Separation of concerns. LSP provides deterministic, fast IDE features. MCP provides AI-assisted features that may be slower or require external dependencies. The LSP server must start in <10ms; the MCP server can take longer.

---

## 3. Feature Roadmap

### MVP (Phase 1) — Must Have for v1.0

| Feature | LSP Method | Priority | Existing? |
|---------|-----------|:--------:|:---------:|
| Syntax highlighting | TextMate grammar | P0 | ✅ Yes |
| Diagnostics (errors/warnings) | `textDocument/publishDiagnostics` | P0 | ✅ Yes |
| Hover documentation | `textDocument/hover` | P0 | ✅ Yes |
| Go to Definition | `textDocument/definition` | P0 | ✅ Yes |
| Document Symbols | `textDocument/documentSymbol` | P1 | ✅ Yes |
| Code Formatting | `textDocument/formatting` | P1 | ❌ No — needs implementation |
| Format on Save | VS Code setting | P1 | ❌ No — needs wiring |
| Workspace Symbols | `workspace/symbol` | P1 | ✅ Yes |
| Version Display | Status bar item | P2 | ❌ No — needs wiring |
| File Icons | Language icon | P2 | ❌ No — needs assets |

**MVP scope:** All P0 features exist. P1 features need formatter integration and wiring. P2 features need UI work.

### Phase 2 — Post-MVP

| Feature | LSP Method | Priority | Existing? |
|---------|-----------|:--------:|:---------:|
| Completion (context-sensitive) | `textDocument/completion` | P0 | ⚠️ Static list only |
| Rename Symbol | `textDocument/rename` | P0 | ⚠️ Single-file only |
| Find References | `textDocument/references` | P0 | ⚠️ Single-file only |
| Signature Help | `textDocument/signatureHelp` | P1 | ✅ Yes |
| Semantic Highlighting | `textDocument/semanticTokens` | P1 | ❌ No |
| Code Actions (quick fixes) | `textDocument/codeAction` | P1 | ✅ 3 patterns |
| Prepare Rename | `textDocument/prepareRename` | P2 | ❌ No |

### Phase 3 — Future

| Feature | LSP Method | Priority | Existing? |
|---------|-----------|:--------:|:---------:|
| Debugger (DAP) | Debug Adapter Protocol | P0 | ❌ No |
| Refactoring | `textDocument/codeAction` | P1 | ❌ No |
| Test Explorer | Custom | P1 | ❌ No |
| Package Manager UI | Custom | P2 | ❌ No |
| Code Lens | `textDocument/codeLens` | P2 | ❌ No |
| Folding Ranges | `textDocument/foldingRange` | P2 | ❌ No |

---

## 4. LSP Integration

### Existing Capabilities (v1.1.0)

The LSP server (`compiler/lsp/server.py`) handles 16 JSON-RPC methods:

| Method | Feature | Status | Limitation |
|--------|---------|--------|------------|
| `initialize` | Server capabilities | ✅ Complete | — |
| `shutdown` / `exit` | Lifecycle | ✅ Complete | — |
| `textDocument/didOpen` | Document sync | ✅ Complete | — |
| `textDocument/didChange` | Document sync | ⚠️ Partial | Declares incremental (change=2) but treats each change as full text |
| `textDocument/didSave` | Document sync | ✅ Complete | — |
| `textDocument/didClose` | Document sync | ✅ Complete | — |
| `textDocument/completion` | Auto-complete | ⚠️ Partial | Static list, not context-sensitive |
| `completionItem/resolve` | Completion detail | ❌ No-op | Returns params unchanged |
| `textDocument/hover` | Hover docs | ✅ Complete | Single-file only |
| `textDocument/definition` | Go to def | ✅ Complete | Single-file only |
| `textDocument/references` | Find refs | ✅ Complete | Single-file only |
| `textDocument/rename` | Rename symbol | ✅ Complete | Single-file only |
| `textDocument/signatureHelp` | Signature help | ✅ Complete | — |
| `textDocument/documentSymbol` | Doc symbols | ✅ Complete | Top-level only |
| `workspace/symbol` | Workspace symbols | ✅ Complete | Open documents only |
| `textDocument/codeAction` | Quick fixes | ✅ Complete | 3 patterns |

### Missing Capabilities (Required for MVP)

| Method | Feature | Effort | Notes |
|--------|---------|--------|-------|
| `textDocument/formatting` | Code formatting | **Low** | `format_source(str)` is ready; wire to LSP |
| `textDocument/rangeFormatting` | Range formatting | **Medium** | Needs formatter to accept range parameter |

### Missing Capabilities (Required for Phase 2)

| Method | Feature | Effort | Notes |
|--------|---------|--------|-------|
| `textDocument/prepareRename` | Validate rename | **Low** | Check if symbol is renameable before executing |
| `textDocument/semanticTokens/full` | Semantic highlighting | **High** | Needs token type classification from AST |
| `textDocument/completion` (context-sensitive) | Smart completion | **High** | Needs scope analysis, import awareness |
| `workspace/didChangeWorkspaceFolders` | Multi-root workspaces | **Medium** | Track folder additions/removals |

### Missing Capabilities (Required for Phase 3)

| Method | Feature | Effort | Notes |
|--------|---------|--------|-------|
| `textDocument/codeLens` | Code lens | **Medium** | Test counts, references |
| `textDocument/foldingRange` | Folding | **Low** | Function blocks, import groups |
| `textDocument/documentHighlight` | Symbol highlighting | **Medium** | Highlight all uses of symbol |
| Debug Adapter Protocol | Debugging | **Very High** | Breakpoints, stepping, variables |

### Performance Requirements

| Metric | Target | Current |
|--------|--------|---------|
| Server startup (`initialize`) | <10ms | ✅ <10ms |
| Diagnostics (per keystroke) | <100ms | ✅ <100ms |
| Hover response | <100ms | ✅ <100ms |
| Completion response | <100ms | ✅ <100ms |
| Go to Definition | <100ms | ✅ <100ms |
| Format (500 LOC) | <200ms | ✅ <200ms |
| Format (2000 LOC) | <500ms | ✅ <500ms |
| Memory (10 open files) | <50MB | ✅ ~10MB |
| Memory (100 open files) | <100MB | ⚠️ Unknown |

### Protocol Considerations

- **Incremental sync:** The server declares `change: 2` (incremental) but processes each change as full text. For MVP this is acceptable (files are small). For Phase 2, implement true incremental parsing to reduce latency on large files.
- **Cancellation:** The server does not handle `$/cancelRequest`. For MVP this is acceptable. For Phase 2, implement cancellation for long-running operations (format, workspace symbols).
- **Progress:** The server does not support `$/progress`. For MVP this is acceptable. For Phase 3, implement progress reporting for workspace-wide operations.

---

## 5. Formatter Integration

### Decision: Use Existing Formatter via LSP

**Choice:** Wire the existing `format_source(str) -> str` function into the LSP `textDocument/formatting` handler.

**Justification:**

1. **API readiness:** `format_source()` accepts a string and returns a string. No file I/O needed. This maps directly to the LSP formatting contract (receive document text, return TextEdits).

2. **Determinism:** The formatter is AST-driven and deterministic. Same input always produces same output. This is critical for format-on-save (no surprise changes).

3. **Performance:** The formatter runs the full parse + format pipeline. For files under 2000 LOC, this completes in <500ms. This is within LSP latency expectations.

4. **No new code needed:** The formatter already implements all formatting rules. The LSP handler is ~30 lines of code.

### Implementation Plan

```
textDocument/formatting request
    │
    ▼
LSP server receives request with document URI + options
    │
    ▼
Get Document.text (current editor content)
    │
    ▼
Call format_source(document.text)
    │
    ▼
If formatted == original: return [] (no edits)
    │
    ▼
Return [TextEdit(range=fullDocument, newText=formatted)]
```

### Format-on-Save Wiring

```json
// In package.json contributes.configuration:
"ailang.formatOnSave": {
    "type": "boolean",
    "default": true,
    "description": "Format AILang files on save"
}
```

The extension registers a `onWillSaveTextDocument` listener that calls `languageClient.sendRequest('textDocument/formatting', ...)` and applies the returned TextEdits.

### Future: Range Formatting

For Phase 2, add `format_range(source: str, start_line: int, end_line: int) -> str` to the formatter. This requires the formatter to accept line range parameters and only reformat the specified region.

---

## 6. Diagnostics

### Severity Mapping

| Compiler Severity | Platform Severity | LSP Severity | VS Code Display |
|-------------------|-------------------|--------------|-----------------|
| `Severity.ERROR` | `Severity.ERROR` | 1 (Error) | Red squiggle |
| `Severity.WARNING` | `Severity.WARNING` | 2 (Warning) | Yellow squiggle |
| `Severity.NOTE` | `Severity.INFO` | 3 (Information) | Blue squiggle |
| (none) | `Severity.HINT` | 4 (Hint) | Gray dim |

### Range Construction

Current behavior in `ail_platform/diagnostics.py`:

```python
# Compiler provides 1-based line/column
line = max(int(compiler_diag.line) - 1, 0)   # Convert to 0-based
column = max(int(compiler_diag.column) - 1, 0)

# Range end is approximated from message length
end_column = column + len(first_line_of_message)
range = DiagnosticRange(
    start=DiagnosticPosition(line, column),
    end=DiagnosticPosition(line, end_column)
)
```

**Limitation:** The range end extends over the message text length, not the actual source token. For example, if the error is "Undefined identifier: foo" at column 5, the range end is `5 + 25 = 30`, which may extend past the actual token.

**Improvement for Phase 2:** Use AST node spans (`start_span`/`end_span`) to compute precise ranges. The AST nodes already carry span information; the LSP server just needs to pass it through.

### Diagnostic Codes

All 31 error codes map directly to LSP diagnostic codes:

| Code | Category | VS Code Behavior |
|------|----------|-----------------|
| LEX001–LEX003 | Lexer errors | Red squiggle on offending character |
| PAR001–PAR003 | Parse errors | Red squiggle on expected token location |
| SEM001–SEM004 | Semantic errors | Red squiggle on identifier |
| TYP001–TYP013 | Type errors | Red squiggle on expression |
| MOD001–MOD005 | Module errors | Red squiggle on import statement |
| CMP001 | Internal error | Red squiggle on entire file |

### Quick Fixes (Code Actions)

Existing code actions in `compiler/lsp/features/code_actions.py`:

| Pattern | Trigger | Fix |
|---------|---------|-----|
| Missing stdlib import | Error message references stdlib module | Insert `import <module>;` at top |
| Unused variable | Warning about unused `let` | Delete the `let` line |
| Create missing module | "module not found" error | Placeholder (no actual file creation) |

**Phase 2 additions:**

| Pattern | Trigger | Fix |
|---------|---------|-----|
| Forward reference | SEM002 error | Suggest reorder (manual) |
| Type mismatch | TYP001 error | Suggest `convert.to_int()` wrapper |
| Missing return | TYP002 error | Suggest adding `return 0` |
| Duplicate declaration | SEM001 error | Suggest rename with suffix |

---

## 7. Workspace Model

### Project Discovery

AILang projects are identified by the presence of `ail.toml` in the workspace root.

```
workspace/
├── ail.toml          ← Project root marker
├── ail.lock          ← Dependency lock file
├── main.ail          ← Entry point
├── lib/              ← Local packages
│   └── my_package/
│       └── ...
└── data/
    └── sample.json
```

**Discovery algorithm:**

1. On activation, scan workspace root for `ail.toml`
2. If found: project mode (full LSP features, package resolution)
3. If not found: standalone mode (basic features, no package resolution)
4. Watch for `ail.toml` creation/deletion (workspace configuration changes)

### Module Resolution

The LSP server resolves modules in this order:

1. **Standard library** — `stdlib/<module>.ail` (bundled with `ailang-lang` package)
2. **Local packages** — `lib/<package>/` directory (project-local)
3. **Installed packages** — `site-packages/ailang_packages/` (pip-installed)

For completion and hover, the LSP server indexes all stdlib modules at startup (~50 functions across 16 modules).

### Multiple Folders

**MVP:** Single workspace folder only. The LSP server processes files from the root folder.

**Phase 2:** Multi-root workspace support. Each folder is an independent AILang project with its own `ail.toml`. The LSP server maintains separate compilation states per folder.

**Implementation:**

```
workspace/
├── folder1/
│   ├── ail.toml      ← Project 1
│   └── main.ail
└── folder2/
    ├── ail.toml      ← Project 2
    └── main.ail
```

The `workspace/didChangeWorkspaceFolders` notification tracks folder additions/removals. Each folder gets its own `Document` map and compilation state.

### Configuration

The extension reads configuration from VS Code settings:

```json
{
    "ailang.compilerPath": "ail",
    "ailang.formatOnSave": true,
    "ailang.enableDiagnostics": true,
    "ailang.maxProblems": 100,
    "ailang.trace.server": "off"
}
```

These are passed to the LSP server via `initializationOptions` during `initialize`.

---

## 8. Extension Settings

### Proposed Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ailang.compilerPath` | `string` | `"ail"` | Path to the `ail` CLI executable. Override if `ail` is not on PATH. |
| `ailang.formatOnSave` | `boolean` | `true` | Format AILang files when saving. |
| `ailang.enableDiagnostics` | `boolean` | `true` | Enable real-time error checking. Disable for performance on large files. |
| `ailang.maxProblems` | `number` | `100` | Maximum diagnostics to report per file. Prevents UI lag on files with many errors. |
| `ailang.trace.server` | `enum` | `"off"` | Log LSP communication. Values: `"off"`, `"messages"`, `"verbose"`. Useful for debugging. |
| `ailang.mcp.autoStart` | `boolean` | `true` | Auto-start MCP server on activation. |
| `ailang.mcp.command` | `string` | `"ail"` | MCP server command. |
| `ailang.mcp.args` | `array` | `["mcp"]` | MCP server arguments. |
| `ailang.mcp.timeout` | `number` | `30000` | MCP initialization timeout (ms). |
| `ailang.mcp.maxReconnectAttempts` | `number` | `3` | Max MCP reconnect attempts before giving up. |

### Settings Precedence

1. VS Code workspace settings (`.vscode/settings.json`) — highest
2. VS Code user settings (`settings.json`) — medium
3. Extension defaults — lowest

### Settings UI

All settings appear under the `AILang` section in VS Code Settings UI. The `trace.server` setting provides a dropdown with `"off"`, `"messages"`, `"verbose"` options.

---

## 9. Release Strategy

### Marketplace Publication

| Aspect | Decision |
|--------|----------|
| Publisher | `ailang` (organizational publisher) |
| Extension ID | `ailang.ailang-vscode` |
| Display Name | `AILang` |
| Categories | Programming Languages |
| Tags | `ailang`, `language`, `lsp`, `ai-first` |
| License | Apache-2.0 |
| Repository | `github.com/akpersonal4/ailang-lang-AILang/extensions/vscode-ailang` |

### Versioning

| Component | Versioning Strategy |
|-----------|-------------------|
| Extension | SemVer (major.minor.patch) |
| LSP Server | Matches compiler version (v1.x.y) |
| TextMate Grammar | Independent (x.y.z) |
| MCP Server | Independent (x.y.z) |

**Version alignment:** Extension major version tracks AILang major version. Extension v1.0.0 ships with AILang v1.x.y.

### Compatibility

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| VS Code | 1.84.0 | Latest stable |
| Python | 3.11+ | 3.12+ |
| `ail` CLI | v1.0.0 | v1.1.0+ |
| OS | Windows, macOS, Linux | Any |

### Testing Strategy

| Level | Tool | Scope |
|-------|------|-------|
| Unit tests | Jest / Mocha | Extension logic (settings, lifecycle) |
| LSP tests | Python unittest | Server-side features (108 existing tests) |
| Integration tests | VS Code Extension Test Host | End-to-end: open file → diagnostics → hover |
| Grammar tests | TextMate test suite | Syntax highlighting correctness |
| Manual tests | VS Code Insiders | Exploratory testing, UX validation |

**Existing LSP test coverage:** 108 automated tests covering all 16 methods, formatting, performance benchmarks, and robustness scenarios. These tests run without VS Code (pure Python) and validate the server-side intelligence.

### Release Process

1. Update `CHANGELOG.md` with new features and fixes
2. Bump version in `package.json`
3. Run `npm run package` to create `.vsix`
4. Run full test suite (`npm test` + `python -m pytest tests/test_lsp.py`)
5. Publish to VS Code Marketplace via `vsce publish`
6. Tag release in git (`v1.x.y`)

---

## 10. Risks

### Startup Performance

| Risk | Impact | Mitigation |
|------|--------|------------|
| LSP server startup >10ms | Users see "loading" indicator on every file open | Pre-warm: start server on first `.ail` file detection, not on VS Code startup |
| MCP server startup >5s | AI features unavailable for several seconds | Lazy start: only start when user invokes AI command |
| Large stdlib index | Slow initial compilation | Cache stdlib AST/symbol table between sessions |

### Large Workspace Scalability

| Risk | Impact | Mitigation |
|------|--------|------------|
| 100+ `.ail` files | LSP server memory grows linearly | LRU cache for compiled documents; evict idle files |
| 10,000+ LOC total | Diagnostics slow on every keystroke | Debounce: wait 300ms after last keystroke before recompiling |
| Deeply nested imports | Circular import detection slows | Cache import resolution; invalidate on file change |

### Cross-Platform Issues

| Risk | Impact | Mitigation |
|------|--------|------------|
| Path separators (`\` vs `/`) | File URIs break on Windows | Use `vscode.Uri.file()` consistently; never concatenate paths |
| Python not on PATH | `ail` command not found | `ailang.compilerPath` setting; `ail doctor` diagnostic |
| Line endings (CRLF vs LF) | Formatting produces inconsistent output | Normalize to `\n` internally; restore on write |
| Shell spawning on Windows | `child_process.spawn` behaves differently | Use `{ shell: true }` on win32 (already implemented) |

### LSP Synchronization

| Risk | Impact | Mitigation |
|------|--------|------------|
| Incremental sync declared but full text sent | Wasted bandwidth on large files | Acceptable for MVP; implement true incremental in Phase 2 |
| Rapid keystrokes overwhelm server | UI freezes, stale diagnostics | Debounce + cancellation support |
| File saved externally | Stale in-memory state | Watch file system; invalidate on external change |
| Multiple VS Code windows | Conflicting LSP servers | One server per workspace folder; isolate state |

### Dependency Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `vscode-languageclient` version mismatch | Runtime errors | Pin to `^9.0.0`; test with VS Code 1.84+ |
| Python version incompatibility | `ail lsp` fails to start | Require Python 3.11+; check in `ail doctor` |
| `ail` CLI not installed | Extension non-functional | Show clear error message; link to installation docs |

---

## Explicitly Out of Scope

| Item | Reason |
|------|--------|
| TypeScript implementation | Extension is plain JS; no build step needed |
| Extension packaging | Use `vsce` tool; not an architecture concern |
| Marketplace publishing | Organizational process, not technical |
| UI assets | Icons, themes, banners — design decisions |
| Theme support | Syntax highlighting via TextMate grammar; themes are separate |
| Multi-language support | AILang only |
| Debugger (DAP) | Phase 3; requires separate architecture |
| Refactoring engine | Phase 3; requires semantic analysis beyond current scope |

---

## Success Criteria

The architecture is complete when:

1. An independent developer can read this document and implement the VS Code extension without making additional architectural decisions
2. All MVP features have clear implementation paths with existing APIs
3. All risks have identified mitigations
4. The feature roadmap is prioritized and time-boxed
5. The LSP integration is fully specified (methods, capabilities, performance targets)
6. The formatter integration decision is justified and reversible
7. The diagnostics mapping is complete (all 31 error codes covered)
8. The workspace model handles single-folder, multi-folder, and standalone modes
9. The release strategy is actionable (versioning, testing, publishing)
10. The document follows AILang's specification-first philosophy

---

## Appendix A: Existing LSP Server Capabilities (v1.1.1)

```json
{
    "capabilities": {
        "textDocumentSync": {
            "openClose": true,
            "change": 2,
            "save": { "includeText": false }
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
        "documentSymbolProvider": true,
        "workspaceSymbolProvider": true,
        "codeActionProvider": true
    },
    "serverInfo": {
        "name": "ailang-lsp",
        "version": "1.1.1"
    }
}
```

## Appendix B: Error Code to LSP Diagnostic Mapping

| Error Code | Severity | LSP Range Source | Quick Fix Available |
|------------|----------|------------------|-------------------|
| LEX001 | Error | Character position | No |
| LEX002 | Error | String literal start | No |
| LEX003 | Error | Escape sequence | No |
| PAR001 | Error | Expected token position | No |
| PAR002 | Error | Import path | No |
| PAR003 | Error | Identifier position | No |
| SEM001 | Error | Duplicate identifier | Suggest rename |
| SEM002 | Error | Forward reference | Suggest reorder |
| SEM003 | Error | Function call | No |
| SEM004 | Error | Unknown stdlib | Add import |
| TYP001 | Error | Expression | `convert.to_int()` |
| TYP002 | Error | Return statement | Add return value |
| TYP003 | Error | Return expression | Fix type |
| TYP004 | Error | If condition | Fix condition type |
| TYP005 | Error | Arithmetic expression | Fix operand types |
| TYP006 | Error | Comparison | Fix operand types |
| TYP007 | Error | Logical operator | Fix operand types |
| TYP008 | Error | Assignment | Fix value type |
| TYP009 | Error | Unary minus | Fix operand type |
| TYP010 | Error | Logical not | Fix operand type |
| TYP011 | Error | Function call | Fix argument count |
| TYP012 | Error | Function call | Fix argument type |
| TYP013 | Error | Function call | Fix callee type |
| MOD001 | Error | Import statement | Remove circular import |
| MOD002 | Error | Import statement | Remove duplicate import |
| MOD003 | Error | Import statement | Fix module path |
| MOD004 | Error | Member access | Fix symbol name |
| MOD005 | Error | Import statement | Fix path |
| CMP001 | Error | Varies | Report bug |
| LSP000 | Error | Varies | Check logs |
