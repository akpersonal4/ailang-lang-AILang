# AILang vs Python — Engineering Olympics

**Date:** 2026-07-10  
**Status:** 🟡 Specification (not yet executed)  
**Testbed:** Inventory Management System (AILang: 8,515 LOC / Python: 6,258 LOC)  
**Python baseline:** 3.12 + pytest + mypy + ruff + black + VS Code  

---

## 0. Purpose

This is NOT a benchmark to prove AILang superior.

This is a benchmark to **determine objectively** where each language performs better.

The AILang thesis makes specific claims:

1. **Compile-time correctness** catches errors that Python discovers at runtime
2. **Deterministic compilation** makes refactoring/renaming safe
3. **AI-friendly syntax** reduces iteration for AI code generation
4. **No null/coercion bugs** eliminates entire vulnerability classes

These claims need measurement — not assertion.

---

## 0.1 Standardised Measurement Protocol

Every test in this Olympics follows the same measurement rules:

### Environment

| Variable | Value |
|----------|-------|
| Machine | Same physical/virtual machine for all runs |
| OS | Same OS version |
| Editor | VS Code (both languages) |
| Python tools | `pytest` + `mypy --strict` + `ruff check` + `black --check` |
| AILang tools | `ail build` + `ail run` + `ail fmt --check` |
| Warmup | None (cold-start measurement) |
| Repeat | 3× for timing tests, 1× for qualitative tests |
| Recording | Log file + timestamp per step |

### Measured Variables

| Variable | Unit | How |
|----------|------|-----|
| Attempts | count | Number of edit→compile cycles |
| Wall time | seconds | Stopwatch from problem statement to green build |
| Files modified | count | Files touched during the task |
| Regressions | count | Existing tests broken by the change |
| LOC touched | lines | Sum of added + modified + deleted lines |
| Compile cycles | count | Number of `ail build` / `pytest + mypy` invocations |
| Detection time | seconds | Time from bug injection to first failure indication |
| Missed call sites | count | References that should have been updated but were not |

### Qualitative Notes

Each run also captures:

- What was the first error encountered?
- Was the error message helpful?
- Did the tool catch it at compile time or runtime?
- How many cognitive context switches were needed?

---

### 0.2 Task Injection Protocol

Each benchmark defines a **starting state** (a git checkout or clean file state) and an **injection** (code change, feature requirement, bug). The runner:

1. Checks out the starting state
2. Reads the injection specification
3. Starts the stopwatch
4. Performs the task (editing code, running tools, fixing errors)
5. Stops the stopwatch when all tests pass / task is verified complete
6. Records all measured variables

---

## P3 — Feature Addition

**ID:** P3  
**Category:** Feature Addition  
**Measure:** Attempts + time to add a new feature  
**Expected winner:** Slight Python  

### Rationale

AILang's compile-time checks catch errors earlier, but its verbosity (recursion, unique variable names, no closures) makes writing new code slower per line. Python's flexibility allows faster initial writing but with more runtime discovery of errors.

### Starting State

The Inventory system at a clean git state with 38/38 tests passing in both languages.

### Injection

Add **GST (Goods & Services Tax) support** to the invoice system:

```text
1. Add a new module/class `gst_calculator` that:
   - Accepts invoice amount and GST rate (18%, 12%, 5%, 0%)
   - Returns base_amount, tax_amount, total_amount
   - Handles rounding to 2 decimal places

2. Modify invoice creation to:
   - Accept an optional gst_rate parameter
   - Call gst_calculator when gst_rate is provided
   - Store tax breakdown in the invoice record

3. Add 3 test cases:
   - Standard 18% GST on ₹1,000 → tax = ₹180, total = ₹1,180
   - Zero GST → tax = ₹0, total = base amount
   - Rounding: ₹99.99 at 18% → tax = ₹18.00 (rounded up)
```

### AILang Protocol

```text
1. Create gst_calculator.ail
2. Modify invoice.ail
3. Create test_gst.ail
4. Run: ail build main.ail
5. If errors → fix → goto 4
6. Run: ail run main.ail
7. Record: attempts, time, files, regressions
```

### Python Protocol

```text
1. Create gst_calculator.py
2. Modify invoice.py
3. Create test_gst.py
4. Run: ruff check .
5. Run: mypy .
6. Run: pytest tests/
7. If errors → fix → goto 4
8. Record: attempts, time, files, regressions, mypy errors, ruff errors, test failures
```

### Data Collection

```text
P3: Feature Addition (GST Support)
├── Language:
├── Total wall time (s):
├── Compile/check cycles:
├── Files created:
├── Files modified:
├── LOC added:
├── First error (type, message):
├── Errors by tool:
│   ├── Compile-time (AILang) / mypy+ruff (Python):
│   └── Runtime (Python only):
├── Regressions introduced:
└── Qualitative notes:
```

---

## P4 — Bug Fix

**ID:** P4  
**Category:** Bug Fix  
**Measure:** Detection time + fix attempts  
**Expected winner:** Slight AILang  

### Rationale

AILang's compile-time checks should catch bugs faster. Python's runtime discovery means bugs may only surface when the specific code path executes.

### Starting State

A clean checkout of the Inventory system with all 38 tests passing.

### Injections (run separately, randomise order)

| Bug ID | Type | Injection Location | Description |
|:------:|------|--------------------|-------------|
| B1 | Off-by-one | `stock_movement` | Change `<` to `<=` in the stock quantity check guard so it allows one extra unit |
| B2 | Wrong key | `invoice` | Change `"invoice_id"` to `"inv_id"` in a `map.get` call |
| B3 | Missing guard | `customer` | Remove the `map.has` check before `map.get` in `customer_get_by_id` |
| B4 | Wrong comparison | `reorder` | Change `>` to `<` in the reorder threshold comparison |
| B5 | Base case bug | `stock_valuation` | Change the recursive base case to use `1` instead of `0` |

### Bug Injection Protocol

For each bug:

1. Apply the injection (single line change in one file)
2. Start stopwatch
3. Run the detection tool:
   - AILang: `ail build main.ail` (compile catches structural errors)
   - Python: `pytest tests/ -x` (test catches logic errors) + `mypy .` (type catches signature errors)
4. If no error detected → mark "undetected"
5. If error detected → measure detection time
6. Fix the bug
7. Run full test suite to confirm no regressions
8. Record

### Data Collection

```text
P4: Bug Fix
├── Bug ID:
├── Language:
├── Detection time (s):
├── Detection method (compile/runtime/test):
├── Fix attempts:
├── Fix time (s):
├── Helpfulness of error message (1-5):
├── Regressions from fix:
└── Qualitative notes:
```

---

## P5 — Repository Rename

**ID:** P5  
**Category:** Refactoring / Rename  
**Measure:** Files touched + missed references + runtime failures  
**Expected winner:** AILang (via `ail rename`)  

### Rationale

AILang's `ail rename` tool scans the entire repository for symbol references. Python relies on VS Code's rename refactoring (which is heuristic-based) or manual search-and-replace. AILang's compiler then validates the rename at compile time.

### Starting State

Clean checkout of the Inventory system.

### Injection

```text
Rename all occurrences of:
    supplier
to:
    vendor_partner

Scope: All source files in the project.
```

### AILang Protocol

```text
1. Run: ail rename supplier vendor_partner
2. Run: ail build main.ail
3. If build errors → fix (check if rename missed references)
4. Run: ail run main.ail
5. Run: ail run tests/runner.py
6. Record files touched, missed references, build cycles
```

### Python Protocol

```text
1. VS Code: Edit → Find & Replace → supplier → vendor_partner (Match Whole Word)
2. Run: ruff check .
3. Run: mypy .
4. Run: pytest tests/
5. If test failures or type errors → manually fix
6. If fixes made → goto 2
7. Record files touched, missed references, fix cycles, test failures
```

### Data Collection

```text
P5: Repository Rename (supplier → vendor_partner)
├── Language:
├── Total wall time (s):
├── Files automatically updated:
├── Files missed (manual fix needed):
├── Missed references (caused runtime failures):
├── Compile/check cycles:
├── Test regressions:
├── Tool used (ail rename / VS Code find-replace):
└── Qualitative notes:
```

---

## P6 — API Upgrade

**ID:** P6  
**Category:** API Upgrade  
**Measure:** Broken call sites detected + time to green build  
**Expected winner:** AILang  

### Rationale

AILang's compiler catches every call site that doesn't match the new signature. Python's mypy catches some, but dynamic call patterns (kwargs, `*args`, duck typing) can mask mismatches.

### Starting State

Clean checkout of the Inventory system.

### Injection

```text
Change the order creation function signature:

  create_order(customer_id, items)
  →
  create_order(customer_id, items, warehouse_id, priority)

Where:
  - warehouse_id: string (default: "main")
  - priority: string ("standard", "express", "rush")
```

### AILang Protocol

```text
1. Modify the function signature in order_sales_order.ail
2. Run: ail build main.ail
3. Note all compile errors (these are broken call sites)
4. Fix each call site with appropriate arguments
5. Run: ail build main.ail
6. If errors remain → goto 4
7. Run tests
8. Record
```

### Python Protocol

```text
1. Modify the function signature in order_sales_order.py
2. Run: mypy .
3. Note all type errors
4. Fix each call site
5. Run: mypy .
6. Run: pytest tests/
7. If errors remain → goto 4
8. Record: detected by mypy, missed by mypy, caught by tests, undetected
```

### Data Collection

```text
P6: API Upgrade (create_order signature change)
├── Language:
├── Total wall time (s):
├── Total call sites:
├── Detected by tool (compile/mypy):
├── Missed by tool (caught by tests):
├── Undetected (runtime failure in production):
├── Compile/check cycles:
├── Test regressions:
└── Qualitative notes:
```

---

## P7 — Maintenance Sprint

**ID:** P7  
**Category:** Maintenance Sprint  
**Measure:** Total prompts + compile cycles + regressions  
**Expected winner:** AILang  

### Rationale

This is the most important single benchmark. It simulates a real maintenance session with a mix of feature additions, bug fixes, and refactoring tasks. AILang's compile-time safety should reduce total iterations. Python's faster edit-run loop may compensate.

### Starting State

Clean checkout of the Inventory system.

### Session (20 changes — 10 features + 5 bugs + 5 refactors)

#### Features (10)

| # | Task | File(s) |
|:-:|------|---------|
| F1 | Add `discount_rate` field to customer records | customer |
| F2 | Add "pending" status to order workflow | order_sales_order |
| F3 | Add `warehouse_transfer` notification type | notification |
| F4 | Add `batch_number` field to stock movements | stock_movement |
| F5 | Add `currency_conversion` to invoice totals | invoice, currency |
| F6 | Add `min_stock_level` alert to dashboard | dashboard |
| F7 | Add `supplier_rating` field to supplier records | supplier |
| F8 | Add `export_pdf` stub to export module | export |
| F9 | Add `audit_category` filter to audit trail | audit |
| F10 | Add `seasonal_discount` to pricing | product, price_history |

#### Bugs (5)

| # | Bug | Location |
|:-:|-----|----------|
| B1 | Wrong comparison operator in stock check | stock_movement |
| B2 | Missing `map.has` guard in customer lookup | customer |
| B3 | Off-by-one in pagination | pagination |
| B4 | Incorrect accumulator initialisation in stock valuation | stock_valuation |
| B5 | Wrong key name in invoice tax calculation | invoice |

#### Refactors (5)

| # | Task | Description |
|:-:|------|-------------|
| R1 | Rename `qty` → `quantity` | All files |
| R2 | Extract `calculate_discount` helper | invoice |
| R3 | Move `validate_email` to helpers module | customer |
| R4 | Rename `create_shipment` → `dispatch_shipment` | shipping |
| R5 | Extract `format_currency` from multiple locations | currency, invoice, report |

### Execution Protocol

```text
1. Randomise the order of the 20 tasks (pre-generated list)
2. For each task:
   a. Read task specification
   b. Implement + build/test
   c. If failure → fix → goto b
   d. Record attempts, time, regressions
3. After all 20 tasks:
   a. Run full test suite
   b. Record total regressions
```

### Data Collection

```text
P7: Maintenance Sprint
├── Language:
├── Total wall time (s):
├── Total compile/check cycles:
├── Total prompts read:
│
├── Features (10):
│   ├── Total attempts:
│   ├── Total time:
│   └── Regressions from features:
│
├── Bugs (5):
│   ├── Total detection time:
│   ├── Total fix attempts:
│   └── Regressions from fixes:
│
├── Refactors (5):
│   ├── Total files touched:
│   ├── Total missed references:
│   └── Regressions from refactors:
│
├── Overall regressions at end:
├── Errors caught at compile time (AILang) / mypy+ruff (Python):
├── Errors discovered at runtime (Python only):
└── Qualitative notes:
```

---

## P8 — Security Hardening

**ID:** P8  
**Category:** Security  
**Measure:** Vulnerabilities detected at compile time  
**Expected winner:** AILang  

### Rationale

AILang eliminates entire vulnerability classes by construction:
- No null references (all `let` declarations have initialisers)
- No type confusion (static type checking)
- No implicit coercion (no `==` between types)
- No dynamic execution (no `eval`)
- Safe map access enforced (`map.has` before `map.get`)

Python with full tooling (mypy + ruff) catches some of these, but runtime-only vulnerabilities slip through.

### Starting State

A purpose-built small application (not the full Inventory) containing known vulnerability patterns, written identically in both languages.

**Note:** Using the full Inventory system would mean injecting vulnerabilities into clean code. Instead, we create a small (100–200 LOC) program in each language that demonstrates vulnerable patterns, and measure which tools detect them.

### Vulnerabilities Tested

| # | Vulnerability | AILang Detection | Python Detection |
|:-:|---------------|:----------------:|:----------------:|
| V1 | Null dereference | ✅ Compile: `let` requires initialiser | ⚠️ mypy: `Optional` type catches some |
| V2 | Missing existence check | ✅ Compile: `map.has` before `map.get` | ❌ Runtime only |
| V3 | Type confusion | ✅ Compile: static type checking | ⚠️ mypy: catches some |
| V4 | Implicit coercion | ✅ Compile: no implicit conversion | ❌ Runtime (Python) |
| V5 | Division by zero | ❌ Runtime (same as Python) | ❌ Runtime |
| V6 | List index out of bounds | ⚠️ `list.get` catches at runtime | ❌ Runtime exception |
| V7 | Unvalidated input used in file path | ❌ Not detected (same as Python) | ❌ Not detected |
| V8 | SQL injection (if SQL existed) | ❌ Not applicable (no SQL in AILang) | ❌ Runtime |
| V9 | Infinite recursion | ❌ Runtime (same as Python) | ❌ Runtime |
| V10 | Variable shadowing confusion | ✅ Compile: unique variable names required | ❌ No detection |

### Test Program

A 150-LOC program in each language that intentionally includes patterns V1–V10. Each vulnerability is in a separate function so detection can be measured independently.

### Protocol

```text
1. Write the test program with all 10 vulnerable patterns
2. For AILang:
   a. Run: ail build
   b. For each V1–V10 that produces a compile error → mark "Detected at compile"
   c. Run: ail run
   d. For each remaining V that crashes at runtime → mark "Detected at runtime"
   e. For each remaining V that runs silently → mark "Undetected"
3. For Python:
   a. Run: ruff check .
   b. Run: mypy .
   c. Run: pytest (if any test cases)
   d. Run: python main.py
   e. Same detection categorisation as AILang
```

### Data Collection

```text
P8: Security Hardening
├── Vulnerability Table:
│   ├── V1 (Null dereference): AILang=[Compile|Runtime|Undetected], Python=[Compile|mypy|Runtime|Undetected]
│   ├── V2 (Missing guard): ...
│   └── V10 (Shadowing): ...
│
├── Total detected at compile time:
│   ├── AILang: N/10
│   └── Python (mypy+ruff): N/10
│
├── Total undetected:
│   ├── AILang: N/10
│   └── Python: N/10
│
└── Qualitative notes:
    - Which errors had clear messages?
    - Which vulnerabilities required runtime to surface?
```

---

## Execution Order

The 6 tests should be run in this order:

```text
1. P8  (Security)     — Synthetic program, no dependency on Inventory
2. P4  (Bug Fix)      — 5 independent injections, can be parallelised
3. P5  (Rename)       — Single transformation, quickest to execute
4. P6  (API Upgrade)  — Single signature change, moderate duration
5. P3  (Feature)      — New module + modifications, longer duration
6. P7  (Sprint)       — 20 tasks, longest duration (likely 2–4 hours)
```

---

## Expected Results Summary

| Test | Expected Winner | Confidence | Rationale |
|:-----|:--------------:|:----------:|-----------|
| P3 Feature Addition | Slight Python | Medium | Python writes faster; AILang compiles safer. Net ~1.2× Python |
| P4 Bug Fix | Slight AILang | Medium | Compile-time detection saves debug loops. Net ~0.8× AILang |
| P5 Rename | AILang | High | `ail rename` + compile validation vs VS Code heuristics |
| P6 API Upgrade | AILang | High | Compiler catches every call site; mypy misses dynamic patterns |
| P7 Maintenance Sprint | AILang | Medium | Mixed tasks favour compile-time safety. Net ~0.7× AILang |
| P8 Security | AILang | High | 6/10 detected at compile vs ~2/10 for Python |

### Overall Scorecard

```text
Category              Expected   Actual (TBD)
─────────────────────────────────────────────
P3 Feature Addition   Python
P4 Bug Fix            AILang
P5 Rename             AILang
P6 API Upgrade        AILang
P7 Maintenance        AILang
P8 Security           AILang
─────────────────────────────────────────────
AILang wins:          Planned 5/6
Python wins:          Planned 1/6
```

---

## Future Tests (P1, P2, P9–P12)

| ID | Test | When | Dependencies |
|:---|------|:----:|-------------|
| P1 | Greenfield Build | Post-RC | Requires new application spec (Order Management) |
| P2 | Validation Speed | Post-RC | Requires large repo setup |
| P9 | Regression Resistance | Post-RC | Requires P3–P8 execution first (data on regression rates) |
| P10 | Scalability | Post-RC | Requires synthetic 25k LOC generator |
| P11 | AI Efficiency | Post-RC | Requires B1 framework + provider keys |
| P12 | Human Readability | Post-RC | Requires independent human evaluation panel |

---

## Appendix: Tools & Versions

### AILang

| Tool | Version | Command |
|------|---------|---------|
| Compiler | v0.9.0 | `ail build <file>` |
| Runtime | v0.9.0 | `ail run <file>` |
| Formatter | v0.9.0 | `ail fmt` |
| Rename | v0.9.0 | `ail rename <old> <new>` |
| Test runner | v0.9.0 | `ail run tests/runner.py` |

### Python

| Tool | Version | Command |
|------|---------|---------|
| Interpreter | 3.12 | `python <file>` |
| Type checker | mypy 1.x | `mypy --strict .` |
| Linter | ruff | `ruff check .` |
| Formatter | black | `black --check .` |
| Test runner | pytest | `pytest tests/ -v` |
| IDE | VS Code | Python extension + Pylance |

---

## Appendix: Data Collection Templates

A single JSON template for recording each test run:

```json
{
  "olympics_version": "1.0",
  "date": "2026-07-10",
  "runner": "",
  "machine": "",
  "os": "",
  "language": "AILang | Python",
  "test_id": "P3 | P4 | P5 | P6 | P7 | P8",
  "test_name": "",
  "results": {
    "total_wall_time_s": 0.0,
    "compile_cycles": 0,
    "files_created": 0,
    "files_modified": 0,
    "loc_touched": 0,
    "test_regressions": 0,
    "compile_time_errors": 0,
    "runtime_errors": 0,
    "undetected_errors": 0,
    "error_messages_helpful": true,
    "attempts": 0
  },
  "qualitative_notes": ""
}
```

---

## Appendix: Session Log Template

For manual execution, a markdown log per test:

```text
# P{N} — {Name} — {Language}

## Setup
- Started at: {time}
- Git commit: {hash}
- Tests passing at start: {N}/{N}

## Execution Log

| Step | Time | Action | Result |
|------|------|--------|--------|
| 1 | +0:00 | {action} | {result} |
| 2 | +0:30 | {action} | {result} |

## Final State
- Ended at: {time}
- Total duration: {minutes}
- Tests passing at end: {N}/{N}
- Regressions: {N}

## Notes
{qualitative observations}
```

---

## License

This benchmark methodology is open for anyone to reproduce. The goal is objective
measurement, not marketing. If you find a flaw in the methodology, please report it.
