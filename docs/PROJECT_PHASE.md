# Project Phase — Platform & Developer Experience Engineering

**Active from:** v0.2.1 (July 2026)
**Current Version:** v0.3.0

## Phase Objective

Build the AI-native engineering ecosystem around the stable AILang core.
The language, compiler, runtime, and standard library are frozen — all new
development targets tooling, automation, and developer experience.

## Phase Scope

Developer experience tools (DX series):

| Tool | Status | Description |
|:----:|:------:|-------------|
| **DX-001** | ✅ Complete | `ail context` — AI onboarding context generator |
| **DX-002** | ✅ Complete | `ail doctor` — repository health checker |
| **DX-003** | ✅ Complete | `ail static_analyzer` — static code analysis |
 | **DX-004** | ✅ Complete | `ail benchmark` — automated benchmark suite execution and regression |
| **DX-005** | ✅ Complete | `ail testgen` — automatic AILang test case generation |
| **DX-006** | 📋 Next | Package Manager — `ail init`, `ail install` |
| **DX-007** | 📋 Recommended | Language Server Protocol — editor intelligence |
| **DX-008** | 📋 Recommended | `ail fmt` — formal formatter hardening |

## What is Frozen (not modified during this phase)

- Language syntax, grammar, and semantics
- Compiler pipeline (lexer, parser, AST, IR)
- Runtime interpreter and optimization cache
- Standard library API signatures
- Existing benchmark applications
- Existing test suite

## Why This Phase

AILang's differentiation comes from AI-friendly tooling, automation,
and developer experience — not from syntax changes. This phase invests
in the ecosystem that makes AILang productive for both human and AI developers.

## Previous Phases

| Phase | Focus | Completed |
|:------|:------|:---------:|
| 1–5B | Core compiler, stdlib, validation | ✅ |
| 6–7 | Documentation, developer ecosystem | ✅ |
| 8–10 | Validation, VS Code extension, formatter | ✅ |
| 11–12 | Dogfooding, governance, public release | ✅ |
| RTO-001 | Variable lookup cache optimization (v0.2.0) | ✅ |
| **Current** | **Platform & Developer Experience (v0.2.1+)** | **In progress** |
