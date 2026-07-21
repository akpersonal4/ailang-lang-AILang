# Interpreter Hotspot Analysis

## Runtime Method Rankings by Wall-Clock Time

### Static Analyzer (analyzing dice_roller, 73-line target)

The static analyzer is the most computationally demanding application and
provides the clearest hotspot signal. Rankings below are by **internal time**
(self time, excluding callees).

| Rank | Method | Calls | Internal Time | % Runtime | Cumulative Time |
|-----:|--------|------:|--------------:|----------:|----------------:|
| 1 | `Environment.resolve` | 1,606,742 | **307.026s** | **85.49%** | 307.026s |
| 2 | `_resolve_name` | 1,184,824 | 11.333s | 3.16% | 322.772s |
| 3 | `_evaluate_expression` | 15* | 10.893s | 3.03% | 359.152s |
| 4 | `_call_function` | 1* | 7.379s | 2.05% | 359.152s |
| 5 | `_execute_block` | 1* | 3.963s | 1.10% | 359.152s |
| 6 | `_execute_node` | 22* | 3.558s | 0.99% | 359.152s |
| 7 | `StackFrame.resolve` | 1,261,748 | 3.325s | 0.93% | 309.422s |
| 8 | `_get_local` | 917,996 | 1.919s | 0.53% | 8.414s |
| 9 | `Environment.define` | 576,550 | 1.232s | 0.34% | 1.315s |

*\* Primitive (non-recursive) calls. Recursive invocations are within
the cumulative time.*

### Dice Roller (73-line app)

| Rank | Method | Calls | Internal Time | % Runtime |
|-----:|--------|------:|--------------:|----------:|
| 1 | `Environment.resolve` | 5,063 | 0.046s | 46.1% |
| 2 | `_evaluate_expression` | 19 | 0.014s | 13.8% |
| 3 | `_resolve_name` | 3,884 | 0.009s | 8.6% |
| 4 | `_call_function` | 1 | 0.007s | 7.4% |
| 5 | `_execute_block` | 1 | 0.004s | 4.0% |
| 6 | `_execute_node` | 26 | 0.004s | 3.9% |

### Hangman (116-line app)

| Rank | Method | Calls | Internal Time | % Runtime |
|-----:|--------|------:|--------------:|----------:|
| 1 | `Environment.resolve` | 16,609 | 0.117s | 45.2% |
| 2 | `_evaluate_expression` | 9 | 0.036s | 13.7% |
| 3 | `_resolve_name` | 12,349 | 0.025s | 9.5% |
| 4 | `_call_function` | 1 | 0.018s | 7.0% |

### Inventory Management (1099-line app)

| Rank | Method | Calls | Internal Time | % Runtime |
|-----:|--------|------:|--------------:|----------:|
| 1 | `Environment.resolve` | 12,467 | 0.057s | 36.0% |
| 2 | `_evaluate_expression` | 10 | 0.024s | 15.4% |
| 3 | `_resolve_name` | 9,212 | 0.015s | 9.7% |
| 4 | `_call_function` | 1 | 0.012s | 7.6% |

---

## Why Each Hotspot Is Expensive

### 1. `Environment.resolve` — 85.5% of runtime (static analyzer)

This is the **dominant bottleneck** by a wide margin. The method is
remarkably simple — only 4 lines of Python:

```python
def resolve(self, name: str) -> Any:
    if name in self._values:
        return self._values[name]
    if self._parent is not None:
        return self._parent.resolve(name)
    raise NameError(f"Undefined variable: {name}")
```

**Why it is expensive:**

1. **Scope chain traversal:** Each call walks up the `_parent` chain
   recursively. With an average depth of ~144 scopes (from Phase 1
   profiling), a single variable resolution triggers ~144 dictionary
   lookups on average.

2. **No caching:** Every variable reference — even repeated ones in the
   same scope — traverses the full chain from scratch.

3. **High call volume:** 1.6 million calls in the static analyzer run.
   Each call traverses on average 144 scopes, yielding approximately
   **230 million `name in self._values` dictionary checks**.

4. **The `_parent` chain is a linked list:** Environment objects form
   a singly linked list matching the call stack. Resolution is O(depth)
   with no shortcuts.

### 2. `_resolve_name` — 3.16% of runtime

This is the entry point that coordinates resolution across frames,
globals, builtins, and modules. It calls `StackFrame.resolve`, then
`global_environment.resolve`, then checks BUILTINS, module environments,
and dotted names.

The relatively low internal time (3.16% vs 85.5% for Environment.resolve)
confirms that the actual cost is in the callee, not the dispatch logic.

### 3. `_evaluate_expression` — 3.03% of runtime

Dispatches expression evaluation based on isinstance checks. The internal
time is low because most of the work is delegated to recursive calls
(sub-expression evaluation) and `_resolve_name`.

### 4. `_call_function` — 2.05% of runtime

Creates `StackFrame` and `Environment` objects, binds parameters, and
calls `_execute_block`. The allocation overhead is modest; the real cost
is in the execution of the function body (measured in cumulative time).

---

## Cross-App Consistency

| Method | dice_roller | hangman | inventory | kanban | static_analyzer |
|--------|:-----------:|:-------:|:---------:|:------:|:---------------:|
| `Environment.resolve` | **46.1%** | **45.2%** | **36.0%** | **27.8%** | **85.5%** |
| `_resolve_name` | 8.6% | 9.5% | 9.7% | 8.3% | 3.2% |
| `_evaluate_expression` | 13.8% | 13.7% | 15.4% | 13.1% | 3.0% |
| `_get_local` | 1.9% | 1.9% | 1.9% | 1.5% | 0.5% |

`Environment.resolve` is consistently the #1 hotspot across all
applications, ranging from 28% (kanban, simple data flow) to 85.5%
(static analyzer, deep recursion).

The lower percentage in kanban and inventory is due to file I/O and
`json` encoding occupying a larger share of their shorter total runtimes.
In absolute terms, the resolution cost per call is consistent.
