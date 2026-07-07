# ail context — Developer Experience Tool

> Standalone utility that generates a single AI-friendly project context document.

## Purpose

The `ail context` tool creates `generated/PROJECT_CONTEXT.md`, a concise summary of the AILang project optimized for LLM consumption. Any AI agent (ChatGPT, Claude, Gemini, Copilot, Cursor, Windsurf) can read this single file to understand the project before generating code.

## Usage

```bash
# Run from project root
python -m tools.ail_context

# Or with the CLI (after installation)
ail context
```

## Output

The tool generates `generated/PROJECT_CONTEXT.md` containing:

1. **Project Overview** — version, status, readiness score
2. **Project Philosophy** — AI-first, deterministic, evidence-first
3. **Compiler Architecture** — pipeline overview
4. **Runtime Architecture** — interpreter and optimizations
5. **Language Constraints** — hard rules and limitations
6. **Active ADRs** — key architectural decisions
7. **Standard Library Summary** — available modules
8. **Runtime Optimization Summary** — RTO-001 details
9. **Benchmark Summary** — 10 benchmarks, 6,610 LOC
10. **Testing Summary** — 624 tests, quality gates
11. **Do Not Change Rules** — frozen components

## Design

- **Standalone** — no modifications to compiler, runtime, or language
- **Read-only** — reads documentation but never modifies source files
- **Modular** — self-contained in `tools/ail_context/`
- **Configurable** — source documents list can be extended