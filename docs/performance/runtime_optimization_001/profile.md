# Python-Level Profile Report

## Methodology

Five real AILang applications were profiled using Python's `cProfile` module.
Each application was compiled once (compile time excluded from profile), then
the runtime execution was profiled in its entirety.

### Profiling Setup

- **Tool:** `cProfile.Profile` (Python 3.12+)
- **Runtime separation:** Compile and runtime phases are timed independently.
  Only the runtime phase is profiled.
- **Metrics recorded:**
  - Total Python function calls (`total_calls`)
  - Primitive (non-recursive) calls (`prim_calls`)
  - Internal time (time spent in function itself, excluding callees)
  - Cumulative time (self + callees)
  - Peak memory (via `tracemalloc`)
- **Source script:** `tools/python_profiler.py`

### Applications Profiled

| App | Lines | Description |
|-----|-------|-------------|
| dice_roller | 73 | Rolls 20 dice, computes stats, prints histogram |
| hangman_game | 116 | Auto-played hangman with random letter guessing |
| inventory_mgmt | 1099 | Inventory demo with 11 items, 4 categories, 8 transactions |
| kanban | 1130 | Kanban board demo with 7 tasks across 4 columns |
| static_analyzer | 839 | Static analyzer analyzing `dice_roller` (73 lines) |

---

## Results Summary

| App | Runtime (s) | Python Calls | Primitive Calls | Peak Memory (MB) |
|-----|------------:|-------------:|----------------:|-----------------:|
| dice_roller | 0.100 | 111,196 | 69,554 | 0.17 |
| hangman_game | 0.260 | 358,646 | 225,280 | 0.33 |
| inventory_mgmt | 0.157 | 257,896 | 178,718 | 0.28 |
| kanban | 0.099 | 138,062 | 95,433 | 0.19 |
| **static_analyzer** | **359.152** | **78,396,988** | **21,237,077** | **0.86** |

### Key Observation

The static analyzer completely dominates all other apps — **359 seconds** vs the
next closest at 0.260 seconds (hangman). This is a factor of **1,380x**.

This is not because the analyzer has more source lines (839 lines vs 1130 for
kanban). It is because the analyzer's execution profile involves:
- Deeply recursive functions (max call depth ~139 on a 25-line target)
- String scanning via character-by-character `length`, `equals`, `substring`
- Call graph construction with scope traversal

---

## Call Volume Breakdown

### `isinstance` Calls

| App | `isinstance` Calls | Runtime Impact |
|-----|-------------------:|---------------:|
| dice_roller | 37,798 | 0.0021s (2.1%) |
| hangman_game | 118,350 | 0.0058s (2.2%) |
| inventory_mgmt | 94,832 | 0.0047s (3.0%) |
| kanban | 50,320 | 0.0025s (2.5%) |
| static_analyzer | **11,024,668** | 0.599s (0.17%) |

Despite 11 million `isinstance` calls in the static analyzer, Python's
implementation is fast enough that it accounts for only 0.17% of runtime.
This demonstrates that **Python interpreter overhead is not the bottleneck**.

### `hasattr` / `getattr` Calls

These are used in `MemberAccessIR` evaluation and `_resolve_name` for dotted
name resolution. For the static analyzer:

| Call | Count | Time | % Runtime |
|------|------:|-----:|----------:|
| `hasattr` | 76,924 | 0.242s | 0.07% |
| `getattr` | 76,924 | 0.168s | 0.05% |

Negligible impact.

### String Operations

| Call | Count | Time | % Runtime |
|------|------:|-----:|----------:|
| `str.split` | 76,924 | 0.467s | 0.13% |
| `string_substring` (Python) | 43,581 | 0.218s | 0.06% |

Also negligible.

---

## Compile vs Runtime Breakdown

| App | Compile (s) | Runtime (s) | Runtime % |
|-----|------------:|------------:|----------:|
| dice_roller | 0.018 | 0.100 | 85% |
| hangman_game | 0.020 | 0.260 | 93% |
| inventory_mgmt | 0.078 | 0.157 | 67% |
| kanban | 0.072 | 0.099 | 58% |
| static_analyzer | 0.078 | **359.152** | **99.98%** |

For computationally intensive programs, compilation is negligible.

---

## Data File Access

The profiler output is saved at `tools/python_profile_data.json` and contains
the top-20 hotspots by internal and cumulative time for each application.
