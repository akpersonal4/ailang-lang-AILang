# DX_TOOL_001 Implementation Plan: ail context

## Tool Specification

- **Name:** `ail context`
- **Purpose:** Generate a single AI-friendly project context document
- **Output:** `generated/PROJECT_CONTEXT.md`
- **Location:** `tools/ail_context/` (standalone package)

## Design Requirements

1. **Standalone** — No changes to compiler/, runtime/, lexer/, parser/, or language spec
2. **Read-only** — Reads documentation, never modifies source files
3. **Modular** — Self-contained implementation
4. **LLM-optimized** — Concise, <8KB total, structured for context windows

## Implementation Steps

- [x] Create `tools/ail_context/` package structure
- [x] Implement `__main__.py` with context generation logic
- [x] Generate `generated/PROJECT_CONTEXT.md` with all required sections
- [x] Add unit tests in `tests/test_ail_context.py`
- [x] Create tool README.md

## Content Sections in PROJECT_CONTEXT.md

1. Project Overview — version, status, readiness
2. Project Philosophy — AI-first, deterministic, evidence-first
3. Compiler Architecture — pipeline stages
4. Runtime Architecture — interpreter, cache optimization
5. Language Constraints — hard rules and limitations
6. Active ADRs — key architectural decisions
7. Standard Library Summary — 16 modules, key functions
8. Runtime Optimization Summary — RTO-001
9. Benchmark Summary — 10 benchmarks, lessons
10. Testing Summary — 624 tests, quality gates
11. Do Not Change Rules — frozen components

## Validation Checklist

- [x] Compiler unchanged (no files modified in compiler/)
- [x] Runtime unchanged (no files modified in runtime/)
- [x] Parser unchanged (no files modified in parser/)
- [x] Existing tests pass
- [x] Existing benchmark applications unchanged
- [x] Existing language behavior unchanged

## Deliverables

- `tools/ail_context/__main__.py` — tool implementation
- `tools/ail_context/README.md` — tool documentation
- `tests/test_ail_context.py` — unit tests
- `generated/PROJECT_CONTEXT.md` — generated context document
- `IMPLEMENTATION_PLAN.md` — this file
- `DX_TOOL_001_REPORT.md` — completion report