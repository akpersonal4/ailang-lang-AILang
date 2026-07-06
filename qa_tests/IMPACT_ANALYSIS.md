# AILang Validation — Impact Analysis

## Executive Summary

The AILang compiler and runtime were validated across 15 test areas with 62+ individual test cases. **7 bugs were discovered**, including 2 high-severity compiler crashes and 2 medium-severity runtime/diagnostic issues. The core language (arithmetic, control flow, list/map operations, string operations) is functionally sound. The main weaknesses are in error diagnostics (cryptic internal errors instead of user-facing messages) and several specified-but-not-implemented features (block scoping, module function references).

---

## Bug Impacts by Stakeholder

### End-User Programmers (Writing AILang Code)

| Bug | Impact on User |
|-----|----------------|
| BUG-001 (empty return crash) | Returning nothing from a function crashes the tool with an internal error. Confusing and unhelpful. |
| BUG-002 (missing init crash) | Typing `let x = ;` crashes the tool. Novice users will encounter this when editing. |
| BUG-003 (module ref) | Cannot store a module function in a variable. All module function references must be call sites. |
| BUG-004 (float literal) | Writing `let x = 3.14` produces "Identifier node missing token" — meaningless. |
| BUG-005 (block shadowing) | Variables declared inside `{ }` blocks leak to outer scope. Hard-to-find bugs. |
| BUG-006 (recursion limit) | Deep recursion fails. No workaround since AILang has no loops. |

### Tool Developers (Maintaining the Compiler)

| Bug | Impact on Maintainer |
|-----|----------------------|
| BUG-001, BUG-002 | Bare `assert` statements mask the real problem. Any AST edge case causes a crash. | 
| BUG-003 | Missing 3-line check in `_resolve_name`. Easy fix. |
| BUG-004 | Root cause is deeper: lexer needs to recognize `.` as invalid in number literals. |
| BUG-005 | Major refactor needed — blocks must create StackFrames. |
| BUG-006 | Platform limitation. Document and move on. |
| BUG-007 | Easy fix: track imports in semantic analyzer. |

### Test Suite (Existing 519 Tests)

None of the 7 bugs affect the existing 519 passing tests — all existing tests operate within the "happy path" and avoid edge cases. This is a **coverage gap** — the test suite was not designed to exercise invalid syntax or boundary conditions.

---

## Business Impact

| Criterion | Impact | Details |
|-----------|--------|---------|
| **Time to fix** | Low | 4 of 7 bugs are <10 line fixes |
| **Backward compatibility** | None | All fixes extend behavior that previously crashed or errored |
| **Developer confidence** | Medium | Crashes on basic syntax errors erode confidence |
| **Spec compliance** | Medium | Spec says block scoping should work (BUG-005), module fns should be referencable (BUG-003) |

---

## Severity Reassessment

| Bug | Assigned | Reassessment | Rationale |
|-----|----------|--------------|-----------|
| BUG-001 | High | High | AssertionError crash on trivial syntax — worst possible UX |
| BUG-002 | High | High | Same as BUG-001 |
| BUG-003 | Medium | Medium | Prevents a documented usage pattern |
| BUG-004 | Medium | Low-Medium | Only affects users who try float literals (explicitly unsupported) |
| BUG-005 | Low | Low | Only affects code that uses block-shadowing (advanced feature) |
| BUG-006 | Low | Low | Platform limitation, well-understood |
| BUG-007 | Low | Low | No functional impact |

---

## Recommended Fix Priority

```
Priority 1 (Immediate — crashes)
├── BUG-001: Replace assert with diagnostic in _build_ReturnStatement
├── BUG-002: Replace assert with diagnostic in _build_VariableDeclaration

Priority 2 (This sprint)
├── BUG-003: Add bare module name lookup in _resolve_name
├── BUG-004: Add lexer-level float literal detection with clear error

Priority 3 (Next sprint)
├── BUG-007: Track imports in semantic analyzer for duplicate detection

Priority 4 (Feature milestone)
├── BUG-005: Implement proper block scoping with new StackFrames
├── BUG-006: Document recursion limit; consider tail-call optimization
```

---

## Effort Estimate

| Bug | Estimated Fix Time | Complexity |
|-----|--------------------|------------|
| BUG-001 | 5 min | Trivial — 1 line change |
| BUG-002 | 5 min | Trivial — 1 line change |
| BUG-003 | 15 min | Simple — add 3 lines to `_resolve_name` |
| BUG-004 | 1-2 hours | Moderate — add lexer error for decimal literals |
| BUG-005 | 4-8 hours | Complex — new StackFrame for each block |
| BUG-006 | 15 min | Documentation only |
| BUG-007 | 30 min | Simple — track imports in set, warn on duplicates |
| **Total** | **~1-2 days** | |

---

## Risk Analysis

### What if these bugs are NOT fixed?

- **High risk (BUG-001, BUG-002)**: Any codebase using `return` without value or making typos in `let` declarations will crash the tool. This makes the compiler seem unstable even for valid-adjacent code.
- **Medium risk (BUG-003)**: Users cannot use module functions as higher-order values. Limits expressiveness.
- **Low risk (BUG-004, BUG-005, BUG-006, BUG-007)**: These affect edge cases or explicitly unsupported syntax.

### What new bugs might fixes introduce?

- BUG-001/BUG-002 fix: Very low risk — just changes crashes to error messages.
- BUG-003 fix: Low risk — adds module lookup before the NameError fallthrough.
- BUG-004 fix: Low risk — reject `.` in number literals at lexer level.
- BUG-005 fix: High risk — changing block semantics could break any code that relies on current (incorrect) behavior.
- BUG-007 fix: Low risk — additive check, no behavioral change.

---

## Conclusion

The AILang compiler is **functionally correct** for common use cases but **fragile at boundary conditions**. The top priority is replacing bare `assert` statements with proper diagnostics (BUG-001, BUG-002) — these are trivial fixes that dramatically improve UX. Fixing BUG-003 and BUG-004 would address the remaining medium-severity gaps. Block scoping (BUG-005) is the most impactful feature gap but requires careful implementation.
