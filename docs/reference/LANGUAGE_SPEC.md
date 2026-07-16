# AILang Language Specification

**Version:** 1.0.7  
**Status:** Complete — Implementation Reference  
**Canonical Source:** This document is the single source of truth for the AILang language.

---

## 1. Introduction

AILang is a dynamically typed programming language designed to be deterministic, specification-driven, and easy for both humans and AI systems to reason about. It features a complete compiler pipeline, a 16-module standard library, and compile-time semantic validation where possible.
 
### 1.1 Design Goals

- **Deterministic** — same input always produces the same output
- **Explicit** — no hidden state, no implicit conversions, no magic
- **Simple grammar** — small, unambiguous syntax that is easy to parse
- **Specification-first** — every feature has a written specification
- **AI-friendly** — designed for reliable generation by large language models

### 1.2 Implementation

AILang is implemented as a multi-stage pipeline:

```
Source Code
  → Lexer (token stream)
  → Parser (Concrete Syntax Tree)
  → AST Builder (Abstract Syntax Tree)
  → Semantic Analyzer (symbol resolution)
  → Type Checker (type validation)
  → IR Builder (Intermediate Representation)
  → Runtime Interpreter (execution)
```

---

## 2. Lexical Structure

### 2.1 Character Set

AILang source files are UTF-8 encoded text. Identifiers, keywords, and numeric literals use ASCII characters only.

### 2.2 Whitespace

Whitespace characters (spaces `0x20`, tabs `0x09`, newlines `0x0A`) separate tokens and are otherwise ignored. Carriage return (`0x0D`) is treated as a line terminator.

### 2.3 Comments

Comments begin with `//` and extend to the end of the line. Multi-line (`/* */`) comments are not supported.

```ail
// This is a comment
fn main() {
    return 0  // inline comment
}
```

### 2.4 Identifiers

Identifiers begin with a letter (`A–Z`, `a–z`) or underscore (`_`), followed by zero or more letters, digits (`0–9`), or underscores. Identifiers are case-sensitive.

```
identifier = (letter | "_") { letter | digit | "_" }
```

Valid identifiers: `x`, `_count`, `math_add`, `toString`, `FibonacciNumber`

### 2.5 Keywords

The following identifiers are reserved as keywords and cannot be used as identifiers:

```
let    fn     if     else   return
import as     true   false
```

### 2.6 Literals

#### 2.6.1 Numeric Literals

Numeric literals are sequences of decimal digits (`0–9`) with an optional fractional part.

```ail
42       // integer
0        // integer zero
3.14     // float
0.5      // float
```

Number representation:
- No hexadecimal, octal, or binary literals
- No scientific notation
- No underscore separators
- Float literals use a single `.` to separate integer and fractional parts

**Examples:**

```text
Valid:

42
3.14
0.5

Invalid:

3.  (trailing dot — use 3.0)
```

#### 2.6.2 String Literals

String literals are delimited by double quotes (`"`).

```ail
"hello world"
"line1\nline2"
"she said \"hello\""
```

Supported escape sequences:

| Escape | Meaning |
|--------|---------|
| `\n`   | Newline (U+000A) |
| `\t`   | Tab (U+0009) |
| `\r`   | Carriage return (U+000D) |
| `\\`   | Backslash (U+005C) |
| `\"`   | Double quote (U+0022) |

- No single-quoted strings (`'`) are supported
- No string interpolation
- No raw strings

#### 2.6.3 Boolean Literals

`true` and `false` are first-class boolean literals. They participate in logical operations, conditionals, comparison results, and return values.

### 2.7 Operators and Punctuation

```
Arithmetic:    +   -   *   /   %
Comparison:    ==  !=  <   <=  >   >=
Logical:       &&  ||  !
Assignment:    =
Grouping:      (   )
Blocks:        {   }
Access:        .
Separators:    ,   ;
```

### 2.8 Lexical Error Codes

| Code | Condition |
|------|-----------|
| LEX001 | Unexpected character |
| LEX002 | Unterminated string literal |
| LEX003 | Invalid escape sequence |


---

## 3. Types

AILang is dynamically typed. The runtime recognizes the following value types:

| Type | Description | Examples |
|------|-------------|----------|
| `int` | Integer (Python arbitrary-precision) | `42`, `-1`, `0` |
| `float` | Float (IEEE 754 double-precision) | from division (`22 / 7`) |
| `string` | Text (Unicode via UTF-8) | `"hello"` |
| `bool` | Boolean | `true`, `false` |
| `list` | Ordered mutable sequence | via `list.new()` |
| `map` | Key-value dictionary | via `map.new()` |
| `set` | Unordered collection of unique values | via `set.new()` |
| `function` | Callable function value | via `fn` declaration |
| `None` | Null/absent value (Python `None`) | from `json.parse("null")` |

### 3.1 Type Coercion

- Numeric operations promote `int` to `float` when either operand is `float`.
- Boolean values participate in arithmetic: `true` is `1`, `false` is `0`.
- Explicit conversion is available via the `convert` module (`to_int`, `to_string`).

---

## 4. Variables and Assignment

### 4.1 Variable Declaration

Variables are declared with `let` and an initializer:

```ail
let name = expression;
```

- Variables are block-scoped.
- A variable must have an initializer (there is no default value).

### 4.2 Variable Assignment

Variables can be reassigned using the `=` operator:

```ail
let x = 10;
x = x + 1;      // reassignment
```

- The `=` operator is an expression (right-associative), returning the assigned value.
- Assignment to an undeclared variable is a compile-time error.

### 4.3 Scope Rules

- Scopes are created by function bodies (`{ }`) and block statements (`{ }`).
- Variables declared in an outer scope are visible in nested scopes.
- An inner scope can shadow an outer variable by declaring a new variable with the same name.

---

## 5. Functions

### 5.1 Function Definition

Functions are defined with `fn`:

```ail
fn name(parameter1, parameter2) {
    body
}
```

- Parameters are positional, comma-separated identifiers.
- Parameters may have default values: `fn add(a, b = 10) { ... }`.
- Parameters without defaults are required; defaults are used when the argument is omitted at the call site.
- Default value expressions are evaluated fresh on each call when the parameter is omitted.
- Required parameters must precede parameters with defaults.
- Empty parameter lists are valid: `fn zero() { ... }`.
- Functions must be defined before they are called (no forward references).
- Empty function bodies are valid: `fn noop() {}`.

### 5.2 Return Values

Functions return values using `return`:

```ail
fn add(a, b) {
    return a + b
}
```

If execution reaches the end of a function body without encountering `return`, the value of the last expression in the body is the implicit return value. If the body is empty, the return value is `None`.

### 5.3 The `main` Function

The entry point of every AILang program is `main()`:

```ail
fn main() {
    return 0
}
```

- `main` is called automatically after all module-level code executes.
- The return value of `main` is discarded by the CLI (use `print()` for output).

### 5.4 Functions as Values

Functions are first-class values and can be stored in variables or data structures:

```ail
let ops = {"max": fn(x, y) { if x > y { return x } else { return y } }};
ops.max(10, 20)
```

---

## 6. Operators

### 6.1 Arithmetic Operators

| Operator | Description | Associativity |
|----------|-------------|---------------|
| `+`      | Addition / string concatenation | Left |
| `-`      | Subtraction | Left |
| `*`      | Multiplication | Left |
| `/`      | Division (returns float) | Left |
| `%`      | Modulo | Left |

- Division always returns a `float`, even when operands are integers.
- `+` on strings performs concatenation.

### 6.2 Comparison Operators

| Operator | Description |
|----------|-------------|
| `==`     | Equal |
| `!=`     | Not equal |
| `<`      | Less than |
| `<=`     | Less than or equal |
| `>`      | Greater than |
| `>=`     | Greater than or equal |

Comparison results are boolean values (`true`/`false`).

### 6.3 Logical Operators

| Operator | Description | Notes |
|----------|-------------|-------|
| `&&`     | Logical AND | Eager (no short-circuit) |
| `\|\|`   | Logical OR  | Eager (no short-circuit) |
| `!`      | Logical NOT | Unary prefix |

- `&&` and `||` evaluate both operands eagerly (no short-circuit). Use nested `if` blocks for conditional evaluation.

### 6.4 Unary Operators

| Operator | Description |
|----------|-------------|
| `-`      | Numeric negation |
| `!`      | Logical NOT |

### 6.5 Assignment Operator

| Operator | Description | Associativity |
|----------|-------------|---------------|
| `=`      | Assignment  | Right |

Right-associative: `a = b = c` parses as `a = (b = c)`.

### 6.6 Operator Precedence

From highest to lowest:

| Level | Operators | Associativity |
|-------|-----------|---------------|
| 1 | `!` (unary) `-` (unary) | Right |
| 2 | `*` `/` `%` | Left |
| 3 | `+` `-` | Left |
| 4 | `<` `<=` `>` `>=` | Left |
| 5 | `==` `!=` | Left |
| 6 | `&&` | Left |
| 7 | `\|\|` | Left |
| 8 | `=` | Right |

---

## 7. Control Flow

### 7.1 If Statement

```ail
if (condition) {
    then_block
} else {
    else_block
}
```

- The condition must be enclosed in parentheses.
- The `else` branch is optional.
- `else if` chains are achieved by nesting:
  ```ail
  if (a) {
      ...
  } else if (b) {
      ...
  } else {
      ...
  }
  ```
- The condition is evaluated as boolean. The number `0` is truthy.

### 7.2 Return Statement

```ail
return expression;
```

Exits the current function and returns the value of the expression.

### 7.3 Blocks

Blocks are sequences of statements enclosed in `{ }`. Blocks create a new lexical scope.

---

## 8. Expressions

### 8.1 Primary Expressions

```
primary ::= identifier
          | number_literal
          | string_literal
          | "true"
          | "false"
          | "(" expression ")"
```

### 8.2 Call Expressions

```ail
function_name(arg1, arg2)
```

- Arguments are comma-separated expressions.
- A trailing comma is not allowed.

### 8.3 Member Access

```ail
receiver.member
receiver.member()
```

- Member access on a map/dict returns the value at that key.
- Member access chains left-to-right: `a.b.c` is `(a.b).c`.
- Used for module-qualified names: `string.uppercase("hello")`.

### 8.4 Assignment Expression

```ail
variable = value
```

The assignment operator `=` is right-associative and returns the assigned value.

---

## 9. Modules and Imports

### 9.1 Import Declaration

```ail
import module_name;
import parent.child;
import module_name as alias;
```

- Import declarations are top-level only (must appear before any function or variable declarations).
- Module paths use identifier segments separated by dots.

### 9.2 Module Resolution

Module paths map to file paths:

```
import math;       → stdlib/math.ail
import math.add;   → stdlib/math/add.ail or stdlib/math.ail (then exports add)
import apps.calc;  → apps/calc.ail (relative to project root)
```

Resolution searches:
1. The standard library directory (`stdlib/`)
2. The project root directory
3. Parent directories walking upward

### 9.3 Import Alias

```ail
import string as str;   // str.uppercase(...)
```

The alias replaces the module name for qualified access.

### 9.4 Module Exports

All top-level function and variable declarations in a module are exported by default. They are accessed through qualified names:

```ail
import math;
math.add(1, 2)        // calls add exported by math.ail
```

### 9.5 Module Restrictions

- Circular imports are detected and reported as compile-time errors (MOD001).
- Duplicate imports of the same qualified name produce a warning (MOD002).
- Import path segments must be identifiers (no string-based import paths).
- Wildcard imports (`import *`) are not supported.

---

## 10. Standard Library

### 10.1 Module Overview

| Module | Description |
|--------|-------------|
| `string` | String manipulation: `concat`, `equals`, `uppercase`, `lowercase`, `length`, `contains`, `starts_with`, `ends_with`, `trim`, `substring`, `find`, `find_from`, `split`, `join` |
| `math` | Arithmetic helpers: `add`, `sub`, `mul`, `div`, `abs`, `min`, `max` |
| `list` | Dynamic array: `new`, `append`, `get`, `len`, `contains`, `remove`, `clear`, `sum`, `find_by_key`, `sort`, `sort_by_key`, `copy`, `filter_by_key` |
| `array` | Alias for list: `new`, `push`, `get`, `len`, `contains`, `remove`, `clear` |
| `map` | Key-value dictionary: `new`, `set`, `get`, `has`, `delete`, `keys`, `get_or_default`, `clear` |
| `set` | Unordered set: `new`, `add`, `contains`, `len`, `remove`, `clear` |
| `file` | File I/O: `exists`, `read`, `write`, `append`, `remove`, `listdir` |
| `path` | Path manipulation: `join`, `basename`, `dirname`, `extension`, `normalize` |
| `json` | JSON: `parse`, `stringify` |
| `csv` | CSV: `parse`, `parse_header`, `stringify` |
| `time` | Time: `now`, `timestamp`, `sleep`, `format` |
| `random` | Random numbers: `int`, `float`, `choice` |
| `environment` | Environment: `get`, `cwd`, `args` |
| `convert` | Type conversion: `to_string`, `to_int`, `to_bool`, `to_number` |
| `io` | I/O helpers: `write`, `writeln`, `println`, `read` |
| `system` | System operations: `exit` |

### 10.2 Built-in Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `print` | `print(...)` | Prints arguments to stdout, separated by spaces, followed by a newline |

### 10.3 Calling Module Functions

```ail
import string;
string.uppercase("hello")       // "HELLO"
string.contains("hello", "el")  // true
```

### 10.4 Collections API

All collection functions mutate their argument in-place and return the mutated collection.

#### List / Array

| Function | Description |
|----------|-------------|
| `list.new() / array.new()` | Create empty list |
| `list.append(list, value) / array.push(list, value)` | Append value to end |
| `list.get(list, index) / array.get(list, index)` | Get element at index (0-based) |
| `list.len(list) / array.len(list)` | Return element count |
| `list.contains(list, value) / array.contains(list, value)` | Check if value exists |
| `list.remove(list, value) / array.remove(list, value)` | Remove first occurrence (no-op if absent) |
| `list.clear(list) / array.clear(list)` | Remove all elements |

#### Map

| Function | Description |
|----------|-------------|
| `map.new()` | Create empty map |
| `map.set(map, key, value)` | Set key-value pair |
| `map.get(map, key)` | Get value by key (raises error if absent) |
| `map.has(map, key)` | Check if key exists |
| `map.delete(map, key)` | Delete key (no-op if absent) |
| `map.keys(map)` | Return list of keys |
| `map.clear(map)` | Remove all entries |

#### Set

| Function | Description |
|----------|-------------|
| `set.new()` | Create empty set |
| `set.add(set, value)` | Add value |
| `set.contains(set, value)` | Check membership |
| `set.len(set)` | Return cardinality |
| `set.remove(set, value)` | Remove value (no-op if absent) |
| `set.clear(set)` | Remove all elements |

---

## 11. Error Handling and Diagnostics

### 11.1 Compile-Time Diagnostics

Errors during compilation are reported through the `DiagnosticReporter` system. Each diagnostic has:

- **Severity**: `ERROR`, `WARNING`, or `NOTE`
- **Error code**: A unique identifier (e.g., `SEM001`)
- **Message**: Human-readable description
- **Location**: Source file line and column

#### Error Codes

| Code | Description |
|------|-------------|
| LEX001 | Unexpected character |
| LEX002 | Unterminated string literal |
| LEX003 | Invalid escape sequence |
| PAR001 | Expected token |
| PAR002 | Invalid import path |
| SEM001 | Duplicate declaration |
| SEM002 | Undefined identifier |
| MOD001 | Circular import detected |
| MOD002 | Duplicate import |
| MOD003 | Module not found |
| MOD004 | Symbol not found in module |
| MOD005 | Import path traversal attempt |
| TYP001 | Unknown type |
| TYP002 | Return outside function |
| TYP003 | Return type mismatch |
| TYP004 | Non-boolean condition |
| TYP005 | Non-numeric operand |
| TYP006 | Type mismatch in comparison |
| TYP007 | Non-boolean logical operand |
| TYP008 | Assignment type mismatch |
| TYP009 | Non-numeric unary operand |
| TYP010 | Non-boolean not operand |
| TYP011 | Argument count mismatch |
| TYP012 | Argument type mismatch |
| TYP013 | Non-function callee |

### 11.2 Runtime Errors

Runtime errors are reported as Python exceptions. Common cases:

- Division by zero
- Index out of bounds on list/array access
- Key not found in map access
- File not found on read/remove
- Type error in built-in function arguments

---

## 12. Grammar

### 12.1 Notation

Extended Backus-Naur Form (EBNF):
- `= ` defines a production
- `|` alternation
- `{ }` repetition (zero or more)
- `[ ]` optional
- `"` terminal symbol
- `? ?` descriptive comment

### 12.2 Complete Grammar

```ebnf
program = { import_declaration }, { declaration } ;

(* --- Imports --- *)
import_declaration = "import", identifier, { ".", identifier },
                     [ "as", identifier ], ";" ;

(* --- Declarations --- *)
declaration = variable_declaration
            | function_declaration ;

variable_declaration = "let", identifier, "=", expression, ";" ;

function_declaration = "fn", identifier, "(", [ parameter_list ], ")", block ;

parameter_list = parameter, { ",", parameter } ;
parameter = identifier, [ "=", expression ] ;

(* --- Statements --- *)
statement = variable_declaration
          | function_declaration
          | expression_statement
          | if_statement
          | return_statement
          | block ;

expression_statement = expression, ";" ;

return_statement = "return", expression, ";" ;

if_statement = "if", "(", expression, ")", block,
               [ "else", ( if_statement | block ) ] ;

(* --- Blocks --- *)
block = "{", { statement }, "}" ;

(* --- Expressions --- *)
expression = assignment_expression ;

assignment_expression = logical_or_expression,
                        [ "=", assignment_expression ] ;

logical_or_expression     = logical_and_expression, { "||", logical_and_expression } ;
logical_and_expression    = equality_expression, { "&&", equality_expression } ;
equality_expression       = comparison_expression,
                            { ( "==" | "!=" ), comparison_expression } ;
comparison_expression     = additive_expression,
                            { ( "<" | "<=" | ">" | ">=" ), additive_expression } ;
additive_expression       = multiplicative_expression,
                            { ( "+" | "-" ), multiplicative_expression } ;
multiplicative_expression = unary_expression,
                            { ( "*" | "/" | "%" ), unary_expression } ;
unary_expression   = [ ( "!" | "-" ) ], postfix_expression ;
postfix_expression = primary_expression, { ".", identifier
                                         | "(", [ argument_list ], ")" } ;

primary_expression = identifier
                   | number_literal
                   | string_literal
                   | "true"
                   | "false"
                   | "(", expression, ")" ;

argument_list = expression, { ",", expression } ;

(* --- Lexical Elements --- *)
identifier = ( letter | "_" ), { letter | digit | "_" } ;
number_literal = digit, { digit }, [ ".", digit, { digit } ] ;
string_literal = '"', { string_char }, '"' ;
string_char = ? any character except '"' or '\\' ?
            | escape_sequence ;
escape_sequence = "\\n" | "\\t" | "\\r" | "\\\\" | "\\\"" ;

letter = "A" | "B" | ... | "Z" | "a" | "b" | ... | "z" ;
digit = "0" | "1" | ... | "9" ;
```

---

## 13. Compilation Pipeline

### 13.1 Phases

| Phase | Input | Output | Description |
|-------|-------|--------|-------------|
| Lexer | Source text | Token stream | Converts text to tokens |
| Parser | Token stream | CST | Builds concrete syntax tree |
| AST Builder | CST | AST | Strips syntactic noise |
| Semantic Analyzer | AST | Annotated AST | Resolves symbols |
| Type Checker | Annotated AST | Type-annotated AST | Validates types |
| IR Builder | Annotated AST | IR | Lowers to intermediate representation |
| Runtime | IR | Execution result | Interprets IR |

### 13.2 Determinism

Every phase is deterministic: the same input always produces the same output.

---

## 14. Language Limitations

- No `while` or `for` loops — use recursion for iteration.
- No string indexing (`s[i]`) — use `string` module functions.
- No character type — use single-character strings.
- No array/list/set literal syntax — use module functions.


- No type annotations on function parameters or return values.
- No `null`, `nil`, `undefined`, or `None` literal — `None` appears only from JSON parsing.
- No struct, class, or user-defined types.
- No exception handling (`try`/`catch`).
- No closures or lambda expressions.
- No generators or iterators.
- No concurrency or parallelism.
- No pattern matching.
- No operator overloading.
- No decorators or annotations.

---

## 15. Examples

### Hello World

```ail
fn main() {
    print("Hello, AILang!");
    return 0
}
```

### Fibonacci

```ail
fn fib(n) {
    if (n == 0) {
        return 0
    }
    if (n == 1) {
        return 1
    }
    return fib(n - 1) + fib(n - 2)
}

fn main() {
    print(fib(10));
    return 0
}
```

### Using the Standard Library

```ail
import string;
import list;
import map;
import json;

fn main() {
    let items = list.new();
    list.append(items, "hello");
    list.append(items, "world");

    let data = json.parse("{\"key\": \"value\"}");

    print(string.uppercase("ailang"));
    return 0
}
```

### Recursive List Processing

```ail
import list;

fn sum_helper(items, i) {
    if (list.len(items) == i) {
        return 0
    }
    return list.get(items, i) + sum_helper(items, i + 1)
}

fn sum(items) {
    return sum_helper(items, 0)
}

fn main() {
    let items = list.new();
    list.append(items, 10);
    list.append(items, 20);
    list.append(items, 30);
    print(sum(items));
    return 0
}
```

---

## 16. CLI Reference

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ail run <file>` | Compile and execute | `ail run main.ail` |
| `ail build <file>` | Compile only | `ail build main.ail` |
| `ail check <file>` | Syntax/semantic validation | `ail check main.ail` |
| `ail test <file_or_dir>` | Run tests | `ail test tests/` |
| `ail fmt <file>` | Format source | `ail fmt main.ail` |
| `ail version` | Show version | `ail version` |

### Project Management

| Command | Description | Example |
|---------|-------------|---------|
| `ail new <name>` | Create new project | `ail new my_app` |

### Package Management

| Command | Description | Example |
|---------|-------------|---------|
| `ail add <dep>` | Add dependency | `ail add math_utils` |
| `ail remove <dep>` | Remove dependency | `ail remove math_utils` |
| `ail install` | Install dependencies | `ail install` |
| `ail update` | Update dependencies | `ail update` |
| `ail list` | List dependencies | `ail list` |
| `ail publish` | Publish package | `ail publish` |

### Tooling

| Command | Description | Example |
|---------|-------------|---------|
| `ail lsp` | Start LSP server | `ail lsp` |
| `ail rename` | Rename symbol | `ail rename` |
| `ail watch` | Watch files | `ail watch main.ail` |

### Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--no-check` | Skip pre-flight check | `ail run --no-check main.ail` |

### Exit Codes

- **0** = Success
- **Non-zero** = Error occurred


## 17. Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | — | Initial release. Lexer, parser, AST, semantic analysis, type checking, IR, runtime, 16 stdlib modules, 27 apps, 360+ tests. |
| 0.1.1 | — | Documentation consolidation. Canonical LANGUAGE_SPEC.md, archived legacy specs, fixed LANGUAGE_TOUR.md inconsistencies, 374 tests. |
| 0.1.2 | — | Bug fix sprint. Fixed AST builder crashes (empty return, missing initializer), module bare-name resolution, float literal diagnostic, block scope shadowing, recursion limit. Added LEX004. 522 tests. |
| 0.2.0 | — | Float literal support. Default parameter values. Compile-time arity validation (range check for defaults). Removed LEX004. 38 inventory tests. |
| 0.3.0 | M63 | Pre-flight check integration. `ail check` auto-runs before `ail run` and `ail test`. `--no-check` flag. |
| 0.4.0 | M64 | CLI tooling. `ail fmt`, `ail lsp`, `ail rename`, `ail watch`, `ail new`. |
| 0.5.0 | M65 | Stdlib expansion. `list.group_by_key`, `list.sum_by_key`, `list.take`, `list.skip`, `list.search_by_name`, `list.exists_by_key`, `map.values`, `map.get_or_default`, `map.safe_get`. |
| 1.0.0 | M66 | Bounded deterministic iteration. `for-in` loops promoted to stable. ADR-00X. |

---

## Appendix A: Syntax Summary

```
// Variables
let name = value;
name = new_value;

// Functions
fn name(params) { body }
fn name() { body }

// Conditionals
if (condition) { body }
if (condition) { body } else { body }
if (condition) { body } else if (condition) { body } else { body }

// Return
return value;

// Imports
import module;
import parent.child;
import module as alias;

// Comments
// single line only

// Literals
42         // integer
"text"     // string
true       // boolean
false      // boolean
```

---

## Appendix B: Reserved Keywords

| Keyword | Context |
|---------|---------|
| `fn` | Function declaration |
| `let` | Variable declaration |
| `if` | Conditional start |
| `else` | Conditional alternative |
| `return` | Return from function |
| `import` | Module import |
| `as` | Import alias |
| `true` | Boolean literal |
| `false` | Boolean literal |

These keywords are reserved and cannot be used as identifiers.

---

## Appendix C: Operators

| Category | Operators | Associativity |
|----------|-----------|---------------|
| Unary | `!` `-` | Right |
| Multiplicative | `*` `/` `%` | Left |
| Additive | `+` `-` | Left |
| Comparison | `<` `<=` `>` `>=` `==` `!=` | Left |
| Logical AND | `&&` | Left |
| Logical OR | `\|\|` | Left |
| Assignment | `=` | Right |

---

## Appendix D: Built-in Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `print` | `print(...)` | Print arguments to stdout, space-separated, followed by newline |

All other standard library functionality is accessed through module imports (`import module; module.fn(...)`).

---

## Appendix E: Diagnostic Codes

| Code | Description | Source |
|------|-------------|--------|
| LEX001 | Unexpected character | Lexer |
| LEX002 | Unterminated string literal | Lexer |
| LEX003 | Invalid escape sequence | Lexer |


| PAR001 | Expected token | Parser |
| PAR002 | Invalid import path | Parser |
| SEM001 | Duplicate declaration | Semantic analysis |
| SEM002 | Undefined identifier | Semantic analysis |
| MOD001 | Circular import detected | Module system |
| MOD002 | Duplicate import | Module system |
| MOD003 | Module not found | Module system |
| MOD004 | Symbol not found in module | Module system |
| MOD005 | Import path traversal attempt | Module system |
| TYP001 | Unknown type | Type checker |
| TYP002 | Return outside function | Type checker |
| TYP003 | Return type mismatch | Type checker |
| TYP004 | Non-boolean condition | Type checker |
| TYP005 | Non-numeric operand | Type checker |
| TYP006 | Type mismatch in comparison | Type checker |
| TYP007 | Non-boolean logical operand | Type checker |
| TYP008 | Assignment type mismatch | Type checker |
| TYP009 | Non-numeric unary operand | Type checker |
| TYP010 | Non-boolean not operand | Type checker |
| TYP011 | Argument count mismatch | Type checker |
| TYP012 | Argument type mismatch | Type checker |
| TYP013 | Non-function callee | Type checker |
