# Compiler Architecture

## Overview

The AILang compiler is a multi-stage pipeline that transforms source code into executable IR. Each stage is independent, testable, and communicates with the next through well-defined data structures.

## Pipeline

```
Source Code
    │
    ▼
┌─────────────┐
│   Lexer     │  Source text → Token stream
└─────────────┘
    │
    ▼
┌─────────────┐
│   Parser    │  Token stream → CST (Concrete Syntax Tree)
└─────────────┘
    │
    ▼
┌─────────────┐
│ AST Builder │  CST → AST (Abstract Syntax Tree)
└─────────────┘
    │
    ▼
┌─────────────┐
│  Semantic   │  AST → Annotated AST (symbol resolution, type checking)
│  Analyzer   │
└─────────────┘
    │
    ▼
┌─────────────┐
│ IR Builder  │  AST → IR (Intermediate Representation)
└─────────────┘
    │
    ▼
┌─────────────┐
│  Runtime    │  IR → Execution
│ Interpreter │
└─────────────┘
```

## Directory Structure

```
compiler/
├── __init__.py          # Package marker
├── __main__.py          # Entry: `python -m compiler` / `ail
├── source.py            # Source file abstraction
├── diagnostics.py       # Error/warning reporting
├── lexer.py             # Lexical analysis
├── parser.py            # Syntactic analysis
├── ast/
│   ├── __init__.py
│   ├── nodes.py         # AST node definitions
│   └── builder.py       # CST → AST conversion
├── semantic/
│   ├── __init__.py
│   ├── analyzer.py      # Semantic analysis
│   └── symbol_table.py  # Symbol table management
├── ir/
│   ├── __init__.py
│   ├── nodes.py         # IR node definitions
│   └── builder.py       # AST → IR conversion
├── types/
│   ├── __init__.py
│   └── checker.py       # Type checking
├── compilation/
│   ├── __init__.py
│   ├── session.py       # Compilation orchestration
│   ├── graph.py         # Module dependency graph
│   └── resolution.py    # Module path resolution
├── runtime/
│   ├── __init__.py
│   ├── interpreter.py   # IR interpreter
│   ├── environment.py   # Scope/environment management
│   ├── stack_frame.py   # Call stack frames
│   └── builtins.py      # Built-in function implementations
├── optimizer/
│   └── __init__.py
└── cli/
    ├── __init__.py
    └── main.py          # CLI entry point
```

## Stage Details

### 1. Source Model (`source.py`)

The Source class represents an input file with its path, text content, and line tracking. It provides methods for extracting line/column information from positions.

### 2. Diagnostics (`diagnostics.py`)

DiagnosticReporter collects errors and warnings during compilation. It supports:
- Error count tracking
- Formatted error messages
- Integration with all pipeline stages

### 3. Lexer (`lexer.py`)

The lexer converts source text into a sequence of tokens. It handles:
- Keywords: `fn`, `let`, `if`, `return`, `import`, `as`, `true`, `false`
- Identifiers and literals (integers, strings)
- Operators and punctuation
- Comments (`//`)
- Escape sequences in strings
- Error reporting for unterminated strings and invalid escapes

### 4. Parser (`parser.py`)

The parser converts tokens into a Concrete Syntax Tree (CST). It implements a recursive-descent parser that follows the grammar exactly. Features:
- Expression parsing with proper precedence
- Block parsing with safety guards against infinite loops
- Import declaration parsing
- Function definition parsing

### 5. AST Builder (`ast/builder.py`)

Converts the CST into an Abstract Syntax Tree (AST) by removing unnecessary syntactic detail. The AST is simpler and easier to analyze.

### 6. Semantic Analyzer (`semantic/analyzer.py`)

Performs semantic analysis on the AST:
- Symbol resolution (matching identifiers to declarations)
- Scope management
- Import resolution
- Forward reference detection
- Type annotation propagation

### 7. Symbol Table (`semantic/symbol_table.py`)

Manages symbol scopes. Supports:
- Nested scopes (enter/exit)
- Symbol declaration and lookup
- Module-level vs function-level scoping

### 8. IR Builder (`ir/builder.py`)

Lowers the annotated AST to an Intermediate Representation (IR). The IR is a flat list of instructions that the runtime can execute directly.

### 9. Runtime Interpreter (`runtime/interpreter.py`)

Executes the IR using a tree-walking interpreter with:
- Lexical scoping (Environment class)
- Call stack management (StackFrame class)
- Return value propagation (ReturnSignal exception)
- Built-in function dispatch

### 10. Built-in Functions (`runtime/builtins.py`)

All built-in and standard library functions are implemented as Python functions and registered in the `BUILTINS` dictionary. New stdlib modules follow this pattern:
1. Implement a Python function in `builtins.py`
2. Register it in the `BUILTINS` dict
3. Create an `.ail` wrapper in `stdlib/` that calls the builtin

### 11. Compilation Session (`compilation/session.py`)

Orchestrates the entire pipeline for multi-module projects:
1. **Discovery**: Find the entry file and all imported modules
2. **Resolution**: Resolve module paths to file paths
3. **Parsing**: Parse all source files
4. **Analysis**: Run semantic analysis on all modules
5. **IR Building**: Build IR for all modules
6. **Bundling**: Package all IR into a single bundle for execution

### 12. Module Resolution (`compilation/resolution.py`)

Resolves import statements to file paths:
- `import math;` → `stdlib/math.ail`
- `import mod.name;` → `mod/name.ail`
- Searches in stdlib directory and relative to the project root

### 13. Dependency Graph (`compilation/graph.py`)

Builds a directed graph of module dependencies. Used for:
- Topological sort for initialization order
- Circular import detection

## Data Flow

```
Source (.ail file)
  → Lexer → [Token]
  → Parser → CST (ProgramNode, FunctionNode, ...)
  → AST Builder → AST (ProgramNode, FunctionDefNode, ...)
  → Semantic Analyzer → Annotated AST
  → IR Builder → IR (ProgramIR, FunctionIR, ...)
  → Runtime Interpreter → Execution Result
```

## Module System

AILang's module system maps imports to file paths:

```
stdlib/              # Standard library directory
├── string.ail
├── math.ail
├── list.ail
├── map.ail
├── set.ail
├── array.ail
├── file.ail
├── path.ail
├── json.ail
├── csv.ail
├── time.ail
├── random.ail
├── environment.ail
├── convert.ail
├── io.ail
└── system.ail
apps/                # Application examples
├── calculator/
├── todo_manager/
└── ... (27 apps)
```

### How Imports Work

1. `import string;` → compiler searches for `string.ail` in stdlib/
2. `import apps.calculator;` → compiler searches for `apps/calculator.ail`
3. The imported module is parsed, analyzed, and compiled alongside the entry file
4. Functions from imported modules are accessed via qualified names: `string.uppercase()`

## Key Design Principles

1. **Specification first**: Each compiler stage follows a written specification
2. **Deterministic**: Same input always produces the same output
3. **Testable**: Each stage has isolated unit tests
4. **Explicit over implicit**: No magic behavior or hidden transformations
5. **Small components**: Each module has a single responsibility

## CLI Usage

```bash
# Run an AILang program
ail path/to/program.ail

# Or use subcommands
ail run path/to/program.ail
ail build path/to/program.ail
ail check path/to/program.ail

# Display help
ail help
ail version
```

The CLI:
- Locates the project root (walks up until `stdlib/` and `pyproject.toml` are found)
- Compiles and executes the program
- Reports errors to stderr
- Returns exit code 0 on success, 1 on error
