# Variable Lookup Cache — Implementation Plan

## 1. Files to Modify

| File | Change |
|------|--------|
| `compiler/runtime/environment.py` | Add `_resolve_cache: dict[str, Environment]`, modify `resolve()` |
| `compiler/runtime/stack_frame.py` | No change needed (delegates to environment) |
| `compiler/runtime/interpreter.py` | No change needed (calls `_resolve_name` → `resolve`) |
| `tests/` | Add `test_scope_cache.py` (~100 new tests) |

## 2. Detailed Implementation

### 2.1 `environment.py` — Cache Storage

Add a cache to `__init__`:

```python
def __init__(self, parent: Environment | None = None) -> None:
    self._values: dict[str, Any] = {}
    self._parent = parent
    self._resolve_cache: dict[str, Environment] = {}
```

No changes to `define` or `assign`.

### 2.2 `environment.py` — Modified `resolve`

Current method:

```python
def resolve(self, name: str) -> Any:
    if name in self._values:
        return self._values[name]
    if self._parent is not None:
        return self._parent.resolve(name)
    raise NameError(f"Undefined variable: {name}")
```

Modified method:

```python
def resolve(self, name: str) -> Any:
    # 1. Check cache — binding already resolved to a target environment
    cached_env = self._resolve_cache.get(name)
    if cached_env is not None:
        return cached_env._values[name]

    # 2. Check own values
    if name in self._values:
        self._resolve_cache[name] = self
        return self._values[name]

    # 3. Check cache on parent — parent may have cached this for us
    if self._parent is not None:
        if name in self._parent._resolve_cache:
            cached_env = self._parent._resolve_cache[name]
            self._resolve_cache[name] = cached_env
            return cached_env._values[name]

    # 4. Walk parent chain (uncached path)
    if self._parent is not None:
        try:
            value = self._parent.resolve(name)
            # The recursive call populated parent's cache.
            # Now populate this environment's cache from parent's cache.
            if name in self._parent._resolve_cache:
                self._resolve_cache[name] = self._parent._resolve_cache[name]
            return value
        except NameError:
            self._resolve_cache[name] = self  # sentinel for "doesn't exist"
            raise

    raise NameError(f"Undefined variable: {name}")
```

### 2.3 Optimization: Short-Circuit Parent Cache Check

Step 3 is an optimization: before walking the parent chain, check if
the *parent* already has a cache entry for this name. If so, we can
populate our cache from the parent's cache in O(1) without recursing.

This is safe because:
- If parent has `name` cached, the binding is at or above the parent
- Our environment would find the same binding walking from here
- The cached-environment pointer is the same

### 2.4 Negative Caching — Removed

**Negative caching was removed from the final implementation.**
`assign` can create new bindings in ancestor environments when the
name does not exist in any environment on the chain (falling through
to `self.define(name, value)` in the topmost environment). This would
make a stale negative cache entry incorrect. Only positive
resolutions are cached.

The initial implementation cached `NameError` sentinels using a
self-reference pattern (the environment itself, since
`self._values[name]` would fail). This was removed after discovering
the `assign`-can-create-bindings edge case during regression testing.

## 3. `assign` Interaction — No Invalidation Needed

`assign` modifies `_values[name]` in the owning environment. The cache
stores a pointer to the owning environment, not the value. Since
`assign` doesn't change which environment owns the binding, the cache
remains valid.

```python
def assign(self, name: str, value: Any) -> None:
    if name in self._values:
        self._values[name] = value   # cache still correct — same env
        return
    if self._parent is not None:
        self._parent.assign(name, value)
        return
    self.define(name, value)
```

## 4. Implementation Steps

1. Modify `environment.py` — add `_resolve_cache` to `__init__`
2. Modify `environment.py` — replace `resolve` with cached version
3. Run existing test suite to verify no regressions
4. Add `test_scope_cache.py` (see `LOOKUP_CACHE_REGRESSION.md`)
5. Run benchmarks (see `LOOKUP_CACHE_BENCHMARK.md`)

## 5. Rollback Plan

The change is ~20 lines of Python in a single file. Rollback is a
`git checkout` on `environment.py`.

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Wrong binding cached due to shadowing | Very Low | High | Cache is per-environment; inner scope can't corrupt outer scope's cache. Regression tests cover shadowing. |
| Memory leak from stale cache entries | Low | Medium | Environments are garbage-collected when frames are popped. No persistent cache. |
| Negative cache stale after `assign` | Low | Medium | `assign` can define new bindings in ancestors. Mitigated by removing negative caching entirely. |
| Cache populated with wrong parent binding | Very Low | High | Step 3 (parent cache check) relies on parent being correct. Tests verify. |
