# Variable Lookup Cache — Design

## 1. Problem

Each variable reference in AILang triggers a recursive walk of the
environment parent chain (`Environment.resolve`, `environment.py:27`).
With an average scope depth of ~144 (static analyzer), a single
reference produces ~144 dictionary containment checks and ~144 Python
function calls. Profiling shows this chain accounts for 85.4% of
wall-clock execution time in the worst case (`Environment.resolve`:
1,606,742 calls, 318.6s internal time).

## 2. What We Cache

We cache **binding resolution** — the mapping `(environment, name) → resolved_environment`.

This is **not** a cache of evaluated values. We do not store `name → value`.
We store `name → the Environment object where that name is defined`.

This distinction matters because:
- Values can change via `assign` — a value cache would need invalidation
  on every assignment.
- Bindings are fixed after module initialization. A `let` declaration
  creates a binding in a specific scope. That binding never moves to a
  different scope. Only the *value* changes.

## 3. Cache Architecture

### 3.1 Per-Environment Cache

Each `Environment` object gains a `_resolve_cache: dict[str, Environment]`.

When `Environment.resolve(name)` walks the parent chain and finds `name`
in a parent environment, it records which environment owns the binding:

```
resolve("x"):
  1. Check self._resolve_cache → miss
  2. Check self._values → miss
  3. Check self._parent → hit → parent owns "x"
  4. Store: self._resolve_cache["x"] = parent
  5. Return parent._values["x"]
```

Next call to `resolve("x")` from this environment: O(1), no chain walk.

### 3.2 No Invalidation Required (Positive Cache Only)

Bindings in AILang are stable after creation:
- `let x = 1` creates a binding in the current scope. `x` is always
  resolved to that scope.
- `x = 2` (assignment) changes the *value* of `x` in the binding's
  scope. It does not change *which scope* owns `x`.
- `let x = 2` (redeclaration) is forbidden in AILang.

Therefore a **positive** binding cache never requires invalidation.

**Negative caching was removed.** The initial implementation cached
`NameError` sentinels for names not found in any scope, but this is
unsound: `assign` can create new bindings in ancestor environments
when the name does not exist in the chain (`assign` → `define` in
empty-`_parent` case), which would make a stale negative entry
incorrect. Only positive resolutions are cached.

**Edge case — inner scope shadows outer:**
```
let x = 1          # outer scope
fn f() {
    let x = 2      # shadows outer x
    return x       # resolves to inner x
}
```
The outer scope's `resolve_cache["x"]` points to outer environment.
The inner scope's `resolve_cache["x"]` points to inner environment.
Both caches are correct because they are stored in different
Environment objects. A lookup starting from the inner scope checks
its own cache first and finds the correct binding.

### 3.3 Scope: Stack Frames vs Environments

Each `StackFrame` creates a new `Environment` with `parent` pointing
to the parent frame's environment. The cache lives on each Environment.

Deep recursion creates many Environment objects. Each has its own
small cache. Cache entries are garbage-collected when the Environment
is garbage-collected (frame popped, no remaining references).

### 3.4 Warm-Up Behavior

On first call to a function, its environment cache is empty. The
first few variable references within that function will miss and
perform the full chain walk. Subsequent references hit.

For a function called repeatedly (e.g., `length` called 178,852 times),
the cache warms up on the first few iterations and the remaining
178,849 calls are O(1).

## 4. Thread Safety

AILang has no concurrency. No locking required.

## 5. Memory Impact

Each cache entry is a `(str → Environment)` mapping. For a typical
function with ~5 local variables, 5 entries. The static analyzer has
~100 distinct functions, each with its own environment. Estimated
additional memory: < 10 KB for the static analyzer workload.

## 6. Assumptions That Make Invalidation Unnecessary

The statement "no invalidation required" depends on these properties of
AILang's current language model:

| Assumption | Why It Matters | What Would Break It |
|------------|---------------|---------------------|
| Bindings never migrate | A `let` declaration's binding is owned by the environment where it was created. It never moves to a different environment. | Dynamic modules, hot reloading, scope injection |
| Environments are mutable only for existing values | `assign` changes `_values[name]` but never changes which environment owns `name`. `define` (new `let`) never changes a parent's bindings. | Dynamic scope (`var`-like bindings that float up the call stack) |
| Imports are initialized once | Module environments are created and populated once during `_initialize_module`. Their bindings are stable for the lifetime of the program. | Dynamic imports, module unloading/reloading |
| Lexical scope is static | The environment parent chain is established at compile time and never rewired. | Eval-like constructs, metaprogramming that alters scope hierarchy |

**If any future language feature introduces** dynamic modules, hot
reloading, dynamic scope, or runtime symbol injection, the cache
design must be revisited. Specifically:

- A cache-flush primitive (`environment._resolve_cache.clear()`) would
  need to be called when bindings are invalidated. Negative caching
  (were it present) would also need explicit invalidation, since
  a name that doesn't exist at time T₁ might exist at time T₂.

This optimization relies on AILang's current lexical scoping model.
Future language features that alter binding ownership must revisit
the cache design.

## 7. Correctness Properties Preserved

| Property | How Cache Preserves It |
|----------|----------------------|
| Lexical scoping | Cache is per-environment. Inner environments have their own cache. |
| Shadowing | Inner cache entry for `x` points to inner environment. Outer cache entry for `x` points to outer environment. Lookup starts at current environment. |
| Mutable values | Cache stores binding location, not value. `assign` modifies `_values[name]` in the target environment. |
| Module imports | Module environments participate in the same cache mechanism. |
| Global variables | Global environment gets its own cache. |
| Recursion | Each recursive call creates a new Environment with an empty cache. Correct behavior maintained. |

## 7. Design Alternatives Considered

### 7.1 Per-Frame Cache (Rejected)

Storing `name → value` in `StackFrame`. Invalidated on every
`assign` call. The invalidation logic adds complexity and the
cache hit rate is lower because frames are ephemeral.

### 7.2 Global Name → Scope Table (Rejected)

Building a mapping at compile time or module init time. Equivalent
to lexical addressing but requires IR changes. Higher complexity
with similar payoff to per-environment caching.

### 7.3 LRU Cache (Rejected)

Unnecessary. Environment caches are small (5-20 entries). All entries
are equally valuable.
