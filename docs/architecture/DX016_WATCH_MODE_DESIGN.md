# DX-016 — Watch Mode (Incremental Compilation)

**Status:** Design Proposal — v0.10.0 (M23)  
**Type:** P1 Developer Experience Tool  
**Requirement:** Benchmark B5–B6 identified edit–compile–fix latency as a top-3 AI friction point  

---

## 1. Problem

Current workflow: edit `.ail` file → `ail build <file>` → see error → fix → `ail build <file>` → ...

Each compile is a **full session**:
- FileWatcher re-scans all `.ail` files
- Parser re-parses every file
- Semantic analyzer re-resolves every symbol
- Type checker re-checks every expression
- IR builder re-compiles every function

For the Inventory benchmark (4,009 LOC across 28 files), a full compile takes ~2.8 seconds. During AI code generation, where individual edits are small (1–5 functions), this becomes the dominant latency.

**The AI should get sub-100ms feedback on single-file edits.**

### Benchmark Measurement

| Edit Type | Current Latency | Target |
|-----------|:---------------:|:------:|
| Fix one function body | 2,800 ms | **<50 ms** |
| Add one function to existing file | 2,800 ms | **<100 ms** |
| Add one file with import | 2,800 ms | **<500 ms** |
| Initial full compile | 2,800 ms | **(no change)** |

---

## 2. Non-Goals

| Not in scope | Reason |
|-------------|--------|
| Hot-reload (re-run on change) | Watch mode compiles only. Re-run is `ail run`. Hot-reload would require runtime state management — P0 for v0.11.0 |
| HMR (Hot Module Replacement) | Requires runtime module system. AILang modules are compile-time only |
| Language server protocol (LSP) | LSP is a separate initiative (DX-017). Watch mode provides CLI feedback only |
| Distributed / remote compilation | Single-machine only |
| Cross-platform filesystem watcher abstraction | Use existing Python libraries (`watchdog`). No custom platform code |

---

## 3. CLI Specification

```
ail watch [<entry_file>] [options]
```

### Positional Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `entry_file` | Optional entry point to watch. If omitted, watches the entire repo | Current directory |

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--poll` | Use polling instead of filesystem events (for network filesystems) | `false` |
| `--poll-interval` | Polling interval in milliseconds (only with `--poll`) | `500` |
| `--verbose` | Log every file check (skip vs compile) | `false` |
| `--no-initial` | Skip initial full build | `false` |
| `--json` | Output machine-readable JSON (for AI tooling) | `false` |

### Exit Codes

| Code | Meaning |
|:----:|---------|
| 0 | Watch mode terminated (user Ctrl+C) |
| 1 | Initial build failed |
| 2 | Filesystem watcher failed to start |

### Output Format (Human)

```
$ ail watch
[14:30:00] ail watch — watching 28 files in C:\repo
[14:30:01] Initial build: 28 files, 0 errors, 0 warnings (2.8s)
[14:30:15] CHANGE: src/entities/supplier.ail (modified)
[14:30:15]   Compile: supplier.ait — OK (12ms)
[14:30:15]   Recompile: catalog/supplier_map.ail — OK (8ms)
[14:30:15]   Recompile: catalog/import.ail — OK (6ms)
[14:30:15]   Total: 3 files recompiled (26ms)
[14:30:22] CHANGE: src/entities/supplier.ail (modified)
[14:30:22]   Compile: supplier.ail — ERROR (15ms)
[14:30:22]     supplier.ail:34:12  ERROR SEM002: Undefined identifier: nonexistent_fn
[14:30:22]   Total: 1 file compiled — 1 error
[14:30:30] CHANGE: src/entities/supplier.ail (modified)
[14:30:30]   Compile: supplier.ail — OK (11ms)
[14:30:30]   Recompile: catalog/supplier_map.ail — OK (7ms)
[14:30:30]   Recompile: catalog/import.ail — OK (5ms)
[14:30:30]   Total: 3 files recompiled (23ms)
[14:30:30] Build: 3 files, 0 errors, 0 warnings
```

### Output Format (JSON)

```json
{
  "type": "change",
  "timestamp": "2026-07-10T14:30:15Z",
  "changed_file": "src/entities/supplier.ail",
  "status": "success",
  "files": [
    { "file": "src/entities/supplier.ail", "status": "compiled", "time_ms": 12 },
    { "file": "src/catalog/supplier_map.ail", "status": "recompiled", "time_ms": 8 },
    { "file": "src/catalog/import.ail", "status": "recompiled", "time_ms": 6 }
  ],
  "total_time_ms": 26,
  "errors": [],
  "warnings": []
}
```

---

## 4. Cache System

### Per-File Compilation Cache

Each `.ail` file has a cache entry:

```python
@dataclass
class CompilationCacheEntry:
    # Identity
    file_path: str
    file_hash: str              # SHA-256 of source content at time of compile
    
    # Compilation artifacts
    ast: ModuleNode | None
    semantic_ok: bool
    type_checks: list[TypeCheckResult]
    ir_module: IRModule | None
    
    # Dependencies
    imports: list[str]          # Module names this file imports
    exported_symbols: set[str]  # Functions/vars defined in this file
    
    # Timing
    compile_time_ms: float
    last_compiled: datetime
```

### Cache Invalidation

When a file change is detected:

```
on_file_change(file_path):
    1. Read file content
    2. Compute SHA-256 hash of new content
    3. If hash == cached_hash:
         skip — no meaningful change (false positive from watcher)
    4. Invalidate this file's cache entry
    5. Recompile this file (see §5)
    6. If recompile succeeds:
         check if exported symbols changed
         if exports changed OR --full-dependents:
           find all files that (transitively) import from this file
           invalidate their caches
           recompile each dependent
         else:
           # Exports unchanged — dependents still valid
           # (Only re-dependents that reference changed internal details)
           # Conservative: always recompile dependents
           recompile all transitive dependents
    7. Report result
```

**Decision on recompilation strategy:** Always recompile transitive dependents. The optimization of checking export stability is left for v0.10.1 — the risk of stale IR from undetected semantic changes is not worth the latency savings at this stage.

### Cache Storage

- **Storage location:** In-memory `dict[str, CompilationCacheEntry]` — the watch process keeps the compiler session alive
- **Size:** ~50 KB per file (AST + IR). For 200 files: ~10 MB. Negligible memory cost
- **Lifetime:** Entire watch session. Cache is discarded when watch terminates
- **On-disk persistence:** Not needed. Cold start is a full build (2–3 seconds). The first build always runs on session start

### Cache Index

```python
CompilationCache:
    entries: dict[str, CompilationCacheEntry]     # file_path → entry
    dependents: dict[str, list[str]]               # module_name → list of dependent file paths
    build_count: int                               # Successful recompilations
    total_errors: int                              # Errors since session start
```

The `dependents` map is built from the imports of each file:

```python
def build_dependents_index(cache: CompilationCache):
    for file_path, entry in cache.entries.items():
        for imported_module in entry.imports:
            # Find which .ail file provides this module
            provider = module_resolver.resolve(imported_module)
            if provider:
                cache.dependents.setdefault(provider, []).append(file_path)
```

---

## 5. Incremental Compilation Flow

### Single-File Edit Latency Budget

Target: **<50 ms** for a single-file edit with no dependents.

| Phase | Budget | Scaling |
|-------|:------:|---------|
| File change detection | 5 ms | O(file count) with polling, O(event volume) with FS events |
| Hash computation | 2 ms | O(file size) |
| Cache lookup | 1 µs | O(1) |
| Parse | 5 ms | O(file size) — single file |
| Semantic analysis | 10 ms | O(symbol count) — single file |
| Type checking | 10 ms | O(expression count) — single file |
| IR build | 10 ms | O(node count) — single file |
| Dependent walk + recompile | Varies | O(dependent file count × compile cost per file) |
| Output formatting | 2 ms | O(output size) |

**Leaf file edit (no dependents):** ~44 ms — within target.  
**Dependent file edit (N dependents):** ~44 ms + N × ~30 ms — acceptable up to ~15 dependents.

### Algorithm Detail

```
incremental_compile(changed_file_path):
    start = now()
    
    # 1. Read and hash
    new_content = read_file(changed_file_path)
    new_hash = sha256(new_content)
    cached = cache.get(changed_file_path)
    
    if cached and cached.file_hash == new_hash:
        return  # No real change (spurious watcher event)
    
    # 2. Reset compilation modules
    #    The compiler needs to be partially reset. Which parts are reusable?
    
    # 3. Parse
    try:
        new_ast = parse(new_content)
    except ParseError as e:
        report_error(changed_file_path, e)
        cache.invalidate(changed_file_path)
        return
    
    # 4. Semantic analysis (single file)
    try:
        semantic_result = analyze(new_ast, module_registry)
    except SemanticError as e:
        report_error(changed_file_path, e)
        cache[changed_file_path] = error_entry(new_hash)
        return
    
    # 5. Type checking (single file)
    try:
        type_result = type_check(new_ast, type_registry)
    except TypeError as e:
        report_error(changed_file_path, e)
        cache[changed_file_path] = error_entry(new_hash)
        return
    
    # 6. IR build (single file)
    ir = build_ir(new_ast)
    
    # 7. Update cache
    cache[changed_file_path] = CompilationCacheEntry(
        file_path=changed_file_path,
        file_hash=new_hash,
        ast=new_ast,
        semantic_ok=True,
        type_checks=type_result,
        ir_module=ir,
        imports=extract_imports(new_ast),
        exported_symbols=extract_exports(new_ast),
        compile_time_ms=(now() - start),
        last_compiled=now()
    )
    
    # 8. Recompile dependents
    dependents = find_dependents(changed_file_path, cache)
    for dep in transitive_closure(dependents, cache):
        incremental_compile_dependent(dep)
    
    # 9. Report
    total_time = now() - start
    report_result(changed_file_path, total_time, dependents)
```

### Dependent Compilation

Dependent files need a full recompile (parse → semantic → type → IR) because:

- Their AST references types/functions from the changed file
- Even if exports are stable, internal implementation details affect inlining or type propagation
- Conservative correctness is preferred over incremental complexity for v0.10.0

However, dependent compilation reuses the **cache's module registry** — the changed file's new exports are already registered. No full-session rebuild is needed.

---

## 6. Dependency Graph

### Graph Structure

The dependency graph is a directed graph where:

- **Nodes:** `.ail` file paths (module names)
- **Edges:** Module A → Module B if A imports B
- **Direction:** Import direction (A depends on B)

```python
DependencyGraph:
    nodes: set[str]                          # All module file paths
    edges: dict[str, list[str]]              # module → list of imported modules
    dependents: dict[str, list[str]]         # module → list of modules that import it
    entry_points: list[str]                  # Modules with "main" function
```

### Construction

The graph is built during the initial compilation:

```python
def build_dependency_graph(cache: CompilationCache) -> DependencyGraph:
    graph = DependencyGraph()
    for file_path, entry in cache.entries.items():
        graph.nodes.add(file_path)
        graph.edges[file_path] = entry.imports
        for imp in entry.imports:
            provider = module_resolver.resolve(imp)
            if provider:
                graph.dependents.setdefault(provider, []).append(file_path)
    return graph
```

### Cycle Detection

AILang does not support circular imports. The dependency graph must remain a DAG. Watch mode enforces this:

```
on_add_file(file_path):
    if add_file_to_graph(file_path) creates cycle:
        report_error(f"Circular import detected: {file_path}")
        remove_file_from_graph(file_path)
        return
```

### Transitive Closure

To find all files affected by a change:

```python
def transitive_closure(file_path: str, graph: DependencyGraph) -> list[str]:
    visited = set()
    result = []
    queue = [file_path]
    
    while queue:
        current = queue.pop(0)
        for dependent in graph.dependents.get(current, []):
            if dependent not in visited:
                visited.add(dependent)
                result.append(dependent)
                queue.append(dependent)
    
    return result
```

This is a simple BFS from the changed node following `dependents` edges. Since the graph is a DAG, no cycle detection is needed during traversal.

---

## 7. File Change Detection

### Platform-Specific Filesystem Watchers

| Platform | Library / Mechanism | Notes |
|----------|-------------------|-------|
| Windows | `watchdog` → `ReadDirectoryChangesW` | Native API. No polling required |
| macOS | `watchdog` → `FSEvents` / `kqueue` | Native. Efficient |
| Linux | `watchdog` → `inotify` | Native. Efficient |
| All | `watchdog` → Polling (fallback) | Required for network FS, WSL, Docker |

### Implementation Decision

Use the `watchdog` Python library, which provides a uniform interface across all platforms:

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AILangWatchHandler(FileSystemEventHandler):
    def __init__(self, compiler, cache):
        self.compiler = compiler
        self.cache = cache
    
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.ail'):
            self.compiler.incremental_compile(event.src_path)
    
    def on_created(self, event):
        if event.src_path.endswith('.ail'):
            self.cache.add_file(event.src_path)
            # .ail files are self-contained; no config required
    
    def on_deleted(self, event):
        if event.src_path.endswith('.ail'):
            # Remove from cache and dependency graph
            self.cache.remove_file(event.src_path)
            report_warning(f"File deleted: {event.src_path}")
    
    def on_moved(self, event):
        if event.src_path.endswith('.ail') and event.dest_path.endswith('.ail'):
            # rename within repo
            self.cache.move_file(event.src_path, event.dest_path)
```

### Debouncing

Filesystem events can fire multiple times for a single save (especially editors that write atomically). A debounce mechanism prevents redundant compilations:

```python
class DebouncedHandler:
    def __init__(self, handler, delay_ms=100):
        self.handler = handler
        self.delay_ms = delay_ms
        self.timers = {}
    
    def on_modified(self, event):
        # Cancel any pending timer for this file
        if event.src_path in self.timers:
            self.timers[event.src_path].cancel()
        # Schedule compilation after debounce window
        self.timers[event.src_path] = Timer(
            self.delay_ms / 1000.0,
            self.handler.on_modified,
            args=[event]
        )
        self.timers[event.src_path].start()
```

Debounce window: **100 ms** — prevents duplicate compiles from editor atomic-save patterns (write → mv → notify × 2–3) while keeping latency under 200 ms total.

### Polling Fallback

When filesystem events are unavailable (NFS, Docker, WSL cross-fs), polling mode reads all `.ail` files every N milliseconds and compares hashes:

- `--poll-interval` default: **500 ms** (500 ms latency is acceptable for AI — still faster than manual `ail build`)
- On each poll: compute SHA-256 of every `.ail` file, compare against cached hashes
- Changes detected: trigger incremental compile for changed files
- Removed files: detect via missing entries from file system scan

---

## 8. Performance Budget

### Latency Targets

| Scenario | Target | Measurement Method |
|----------|:------:|--------------------|
| Single-file edit, no dependents | **<50 ms** | `time()` around incremental_compile |
| Single-file edit, 3 dependents | **<200 ms** | Same |
| Add new file (1 import) | **<500 ms** | Includes first compile + graph update |
| Delete file with 5 dependents | **<5 ms** | Cache invalidation only. No compilation |
| Rename file (2 files changed) | **<100 ms** | Recompile + graph update |
| Initial full build (28 files) | **<3,000 ms** | No change from current |
| False positive watcher event | **<1 ms** | Hash comparison, no compile |

### Scalability Bounds

| Metric | Budget | Notes |
|--------|:------:|-------|
| Max files in watch | 5,000 | 5k × ~50 KB cache = 250 MB RAM |
| Max dependents per file | 500 | Transitive closure BFS over 500 nodes: <1 ms |
| Max single-compile time | 50 ms per file | Parser + semantic + type + IR |
| Max concurrent file changes | 10 files | Debounce coalesces. Sequential compilation |

---

## 9. Compiler Session Reuse

Watch mode keeps the compiler session alive. Key session-level state that survives across recompilations:

| Component | Reused? | Notes |
|-----------|:-------:|-------|
| Module registry | Yes | Maps module names to file paths. Updated when files added/removed |
| Type registry | Yes | Maps type names to type definitions. Updated incrementally |
| Token cache | No | Tokens are ephemeral. Re-parsed each compile |
| Symbol table | Partially | Per-file symbol table rebuilt. Cross-file references resolved via module registry |
| Error collector | Yes | Accumulated across compilations. Cleared on successful build |
| Import resolver | Yes | Module path resolution. Read-only. Never changes within a session |

### Session Lifecycle

```python
class WatchSession:
    def __init__(self, root_dir, options):
        self.root_dir = root_dir
        self.options = options
        self.cache = CompilationCache()
        self.session = CompilerSession(root_dir)  # Reused across compiles
        self.error_count = 0
        self.build_count = 0
    
    def initial_build(self):
        result = self.session.build_all(self.root_dir)
        self.cache.populate_from(result)
        return result
    
    def on_file_change(self, file_path):
        # Reuse self.session — don't create a new one
        result = self.session.incremental_compile(file_path, self.cache)
        self.cache.update(file_path, result)
        for dep in result.dependents:
            dep_result = self.session.compile_dependent(dep, self.cache)
            self.cache.update(dep, dep_result)
        return result
    
    def stop(self):
        self.session.close()
```

### Partial Reset

When a dependent file needs recompilation, the session's module and type registries must reflect the changed file's new exports before processing dependents:

```
compile_dependent(dep_path, cache):
    # Before recompiling dep, ensure its imports point to fresh exports
    for import_name in cache[dep_path].imports:
        provider = module_registry.resolve(import_name)
        if cache[provider].is_stale:
            # Recursive: parent should have already recompiled this
            pass  # Guaranteed by transitive closure ordering
    
    # Recompile dependent with fresh module registry
    compile(dep_path, module_registry, type_registry)
```

---

## 10. Cooldown / Batch Handling

### Burst File Changes

When the AI generates multiple files in rapid succession (e.g., a benchmark generates 5 files at once), watch mode must avoid 5 separate compile cycles.

**Strategy: Debounce + Cooldown**

1. Each file change starts a 100 ms debounce timer
2. After the last debounce fires, start a **200 ms cooldown** timer
3. During cooldown, collect all changed files
4. After cooldown: process all changed files as a batch

```
Time 0 ms:     File A modified → debounce timer starts (100 ms)
Time 20 ms:    File B modified → debounce timer starts (100 ms)
Time 100 ms:   Debounce fires → cooldown timer starts (200 ms)
Time 110 ms:   File C modified → restart cooldown (200 ms, no debounce needed)
Time 310 ms:   Cooldown expires → batch compile A, B, C
```

**Batch compile:** Process changed files in dependency order (lower-level files first). After each file's compile, invalidate dependent caches. After all files are compiled, recompile all affected dependents (exactly once each, not N times for N changed files).

### Total Latency for Batch

| Scenario | Latency |
|----------|:-------:|
| AI generates 5 new files | ~500 ms debounce/cooldown + ~250 ms compile = **~750 ms** |
| AI edits 3 existing files | ~500 ms debounce/cooldown + ~150 ms compile = **~650 ms** |
| Single user save | ~100 ms debounce + ~44 ms compile = **~144 ms** |

---

## 11. Rollback / Error Recovery

### On Compilation Error

- The previous successful compilation remains in cache
- The erroring file's cache entry is updated with the error state
- Dependent files are NOT recompiled (they would fail if the changed file's exports are needed)
- The error is displayed prominently
- On next save of the same file: retry from scratch

### On Watcher Failure

- If the filesystem watcher fails (e.g., `inotify` limit reached), fall back to polling mode
- Display a warning to the user: `Event-based watching failed. Falling back to --poll.`
- Continue operation in polling mode

### On Repository Restructure

- If `.ail` files are moved/deleted/renamed in bulk:
  - Watch mode detects each change independently
  - Each deletion removes the file from cache + graph
  - Each creation triggers a fresh compile
  - Existing files that imported deleted files will fail on next compile — expected behavior

---

## 12. Benchmark Impact Estimate

### Latency Comparison

| Operation | Current (`ail build`) | Watch Mode (`ail watch`) | Speedup |
|-----------|:--------------------:|:------------------------:|:-------:|
| Edit 1 function, 1 file | 2,800 ms | **44 ms** | **64×** |
| Edit 1 function, has 3 dependents | 2,800 ms | **~150 ms** | **19×** |
| Add 1 function to leaf file | 2,800 ms | **44 ms** | **64×** |
| Add 1 file (imported by main) | 2,800 ms | **~500 ms** | **5.6×** |
| Fix compile error, retry | 2,800 ms | **44 ms** | **64×** |
| Full rebuild (28 files) | 2,800 ms | 2,800 ms | **1×** |

### AI Turn Reduction

With sub-100 ms feedback, the AI can adopt a **tighter iteration loop:**

```
Without watch:
  generate → "ail build" → wait 2.8s → parse error → fix → "ail build" → 2.8s → ...
  Total for 3 iterations: ~16.8 seconds (3 × 2.8s + generation time)

With watch:
  generate → save file → see result in 44ms → fix → save → see result → ...
  Total for 3 iterations: ~3 seconds (negligible wait)
```

**Estimated AI iteration time reduction: 5× for single-file edits.**

### Risk

| Risk | Severity | Mitigation |
|------|:--------:|------------|
| Platform-specific watcher issues | Medium | Polling fallback always available. Test on Windows/macOS/Linux CI |
| Memory leak from long-running session | Medium | Monitor cache size. Set 5,000-file upper bound with warning |
| Stale cache after external file edit | Low | Inotify watches cover all edits. Polling fallback covers edge cases |
| Compile error spam during rapid editing | Low | Cooldown batching suppresses intermediate errors. Only final state reported |
| Cache consistency after complex rename | Low | `on_moved` handler updates graph. Dependents recompile |

---

## 13. Implementation Plan

### Phase 1: Cache System

| Component | Description | LOC |
|-----------|-------------|:---:|
| `CompilationCacheEntry` | Dataclass. Stores hash, AST, IR, exports | ~40 |
| `CompilationCache` | Dict-based cache with hash-based invalidation | ~80 |
| Dependency graph builder | Build `dependents` index from imports | ~60 |

### Phase 2: Incremental Compilation

| Component | Description | LOC |
|-----------|-------------|:---:|
| `incremental_compile()` | Parse → semantic → type → IR for single file | ~80 |
| `compile_dependents()` | Transitive closure walk + dependent recompile | ~60 |
| `batch_compile()` | Cooldown-based batch processing | ~60 |

### Phase 3: Filesystem Watcher

| Component | Description | LOC |
|-----------|-------------|:---:|
| `AILangWatchHandler` | `watchdog` event handler class | ~80 |
| `DebouncedHandler` | Debounce + cooldown timer management | ~60 |
| Polling fallback | SHA-256 hash comparison polling | ~60 |

### Phase 4: CLI

| Component | Description | LOC |
|-----------|-------------|:---:|
| `ail watch` entry point | Argument parsing, session start | ~60 |
| Human output formatter | Timestamped log lines | ~80 |
| JSON output formatter | Machine-readable output | ~60 |

### Phase 5: Session Management

| Component | Description | LOC |
|-----------|-------------|:---:|
| `WatchSession` | Session lifecycle, cache persistence | ~80 |
| Error recovery | Cache fallback, watcher failure fallback | ~40 |

### Estimated Total: ~820 LOC (Phase 1–5)

### Dependencies

- `watchdog` Python package — 150 KB install. Pure Python. No native compilation needed
- `pywin32` (Windows) — transitive dependency of `watchdog` on Windows

### Testing Strategy

| Test type | Coverage |
|-----------|----------|
| Unit: cache | Invalidation, hash comparison, update, remove |
| Unit: dependency graph | BFS, transitive closure, cycle detection |
| Unit: incremental compile | Parse → IR for single file after cache invalidation |
| Unit: debounce | Timer management, batch collection |
| Integration: file change | Touch `.ail` file, verify recompile |
| Integration: multi-file change | Touch 3 files, verify batch compile |
| Integration: error recovery | Introduce syntax error, fix, recompile |
| Integration: polling mode | Disable events, verify polling detection |
| Performance: 50ms target | Measure 100 single-file edits, report P50/P95/P99 |

---

## 14. Rejected Alternatives

| Alternative | Reason |
|-------------|--------|
| `inotify` directly | Platform-specific. `watchdog` provides uniform interface across all 3 platforms |
| On-disk cache (SQLite) | Adds dependency and complexity. In-memory is fast enough and simpler |
| Thread pool for parallel recompilation | AILang compilation is I/O bound on file reads, not CPU. Single-threaded is simpler and sufficient |
| File-level IR caching (no re-parse) | Without a stable export signature format, re-parsing is the safe choice. Can be optimized in v0.10.1 |
| Automatic `ail run` on successful compile | Changes execution model. Hot-reload is a distinct feature for v0.11.0 |
| Watch by pattern (e.g., `ail watch src/*.ail`) | Watching the entire repo is the common case. Pattern filtering can be added if needed |

---

## 15. Decision

**Verdict:** ACCEPT.

Watch mode solves a measured benchmark friction point: 2.8-second full-compile latency on every AI iteration for the Inventory benchmark. For single-file edits, the target 44 ms latency (64× speedup) maps to a 5× reduction in AI iteration time.

The implementation is self-contained (~820 LOC), uses the well-maintained `watchdog` library for cross-platform file watching, and preserves the existing compiler pipeline — incremental compilation is a caching layer on top of the existing phases.

Key design decisions:
- **In-memory cache** — no on-disk persistence. Cold start is a full build (acceptable for the first compile)
- **Always recompile dependents** — conservative correctness. Export-stability optimization deferred
- **Debounce + cooldown** — handles rapid AI generation bursts without redundant work
- **Polling fallback** — ensures compatibility with network filesystems and WSL
- **Session reuse** — module registry and type registry survive across recompilations
