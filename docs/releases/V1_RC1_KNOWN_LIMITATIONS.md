# v1.0.0-RC1 — Known Limitations

**Last updated:** 2026-07-10

This document lists known limitations of AILang v1.0.0-RC1, with severity, impact, and available workarounds.

---

## 1. Language Limitations

### 1.1 No Loops in Stable Language

| Attribute | Value |
|-----------|-------|
| **Severity** | Medium |
| **Impact** | All iteration requires manual recursion, increasing verbosity and cognitive load |
| **Workaround** | Use recursion with accumulator parameters; `for`-in available behind `--experimental-loops` flag |
| **Planned** | Post-1.0 evaluation based on community feedback |

Recursion-only iteration is an intentional design choice for v1.0. The language eliminates `while`/`for` to enforce structural recursion, which makes programs more amenable to static analysis and AI verification. A `for`-in primitive is available experimentally behind `--experimental-loops` and may be promoted to stable in v1.1 if community feedback supports it.

### 1.2 Eager `&&` / `||` Evaluation

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | Both operands of `&&` and `||` always execute. Guard-dependent expressions (e.g., `map.has(map, key) && map.get(map, key)`) will crash if the left operand is false/true respectively |
| **Workaround** | Use nested `if` statements for guard-dependent logic instead of `&&` |
| **Planned** | Not planned — intentional design choice for simplicity |

Example of the workaround:

```
// Instead of:
//   map.has(m, key) && map.get(m, key)  // BUG: map.get runs even if map.has is false

// Use:
if map.has(m, key) {
    let value = map.get(m, key)
    // ...
}
```

### 1.3 No Nested Functions

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | Cannot define functions inside other functions |
| **Workaround** | All functions are top-level; use unique names to avoid collisions |
| **Planned** | Not planned — intentional design choice |

### 1.4 No Forward References

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | A function must be defined before it is called |
| **Workaround** | Order functions bottom-up (callees before callers); use `ail order` to detect violations |
| **Planned** | Not planned — intentional design choice |

### 1.5 Unique Variable Names Required

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | Cannot reuse variable names like `i`, `result`, `acc` across different functions in the same module |
| **Workaround** | Use descriptive unique names (e.g., `sumIndex`, `fileResult`, `customerAcc`) |
| **Planned** | Not planned — intentional design choice for AI-friendly code |

### 1.6 `string.concat` Limited to 2 Arguments

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | `string.concat(a, b, c)` is an error |
| **Workaround** | Use `+` operator for 3+ strings: `a + b + c` |
| **Planned** | Not planned — intentional design choice |

### 1.7 No Multi-line Comments

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | Cannot use `/* */` block comments |
| **Workaround** | Use `//` line comments on each line |
| **Planned** | Not planned — low priority |

---

## 2. Runtime Limitations

### 2.1 Python Recursion Limit (~500 Calls)

| Attribute | Value |
|-----------|-------|
| **Severity** | Medium |
| **Impact** | Recursive functions deeper than ~500 calls raise a `RecursionError` |
| **Workaround** | Refactor into tail-recursive patterns; decompose into multiple functions; reduce recursion depth |
| **Planned** | Post-1.0 — trampolining or stack emulation under evaluation |

The tree-walking interpreter imposes an effective recursion limit of approximately 500 calls due to Python's stack frame overhead (raised from 1000 to 10000 in v0.1.2, but AILang function calls consume ~20 Python frames each).

### 2.2 No Tail-Call Optimization

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | Tail-recursive functions consume stack space proportional to iteration count |
| **Workaround** | Keep recursion depth under 500; decompose long iterations |
| **Planned** | Post-1.0 |

### 2.3 Dynamic Typing at Runtime

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | Type errors (e.g., passing a string to `math.add`) are only caught at runtime, not compile time |
| **Workaround** | Use the static type checker; write tests; review function signatures |
| **Planned** | Gradual typing considered for post-1.0 |

---

## 3. Compiler Limitations

### 3.1 Single-Error-At-A-Time Reporting

| Attribute | Value |
|-----------|-------|
| **Severity** | Medium |
| **Impact** | Compiler reports one error per run; fixing it may reveal more errors — inflates AI iteration counts |
| **Workaround** | None; always run `ail build` after each fix |
| **Planned** | Post-1.0 — requires multi-error IR analysis |

### 3.2 No Incremental Compilation for Single Files

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | Full rebuild every time (typically <300ms) |
| **Workaround** | Use `ail watch` for automatic recompilation on file change |
| **Planned** | Post-1.0 |

### 3.3 Duplicate Import Silently Accepted (BUG-007)

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | `import a; import a` does not produce an error |
| **Workaround** | Avoid duplicate imports |
| **Planned** | Fix before v1.0.0-RC1 final |

### 3.4 `Environment.assign` Creates Bindings Silently

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | Assigning to an undeclared variable creates a new binding instead of reporting an error — masks typos |
| **Workaround** | Ensure all variables are declared with `let` before assignment |
| **Planned** | Post-1.0 — add "variable not declared" diagnostic |

---

## 4. Tooling Limitations

### 4.1 No Package Registry

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | Package manager supports local and Git-based installs only; no public registry |
| **Workaround** | Share packages via Git URLs; use local path references for monorepo packages |
| **Planned** | Post-1.0 — registry at `ailang.dev/packages` under evaluation |

### 4.2 LSP Performance on Large Files

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | Very large files (>2,000 LOC) may cause noticeable latency in the language server |
| **Workaround** | Split large modules into smaller files |
| **Planned** | Post-1.0 — incremental LSP analysis |

---

## 5. Application Limitations

### 5.1 Not Suitable for Algorithmic Workloads

| Attribute | Value |
|-----------|-------|
| **Severity** | Medium |
| **Impact** | Some algorithmic programs (Sudoku solver) time out at 30–60s due to recursion overhead |
| **Workaround** | AILang is designed for CRUD/data-processing, not heavy computation |
| **Planned** | Not planned — out of scope for v1.x |

### 5.2 Verbosity vs Python

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | AILang requires ~36% more LOC than equivalent Python (recursion + unique variable names + explicit guards) |
| **Workaround** | Use `--experimental-loops` for iteration; use descriptive but concise variable names |
| **Planned** | Structural — unlikely to change significantly |

---

## 6. Ecosystem Limitations

### 6.1 No Community Validation

| Attribute | Value |
|-----------|-------|
| **Severity** | Medium |
| **Impact** | No external users have validated the language for real-world workloads |
| **Workaround** | The RC period is explicitly designed to gather community feedback |
| **Planned** | By definition, this is the purpose of the RC |

### 6.2 Single Implementation

| Attribute | Value |
|-----------|-------|
| **Severity** | Low |
| **Impact** | Only one compiler/interpreter implementation (Python tree-walking) |
| **Workaround** | N/A — the reference implementation is the implementation |
| **Planned** | Self-hosting compiler is a post-1.0 goal |

---

## Bug Reference

| # | Bug | Severity | Status | Documented In |
|:-:|-----|:--------:|:------:|:--------------|
| BUG-006 | Python recursion limit (~500 calls) | Low | Open | This doc §2.1 |
| BUG-007 | Duplicate import silently accepted | Low | Open | This doc §3.3 |

---

## Limitation Summary

| Category | Total | Acceptable | Needs Work | Blocking |
|:---------|:-----:|:----------:|:----------:|:--------:|
| Language | 7 | 7 | 0 | 0 |
| Runtime | 3 | 3 | 0 | 0 |
| Compiler | 4 | 4 | 0 | 0 |
| Tooling | 2 | 2 | 0 | 0 |
| Application | 2 | 2 | 0 | 0 |
| Ecosystem | 2 | 2 | 0 | 0 |
| **Total** | **20** | **20** | **0** | **0** |
