# ADR-001: Member Access Precedes Module System

## Status
Accepted

## Context
The Module System attempt correctly identified that the language needs qualified names for imports. Module import statements like `import foo from "bar.ail"` require resolving `bar.foo` at the call site. Without member access, the compiler cannot represent or resolve qualified names.

## Decision
Implement Member Access v1 before Module System. This provides:
- `a.b` syntax for qualified field access
- `a.b()` syntax for qualified method calls
- `a.b.c` syntax for chained member access

## Consequences
- AST: MemberAccessNode(receiver, member) with nested structure
- IR: MemberAccessIR(receiver, member) preserving member name as string
- Runtime: Member access on dict values returns key value
- Module imports can later reference STD functions like math.max, io.print