# AILang A101 Phase 0 — Reproduction & Baseline Evidence

> **Date:** 2026-08-20
> **Version:** v1.1.21 (published), v1.1.20 (repo)
> **Purpose:** Reproduce all P0 findings before any product code changes

---

## 1. F-04: Cumulative Recursion Budget

### Finding
The trampoline iteration budget is **cumulative** across the entire program execution, not per-chain. Multiple independent recursive workloads share the same 100,000-iteration budget (`max_call_depth * 50 = 2000 * 50`).

### Reproduction

**Test 1: Single workload (scalar tail recursion)**
- `deep_scalar(50000, 0)` → **PASS** (50k iterations within budget)
- `deep_scalar(95000, 0)` → **PASS** (95k iterations within budget)

**Test 2: Single workload (list-carrying recursion)**
- `deep_list(50000, items)` → **PASS**
- `deep_list(60000, items)` → **PASS**
- `deep_list(95000, items)` → **PASS** (solo)

**Test 3: Cumulative budget exhaustion**
- `deep_scalar(50000, 0)` → PASS (uses 50k of 100k budget)
- `deep_list(60000, items)` → **FAIL**: `Recursion depth exceeded (limit: 2000)`
- Total attempted: 50k + 60k = 110k > 100k limit
- Second workload fails even though its own depth (60k) is well within the 100k budget

**Test 4: Multi-pass business workload**
- 400-record build/validate/sum pipeline → **PASS** (total ~1200 iterations)

### Evidence Files
- `temp_phase0/test_cumulative_budget.ail` — confirms cumulative budget bug
- `temp_phase0/test_absolute_limits.ail` — 95k solo works, 95k after 95k fails
- `temp_phase0/test_f04_budget.ail` — individual workloads pass

### Root Cause
`_trampoline_iterations` counter is saved/restored per `_trampoline_call` (lines 451, 516 of interpreter.py), but `_inline_tail_chain` (line 534) increments the same counter without isolation. The counter is shared across the entire program.

### Impact
Multi-pass pipelines (build → filter → sum) with >500 records per pass will fail when the cumulative iterations exceed 100,000. The error message says "limit: 2000" which is misleading.

---

## 2. F-09: Hangman Crash (Same-State Recursion)

### Finding
Two functions in the hangman app recurse with identical state, causing infinite recursion:

1. **`reveal_random`** (line 59-68): When `remaining > 0` and the randomly picked letter is already guessed, it recurses with the same `remaining` value
2. **`play_hangman`** (line 105-106): When the random guess is already guessed, it recurses with identical `guessed`, `lives`, and `hint_given`

### Reproduction

**Test 1: `reveal_random` with pre-guessed letter**
- Pre-fill `guessed` with "a", call `reveal_random("hello", guessed, 3)`
- Function picks "a" (already guessed), recurses with `remaining=3` (unchanged)
- Result: **CRASH** after 2000 iterations with `Recursion depth exceeded (limit: 2000)`

**Test 2: `play_hangman` with pre-guessed letter**
- Pre-fill `guessed` with "a", call `play_hangman("hello", guessed, 6, false)`
- Function guesses "a" (already guessed), recurses with identical state
- Result: **CRASH** after 2000 iterations

### Evidence Files
- `temp_phase0/test_f09_hangman.ail` — `reveal_random` infinite recursion
- `temp_phase0/test_f09_play_hangman.ail` — `play_hangman` infinite recursion

### Root Cause
Both functions use random selection without filtering already-guessed letters. When the random pick lands on an already-guessed letter, the function recurses without making progress (no state change → infinite loop).

### Impact
The hangman game crashes non-deterministically depending on the random seed and word. For words where all letters are guessed before `remaining` reaches 0, the game always crashes.

---

## 3. Malformed Numeric Input (F-01/F-02)

### Finding
`convert.to_int()` raises a `RuntimeError` on malformed input (decimal strings, non-numeric strings, empty strings) instead of returning a try-value or sentinel.

### Reproduction

| Input | Result | Expected |
|-------|--------|----------|
| `"42"` | `42` | `42` |
| `42` | `42` | `42` |
| `"12.50"` | **RuntimeError** | Try-value or `null` |
| `"hello"` | **RuntimeError** | Try-value or `null` |
| `""` | **RuntimeError** | Try-value or `null` |

### Evidence File
- `temp_phase0/test_malformed_input.ail` — crashes on decimal input

### Root Cause
`native_to_int` (builtins.py:347-374) calls `int(value)` which raises `ValueError` on decimals. The function catches this and re-raises as `RuntimeError`. No `try_to_int` or `to_float` variants exist.

### Impact
Business applications processing monetary values (e.g., "12.50") cannot safely parse user input. The only option is to crash or implement workarounds in AILang code.

---

## 4. Recursion Limit Message Accuracy (F-14)

### Finding
The error message says `"Recursion depth exceeded (limit: 2000)"` but the actual limit is **100,000** iterations (`max_call_depth * 50`). The "2000" refers to `max_call_depth` which is the *Python host stack* limit, not the *AILang iteration* limit.

### Reproduction

| Test | Depth | Result |
|------|-------|--------|
| Scalar tail recursion | 50,000 | **PASS** |
| Scalar tail recursion | 95,000 | **PASS** |
| List-carrying recursion | 95,000 | **PASS** (solo) |
| List-carrying recursion | 95,000 | **FAIL** (after 95k scalar) |

The actual limit is 100,000 iterations, but the message claims 2000.

### Evidence Files
- `temp_phase0/test_recursion_deep.ail` — scalar at 50k passes
- `temp_phase0/test_absolute_limits.ail` — shows 95k works solo

### Root Cause
The error message template in interpreter.py:478 uses `self._max_call_depth` (2000) but the actual check is `self._trampoline_iterations > self._max_call_depth * 50` (100,000). The message should reference the iteration limit, not the depth limit.

### Impact
Developers see "limit: 2000" and assume their code is hitting a shallow recursion limit, when the actual constraint is 100,000 cumulative iterations. This makes debugging harder.

---

## 5. Baseline Metrics

| Metric | Value |
|--------|-------|
| Scalar tail recursion limit | ~100,000 iterations |
| List-carrying recursion limit | ~100,000 iterations (solo) |
| Cumulative budget | 100,000 (shared across all workloads) |
| Python recursion limit | `max_call_depth * 10 + 1000 = 21,000` |
| Default `max_call_depth` | 2,000 |
| Trampoline multiplier | 50x |
| `convert.to_int` behavior | Crashes on decimal/non-numeric input |
| `convert.to_float` | **Does not exist** |
| `try_to_int` / `try_to_float` | **Do not exist** |
| Existing test suite | 77 Python test files, some pre-existing failures |

---

## 6. Sign-off

Phase 0 reproduction is complete. All four P0 findings are confirmed with reproducible evidence.

**Next:** Phase 1 — P0-A (numeric conversion), P0-C (recursion documentation), P0-D (limit documentation).
