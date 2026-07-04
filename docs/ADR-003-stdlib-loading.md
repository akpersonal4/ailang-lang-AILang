# ADR-003: Standard Library Loading Strategy

## Status
Accepted (Deferred Implementation)

## Context
AILang requires a Standard Library mechanism for common functions (math, strings, io, types).

## Decision
Standard Library shall be compiled together with the user program. IR caching may be introduced later as an implementation optimization. Runtime shall never compile source code.

## Rationale
- Maintains deterministic compilation (PROJECT_CONSTITUTION Rule 5)
- Preserves clean separation between compiler and runtime
- Stdlib source remains single source of truth
- AI-friendly: stdlib is readable and modifiable

## Consequences
Implementation deferred until CLI validation complete and syntax freeze achieved.