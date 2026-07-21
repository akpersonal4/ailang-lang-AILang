# ADR-00X: Bounded Deterministic Iteration

**Date:** 2026-07-14
**Status:** Experimental (behind `--experimental-loops`)
**Supersedes:** ADR-001 and ADR-002 (conditional — only if promoted to stable)
**Relevant ADRs:** ADR-001, ADR-002, ADR-005, ADR-006, ADR-007, ADR-009

---

## 1. Problem Statement

Recursion-only iteration (ADR-001/002) creates friction in AI-assisted development:

| Friction Source | Impact | Evidence |
|----------------|--------|----------|
| Recursive boilerplate | 5-15 LOC per iteration pattern | M65A: 175 helpers, 2,050 LOC |
| Unique variable names | Cognitive load for AI | M62: 38% of AILang cycles |
| Bottom-up ordering | Error-prone for large files | M63: `ail check` detects violations |
| No `break`/`continue` | Verbose early-exit patterns | Manual flag + if-wrapper |

**Research Question:** Can bounded iteration improve AI productivity without reducing compile-time determinism?

---

## 2. Decision

**Experiment with bounded deterministic iteration as syntax sugar over recursion.**

The `for item in collection { body }` construct:

1. Lowers deterministically to a recursive helper function at IR-build time
2. Preserves all existing ADRs (no new IR nodes, no runtime changes)
3. Remains behind `--experimental-loops` until promotion criteria are met
4. Is explicitly **not** a language evolution — it is a compiler transformation

---

## 3. Formal Semantics

### 3.1 Syntax

```
for <variable> in <expression> {
    <body>
}
```

### 3.2 Rules

| # | Rule | Enforcement | Rationale |
|:-:|------|-------------|-----------|
| 1 | **Deterministic iteration order** | Lowering uses `list.get(index)` — indices are ordered 0..N-1 | Same input always produces same output |
| 2 | **Immutable iterator variable** | `let <variable> = list.get(...)` — declared with `let`, cannot reassign | Prevents loop variable mutation |
| 3 | **Loop-local scope** | Variable is declared inside generated function body | No leakage to enclosing scope |
| 4 | **No variable capture (initial)** | Generated function is module-level, cannot access enclosing function's scope | ADR-005 compliance |
| 5 | **No iterator escape** | `return` inside body exits the generated helper, not the enclosing function | Deterministic control flow |
| 6 | **No collection mutation** | The iterated collection is not modified by the loop body (enforced by convention, not compiler) | Prevents iteration-order bugs |
| 7 | **No nested function interaction** | Generated functions are independent; no closure creation | ADR-005 compliance |
| 8 | **No hidden state** | All state is explicit in function parameters and return values | Determinism guarantee |

### 3.3 Capture Semantics (M27 Extension)

After M27, rules 4 is relaxed for **enclosing function variables**:

| Variable Type | Behavior | Mechanism |
|--------------|----------|-----------|
| Read-only | Passed as parameter, threaded through recursion | Value copy on each frame |
| Written (single accumulator) | Parameter + return value capture | Base case returns final value; call site assigns back |
| Written (multiple accumulators) | **Rejected** | ValueError: "Only one accumulator variable allowed" |

**Scope:** The for-loop body **captures by value** all variables from enclosing scopes that it references. If a captured variable is **assigned** inside the body, the final value **replaces** the original after the loop completes.

---

## 4. Lowering Specification

### 4.1 Input

```ail
for item in collection {
    process(item);
}
```

### 4.2 Output

```ail
fn __for_fn_N(__lst_N, __idx_N) {
    if (__idx_N < list.len(__lst_N)) {
        let item = list.get(__lst_N, __idx_N);
        process(item);
        __for_fn_N(__lst_N, __idx_N + 1);
    } else {
        nil;
    }
}
__for_fn_N(collection, 0);
```

### 4.3 With Single Accumulator Capture

```ail
let total = 0;
for item in items {
    total = total + item;
}
```

↓

```ail
fn __for_fn_N(__lst_N, __idx_N, total) {
    if (__idx_N < list.len(__lst_N)) {
        let item = list.get(__lst_N, __idx_N);
        total = total + item;
        __for_fn_N(__lst_N, __idx_N + 1, total);
    } else {
        total;
    }
}
let total = __for_fn_N(items, 0, 0);
```

### 4.4 Lowering Properties

| Property | Guarantee |
|----------|-----------|
| Determinism | Generated code is identical for same input AST |
| No new IR nodes | Uses existing `FunctionIR`, `CallIR`, `IfIR`, `AssignmentIR` |
| No runtime changes | Interpreter unchanged |
| No hidden state | All state in parameters and return values |
| Transparent | Developer can read the generated recursion |

---

## 5. Feature Restrictions

### 5.1 Explicitly Forbidden

| Construct | Reason |
|-----------|--------|
| `break` | Would require new IR node + runtime support |
| `continue` | Would require new IR node + runtime support |
| Labels | No use case without break/continue |
| Iterator mutation | Violates Rule 2 (immutable iterator variable) |
| Collection mutation during iteration | Violates Rule 6 (no collection mutation) |
| Generators | No generator protocol in AILang |
| `yield` | No generator protocol in AILang |
| Closures | Violates ADR-005 (static lexical scoping) |
| Comprehensions | Separate feature, not part of for-in |
| Async iteration | No async model in AILang |

### 5.2 What For-In IS

- **Syntax sugar over recursion** — nothing more
- **Compile-time transformation** — no runtime support needed
- **Deterministic by construction** — lowering produces ordered recursive calls
- **Transparent** — the generated recursion is readable and predictable

### 5.3 What For-In IS NOT

- **Not a loop construct** — it is a macro that expands to recursion
- **Not a language evolution** — it is a compiler transformation
- **Not a replacement for manual recursion** — complex patterns still need manual helpers
- **Not stable** — behind `--experimental-loops` flag until promotion criteria met

---

## 6. Promotion Criteria

### 6.1 Gate Requirements (ALL required)

| Gate | Threshold | Current Status |
|:-----|:----------|:---------------|
| LOC reduction | >= 10% | ⏳ Pending M66 replay |
| Recursive helper reduction | >= 30% | ⏳ Pending M66 replay |
| Correction cycles | 5 → 4 or less | ⏳ Pending AI runs |
| Compile failures | No increase | ✅ PASS (0 regressions) |
| Runtime failures | No increase | ✅ PASS (0 regressions) |
| False positives | No increase | ✅ PASS (0 regressions) |
| Nondeterministic behavior | No increase | ✅ PASS (0 regressions) |
| Compiler guarantees | Identical | ✅ PASS (no new IR nodes) |

### 6.2 Decision Matrix

| Result | Action |
|--------|--------|
| Strong improvement + no regressions | Promote to Stable |
| Moderate improvement + minor concerns | Keep Experimental |
| Weak improvement | Reject |
| Determinism regression | Immediate rejection |

---

## 7. Answer to Final Question

> Is recursion a core value of AILang, or merely an implementation strategy used to achieve determinism?

**Recursion is an implementation strategy.** The core value is **determinism** — same input always produces same output, no hidden state, no unpredictable behavior.

Recursion was chosen because:
1. It eliminates loop complexity (break/continue, variable scoping, iteration order)
2. It forces explicit state management (no loop-carried mutation hidden in body)
3. It is simpler to compile (no loop unrolling, no iterator protocol)

**However**, if a loop construct can be implemented that:
- Preserves deterministic compilation
- Preserves all existing ADRs
- Reduces AI friction measurably
- Remains transparent (syntax sugar over recursion)

...then it is consistent with AILang's core values.

**The for-in loop is not a departure from determinism — it is a deterministic transformation that happens to look like a loop.**

---

## 8. Implementation Status

| Component | Status | Location |
|-----------|:------:|----------|
| Lexer (`FOR` token) | ✅ | `compiler/lexer.py` |
| Parser (`parse_for_statement`) | ✅ | `compiler/parser/statements.py` |
| AST (`ForStatementNode`) | ✅ | `compiler/ast/nodes.py` |
| Semantic analyzer | ✅ | `compiler/semantic/analyzer.py` |
| Type checker | ✅ | `compiler/types/checker.py` |
| IR builder (lowering) | ✅ | `compiler/ir/builder.py` |
| Capture semantics (M27) | ✅ | `compiler/ir/builder.py` |
| CLI flag | ✅ | `compiler/cli/main.py` |
| VS Code grammar | ✅ | `extensions/vscode-ailang/` |
| Tests (16 cases) | ✅ | `tests/test_experimental_loops.py` |

---

## 9. References

| Document | Purpose |
|----------|---------|
| M25/M26 Evaluation | `docs/benchmarks/LOOP_PRIMITIVE_EVALUATION.md` |
| M26 Capture Investigation | `docs/architecture/M26_LOOP_CAPTURE_SEMANTICS.md` |
| M65A Recursion Audit | `docs/research/M65A_RECURSION_AUDIT.md` |
| M65A Stdlib Gap Analysis | `docs/research/M65A_STDLIB_GAP_ANALYSIS.md` |
| M66 Validation Report | `docs/benchmarks/M66_FOR_IN_VALIDATION.md` |
