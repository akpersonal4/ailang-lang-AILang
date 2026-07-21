# ADR-002: Module System Architecture

## Status
Accepted

## Context
Multi-file programs require module boundaries.

## Decision
File-based modules with path-derived names.

## Alternatives
- Package namespace system: rejected, too complex
- No modules: rejected, blocks real-world programs
- Dynamic imports: rejected, prevents static analysis

## Consequences
- Import syntax: import path symbol as alias
- Module resolution: filesystem-based
- No circular imports
- CompilationSession orchestrates multi-file compilation