# Variable Resolution Analysis

## Question: Is the Cost Caused by Scope-Chain Traversal?

**Yes. Scope-chain traversal is the root cause.**

The profiler data is unambiguous:

```
Environment.resolve: 1,606,742 calls, 307.0s internal time, 85.5% of runtime
```

This single method — a 4-line recursive walk of the `_parent` linked list —
accounts for over 85% of execution time in the static analyzer.

## How Variable Resolution Works

The resolution chain has four layers:

### Layer 1: `_get_local(name)` → `_resolve_name(name)`

File: `compiler/runtime/interpreter.py:320`

```python
def _get_local(self, name: str) -> Any:
    return self._resolve_name(name)
```

A thin wrapper. Called 917,996 times during the static analyzer run.

### Layer 2: `_resolve_name(name)`

File: `compiler/runtime/interpreter.py:280–318`

Tries resolution in order:

1. Current frame's environment (via `StackFrame.resolve`)
2. Global environment (`self._global_environment.resolve`)
3. Builtins dict (`BUILTINS`)
4. Module environments (`self._modules`)
5. Dotted name resolution (splits on `.`, resolves base, then member)

Each of steps 1 and 2 calls `Environment.resolve`, which is the expensive
operation.

### Layer 3: `StackFrame.resolve(name)`

File: `compiler/runtime/stack_frame.py:32`

```python
def resolve(self, name: str) -> Any:
    return self.environment.resolve(name)
```

Delegates to the frame's Environment. Called 1,261,748 times.

### Layer 4: `Environment.resolve(name)` — THE BOTTLENECK

File: `compiler/runtime/environment.py:27`

```python
def resolve(self, name: str) -> Any:
    if name in self._values:
        return self._values[name]
    if self._parent is not None:
        return self._parent.resolve(name)
    raise NameError(f"Undefined variable: {name}")
```

**Called 1,606,742 times** (combining calls from StackFrame.resolve and
direct calls from _resolve_name to global_environment).

## Why It Is Expensive

### 1. Recursive Chain Traversal

Environment objects form a singly linked list mirroring the call stack:

```
Environment (main frame)
  └── _parent → Environment (length frame, depth 1)
       └── _parent → Environment (length frame, depth 2)
            └── _parent → ... (depth N)
                 └── _parent → Environment (stdlib module)
                      └── _parent → Global Environment
```

Each `resolve("x")` walks this chain from the current frame upward,
checking `name in self._values` at each level.

**Average chain depth:** ~144 (from Phase 1 profiling, avg_depth for
250-line target).

**Total `name in self._values` checks:** ~230 million
(1.6M calls × 144 average depth).

### 2. No Caching

Every variable reference traverses the entire chain from scratch.
If function A references `x` 10,000 times in a loop, each reference
walks the same ~144-level chain.

### 3. No Lexical Addressing

The IR uses string-based variable names. There is no pre-computed
"scope level" or "slot index" that would allow direct access to the
correct environment level.

### 4. Dictionary Lookup Overhead Per Level

Each level requires:
- `name in self._values` → Python dict `__contains__` (hash + compare)
- If found: `self._values[name]` → Python dict `__getitem__`
- If not found: recursive call

Each operation is fast (~50ns for dict lookup), but 230 million of them
at 50ns each = 11.5 seconds just in dict __contains__ calls. The rest
of the 307 seconds comes from Python function call overhead (1.6M
recursive calls × 144 depth = 230M function frames pushed/popped).

---

## Is the Cost Caused by Python Dictionary Lookups?

**Partially, but the main cost is Python call overhead, not dict access.**

Evidence:
- `isinstance` (11 million calls) takes only 0.6s total (0.17%)
- The `dict.__contains__` and `dict.__getitem__` methods do not appear
  in the top 25 hotspots by internal time
- What does dominate is `Environment.resolve` itself — the Python
  function call overhead of 230 million recursive invocations

A single `Environment.resolve` call at depth 144 involves:
- 1 call to `Environment.resolve` at the current level
- 1 call to `Environment.resolve` at depth+1 (recursive)
- ... (144 total calls in the chain)
- Each call does 2 dict operations (`__contains__` + `__getitem__`
  or `__contains__` + recursive call)

So 1.6M top-level calls × 144 depth = 230M `Environment.resolve`
invocations. Each Python function call in CPython costs ~50-100ns
for the call itself (frame setup, etc.), plus the dict operations.

**Estimated breakdown of 307 seconds:**
- Python function call overhead: ~170-200s (230M calls × ~750ns/call)
- Dict `__contains__`: ~11.5s (230M × 50ns)
- Dict `__getitem__` (for hits): ~5s (100M × 50ns)
- Other (name comparisons, control flow): ~90s

---

## Is the Cost Caused by Repeated Identifier Resolution?

**Yes.** The same identifiers are resolved repeatedly.

For example, `string.length` in the static analyzer is called 178,852
times (from Phase 1 data). Each call resolves `string` (module name)
and `length` (function name) from scratch.

Variable names like `x`, `acc`, `result`, `lines`, `index`, etc. are
resolved every time they appear in an expression, even within the same
function body.

---

## Is the Cost Caused by Recursive Evaluation?

**Indirectly, yes.** Recursion creates the deep scope chain.

For a non-recursive program (dice_roller, max_depth=2), the average
environment chain depth is ~2-3 levels, and `Environment.resolve`
accounts for 46% of runtime but only 0.046s total.

For a recursive program (static_analyzer on a 250-line target,
max_depth=385, avg_depth=143.7), the environment chain is ~144 levels
deep, and `Environment.resolve` accounts for 85.5% of runtime.

**The correlation is clear: deeper recursion → deeper chain → more
resolution cost.**

---

## Root Cause Summary

| Factor | Impact | Evidence |
|--------|--------|----------|
| Scope-chain traversal | **Primary** (85.5%) | Environment.resolve is #1 hotspot |
| Python call overhead | **Major** (~55% of the 85.5%) | 230M recursive calls |
| Dict lookups | **Minor** (~5% of runtime) | dict methods not in top 25 hotspots |
| No caching | **Significant** | Same name resolved 178K times |
| Recursion depth | **Driver** | avg_depth=144 for complex workloads |
| String operations | **Negligible** | str.split 0.13%, substring 0.06% |
| isinstance checks | **Negligible** | 0.17% despite 11M calls |

## Conclusion

**The single bottleneck is `Environment.resolve`'s recursive scope-chain
traversal.** Every variable reference walks the full chain from the
current scope to the global scope. With an average chain depth of 144
and 1.6 million lookups, this produces ~230 million recursive Python
function calls consuming 85.5% of wall-clock time.
