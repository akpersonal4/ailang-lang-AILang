# Getting Started with AILang

AILang is an AI-first programming language designed to be deterministic, specification-first, and easy for both humans and AI systems to reason about.

## Hello, World!

```ail
fn main() {
    print("Hello, AILang!");
    return 0
}
```

Every AILang program needs a `main()` function — this is the entry point. The `print()` builtin writes to stdout.

Save this as `hello.ail` and run:

```bash
ail run hello.ail
```

## Variables

Variables are declared with `let`:

```ail
fn main() {
    let name = "AILang";
    let version = 1;
    let pi = 22 / 7;
    print("Welcome to", name);
    return 0
}
```

Variables can be reassigned using `=`:

```ail
fn main() {
    let x = 1;
    x = 2;       // reassignment
    let y = x;
    print(y);
    return 0
}
```

All variables are block-scoped.

## Functions

Define functions with `fn`:

```ail
fn greet(name) {
    print("Hello,", name);
    return 0
}

fn add(a, b) {
    return a + b
}

fn main() {
    greet("Alice");
    let sum = add(3, 4);
    print("3 + 4 =", sum);
    return 0
}
```

Functions must be defined before they are called (no forward references). A function with an empty body uses `{}`.

## Conditionals

Use `if` with parentheses:

```ail
fn max(a, b) {
    if (a > b) {
        return a
    }
    return b
}

fn main() {
    let result = max(10, 20);
    print("Max is", result);
    return 0
}
```

Chained conditions use `&&`:

```ail
fn in_range(x, low, high) {
    if (x >= low && x <= high) {
        return 1
    }
    return 0
}
```

## Recursion

AILang does not have loop constructs. Use recursion for iteration:

```ail
fn factorial(n) {
    if (n == 0) {
        return 1
    }
    return n * factorial(n - 1)
}

fn main() {
    print("5! =", factorial(5));
    return 0
}
```

## Arithmetic Operators

| Operator | Description |
|----------|-------------|
| `+` | Addition |
| `-` | Subtraction or unary negation |
| `*` | Multiplication |
| `/` | Division (returns float) |
| `%` | Modulo |

## Comparison Operators

| Operator | Description |
|----------|-------------|
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |

## Boolean Operators

| Operator | Description | Notes |
|----------|-------------|-------|
| `&&` | Logical AND | Eager (no short-circuit) |
| `\|\|` | Logical OR | Eager (no short-circuit) |
| `!` | Logical NOT | Unary prefix |

**No short-circuit evaluation.** Both operands of `&&` and `||` are always evaluated before the operator is applied. Use nested `if` statements when the second operand depends on the first:

```ail
// WRONG — both operands evaluated eagerly, crashes if list is empty:
if (list.len(items) > 0 && list.get(items, 0) == x) { ... }

// CORRECT — nested if guards the second check:
if (list.len(items) > 0) {
    if (list.get(items, 0) == x) { ... }
}
```

Boolean literals `true` and `false` are first-class values:

```ail
fn main() {
    let is_valid = true;
    if (!false && is_valid) {
        return 1
    }
    return 0
}
```

## Comments

```ail
// This is a single-line comment
fn main() {
    return 42  // Inline comment
}
```

Multi-line comments are not supported.

## Strings

Strings are delimited by double quotes:

```ail
let s = "hello world";
let escaped = "line1\nline2\twith\ttabs";
let quote = "she said \"hello\"";
```

| Escape | Meaning |
|--------|---------|
| `\n` | Newline |
| `\t` | Tab |
| `\\` | Backslash |
| `\"` | Double quote |

## Importing Modules

```ail
import string;
import json;
import list;
import math;

fn main() {
    let s = string.uppercase("hello");
    let data = json.parse("{\"a\": 1}");
    let items = list.new();
    list.append(items, 10);
    let sum = math.add(1, 2);
    return 0
}
```

Module paths map to file paths: `math.add` maps to `stdlib/math.ail`.

## Using the Standard Library

See the [Standard Library Reference](STDLIB_REFERENCE.md) for the complete API.

Quick examples:

```ail
import file;
import random;
import time;

fn main() {
    file.write("test.txt", "hello world");
    let content = file.read("test.txt");
    file.remove("test.txt");

    let rand_int = random.int(1, 100);
    let now = time.now();

    print(content, rand_int, now);
    return 0
}
```

## VS Code Extension

AILang has a VS Code extension that provides syntax highlighting, snippets, bracket matching, auto-indentation, and more.

Install from the VS Code Marketplace or side-load from the repo:

```bash
# From the repository root
code --install-extension extensions/vscode-ailang
```

Features:
- **Syntax highlighting** — keywords, strings, numbers, comments, operators, modules
- **Code snippets** — `main`, `fn`, `if`, `ifelse`, `import`, `return`, `let`, `recur`
- **Bracket matching** — auto-close and surround `{}`, `()`, `""`
- **Auto-indentation** — automatic indent after `{`, outdent on `}`
- **Line comments** — `//` support with toggling
- **Folding** — `#region`/`#endregion` markers

## Code Formatting

AILang includes a deterministic source code formatter (`ail fmt`). It enforces a single canonical style with no configuration options.

```bash
# Format a file in-place
ail fmt hello.ail

# Check without modifying
ail fmt --check hello.ail

# Format from stdin
cat hello.ail | ail fmt --stdin
```

### Formatting Rules

| Rule | Example |
|------|---------|
| 4-space indentation | `    return x;` |
| Opening brace on same line | `fn main() {` |
| `} else {` on one line | `} else {` |
| Space around binary operators | `a + b`, `x == y` |
| Space after comma | `fn add(a, b)` |
| Single blank line between functions | `fn foo() { }` + blank + `fn bar() { }` |
| Trailing whitespace removed | `return 0;` not `return 0;   ` |
| Newline at EOF | Always present |
| Comments preserved | Inline and standalone comments retained |

Formatting is deterministic and idempotent — running `ail fmt` twice on the same file always produces identical output.

## Next Steps

- Read the [Language Tour](LANGUAGE_TOUR.md) for a deep dive into syntax and semantics.
- Browse the [Standard Library Reference](STDLIB_REFERENCE.md) for all available modules.
- Explore example programs in the `examples/` and `apps/` directories.
- See the [Compiler Architecture](COMPILER_ARCHITECTURE.md) guide to understand how AILang works internally.
