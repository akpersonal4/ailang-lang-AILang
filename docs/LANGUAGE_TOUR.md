# AILang Language Tour

## Overview

AILang is a minimal, deterministic, AI-first programming language. This tour covers every language feature with examples.

## Why AILang?

AILang is designed around four principles:

- **Deterministic** — The same source code always produces the same output. No undefined behavior, no implicit state, no platform-dependent results. This makes AILang ideal for AI code generation and critical systems.

- **Explicit** — Everything is visible. Import what you use, declare what you need, control flow is unambiguous. There are no magic imports, no implicit globals, no hidden type coercions.

- **Specification-first** — The language is defined by a single canonical specification (`LANGUAGE_SPEC.md`) that is verified against the actual compiler implementation. AI systems can learn AILang from the spec alone — proven by 100% first-pass success on 23 AI-generated programs.

- **AI-friendly** — Simple syntax, no ambiguities, consistent grammar. The language was designed from the start to be as easy for AI models to generate as for humans to read. Every construct has exactly one way to express it.

## 1. Program Structure

An AILang program is a sequence of:
- Import declarations (optional, must be at the top)
- Function definitions

### Entry Point

Every program must have a `main()` function:

```ail
fn main() {
    return 42
}
```

The `main()` function is called when the program runs. Its return value is discarded by the CLI (all output must use `print()`).

## 2. Functions

### Function Definitions

```ail
fn function_name(param1, param2) {
    // body
    return value
}
```

Parameters are positional. All parameters are required (no default values, no varargs).

### Return Values

Functions return values explicitly with `return`:

```ail
fn add(a, b) {
    return a + b
}
```

Empty function bodies are valid:

```ail
fn noop() {}
```

### Calling Functions

```ail
fn main() {
    let result = add(3, 4);
    print(add(10, 20));
    return 0
}
```

### Known Limitation: Forward References

Functions must be defined before they are called. This code will fail:

```ail
fn main() {
    return helper()  // Error: 'helper' not defined yet
}
fn helper() {
    return 42
}
```

Define helper functions first:

```ail
fn helper() {
    return 42
}
fn main() {
    return helper()  // OK
}
```

## 3. Variables

### Declaration

Variables are declared with `let`:

```ail
let name = "Alice";
let count = 42;
let result = add(3, 4);
```

### Scope

Variables are block-scoped:

```ail
fn main() {
    let x = 1;
    if (x == 1) {
        let y = 2;  // y only exists inside this block
        print(y);
    }
    // print(y);  // Error: y not in scope
    return 0
}
```

### Reassignment

Variables can be reassigned using `=`:

```ail
let x = 1;
x = 2;  // OK — reassignment
```

The `=` operator is an expression (right-associative) and returns the assigned value.

## 4. Types

AILang is dynamically typed. The runtime recognizes these types:

| Type | Examples | Notes |
|------|----------|-------|
| `int` | `42`, `-1`, `0` | Integer literals |
| `float` | `22 / 7`, `10 / 3` | Result of division |
| `string` | `"hello"` | Double-quoted only |
| `bool` | `true`, `false` | First-class literals |
| `list` | `list.new()` | Via stdlib `list` module |
| `map` | `map.new()` | Via stdlib `map` module |
| `set` | `set.new()` | Via stdlib `set` module |
| `function` | `add` | Callable values |
| `None` | (no literal) | Result of `json.parse("null")` |

## 5. Expressions

### Arithmetic

```ail
let sum = 1 + 2;
let diff = 10 - 5;
let product = 3 * 4;
let quotient = 10 / 3;   // -> 3.333...
let remainder = 17 % 5;  // -> 2
let neg = -42;
```

Integer division is not supported. Use `convert.to_int(n / 2)` for integer truncation.

### Comparison

```ail
5 == 5   // true
5 != 10  // true
5 < 10   // true
10 > 5   // true
5 <= 5   // true
10 >= 10 // true
```

### Boolean Logic

```ail
true && false   // false
true || false   // true
!true           // false
```

Booleans participate in arithmetic: `true + true + false` evaluates to `2`.

**Important:** `&&` and `||` evaluate **both operands** before applying the operator. AILang does not perform short-circuit evaluation. Programs must not rely on lazy evaluation for guarded access.

```ail
// WRONG — crashes if list is empty (both operands evaluated before &&):
if (list.len(items) > 0 && list.get(items, 0) == x) { ... }

// CORRECT — use nested if for guarded access:
if (list.len(items) > 0) {
    if (list.get(items, 0) == x) { ... }
}
```

### Chained Conditions

```ail
if (x > 0 && x < 10) { ... }
```

### Precedence

Expressions follow standard arithmetic precedence:
1. Unary `-`, `!`
2. `*`, `/`, `%`
3. `+`, `-`
4. `<`, `>`, `<=`, `>=`, `==`, `!=`
5. `&&`
6. `||`

Use parentheses for explicit grouping:

```ail
let result = (1 + 2) * 3;  // 9, not 7
```

## 6. Control Flow

### If / Else Statements

```ail
if (condition) {
    // true branch
}

if (condition) {
    // true branch
} else {
    // false branch
}

if (condition) {
    // ...
} else if (other_condition) {
    // ...
} else {
    // ...
}
```

The `else` keyword is supported. `else if` is syntactic nesting of an `if` inside an `else` block.

Sequential ifs with early return are also idiomatic:

```ail
fn grade(score) {
    if (score >= 90) { return "A" }
    if (score >= 80) { return "B" }
    if (score >= 70) { return "C" }
    if (score >= 60) { return "D" }
    return "F"
}
```

### No Loops

AILang does not have `while` or `for` loops. Use recursion:

```ail
fn countdown(n) {
    if (n == 0) { return 0 }
    print(n);
    return countdown(n - 1)
}
```

## 7. Comments

```ail
// Single-line comment
fn main() {
    // Comments can appear anywhere
    return 42  // Inline comment
}
```

Multi-line comments (`/* */`) are not supported.

## 8. Strings

```ail
let s = "hello";
let escaped = "tab\there\nnewline";
let quote = "she said \"hi\"";
let empty = "";
```

### Escape Sequences

| Sequence | Character |
|----------|-----------|
| `\n` | Newline (LF, 0x0A) |
| `\t` | Tab (0x09) |
| `\\` | Backslash |
| `\"` | Double quote |

### String Module

String manipulation is available through the `string` module:

```ail
import string;
let upper = string.uppercase("hello");      // "HELLO"
let trimmed = string.trim("  hi  ");         // "hi"
let slice = string.substring("hello", 1, 4); // "ell"
```

## 9. Boolean Literals

`true` and `false` are first-class literals:

```ail
fn main() {
    if (true) {
        return 1
    }
    return 0
}
```

## 10. Modules and Imports

### Import Syntax

```ail
import module_name;
import parent.child;
import module_name as alias;
```

### Module Resolution

A module path maps to a file path:
- `import math;` → `stdlib/math.ail`
- `import string;` → `stdlib/string.ail`
- `import parent.child;` → `parent/child.ail`

### Circular Imports

Circular imports are detected and reported as errors at compile time.

## 11. Member Access

```ail
module.function()     // Call function from module
map.get(data, "key")  // Module function call
value.member          // Member access (map key lookup)
```

Member access on maps returns the value at that key:

```ail
import map;
let data = map.new();
map.set(data, "name", "Alice");
let name = data.name;  // Equivalent to map.get(data, "name")
```

## 12. Built-in Functions

### `print(...)`

Prints values to stdout. Accepts multiple arguments, each separated by a space:

```ail
print("Hello");           // Hello
print("Value:", 42);      // Value: 42
print("A", "B", "C");     // A B C
```

All output must use `print()`. The CLI does not print the return value of `main()`.

## 13. Complete Grammar Reference

The canonical grammar is defined in the [Language Specification](../LANGUAGE_SPEC.md#12-grammar). Key productions:

```
program = { import_declaration }, { declaration } ;

import_declaration = "import", identifier, { ".", identifier },
                     [ "as", identifier ], ";" ;

declaration = variable_declaration
            | function_declaration ;

variable_declaration = "let", identifier, "=", expression, ";" ;

function_declaration = "fn", identifier, "(", [ parameter_list ], ")", block ;

parameter_list = identifier, { ",", identifier } ;

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

block = "{", { statement }, "}" ;

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
```

## 14. Known Limitations

| Limitation | Workaround |
|------------|------------|
| No loops (while/for) | Use recursion |
| No string indexing (`s[i]`) | Use `string.substring()`, `string.contains()`, `string.length()` |
| No forward references | Define functions in dependency order |
| No float literals | Use integer division: `22 / 7` |
| No None/null literal | Use `json.parse("null")` for Python None |
| No integer division | Use `convert.to_int(n / d)` |
| No character type | Use single-character strings |
| No multi-line comments | Use single-line `//` comments |
| No string interpolation | Use `print()` with multiple arguments |
| No destructuring | Use `list.get()`, `map.get()` |
