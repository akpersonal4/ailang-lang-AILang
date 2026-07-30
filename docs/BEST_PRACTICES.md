# AILang Best Practices

## 1. Project Organization

### Standard Layout

```
my_project/
├── main.ail            # Entry point
├── ail.toml            # Project manifest
├── README.md           # Project documentation
├── LICENSE             # License file
├── src/                # Source modules (optional)
│   ├── module1.ail
│   └── module2.ail
├── tests/              # Test files
│   ├── test_module1.ail
│   └── test_module2.ail
├── data/               # Static data files
│   └── sample.json
└── config/             # Configuration
    └── app.ail
```

### When to Use Flat vs. Directory Structure

- **Small projects (< 5 files)**: Flat structure is simpler
- **Large projects (> 5 files)**: Use `src/` for source code, `tests/` for tests

## 2. Imports

### Always Import at Top Level

```text
// ✅ Correct
import file;
import json;
import math;
import list;

fn main() {
    // ...
}

// ❌ Wrong — import inside function
fn main() {
    import file;  // ERROR: Import not at top level
}
```

### Order Imports Logically

```text
// Stdlib imports first
import file;
import json;
import list;
import math;
import string;
import map;
import time;

// Then project imports
import my_module;
import config;
```

### Only Import What You Use

Unused imports are not errors, but they clutter the file. Remove them for clarity.

## 3. Function Ordering (Bottom-Up)

### The Golden Rule

**Callee before caller.** Define helper functions before the functions that use them.

```text
// ✅ Correct — bottom-up ordering
fn add(a, b) {
    return math.add(a, b)
}

fn calculate_total(items, index) {
    if (index >= list.len(items)) {
        return 0
    }
    let item = list.get(items, index);
    return add(item.price, calculate_total(items, index + 1))
}

fn main() {
    // ...
}

// ❌ Wrong — forward reference
fn main() {          // main() calls calculate_total()
    let result = calculate_total(items, 0);
}

fn calculate_total(items, index) {  // defined AFTER main()
    // ...
}
```

### Level 0 → Level N Pattern

```
Level 0: Pure utility functions
Level 1: Functions that use Level 0
Level 2: Business logic
Level N: main()
```

## 4. Naming Conventions

### Functions

Use `snake_case` for function names:

```text
fn calculate_total() {}
fn parse_csv_file() {}
fn get_user_name() {}
```

### Variables

Use `snake_case` for variable names, descriptive and unique:

```text
let total_amount = 0;
let user_name = "Alice";
let item_count = list.len(items);
```

### Constants

Use `SCREAMING_SNAKE_CASE` for configuration constants:

```text
let MAX_RETRIES = 3;
let DEFAULT_TIMEOUT = 30;
let API_ENDPOINT = "https://api.example.com";
```

### Avoid Generic Names

```text
// ❌ Hard to understand
let x = 5;
let data = json.parse(raw);
let result = list.get(items, i);

// ✅ Self-documenting
let item_count = 5;
let parsed_data = json.parse(raw);
let current_item = list.get(items, index);
```

## 5. Unique Variable Names

**Every variable must have a unique name.** No reuse of `i`, `j`, `x`, `result`, `acc`, `temp` across different functions.

```text
// ✅ Correct — unique names
fn sum_items(items) {
    let sum_result = 0;
    // ...
    return sum_result
}

fn find_max(numbers) {
    let max_found = 0;
    // ...
    return max_found
}

// ❌ Wrong — reused names across functions
fn sum_items(items) {
    let result = 0;  // 'result' also used in find_max()
    // ...
}

fn find_max(numbers) {
    let result = 0;  // collision!
    // ...
}
```

## 6. Error Handling

### Guard Map Access

Always check `map.has()` before `map.get()`:

```text
// ✅ Correct
if (map.has(config, "api_key")) {
    let api_key = map.get(config, "api_key");
}

// ❌ Wrong — may fail
let api_key = map.get(config, "api_key");  // CRASH if key missing
```

### Guard List Access

Always check `list.len()` before `list.get()`:

```text
// ✅ Correct
if (list.len(items) > 0) {
    let first = list.get(items, 0);
}

// ❌ Wrong — may fail
let first = list.get(items, 0);  // CRASH if empty
```

### Handle File Operations

Check `file.exists()` before reading or writing:

```text
// ✅ Correct
if (file.exists("config.json")) {
    let content = file.read("config.json");
}

// ❌ Wrong
let content = file.read("config.json");  // CRASH if missing
```

## 7. Recursion Patterns

### Use Helper Functions for Accumulation

```text
// ✅ Correct — recursive helper
fn sum_all(items) {
    return sum_helper(items, 0)
}

fn sum_helper(items, index) {
    if (index >= list.len(items)) {
        return 0
    }
    let current = list.get(items, index);
    return math.add(current, sum_helper(items, index + 1))
}
```

### Iterate Forward Through Lists

```text
fn process_all(items, index) {
    if (index >= list.len(items)) {
        return
    }
    let item = list.get(items, index);
    process_item(item);
    process_all(items, index + 1)  // Next index
}
```

## 8. String Concatenation

### Use `string.concat()` for Exactly 2 Strings

```text
let full_name = string.concat(first_name, " ");
let full_name = string.concat(full_name, last_name);
```

### Use `+` for 3+ Strings

```text
// ✅ Correct — 4 strings combined
let message = "Hello, " + name + "! You are " + age + " years old.";
```

## 9. Documentation

### Comment Every Function

```text
// Calculate the total price of all items
fn calculate_total(items) {
    // ...
}

// Format a date string for display
fn format_date(timestamp) {
    return time.format(timestamp, "%Y-%m-%d")
}
```

### Use Inline Comments Sparingly

Comments should explain *why*, not *what*. The code should be self-explanatory for *what*.

```text
// ✅ Good — explains why
let retry_count = 3;  // Network calls may fail transiently

// ❌ Redundant — states the obvious
let total = math.add(a, b);  // Add a and b  // OBVIOUS
```

## 10. Testing

### Test File Naming

```
test_<module_name>.ail
```

### Test Function Naming

```
fn test_<behavior>() { }
```

### Test Structure

```text
// tests/test_calculator.ail
import math;

fn test_add_positive_numbers() {
    let result = math.add(2, 3);
    if (result != 5) {
        print("FAIL: expected 5, got " + convert.to_string(result));
    }
}

fn test_add_negative_numbers() {
    let result = math.add(-2, -3);
    if (result != -5) {
        print("FAIL: expected -5, got " + convert.to_string(result));
    }
}

fn main() {
    test_add_positive_numbers();
    test_add_negative_numbers();
    print("ALL PASSED");
    return 0
}
```

## 11. Formatting

### Run `ail fmt` Before Building

```text
ail fmt main.ail
ail check main.ail
ail build main.ail
ail run main.ail
```

This ensures consistent formatting across all files and team members.

## 12. The Development Workflow

Always use the official pipeline:

```text
ail fmt    →  Format code
ail check  →  Check for errors
ail build  →  Compile
ail test   →  Run tests
ail run    →  Execute