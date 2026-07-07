# Module System v1 — Complete Specification

## 1. Goals

- Enable multi-file AILang programs
- Provide namespace-like organization via module paths
- Support explicit imports with optional aliases
- Maintain deterministic compilation
- Preserve AI-friendly syntax

## 2. Non-goals

- No package manager
- No dependency downloading
- No versioning
- No circular imports
- No dynamic imports
- No reflection

## 3. Terminology

- **Module**: A single `.ail` source file
- **Package**: A directory containing modules
- **Import**: Declaration that brings symbols from another module into scope
- **Export**: Public symbols declared by a module
- **Module path**: Qualified name like `math.max`
- **Alias**: Alternative local name for an imported symbol

## 4. Module Model

AILang uses a **file-based module model**:

- Each `.ail` file is a module
- Module path derives from file path relative to project root
- Default export: all top-level declarations are exported
- No explicit `export` keyword in v1

## 5. File Layout

```
project/
  main.ail
  math/
    max.ail
    min.ail
  io/
    print.ail
```

Module paths:
- `main` → `main.ail`
- `math.max` → `math/max.ail`
- `io.print` → `io/print.ail`

## 6. Import Syntax

```ebnf
import_declaration
    → "import" identifier ( "." identifier )* [ "as" identifier ] ";"
    → "import" "*" [ "as" identifier ] "from" string_literal ";"
```

Examples:
```ail
import math.max;
import io.print as p;
import math.*;
```

## 7. Qualified Names

Qualified names identify symbols across modules:

```
math.max
io.print
config.db.port
```

Qualified names reuse MemberAccess AST/IR nodes.

## 8. Symbol Visibility

- All top-level declarations are public by default
- No `private` modifier in v1
- Future: `pub` / `priv` modifiers

## 9. Export Rules

- Every top-level function/variable is exported
- No selective export in v1
- Future: `export` keyword for explicit control

## 10. Module Resolution

Resolution algorithm:
1. Start at project root
2. Follow module path segments as directory/file names
3. Append `.ail` to final segment
4. Verify file exists

Example: `math.max` → `math/max.ail`

## 11. Dependency Graph

- Directed acyclic graph (DAG)
- Nodes: modules
- Edges: imports
- Cycle detection during compilation
- Error on circular imports

## 12. Circular Import Behavior

**Statically forbidden.** Compiler reports error:

```
MOD001: Circular import detected: math.max → math.utils → math.max
```

## 13. Duplicate Import Behavior

Allowed but warned:

```
MOD002: Duplicate import of math.max (ignored)
```

## 14. Compilation Model

1. Parse all imported modules
2. Build unified AST with ImportDeclarationNodes
3. Semantic analysis resolves imports to declarations
4. Type checker validates cross-module references
5. IR builder emits module initialization code

## 15. Runtime Initialization Model

- Module-level code executes on first import
- Execution order follows dependency graph (topological sort)
- Each module initializes exactly once
- Thread-safe initialization in future

## 16. Error Conditions

| Code | Description |
|------|-------------|
| MOD001 | Circular import detected |
| MOD002 | Duplicate import |
| MOD003 | Module not found |
| MOD004 | Symbol not found in module |
| MOD005 | Import path traversal attempt |

## 17. Examples

### Simple Import

```ail
// math/max.ail
fn max(a, b) { if a > b { a } else { b } }

// main.ail
import math.max;
math.max(10, 20)
```

### Alias Import

```ail
import io.print as p;
p("hello")
```

### Wildcard Import

```ail
import math.*;
max(10, 20)
```

## 18. Future Extension Points

- Explicit `export` keyword
- `pub`/`priv` visibility modifiers
- Package manager
- Version constraints
- Conditional imports
- Re-export (`export import`)