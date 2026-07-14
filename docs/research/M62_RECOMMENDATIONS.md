# M62 Recommendations

**Date:** 2026-07-14
**Parent:** [M62 AI Correction Analysis](M62_AI_CORRECTION_ANALYSIS.md)
**Status:** APPROVED

---

## 1. Executive Recommendation

**Implement Fix 1 (Pre-Flight Ordering Check) immediately.** It eliminates 38% of all AILang correction cycles with ~200 lines of code. After this single fix, AILang becomes 30% more efficient than Python in correction cycles.

The remaining fixes (Phase 2+3) are optional enhancements that compound the advantage but are not required to close the correction cycle gap.

---

## 2. Concrete Next Steps

### Step 1: Implement `ail check` (Fix 1)

**Files to modify:**
- `compiler/cli/main.py` — Add `cmd_check()` function
- `compiler/semantic/analyzer.py` — Add `check_forward_references()` method
- `compiler/cli/main.py` — Add `check` to CLI command router

**Implementation spec:**

```python
def cmd_check(args):
    """Check for forward references and ordering violations."""
    file_path = args.file
    root = args.root or os.getcwd()
    
    # Compile and collect errors
    errors = []
    try:
        compile_file(file_path, root=root)
    except CompilationError as e:
        errors = e.errors
    
    # Filter for forward reference errors
    forward_refs = [e for e in errors if e.code == "SEM002"]
    
    if forward_refs:
        print(f"Found {len(forward_refs)} ordering violation(s):")
        for err in forward_refs:
            print(f"  {err.file}:{err.line}:{err.col} — {err.message}")
            # Search imported modules for matching definitions
            for module in imported_modules:
                if err.identifier in module.definitions:
                    print(f"    Suggestion: Move '{err.identifier}' definition before this call")
                    print(f"    Or: Add 'import {module.name};' at top of file")
    else:
        print("No ordering violations found.")
    
    return len(forward_refs) == 0
```

**Test cases:**
1. File with correct ordering → 0 violations
2. File with forward reference → 1 violation with suggestion
3. File with multiple forward references → N violations
4. File with missing import → 1 violation with import suggestion

**Estimated time:** 2-3 hours
**Estimated LOC:** 200

---

### Step 2: Implement `map.from_pairs` (Fix 2)

**Files to modify:**
- `compiler/runtime/builtins.py` — Add `map_from_pairs()` function
- `stdlib/map.ail` — Add wrapper

**Implementation spec:**

```python
def map_from_pairs(pairs_list):
    """Create a map from a list of [key, value] pairs."""
    m = {}
    i = 0
    while i < len(pairs_list):
        pair = pairs_list[i]
        m[pair[0]] = pair[1]
        i += 1
    return m
```

**Test cases:**
1. Empty list → empty map
2. Single pair → single-entry map
3. Multiple pairs → multi-entry map
4. Duplicate keys → last wins

**Estimated time:** 30 minutes
**Estimated LOC:** 40

---

### Step 3: Implement `list.pluck` alias (Fix 5)

**Files to modify:**
- `compiler/runtime/builtins.py` — Add `list_pluck()` as alias for `list_collect_key`
- `stdlib/list.ail` — Add wrapper

**Estimated time:** 10 minutes
**Estimated LOC:** 10

---

### Step 4: Extend `ail test` with ordering check (Fix 3)

**Files to modify:**
- `compiler/cli/main.py` — Add ordering check to `cmd_test()`

**Estimated time:** 1 hour
**Estimated LOC:** 50

---

## 3. Measurement Protocol

After implementing each fix, measure:

1. **Correction cycle count** — Re-run M59 benchmarks (Ticket + Workflow) with the fix active
2. **False positive rate** — Check if `ail check` reports violations that aren't actually problems
3. **Developer satisfaction** — Qualitative feedback on whether the fix reduced friction

### Success Criteria

| Metric | Before | Target |
|--------|:------:|:------:|
| AILang correction cycles (M59) | 8 | ≤ 5 |
| AILang/Python ratio | 1.13× | ≤ 0.7× |
| False positive rate | N/A | ≤ 5% |
| `ail check` runtime | N/A | ≤ 0.5s |

---

## 4. What NOT to Do

| Proposed Fix | Reason to Defer |
|--------------|-----------------|
| Fix 6: `string.concat` variadic | Already handled by `+` operator; no cycles caused by this |
| Loops (ADR-001 permanent) | Would eliminate recursive helper cycles but violates architectural decision |
| Forward references (ADR-004 permanent) | Would eliminate 38% of cycles but violates architectural decision |
| Generic types | Would reduce some type mismatch cycles but violates v1.x scope |

---

## 5. Long-Term Vision

After Phase 1+2 implementation:

1. **AILang correction cycles:** 26 → 11 (58% reduction)
2. **Python correction cycles:** 23 (unchanged)
3. **AILang/Python ratio:** 1.13× → 0.48×
4. **AILang advantage:** 52% fewer cycles than Python

**The narrative flips from:**
> "AILang requires 13% more iterations than Python"

**to:**
> "AILang requires 52% fewer iterations than Python"

This is the strongest possible evidence that AILang's deterministic design, combined with targeted tooling, delivers on the promise of AI-first business software development.

---

## 6. Related Documents

- [M62 AI Correction Analysis](M62_AI_CORRECTION_ANALYSIS.md) — Full analysis
- [M62 Root Cause Table](M62_ROOT_CAUSE_TABLE.md) — Every cycle classified
- [M62 ROI Prioritization](M62_ROI_PRIORITIZATION.md) — Expected reduction per fix
- [P0 Boilerplate Reduction Plan](../roadmap/P0_BOILERPLATE_REDUCTION_PLAN.md) — Measured BRE metrics
- [AILANG_DEVELOPMENT_PLAYBOOK.md](../guides/AILANG_DEVELOPMENT_PLAYBOOK.md) — Forward reference patterns
- [DEPENDENCY_ORDERING_ANALYSIS.md](../architecture/DEPENDENCY_ORDERING_ANALYSIS.md) — Ordering penalty measurements
