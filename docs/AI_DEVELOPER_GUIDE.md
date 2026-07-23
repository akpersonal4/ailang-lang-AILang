# AI Developer Guide

## 1. Introduction

AILang is designed for AI-assisted development. This guide explains how to use AI tools effectively with AILang, including best practices for prompting, deterministic workflows, and common pitfalls to avoid.

## 2. Deterministic Workflows

### The Official Pipeline

Always use this pipeline when generating AILang code with AI:

```text
ail fmt    →  Format code
ail check  →  Check for errors
ail build  →  Compile
ail test   →  Run tests
ail run    →  Execute
```

### Why This Works for AI

1. **`ail fmt`** normalizes formatting so AI models see consistent code structure
2. **`ail check`** catches forward references and ordering violations before compilation
3. **`ail build`** compiles and reports any remaining errors
4. **`ail test`** verifies behavior
5. **`ail run`** executes the program

### Using `--no-check` (Rare)

Only use when testing a specific compile error:

```text
ail run --no-check main.ail
ail test --no-check tests/
```

## 3. Using `ail context`

### Get Machine-Readable Context

```text
ail context --json
```

This outputs JSON with:
- Language rules
- Available stdlib modules
- Diagnostic codes
- Workflow instructions
- Retrieval policy

### Get LLM-Optimized Context

```text
ail context --llm
```

Minimal token usage, maximum signal for AI models.

### Get Compact Context

```text
ail context --compact
```

Even smaller — just the essentials.

### Get Full Context

```text
ail context --full
```

Complete project information including file listing.

## 4. Using `ail doctor`

### Check Environment

```text
ail doctor
```

Verifies:
- AILang installation
- Stdlib availability
- Project structure
- Version consistency

### Repository Health (Contributors)

```text
ail doctor --repo
```

## 5. Using `ail check`

### Validate Before Building

```text
ail check main.ail
```

Detects:
- Forward references (callee defined after caller)
- Missing imports
- Ordering violations

### Machine-Readable Output

```text
ail check --json
```

Outputs JSON with exact error locations and suggestions.

### Check Multiple Files

```text
ail check --recursive .
```

## 6. Using `ail fmt`

### Format Code

```text
ail fmt main.ail
```

### Check Formatting

```text
ail fmt --check main.ail
```

### Show Changes

```text
ail fmt --diff main.ail
```

## 7. Using `ail heal`

### Get Fix Suggestions

```text
ail heal
```

Lists available topics. For specific errors:

```text
ail heal TYP001
ail heal SEM002
```

### Analyze a File

```text
ail heal main.ail
```

## 8. Using `ail explain`

### Understand Error Codes

```text
ail explain TYP001
ail explain SEM002
ail explain MOD004
```

### List All Codes

```text
ail explain
```

## 9. Common AI Mistakes

### Mistake 1: Missing Imports

**Problem:** AI generates code using stdlib functions without importing the module.

```text
// ❌ Wrong — missing import
fn main() {
    let data = json.parse(raw);  // ERROR: json not imported
}
```

**Fix:** Add the import at the top of the file.

```text
// ✅ Correct
import json;

fn main() {
    let data = json.parse(raw);
}
```

**Recommended Prompt:**
> "Add the necessary import statements at the top of the file before using any stdlib functions."

### Mistake 2: Undefined Identifiers

**Problem:** AI uses a variable or function that hasn't been defined.

```text
// ❌ Wrong — undefined identifier
fn main() {
    let total = calculate_total(items);  // ERROR: calculate_total not defined
}
```

**Fix:** Define the function before `main()`.

```text
// ✅ Correct
fn calculate_total(items) {
    return list.sum(items)
}

fn main() {
    let total = calculate_total(items);
}
```

**Recommended Prompt:**
> "Define all helper functions before main(). Use bottom-up ordering: callee before caller."

### Mistake 3: Stdlib Function Misuse

**Problem:** AI uses function names from other languages.

```text
// ❌ Wrong — wrong stdlib function
let length = string.len(text);     // ERROR: string.len doesn't exist
let data = json.load("file.json"); // ERROR: json.load doesn't exist
```

**Fix:** Use the correct AILang function names.

```text
// ✅ Correct
let length = string.length(text);
let data = json.parse("file.json");
```

**Common Mismatches:**

| Wrong (Other Languages) | Correct (AILang) |
|-------------------------|------------------|
| `string.len()` | `string.length()` |
| `json.load()` | `json.parse()` |
| `json.dump()` | `json.stringify()` |
| `print()` | `io.println()` |
| `str()` | `convert.to_string()` |
| `int()` | `convert.to_int()` |
| `len()` | `string.length()` / `list.len()` |
| `file.read()` | `file.read()` (same) |
| `time.sleep()` | `time.sleep()` (same) |

**Recommended Prompt:**
> "Use AILang stdlib function names. Check STDLIB_REFERENCE.md for the correct function names."

### Mistake 4: Forward References

**Problem:** AI defines functions in the wrong order.

```text
// ❌ Wrong — forward reference
fn main() {
    let result = helper();  // ERROR: helper not defined yet
}

fn helper() {
    return 42
}
```

**Fix:** Move `helper()` above `main()`.

```text
// ✅ Correct
fn helper() {
    return 42
}

fn main() {
    let result = helper();
}
```

**Recommended Prompt:**
> "Use bottom-up ordering. Define utility functions first, then business logic, then main() last."

### Mistake 5: Variable Name Collisions

**Problem:** AI reuses the same variable name in different functions.

```text
// ❌ Wrong — 'result' used in both functions
fn calculate_total(items) {
    let result = 0;
    // ...
    return result
}

fn find_max(items) {
    let result = 0;  // collision with calculate_total
    // ...
    return result
}
```

**Fix:** Use unique variable names.

```text
// ✅ Correct
fn calculate_total(items) {
    let total_sum = 0;
    // ...
    return total_sum
}

fn find_max(items) {
    let max_value = 0;
    // ...
    return max_value
}
```

**Recommended Prompt:**
> "Use unique variable names across all functions. No reuse of 'result', 'i', 'x', 'acc', or 'temp'."

### Mistake 6: Missing Guards

**Problem:** AI accesses lists or maps without checking bounds.

```text
// ❌ Wrong — no guard
let first = list.get(items, 0);  // CRASH if empty
let value = map.get(config, "key");  // CRASH if key missing
```

**Fix:** Add guards.

```text
// ✅ Correct
if (list.len(items) > 0) {
    let first = list.get(items, 0);
}

if (map.has(config, "key")) {
    let value = map.get(config, "key");
}
```

**Recommended Prompt:**
> "Always guard list.get() with list.len() check and map.get() with map.has() check."

### Mistake 7: String Concatenation

**Problem:** AI uses `string.concat()` with more than 2 arguments.

```text
// ❌ Wrong — too many args
let message = string.concat("Hello, ", name, "!");  // ERROR
```

**Fix:** Use `+` for 3+ strings.

```text
// ✅ Correct
let message = "Hello, " + name + "!";
```

**Recommended Prompt:**
> "string.concat() takes exactly 2 arguments. Use + for combining 3 or more strings."

### Mistake 8: Nested Functions

**Problem:** AI defines a function inside another function.

```text
// ❌ Wrong — nested function
fn main() {
    fn helper() {  // ERROR: nested functions not allowed
        return 42
    }
    let result = helper();
}
```

**Fix:** Move helper to top level.

```text
// ✅ Correct
fn helper() {
    return 42
}

fn main() {
    let result = helper();
}
```

**Recommended Prompt:**
> "All functions must be at the top level. No nested function definitions."

### Mistake 9: Using Loops

**Problem:** AI uses `for` or `while` loops.

```text
// ❌ Wrong — loops don't exist
for (let i = 0; i < 10; i++) {  // ERROR
    process(i);
}
```

**Fix:** Use recursion.

```text
// ✅ Correct
fn process_range(index) {
    if (index >= 10) {
        return
    }
    process(index);
    process_range(index + 1)
}
```

**Recommended Prompt:**
> "AILang does not have loops. Use recursion with an index parameter instead."

### Mistake 10: Missing `return` Value

**Problem:** AI writes `return;` without a value.

```text
// ❌ Wrong — return without value
fn get_value() {
    return;  // ERROR: return needs a value
}
```

**Fix:** Always return a value.

```text
// ✅ Correct
fn get_value() {
    return 42
}
```

**Recommended Prompt:**
> "Every return statement must have a value. Use 'return expr', never 'return;'."

## 10. Effective Prompting

### Template for Code Generation

```
Generate AILang code that:
1. Uses bottom-up ordering (callee before caller)
2. Has unique variable names across all functions
3. Guards list.get() with list.len() and map.get() with map.has()
4. Uses recursion instead of loops
5. Uses string.concat() for 2 args, + for 3+
6. All functions at top level
7. Every return has a value
8. Imports at top level only

Task: [describe the program]
```

### Template for Error Fixing

```
Fix this AILang error:

Error: [paste error message]

Code:
[paste code]

Rules:
- Callee must be defined before caller
- All functions at top level
- Unique variable names
- Guard all list/map access
```

## 11. AI Tool Integration

### MCP Server

AILang provides an MCP (Model Context Protocol) server for AI tool integration:

```text
ail mcp
```

This exposes compiler capabilities to AI tools via stdio transport.

### Context Retrieval

AI tools can retrieve context using:

```text
ail context --json
ail docs AGENTS
ail docs LANGUAGE_SPEC
ail docs STDLIB_REFERENCE
```

### Error Recovery

When AI-generated code fails:

1. Run `ail check` to get exact error locations
2. Run `ail explain <CODE>` to understand the error
3. Run `ail heal` to get fix suggestions
4. Fix and re-run