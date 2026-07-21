# v0.4.0 Release Validation — DX-007 AILang Language Server

## Feature Checklist

| Feature | Status | Verified |
|---------|:------:|:--------:|
| LSP Architecture Document | ✅ Complete | ✅ |
| JSON-RPC wire protocol (stdin/stdout) | ✅ Complete | ✅ |
| Document lifecycle (open/change/save/close) | ✅ Complete | ✅ |
| Diagnostics (lexical, parse, semantic, type, module) | ✅ Complete | ✅ |
| Go to Definition | ✅ Complete | ✅ |
| Hover Information | ✅ Complete | ✅ |
| Auto Completion | ✅ Complete | ✅ |
| Find References | ✅ Complete | ✅ |
| Rename Symbol | ✅ Complete | ✅ |
| Signature Help | ✅ Complete | ✅ |
| Document Symbols | ✅ Complete | ✅ |
| Workspace Symbol Search | ✅ Complete | ✅ |
| Code Actions (foundation) | ✅ Complete | ✅ |
| Shared AST utilities (no duplication) | ✅ Complete | ✅ |
| No duplicate compiler logic | ✅ Complete | ✅ |

## Acceptance Tests (103 tests)

| # | Test | Status |
|:-:|------|:------:|
| 1–8 | Lifecycle (initialize, shutdown, exit, dispatch) | ✅ Pass |
| 9–14 | Text sync (didOpen, didChange, didSave, didClose, multi-doc) | ✅ Pass |
| 15–26 | Diagnostics (valid, lexical, parse, semantic, type, import, duplicate, positions, severity, messages, compare) | ✅ Pass |
| 27–34 | Completion (keywords, builtins, stdlib modules/functions, user functions, ordering, kinds, empty file) | ✅ Pass |
| 35–42 | Hover (variable, builtin, stdlib, import, function def, parameter, outside, member access) | ✅ Pass |
| 43–48 | Definition (local var, function, user fn, undefined, non-identifier, valid range) | ✅ Pass |
| 49–53 | References (variable, function, no results, parameter, multiple) | ✅ Pass |
| 54–59 | Rename (variable, all refs, parameter, function, undefined, valid format) | ✅ Pass |
| 60–65 | Signature Help (user fn, print, stdlib, nested call, outside, empty) | ✅ Pass |
| 66–70 | Document Symbols (functions, imports, empty file, kinds, location uri) | ✅ Pass |
| 71–77 | Performance (initialize, compile large file, completion, diagnostics, hover, definition, large file diagnostics) | ✅ Pass |
| 78–86 | Robustness (empty, malformed, large file, rapid updates, repeated init/shutdown, concurrent, unicode, syntax errors, invalid method) | ✅ Pass |
| 87–89 | Message Dispatch (initialize request, notification, completion request) | ✅ Pass |
| 90–92 | Diagnostics Round-trip (didOpen, didChange, valid program) | ✅ Pass |
| 93–99 | Server Feature Dispatch (hover, completion, definition, references, rename, signature help, doc symbols) | ✅ Pass |
| 100–101 | Workspace Symbols (query match, empty query) | ✅ Pass |
| 102–103 | Code Actions (returns list, import error) | ✅ Pass |

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LSP location | `compiler/lsp/` (not `tools/`) | Direct access to compiler internals without subprocess |
| Compilation mode | In-process, full recompile on change | <50ms for typical files, no serialization overhead |
| Transport | stdin/stdout | Standard LSP transport, works with all editors |
| AST utilities | Centralized in `utils.py` | Eliminated 300+ lines of 5× duplicated code |

## Files Changed

| File | Change |
|------|--------|
| `docs/architecture/LSP_ARCHITECTURE.md` | NEW — Architecture document |
| `compiler/lsp/utils.py` | NEW — Shared AST utilities (walk_ast, find_node_at_offset, position_to_offset, find_references, etc.) |
| `compiler/lsp/features/workspace_symbols.py` | NEW — Workspace symbol search |
| `compiler/lsp/features/code_actions.py` | NEW — Code actions foundation |
| `compiler/lsp/server.py` | MODIFIED — Added workspace/symbol and textDocument/codeAction handlers, extended capabilities |
| `compiler/lsp/features/definition.py` | MODIFIED — Uses shared utils |
| `compiler/lsp/features/hover.py` | MODIFIED — Uses shared utils |
| `compiler/lsp/features/references.py` | MODIFIED — Uses shared utils |
| `compiler/lsp/features/rename.py` | MODIFIED — Uses shared utils |
| `compiler/lsp/features/signature_help.py` | MODIFIED — Uses shared utils |
| `tests/test_lsp.py` | MODIFIED — 4 new tests (workspace symbols, code actions) |
| `DEVELOPMENT_STATUS.md` | MODIFIED — DX-007 status, v0.4.0 milestone |
| `CHANGELOG.md` | MODIFIED — v0.4.0 entries |
