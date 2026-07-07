# Variable Lookup Cache — Regression Test Specification

## 1. Test File

`tests/test_scope_cache.py` — approximately 100 test cases.

May also add test cases to existing test files if a relevant fixture
already exists there.

## 2. Test Categories

### 2.1 Basic Resolution (10 tests)

Validate that basic variable resolution still works with the cache.

| # | Test | What It Verifies |
|---|------|-----------------|
| 1 | Resolve local variable | `let x = 1; return x` |
| 2 | Resolve from parent scope | `let x = 1; fn f() { return x }` |
| 3 | Resolve from global scope | `let x = 1` in module top level, accessed from function |
| 4 | Resolve after `define` | `let x = 1; let y = x` |
| 5 | Multiple local variables | `let a = 1; let b = 2; return a + b` |
| 6 | Nested function resolution | `fn outer() { let x = 1; fn inner() { return x } }` |
| 7 | Deeply nested (5+ levels) | 5 levels of nested `let`/functions, resolve from innermost |
| 8 | Builtin resolution | `print(1)` — resolves `print` from BUILTINS |
| 9 | Module member resolution | `string.length("abc")` — resolves `string` then `length` |
| 10 | Repeated resolution of same name | `return x + x + x` — cache should hit on 2nd and 3rd access |

### 2.2 Shadowing (15 tests)

Validate that cache doesn't cause scope confusion when names shadow.

| # | Test | What It Verifies |
|---|------|-----------------|
| 11 | Simple shadow | `let x = 1; fn f() { let x = 2; return x }` → 2 |
| 12 | Shadow then access outer | `let x = 1; fn f() { let x = 2; return x }` and separately access global x |
| 13 | Double shadow | `let x = 1; fn f() { let x = 2; fn g() { let x = 3; return x } }` → 3 |
| 14 | Shadow after return | Outer x unchanged after inner scope defines same name |
| 15 | Shadow in sibling functions | `fn a() { let x = 1; return x }; fn b() { let x = 2; return x }` |
| 16 | Shadow with different types | `let x = "hello"; fn f() { let x = 42; return x }` |
| 17 | Shadow only in specific branch | `if condition { let x = 1 }` (AILang: `let` in `if` creates binding in current scope) |
| 18 | Parameter shadowing local | `let x = 1; fn f(x) { return x }` — parameter shadows outer x |
| 19 | Multiple parameters shadowing | `let a = 1; let b = 2; fn f(a, b) { return a + b }` |
| 20 | Shadow builtin | `let print = 42; return print` — should return 42, not function |
| 21 | Shadow across modules | Module A defines `helper`. Module B defines `helper`. B's `helper` should shadow A's. |
| 22 | Deep shadow chain | 5 levels of `let x`, each shadowing previous, resolve at each level |
| 23 | Shadow then reassign | `let x = 1; fn f() { let x = 2; x = 3; return x }` → 3 |
| 24 | Shadow cleared after scope exit | After `fn f() { let x = 2 }`, outer x is still 1 |
| 25 | Shadow with recursive call | `let x = 1; fn f(n) { let x = n; if n > 0 { return f(n-1) }; return x }` |

### 2.3 Recursion (10 tests)

Validate that each recursive call creates a new environment with its
own cache (no cross-frame cache contamination).

| # | Test | What It Verifies |
|---|------|-----------------|
| 26 | Simple recursion | `fn f(n) { if n == 0 { return 0 }; return 1 + f(n-1) }` |
| 27 | Recursion with local | `fn f(n) { let x = n; if n == 0 { return 0 }; return x + f(n-1) }` |
| 28 | Mutual recursion | `fn even(n) { if n == 0 { return 1 }; return odd(n-1) }; fn odd(n) { if n == 0 { return 0 }; return even(n-1) }` |
| 29 | Recursion depth > 100 | Verifies cache doesn't degrade with depth |
| 30 | Recursion with parameter shadowing | Parameter name shadows module-level name |
| 31 | Recursive call reads outer variable | `let base = 10; fn f(n) { if n == 0 { return base }; return n + f(n-1) }` |
| 32 | Recursion modifies accumulator via assign | Verify assign finds the correct scope |
| 33 | Tree recursion | `fn fib(n) { if n <= 1 { return n }; return fib(n-1) + fib(n-2) }` |
| 34 | Recursion returning function value | Recursive calls where return value is a function, not a scalar |
| 35 | Recursion after cache warm-up | Call recursive function twice; second call should benefit from warm cache |

### 2.4 Reassignment / Mutation (15 tests)

Validate that `assign` correctly updates values and the cache doesn't
prevent seeing the new value.

| # | Test | What It Verifies |
|---|------|-----------------|
| 36 | Simple reassignment | `let x = 1; x = 2; return x` |
| 37 | Reassign after function call | `let x = 1; fn f() { x = 2 }; f(); return x` |
| 38 | Reassign in parent scope from inner function | `let x = 1; fn f() { x = 2 }; f(); return x` |
| 39 | Reassign multiple times | `let x = 1; x = 2; x = 3; return x` |
| 40 | Reassign through module boundary | Module A variable, module B reassigns it |
| 41 | Reassign with recursion | Recursive function updates an accumulator via assign |
| 42 | Reassign list element | `let xs = list.new(); list.append(xs, 1); list.get(xs, 0)` |
| 43 | Reassign map value | `let m = map.new(); map.set(m, "k", 1); map.get(m, "k")` |
| 44 | Reassign after cache warm-up | `let x = 1; f(x); x = 2; f(x)` — f reads x each time |
| 45 | Reassign in loop (recursive equivalent) | Recursive function that accumulates state via assign |
| 46 | Reassign to same value | `let x = 1; x = 1` — no-op, but cache must work |
| 47 | Reassign from different scopes | Both inner and outer functions reassign the same variable |
| 48 | Define after reassign | `let x = 1; x = 2; let y = x` |
| 49 | Reassign triggers parent chain walk | Variable is in grandparent scope — assign must walk chain, cache must not interfere |
| 50 | Reassign with negative cache | `let x = 1; fn f() { x = 2 }` — inner scope doesn't define x, assign walks to outer |

### 2.5 Module Variables (10 tests)

Validate that variables defined in modules resolve correctly.

| # | Test | What It Verifies |
|---|------|-----------------|
| 51 | Import and use module variable | `import math; math.add(1, 2)` |
| 52 | Module variable accessed multiple times | `math.add(1, 2); math.add(3, 4)` |
| 53 | Cross-module variable access | Module B accesses variable from Module A |
| 54 | Module function recursion | Function in module A calls itself recursively |
| 55 | Module function calls another module function | `import string; import convert; convert.to_string(string.length("abc"))` |
| 56 | Module with circular import | A imports B, B imports A (if AILang allows) |
| 57 | Module variable shadowed by local | `import math; fn f() { let add = 42; return add }` |
| 58 | Module reload idempotent | Initialize module twice, verify cache consistency |
| 59 | Dotted name resolution | `string.length` — resolves module then member |
| 60 | Deeply nested module | `string.substring` where `string` is a module environment |

### 2.6 Imported Symbols (8 tests)

| # | Test | What It Verifies |
|---|------|-----------------|
| 61 | Import stdlib function | `import string; string.length("abc")` |
| 62 | Multiple imports | `import string; import convert; import math` |
| 63 | Import in inner scope | `fn f() { import string; return string.length("abc") }` |
| 64 | Import same module twice | Idempotent |
| 65 | Import resolves to module environment | The imported name is an Environment object |
| 66 | Imported function called repeatedly | Cache warm-up on imported functions |
| 67 | Imported function recursion | `string.substring` called recursively via AILang function |
| 68 | Combined import and local resolution | `import string; let x = 1; string.length("a") + x` |

### 2.7 Edge Cases (10 tests)

| # | Test | What It Verifies |
|---|------|-----------------|
| 69 | NameError for undefined variable | `return undefined_var` → error |
| 70 | NameError after successful resolves | Mix of valid and invalid names |
| 71 | Empty function | `fn f() { return 0 }` — no local variables |
| 72 | Function with many parameters | `fn f(a,b,c,d,e,f,g,h,i,j) { return a }` — 10 params |
| 73 | Assignment to undefined variable | `x = 1` where x not defined → creates in current scope |
| 74 | Variable defined in sibling block | `fn f() { if true { let x = 1 }; return x }` |
| 75 | Dotted name with multiple dots | `a.b.c` — should resolve step by step |
| 76 | Very long variable names | 100-char variable name |
| 77 | Unicode variable names | `let café = 1; return café` (if supported) |
| 78 | Empty string variable name | Edge case (should be rejected by parser, but verify no crash in runtime) |

### 2.8 Cache-Specific Behavior (10 tests)

These tests explicitly verify cache behavior, not just correctness.
They may use introspection hooks.

| # | Test | What It Verifies |
|---|------|-----------------|
| 79 | Cache populated after first resolve | Access variable once, verify cache has entry |
| 80 | Cache miss on first access, hit on second | Access x twice — first should be miss, second should be hit |
| 81 | Different environments have different caches | Inner and outer scope caches are independent |
| 82 | Cache cleared when environment is GC'd | No memory leak from cache entries |
| 83 | Negative cache prevents re-scanning | Access undefined name, verify cache prevents repeated chain walk |
| 84 | Cache survives assign | `let x = 1; x = 2; return x` — cache entry still valid |
| 85 | Cache hit after recursive call returns | Variable in outer scope, recursive call doesn't corrupt outer's cache |
| 86 | Cache miss on new environment | Each new environment starts with empty cache |
| 87 | Multiple names in cache | Verify cache stores multiple entries correctly |
| 88 | Cache hit rate > 90% for repeated access | Simulate a tight loop (via recursion) with repeated variable access |

### 2.9 Stress Tests (12 tests)

| # | Test | What It Verifies |
|---|------|-----------------|
| 89 | 1000 recursive calls with local variables | Stress test for cache + recursion |
| 90 | 100 nested scopes | 100 levels of function nesting, resolve from innermost |
| 91 | 500 different variable names | Large cache, verify no HashMap degradation |
| 92 | Alternating resolution and assignment | `let x = 1; x = 2; return x; let y = x` — mix of ops |
| 93 | Deep recursion with reassignment | Recursive function that increments a counter via assign |
| 94 | Chain of 20 function calls, each with locals | Each function defines locals, calls next, returns |
| 95 | Same name resolved in 100 environments | 100 nested functions each defining `x`, resolve at each level |
| 96 | Cache under memory pressure | (If practical) verify cache doesn't cause OOM |
| 97 | Repeated module access | Access `string.length` 10,000 times in a loop |
| 98 | Mix of local, global, module, and builtin resolves | `import string; let x = 1; fn f() { let y = 2; return string.length("a") + x + y + print }` |
| 99 | Recursive sorting algorithm | Bubble sort or quicksort using recursion (tests cache in algorithmic context) |
| 100 | End-to-end: run all benchmark apps | dice_roller, hangman, inventory_mgmt, kanban output must match pre-cache output |

## 3. Cache Correctness Invariants

These tests verify that the cache preserves correctness properties,
not just that the program produces correct output. They use cache
introspection (`get_cache_info()`) to assert internal state.

### Invariant 1: Cache entires reflect binding location, not value

```ailang
let x = 1
print(x)
x = 2
print(x)
```

**Verifies:**
- First `x` access: cache miss → resolved chain → cache populated
- Second `x` access: cache hit → returns `_values["x"]` from same env
- After `x = 2`: cache entry still points to the same environment.
  The value `2` is found via `cached_env._values["x"]`.
- Output: `1` then `2`

### Invariant 2: Inner scope cache never contaminates outer scope

```ailang
let x = 1      # outer env cache["x"] → outer env
fn f() {
    let x = 5  # inner env cache["x"] → inner env
    print(x)   # 5
}
f()
print(x)       # 1
```

**Verifies:**
- Inner `x` resolves to inner environment (its own cache entry)
- After `f()` returns, outer `x` still resolves to outer environment
- The two cache entries point to different `Environment` objects
- Output: `5` then `1`

### Invariant 3: Recursive frames each resolve their own binding

```ailang
fn f(n) {
    let x = n
    if n == 0 {
        return 0
    }
    return x + f(n - 1)
}
print(f(3))
```

**Verifies:**
- Each recursive call to `f` creates a new `Environment` with
  its own `_resolve_cache`
- `x` in frame at depth D resolves to that frame's environment,
  not to frame D+1's or D-1's
- Output: `6`

### Invariant 4: Module lookup cached independently

```ailang
import string
print(string.length("abc"))
print(string.length("xyz"))
```

**Verifies:**
- First `string` resolution: module environment cached in caller's
  `_resolve_cache["string"]`
- Second `string` resolution: cache hit → O(1)
- `length` resolution within `string` module environment also cached

### Invariant 5: No negative cache for failed lookups

```ailang
does_not_exist  # NameError — no cache entry created
```

**Verifies:**
- First lookup: misses all scopes → `NameError`
- No cache entry is created for the failed name (negative caching
  was removed because `assign` can create new bindings in ancestor
  environments, making any negative entry stale)
- Subsequent access still requires a fresh chain walk

### Invariant 6: Negative cache does not exist (see Invariant 5)

Negative caching was removed. See `LOOKUP_CACHE_DESIGN.md` §3.2 and
`LOOKUP_CACHE_IMPLEMENTATION.md` §2.4 for rationale.

## 4. Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run only cache-specific tests
python -m pytest tests/test_scope_cache.py -v

# Run existing tests to verify no regressions
python -m pytest tests/ -v --ignore=tests/test_scope_cache.py
```

## 5. Test Infrastructure

Cache introspection requires a hook in `Environment`:

```python
# For testing only — exposed via Runtime
def get_cache_info(self) -> dict:
    return {
        "cache_size": len(self._resolve_cache),
        "entries": list(self._resolve_cache.keys()),
    }
```

Test 79-88 use `get_cache_info()` to verify cache state.

## 6. Expected Results

- All 100 tests pass
- No regressions in existing 522 tests
- Output of all benchmark apps is byte-identical to pre-cache output
