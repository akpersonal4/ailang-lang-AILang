# Inventory Benchmark Harness — B2–B6 Specification

**Date:** 2026-07-08
**Framework:** `benchmarks/framework/` (existing)
**Subject:** Inventory Management System (8,515 LOC AILang / 6,258 LOC Python)
**Status:** Executable — dataset fixtures at `benchmarks/datasets/b{2,3,4,5,6}_inventory/` and runner at `benchmarks/inventory/runner.py`

---

## 1. Purpose

The INVENTORY_SCALABILITY_BENCHMARK and INVENTORY_PYTHON_COMPARISON established **what is empirically measurable** (compile time, test runtime, LOC density, error-discovery speed). The remaining unanswered questions require **controlled AI model queries**:

| Question | Benchmark | Measured In |
|----------|-----------|-------------|
| How many AI iterations to implement a feature? | **B2 Feature Implementation** | This document |
| Which ecosystem suffers more from refactoring? | **B4 Refactoring** | This document |
| Which system localizes failures better? | **B3 Bug Fix** | This document |
| After 50 changes, what happens to each system? | **B6 Long-Term Maintenance** | This document |

This document defines the exact protocol so that **anyone can reproduce the results** with any supported AI provider.

---

## 2. General Protocol

### 2.1 AI Models

Every benchmark must be run with a minimum of **3 models**, one from each tier:

| Tier | Provider | Model | Why |
|:----:|----------|-------|-----|
| **1** | Anthropic | `claude-sonnet-4-20250514` | Best-in-class code generation |
| **2** | OpenAI | `gpt-4o-2025-05-13` | Strong general-purpose coding |
| **3** | Open-weight | `deepseek-coder-v2` or `llama-4-70b` | Representative of open models |

**Configuration:** Use the existing `benchmarks/providers/` framework. Set via environment variables:
```
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=...
```

**Temperature:** `0.0` for all benchmarks (deterministic output).
**System prompt:** None (empty). All context in user message.

### 2.2 Prompt Template

Every prompt follows this structure:

```
You are implementing a feature in {LANGUAGE}.
{SOURCE_CONTEXT}

TASK:
{task_description}

CONSTRAINTS:
{language_constraints}

EVALUATION:
{evaluation_criteria}
```

### 2.3 Stopping Conditions

A single trial stops when **any** of these conditions is met:

| Condition | Rule |
|-----------|------|
| **Compile success** (AILang) | `ail build` exits 0 with zero errors |
| **Syntax success** (Python) | `python -c "import ast; ast.parse(open(file).read())"` succeeds |
| **Test pass** | `python tests/runner.py` (or AILang equivalent) exits 0 |
| **Max iterations** | 10 attempts per trial |
| **Max tokens** | 100,000 total prompt + completion tokens consumed |
| **Timeout** | 30 minutes wall-clock per trial |

If max iterations is reached, record as **FAILED** and note the failure mode.

### 2.4 Measurement Rules

Every trial records these metrics:

```
{
  "benchmark_id": "B2-L1",
  "language": "ailang|python",
  "model": "claude-sonnet-4-20250514",
  "temperature": 0.0,

  "iterations": 3,
  "compile_attempts": 2,
  "runtime_attempts": 1,
  "first_compile_pass": true|false,
  "first_test_pass": true|false,

  "prompt_tokens": 4523,
  "completion_tokens": 1241,
  "total_tokens": 5764,

  "wall_clock_seconds": 127.3,
  "files_modified": 2,
  "loc_added": 15,
  "loc_deleted": 3,

  "error_types": ["forward_ref", "map_key"],
  "error_count": 2,
  "ai_regressions": 0,

  "final_status": "PASS|FAIL|PARTIAL"
}
```

### 2.5 Repeatability

Each (benchmark, language, model) combination must be run **3 times** on different days to account for model nondeterminism despite temperature=0. Report median, min, max for each metric.

---

## 3. B2 — Feature Implementation Benchmark

**Question:** How many AI iterations does it take to implement a new feature in AILang vs Python?

### 3.1 Task Definitions

All tasks target the **running inventory system** — the AI must add a feature to the existing codebase, not write from scratch.

#### B2-T1: Low Complexity — Stock Alert Threshold

**Difficulty:** 1 function, ≤20 LOC (AILang) / ≤10 LOC (Python)
**Goal:** Add a `movement_check_alert_threshold` function to `stock_movement`.

**Prompt (AILang version):**
```
You are implementing a feature in AILang.

The existing inventory system lives in apps/inventory/.
Here is the stock_movement module:

<module name="stock_movement.ail">
{content of stock_movement.ail}
</module>

TASK:
Add a function called `movement_check_alert_threshold` that:

1. Takes a product_id and a threshold (integer).
2. Uses `movement_get_quantity_on_hand` to get current QOH.
3. If QOH < threshold, returns a map with keys:
   - "product_id": the product_id
   - "current_qoh": the QOH value
   - "threshold": the threshold
   - "alert": true
4. If QOH >= threshold, returns a map with:
   - "product_id": the product_id
   - "alert": false
5. If the product has no movements, return false.

CONSTRAINTS:
- No loops (recursion only)
- No nested functions
- All functions at top level
- `let` requires an initializer: `let x = value`
- `return` requires a value: `return expr`
- Use `helpers_get_map_value_safe` instead of `map.get`
- Use `string.concat` with max 2 args (use + for 3+)
- No forward references (callee must appear before caller)
- Unique variable names throughout (no reuse of i, x, result)

EVALUATION:
The function must:
1. Compile with `ail build stock_movement.ail`
2. Return correct alert when QOH < threshold
3. Return non-alert when QOH >= threshold
4. Return false for unknown product
```

**Modifications for Python version:**
- Language: Python
- File: `apps/inventory_py/inventory/stock_movement.py`
- Remove recursion constraint, use `def` syntax, standard Python
- Constraints: standard Python 3.12
- Evaluation: `python -c "from inventory.stock_movement import ..."`

#### B2-T2: Medium Complexity — Product Deactivation Cascade

**Difficulty:** 3-5 functions, ≤100 LOC (AILang) / ≤60 LOC (Python)
**Goal:** When a product is deactivated, automatically cancel all pending POs, reservations, and movements.

#### B2-T3: High Complexity — Multi-Warehouse Transfer with Approval

**Difficulty:** Multiple files, ≤300 LOC (AILang) / ≤200 LOC (Python)
**Goal:** Add an approval step to the warehouse transfer workflow: manager must approve transfers > 100 units.

### 3.2 Pass/Fail Criteria

| Level | Criteria |
|-------|----------|
| **T1** | Compiles + test passes for alert above/below threshold + unknown product |
| **T2** | Compiles + all cascade scenarios verified (3 test cases) |
| **T3** | Compiles + full workflow test: create → approve → execute → verify stock |

### 3.3 Success Criteria

- AILang requires **fewer iterations** to first compile than Python requires to first syntax-check-free run
- AILang requires **≤80%** of Python's total token consumption to reach correct implementation

---

## 4. B3 — Bug Fix Benchmark

**Question:** Which system localizes failures better when bugs are introduced?

### 4.1 Bug Definitions

Five bugs are introduced into the **existing, working** inventory system. The AI is given the buggy code and the error output, and asked to fix it.

#### B3-B1: Off-by-one in recursive list traversal

**File:** `stock_movement` (AILang) / `inventory/stock_movement.py` (Python)
**Bug:** A recursive helper uses `>` instead of `>=` in the base case, skipping the last element.
**Detection:** `movement_list_by_product` returns N-1 items instead of N.
**Prompt addition:** "The list_by_product function returns 3 items but there are 4 movements for this product."

#### B3-B2: Wrong map key

**File:** `purchase_order` (AILang) / `orders/purchase_order.py` (Python)
**Bug:** `purchase_create` sets `"vendor_id"` but `purchase_get` looks for `"vendorId"`.
**Detection:** `purchase_get` returns items with missing vendor information.
**Prompt addition:** "The vendor field is empty in returned purchase orders."

#### B3-B3: Missing guard (no map.has before map.get)

**File:** `stock_valuation` (AILang only — doesn't apply to Python)
**Bug:** `valuation_get` calls `map.get` without checking `map.has` first.
**Detection:** Runtime error "map key not found" when product valuations exist.
**Note:** This bug cannot occur in Python (dict access uses brackets/default).

#### B3-B4: Wrong comparison operator

**File:** `reorder` (AILang) / `business/reorder.py` (Python)
**Bug:** `reorder_check` uses `<` instead of `<=` — triggers reorder when QOH equals threshold.
**Detection:** Reorder triggers when QOH exactly equals reorder point.

#### B3-B5: Infinite recursion (missing base case)

**File:** `helpers` (AILang) / `core/helpers.py` (Python)
**Bug:** A recursive helper function has the base case commented out.
**Detection:** Stack overflow / max recursion depth exceeded.
**Note:** AILang detects this as a runtime stack error; Python hits `RecursionError`.

### 4.2 Error Presentation

The AI receives exactly:

```
SOURCE CODE:
{buggy source code — entire file}

ERROR:
{exact error message from the compiler or runtime}

EXPECTED BEHAVIOR:
{one-sentence description of correct behavior}
```

### 4.3 Pass/Fail Criteria

| Metric | Criteria |
|--------|----------|
| **First-fix compile** | Does the first attempt compile? (AILang) or syntax-parse? (Python) |
| **First-fix test pass** | Does the first attempt pass the full test suite? |
| **Iterations to correct** | How many fix attempts until all tests pass? |
| **Error count** | How many different errors does the fix introduce? |

### 4.4 Success Criteria

- AILang **first-fix compile rate ≥ 80%** (4 of 5 bugs fixed in first attempt)
- AILang requires **fewer fix iterations** than Python (mean across all 5 bugs)
- AILang has **zero runtime regressions** after fix (compiler catches cascading errors)

---

## 5. B4 — Refactoring Benchmark

**Question:** When renaming `supplier` → `vendor_partner` across the codebase, which ecosystem suffers more?

### 5.1 Refactoring Task: Rename Entity

**Scope:** Rename the `supplier` entity to `vendor_partner` across the entire codebase.

**Files affected (AILang):**
- `supplier.ail` — module file (rename to `vendor_partner.ail`)
- All 38 test files that `import supplier` or call `supplier.*` functions
- All 46 app modules that reference `supplier_*` functions

**Files affected (Python):**
- `models/supplier.py` (rename to `models/vendor_partner.py`)
- `models/__init__.py` (update import)
- All test files that import or call supplier functions
- All app modules that reference supplier functions

**Prompt (identical structure for both languages):**

```
TASK:
Rename the entity "supplier" to "vendor_partner" across the entire codebase.

RULES:
1. Rename the file {file_path_supplier} to {file_path_vendor_partner}.
2. Update all import statements that reference "supplier".
3. Update all function calls that start with "supplier_".
4. Update all internal variable names and map keys that use "supplier".
5. Do NOT change any behavior or logic.
6. Do NOT rename unrelated entities (e.g., do not touch "supply_chain", "supplier_id" in unrelated contexts).

{full source code of all files}

EVALUATION:
After the rename:
1. {LANGUAGE} must compile/build without errors.
2. All 38 tests must pass.
3. No references to "supplier" as a module/entity name should remain (case-sensitive).
```

### 5.2 Measurement

| Metric | How to measure |
|--------|----------------|
| **Files modified** | Count files changed by the AI |
| **LOC changed** | Total added + deleted |
| **Compile errors after first attempt** | Count of build errors |
| **Test regressions** | Count of tests that fail after first attempt |
| **Iterations to correct** | Attempts until all tests pass |
| **Missed references** | Grep for remaining "supplier" references after "done" |
| **Overt renaming** | Count of incorrectly renamed unrelated terms |

### 5.3 Success Criteria

- AILang introduces **fewer test regressions** than Python (mean over 3 trials)
- AILang has **zero compile errors** after refactoring (structural guarantee — if it compiles, all references are consistent)
- AILang requires **≤3 iterations** to complete the rename correctly

---

## 6. B5 — Upgrade Benchmark

**Question:** When a stdlib function changes signature, how does each ecosystem cope?

### 6.1 Upgrade Scenarios

#### B5-S1: Function signature change

**Scenario:** A core helper function `helpers_generate_id(prefix)` adds a second parameter `length` with a default of 8.

**Simulate by:**
1. AILang: Modify `stdlib/map.ail` or `helpers.ail` to add the parameter
2. Python: Modify `core/helpers.py` to add the parameter

**Prompt:**
```
TASK:
Update the entire codebase to work with the new signature of `helpers_generate_id`.

Old signature: helpers_generate_id(prefix)
New signature: helpers_generate_id(prefix, length) where length defaults to 8.

RULES:
1. Update all call sites that explicitly pass the old signature.
2. Do not break existing behavior — calls without the new param must still work.
3. If AILang: no default parameters exist, so all call sites must be updated.
```

#### B5-S2: Deprecation

**Scenario:** `storage_add` is deprecated in favor of `storage_insert`. Old name still works but produces a warning.

**Prompt:**
```
TASK:
Migrate all call sites from `storage_add` to `storage_insert`.

RULES:
1. Replace every call to `storage_add` with `storage_insert`.
2. Keep `storage_add` defined as an alias.
3. Do not change behavior.
```

### 6.2 Measurement

| Metric | How |
|--------|-----|
| **Files changed** | git diff --stat |
| **Call sites updated** | Grep count before/after |
| **Missed sites** | Grep for old function name after "done" |
| **Compile errors** | Build output |
| **Iterations** | Until zero errors |

### 6.3 Success Criteria

- AILang upgrades involve **fewer files changed** than Python equivalents
- AILang requires **fewer iterations** to resolve compile errors
- **No broken builds** after AILang upgrade (all tests pass on first compile success)

---

## 7. B6 — Long-Term Maintenance Benchmark

**Question:** After 50 incremental changes, which system has accumulated less technical debt?

### 7.1 Maintenance Cycle

Simulate a 6-month maintenance cycle across the inventory system. Each cycle = 1 change.

| Phase | Cycles | Activity | Examples |
|-------|--------|----------|----------|
| **Month 1–2** | 15 | Add features | New report, dashboard widget, export format |
| **Month 3–4** | 20 | Fix bugs | Edge cases, error handling, input validation |
| **Month 5** | 10 | Refactor | Rename 3 entities, extract 2 modules |
| **Month 6** | 5 | Upgrade | Change 2 function signatures |

**Total: 50 changes.**

### 7.2 Change Catalog

Each change is a structured task from a catalog. Example entries:

```
CHANGE-001 (Feature): Add a CSV export for the monthly sales report.
  Prompt: "Add a function sales_export_csv that..."
  Files affected: report.ail, main.ail
  Expected LOC: 15-25 (AILang) / 10-15 (Python)

CHANGE-016 (Bug): "product_search" returns duplicate results when name contains special characters.
  Prompt: "Fix the duplicate result bug in product_search..."

CHANGE-031 (Refactor): Rename "warehouse" to "storage_location" across the codebase.
  Prompt: "Rename the warehouse entity to storage_location..."

CHANGE-046 (Upgrade): `movement_create` now requires a `reference_type` parameter.
  Prompt: "Update all call sites of movement_create to include the new parameter..."
```

### 7.3 Measurement Rules

After **every 10th change**, run the full test suite and record:

| Metric | How |
|--------|-----|
| **Test pass count** | `tests/runner.py` exit code |
| **Test regression count** | Tests passing before - tests passing after |
| **Compile errors** | `ail build` errors (AILang) |
| **Cumulative LOC** | Total source lines |
| **Cumulative function count** | Total function definitions |
| **Compile time** | Build time in seconds |
| **Test run time** | Suite time in seconds |
| **Orphaned code** | Functions never called (static analysis) |

### 7.4 Stopping Conditions

| Condition | Action |
|-----------|--------|
| **Any change fails to compile after 3 attempts** | Record as FAILED, continue to next change |
| **Test regression persists >5 changes** | Record as BROKEN, halt |
| **Cumulative compile time >5s** | Record as SLOW, continue |
| **Total token consumption >1M** | Record as EXPENSIVE, continue |
| **All 50 changes complete** | Record as COMPLETE |

### 7.5 Success Criteria

| Metric | Target |
|--------|--------|
| Cumulative AILang iterations | **≤ 60%** of Python |
| Cumulative AILang test regressions | **≤ 50%** of Python |
| AILang code compiles after every operation | **100%** (no broken intermediate states) |
| AILang compile time after 50 changes | **< 2×** baseline compile time |
| AILang LOC growth rate | **< Python** LOC growth rate (denser fixes) |
| Python regressions that AILang avoids | **Count of Python-specific regression classes** |

---

## 8. Execution Instructions

### 8.1 Prerequisites

```bash
# AILang
git clone https://github.com/anomalyco/ailang.git
cd ailang
pip install -e .
ail build apps/inventory/*.ail
ail run apps/inventory/tests/runner.ail
# Verify: 38/38 PASS

# Python
cd apps/inventory_py
python tests/runner.py
# Verify: 38/38 PASS

# AI Providers
pip install openai anthropic
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."
export DEEPSEEK_API_KEY="..."
```

### 8.2 Automated Runner

```bash
# List available inventory datasets
python -m benchmarks inventory list

# Show task definition for a benchmark
python -m benchmarks inventory show B2
python -m benchmarks inventory show B2 T1
python -m benchmarks inventory show B3
python -m benchmarks inventory show B5

# Run a benchmark against the AILang codebase
python -m benchmarks inventory run B2 ailang
python -m benchmarks inventory run B3 ailang
python -m benchmarks inventory run B4 python
python -m benchmarks inventory run B6 ailang
```

### 8.3 Dataset Fixtures

All task definitions live in **`benchmarks/datasets/`**:

| Dataset | Path | Contents |
|---------|------|----------|
| B2 | `benchmarks/datasets/b2_inventory/` | `task.json` + reference implementations in `ailang/` and `python/` |
| B3 | `benchmarks/datasets/b3_inventory/` | `task.json` + 5 buggy modules in `ailang/` and `python/` |
| B4 | `benchmarks/datasets/b4_inventory/` | `task.json` — rename `supplier` → `vendor_partner` |
| B5 | `benchmarks/datasets/b5_inventory/` | `task.json` + scenario prompts in `scenarios/` |
| B6 | `benchmarks/datasets/b6_inventory/` | `task.json` + `changes.json` (50-change catalog) |

### 8.4 Manual Method

```bash
# 1. Copy the prompt from the task definition:
python -m benchmarks inventory show B2 T1 > prompt.md

# 2. Paste into AI chat or API call

# 3. Apply the AI's output to the codebase (apps/inventory/ or apps/inventory_py/)

# 4. Run the build/test command:
#    AILang:   python -m benchmarks inventory run B2 ailang
#    Python:   python -m benchmarks inventory run B2 python

# 5. If fail, feed error back to AI (next iteration)

# 6. Record all metrics in the JSON format (see §2.4)
```

### 8.5 Recording Results

Each run produces:

```
benchmarks/results/{benchmark_name}/{run_id}/
├── measurements.json    # Raw metrics
├── environment.json     # System snapshot
└── report.md            # Human-readable summary
```

For manual AI interaction runs, manually create:

```
benchmarks/results/inventory/{benchmark_id}-{language}/{run_id}/
├── measurements.json    # Raw metrics (from template in §2.4)
├── prompt.md            # Exact prompt sent
├── responses/           # Each AI response (numbered)
│   ├── 001.md
│   ├── 002.md
│   └── ...
├── final_source/        # Final source code after fix
├── environment.json     # System snapshot
└── report.md            # Human-readable summary
```

### 8.6 Aggregate Report

After all benchmarks complete, produce:

```
docs/benchmarks/INVENTORY_AI_COMPARISON.md

Format:
## Head-to-Head Results (All Models)

| Metric | AILang | Python | Ratio | Models Tested |
|--------|--------|--------|-------|---------------|
| B2: Mean iterations | X | Y | X/Y | 3 |
| B3: First-fix compile rate | X% | Y% | — | 3 |
| B4: Regression count | X | Y | X/Y | 3 |
| B5: Files affected | X | Y | X/Y | 3 |
| B6: Cumulative iterations | X | Y | X/Y | 3 |
| B6: Cumulative regressions | X | Y | X/Y | 3 |
| B6: Final compile time | Xs | N/A | — | 3 |
```

---

## 9. Threats to Validity

| Threat | Mitigation |
|--------|------------|
| Model improves between runs | Pin model version in results header |
| Learning effect (AI sees same task twice) | Randomize order of AILang/Python trials across different sessions |
| Prompt engineering skill bias | Use exact prompts from this document (no rewording) |
| AILang constraints produce more verbose code | Record LOC in addition to iterations — both matter |
| Python tests are less thorough than AILang tests | Ensure test equivalence: same assertions, same edge cases |
| Single codebase (inventory) may not generalize | Run each task against existing B2 generic datasets first as validation |
| AI generated both AILang and Python codebases | Cross-validation: have a human verify the Python code is idiomatic |

---

## 10. Related Documents

- [Engineering Benchmark Plan](../ENGINEERING_BENCHMARK_PLAN.md) — B1–B7 methodology (parent document)
- [Inventory Python Comparison](INVENTORY_PYTHON_COMPARISON.md) — Empirical comparison (no AI queries)
- [Inventory Scalability Benchmark](INVENTORY_SCALABILITY_BENCHMARK.md) — AILang scaling results
- [AILang Benchmark Whitepaper](AILANG_BENCHMARK_WHITEPAPER.md) — v0.1.2 aggregate results
- `benchmarks/datasets/b{2,3,4,5,6}_inventory/` — Inventory task definitions and reference implementations
- `benchmarks/inventory/runner.py` — Directly executable runner (see §8.2)
- `benchmarks/framework/` — General-purpose runner, metrics, and reporting infrastructure
- `benchmarks/__main__.py` — CLI entry point (`python -m benchmarks inventory list|show|run`)
