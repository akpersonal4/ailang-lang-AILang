# AILang Style Guide

## 1. Naming Conventions

### Functions

Use `snake_case` — all lowercase with underscores between words.

```text
// ✅ Correct
fn calculate_total() {}
fn parse_input() {}
fn format_output() {}

// ❌ Wrong
fn calculateTotal() {}    // camelCase
fn CalculateTotal() {}    // PascalCase
fn calculate-total() {}   // kebab-case
```

### Variables

Use `snake_case` — all lowercase, descriptive, unique across all functions.

```text
// ✅ Correct
let user_name = "Alice";
let total_count = 100;
let parsed_data = json.parse(raw);

// ❌ Wrong
let userName = "Alice";    // camelCase
let n = "Alice";           // too short, not descriptive
let data = json.parse(raw); // too generic
```

### Constants

Use `SCREAMING_SNAKE_CASE` — all uppercase with underscores.

```text
// ✅ Correct
let MAX_FILE_SIZE = 1048576;
let DEFAULT_PORT = 8080;
let API_BASE_URL = "https://api.example.com";
```

### Modules

Module names (in `import` statements) are always lowercase:

```text
import file;
import json;
import list;
import math;
import string;
```

## 2. File Organization

### Order Within a File

```text
// 1. Imports (stdlib first, then project modules)
import file;
import json;
import math;
import my_project_module;

// 2. Module-level constants
let MAX_RETRIES = 3;

// 3. Utility functions (Level 0)
fn helper_one() { }

// 4. Business logic functions (Level 1+)
fn process_data() { }

// 5. main() function (always last)
fn main() { }
```

### Maximum Line Length

Keep lines under 100 characters. The `ail fmt` tool enforces this automatically.

## 3. Comments

### Function Comments

Every function should have a comment describing its purpose:

```text
// Calculate the total price including tax
fn calculate_total(price, tax_rate) {
    let tax = math.mul(price, tax_rate);
    return math.add(price, tax)
}
```

### Section Comments

Use section comments to separate logical groups:

```text
// ============================================================
// Utility Functions
// ============================================================

fn helper_a() { }

fn helper_b() { }

// ============================================================
// Business Logic
// ============================================================
```

### Inline Comments

Minimize inline comments. The code should be self-documenting:

```text
// ✅ Good — explains non-obvious behavior
let retry_count = 3;  // API may return 429 rate-limit errors

// ❌ Bad — obvious
let total = a + b;  // Add a and b  // UNNECESSARY
```

## 4. Spacing

### Function Definitions

One blank line between function definitions:

```text
fn first_function() {
    return 0
}

fn second_function() {
    return 0
}
```

### Operators

Spaces around binary operators:

```text
// ✅ Correct
let result = math.add(a, b);
let message = "Hello, " + name;

// ❌ Wrong
let result=math.add(a,b);
let message="Hello, "+name;
```

### Braces

Opening brace on the same line as the function declaration or control flow:

```text
// ✅ Correct
fn main() {
    if (condition) {
        // body
    }
}

// ❌ Wrong
fn main()
{
}
```

## 5. Indentation

Use 4 spaces per indentation level. The `ail fmt` tool enforces this automatically.

```text
fn main() {
    if (condition) {
        let x = 10;
        process(x);
    }
    cleanup();
}
```

## 6. Control Flow

### If Statements

```text
// ✅ Correct
if (condition) {
    do_something();
}

if (condition) {
    do_something();
} else {
    do_other();
}

if (condition) {
    do_a();
} else if (other) {
    do_b();
} else {
    do_c();
}
```

### Recursion Pattern

```text
// ✅ Correct
fn traverse(items, index) {
    if (index >= list.len(items)) {
        return 0
    }
    let item = list.get(items, index);
    let current = process(item);
    return math.add(current, traverse(items, index + 1))
}
```

## 7. Expressions

### Parentheses

Use parentheses around conditions:

```text
// ✅ Correct
if (count > 0) {
    process(items);
}

// ❌ Wrong — missing parentheses
if count > 0 {
    process(items);
}
```

### Semicolons

Statements end with semicolons:

```text
// ✅ Correct
let x = 5;
let y = foo();
return x;

// Function declarations do NOT need semicolons
fn main() {
    return 0
}
```

## 8. String Literals

Use double quotes for all strings:

```text
// ✅ Correct
let name = "Alice";
let path = "/usr/local/bin";
let message = "Hello, World!";

// ❌ Wrong — single quotes
let name = 'Alice';
let path = '/usr/local/bin';
```

## 9. Numbers

Use decimal notation for most numbers:

```text
// ✅ Correct
let count = 100;
let price = 9.99;
let negative = -42;

// ❌ Wrong — hex/octal/binary not supported
let count = 0xFF;
let price = 0o77;