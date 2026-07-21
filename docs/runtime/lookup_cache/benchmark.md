# Variable Lookup Cache — Benchmark Specification

## 1. Methodology

Benchmark every real AILang application before and after the cache
change. Use the existing `tools/python_profiler.py` for all
measurements to ensure comparable results.

### 1.1 Before-and-After Protocol

1. Checkout pre-cache commit.
2. Run `tools/python_profiler.py` on all 5 benchmark apps.
3. Save results as `profile_pre_cache.json`.
4. Apply cache implementation.
5. Run `tools/python_profiler.py` on all 5 benchmark apps.
6. Save results as `profile_post_cache.json`.
7. Compare.

### 1.2 Measurements Per App

| Metric | Source | Notes |
|--------|--------|-------|
| Runtime (seconds) | `profiler.runtime_time` | Total wall-clock execution |
| Python calls | `profiler.total_calls` | All Python function calls |
| Primitive calls | `profiler.primitive_calls` | Non-recursive calls |
| `Environment.resolve` calls | `profiler.interpreter_calls.resolve.calls` | |
| `Environment.resolve` internal time | `profiler.interpreter_calls.resolve.internal_time` | Self time, excluding callees |
| `Environment.resolve` % runtime | computed | internal_time / runtime_time |
| Peak memory | `profiler.peak_memory_mb` | tracemalloc peak |
| Cache hit rate | **NEW — must add to profiler** | see 1.3 |

### 1.3 Cache-Specific Metrics

The profiler must be extended to record:

- `cache_hits`: number of times `_resolve_cache` returned a hit
- `cache_misses`: number of times `_resolve_cache` was checked and missed
- `cache_negative_hits`: number of times a negative cache entry prevented re-scanning
- `environment_count`: total number of `Environment` objects in the runtime
- `cache_entries`: total number of cache entries across all environments
- `peak_env_cache_size`: maximum entries in a single environment's cache
- `avg_cache_size`: mean entries per environment
- `cache_memory_bytes`: estimated memory consumed by cache entries (keys + values + dict overhead)

Add a `CacheStats` counter to `Environment` and expose via a
`get_cache_stats()` method on `Runtime`.

### 1.4 Memory Measurement

Memory is measured at two levels:

1. **Process-level peak** (via `tracemalloc`): total Python heap usage
   before vs after. This captures the net memory impact including
   dict allocations, cache entries, and any GC overhead.

2. **Cache-specific accounting**: each `Environment` records its
   `_resolve_cache` dict size. The aggregate is computed by walking
   all reachable environments (global, module, frame-stack).

   Cache memory is estimated as:
   ```python
   # Per entry: key (str) ~50 bytes + value (ref) ~8 bytes
   # Dict overhead: ~72 bytes per entry (Python 3.12)
   ESTIMATED_BYTES_PER_CACHE_ENTRY = 130
   cache_memory = total_entries * ESTIMATED_BYTES_PER_CACHE_ENTRY
   ```

   This is an upper-bound estimate. Actual memory depends on string
   interning and dict resizing behavior.

### 1.4 Derived Metrics

- **Cache hit rate:** `hits / (hits + misses)`
- **Speedup factor:** `pre_runtime / post_runtime`
- **Call reduction:** `pre_resolve_calls - post_resolve_calls`
- **Memory delta:** `post_peak_memory - pre_peak_memory`

## 2. Benchmark Applications

| App | Lines | Characteristic | Expected Cache Impact |
|-----|-------|---------------|----------------------|
| dice_roller | 73 | Shallow recursion, print-heavy | Low-Moderate |
| hangman_game | 116 | Moderate recursion, random-access | Moderate |
| inventory_mgmt | 1099 | Data-driven, linear flow | Low (already fast) |
| kanban | 1130 | Data-driven, some I/O | Low (I/O dominates) |
| static_analyzer | 839 | Deep recursion, string scanning | High (85.4% resolve) |

## 3. Expected Results Format

```
=== PRE-CACHE ===
App                  Runtime(s)   resolve(s)   resolve%   resolve_calls
dice_roller             0.087        0.040        45.6%         5,063
hangman_game            0.245        0.107        43.5%        16,549
inventory_mgmt          0.154        0.057        37.0%        12,467
kanban                  0.093        0.028        29.6%         6,847
static_analyzer       373.053      318.615        85.4%     1,606,742

=== POST-CACHE ===
App                  Runtime(s)   resolve(s)   resolve%   resolve_calls  cache_hit%
dice_roller             0.0??        0.0??          ?.?%          ????        ??.?%
hangman_game            0.0??        0.0??          ?.?%          ????        ??.?%
inventory_mgmt          0.0??        0.0??          ?.?%          ????        ??.?%
kanban                  0.0??        0.0??          ?.?%          ????        ??.?%
static_analyzer          ?.???         ?.???          ?.?%          ????        ??.?%

=== SPEEDUP ===
App                  Pre(s)   Post(s)   Ratio   resolve_reduction
dice_roller            0.087      0.0??    ?.??x            ??.?%
hangman_game           0.245      0.0??    ?.??x            ??.?%
inventory_mgmt         0.154      0.0??    ?.??x            ??.?%
kanban                 0.093      0.0??    ?.??x            ??.?%
static_analyzer      373.053       ?.???    ?.??x            ??.?%
```

## 4. Expected Results (Hypotheses, Not Targets)

Based on profiler evidence:

- **Static analyzer:** `Environment.resolve` is 85.4% of runtime
  with 1.6M calls. With caching, the number of chain walks should
  drop to ~number of distinct (environment, name) pairs. If the
  analyzer has ~100 distinct variable names and ~1000 environments,
  that's ~100K distinct pairs — a ~94% reduction in chain walks.
  Estimated runtime: **novel measurement** (no target percentage).

- **Hangman:** Similar pattern at smaller scale. Resolve is 43.5%.
  Cache hit rate will be high because the same variables are
  accessed repeatedly within each function.

- **Dice roller / kanban / inventory:** Low baseline runtime
  (<0.25s). Any speedup will be within measurement noise. These
  are primarily regression tests, not performance tests.

## 5. Profiler Extension

Add to `tools/python_profiler.py`:

```python
class CacheStats:
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.negative_hits = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def __repr__(self) -> str:
        return f"hits={self.hits} misses={self.misses} neg={self.negative_hits} rate={self.hit_rate:.1%}"
```

In `Environment`:

```python
self._cache_stats = CacheStats()
```

In `resolve`:

```python
def resolve(self, name: str) -> Any:
    cached_env = self._resolve_cache.get(name)
    if cached_env is not None:
        if cached_env is self and name not in self._values:
            self._cache_stats.negative_hits += 1
            raise NameError(...)
        self._cache_stats.hits += 1
        return cached_env._values[name]

    self._cache_stats.misses += 1
    # ... rest of resolve
```

Runtime exposes:

```python
def get_cache_stats(self) -> dict:
    """Aggregate cache stats across all environments."""
    # Walk global, module, and frame environments
```

## 6. Correctness Validation During Benchmarking

Each benchmark run must produce identical output (stdout) before and
after the cache change. Use `assert` or `diff` on captured output.

For the static analyzer, the report text must be byte-identical.
