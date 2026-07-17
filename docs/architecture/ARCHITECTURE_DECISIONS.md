# Architecture Decision Records

Every major permanent decision made during AILang development, preserved so that future contributors understand why things are the way they are.

---

## ADR-001: Recursion-Only Iteration

**Problem:** AILang needs a way to express repeated computation.

**Decision:** Provide recursion as the only iteration mechanism. No `while`, `for`, or `loop` keywords.

**Reason:**
- Eliminates an entire class of compiler complexity (loop unrolling, break/continue, loop variable scoping)
- Maintainers write recursive helpers once (see `examples/patterns/`) and reuse them
- Forces explicit state management — no loop-carried mutation hidden in body
- AI models generate recursive functions more reliably than loop variants in this language

**Alternatives Considered:**
- `while` loops — added parsing complexity, break/continue semantics, variable scoping questions
- `for` loops — iterator protocol, range expressions, loop variable scoping
- Scheme-style named `let` — elegant but unfamiliar to most users
- Combinators (map/filter/reduce as builtins) — could complement recursion, rejected to keep core minimal

**Evidence:** 10/10 benchmarks use recursion for iteration. All 42 benchmark apps compile and run. ~6,610 LOC of AILang built with recursion only.

**Status:** Accepted. Permanent.

**Future Impact:** Any future iteration mechanism must justify its addition against the evidence bar (≥6 benchmarks demonstrating the issue). Recursion patterns are well-established in `examples/patterns/`.

---

## ADR-002: No Loop Constructs

**Problem:** Whether to add `while` or `for` to the language.

**Decision:** Do not add them. Recursion is sufficient.

**Reason:** Same as ADR-001. Loops would add complexity without solving any problem that recursion cannot solve. The governance process requires ≥6 benchmarks demonstrating a deficiency before a language change; no benchmark has shown loop necessity.

**Alternatives Considered:** See ADR-001.

**Evidence:** 0/10 benchmarks required loops. All programs express iteration via recursive helper + wrapper functions.

**Status:** Accepted. Permanent.

**Future Impact:** If future applications genuinely require loop constructs, ADR-001 and ADR-002 must be revisited with evidence.

---

## ADR-003: No Short-Circuit Evaluation (Eager `&&`/`||`)

**Problem:** Whether `&&` and `||` should short-circuit (skip right operand when left determines the result).

**Decision:** Both operands always evaluate. `&&` and `||` are eager.

**Reason:**
- Simpler evaluation model — no conditional branches at the operator level
- Predictable execution order — both sides always execute, so side effects (if any) are deterministic
- Avoids subtle bugs where short-circuit behavior is assumed but not guaranteed

**Alternatives Considered:**
- Standard short-circuit `&&`/`||` — requires conditional compilation in IR, adds complexity
- Bitwise operators only — would require explicit `if` for conditional logic

**Evidence:** 3/10 benchmarks were initially caught by eager `&&`. After documentation in the Playbook and use of nested `if`, all programs run correctly. The nested `if` pattern is clear and explicit.

**Status:** Accepted. Permanent.

**Future Impact:** All future code must use nested `if` when the right operand depends on the left. This is documented in AGENTS.md Hard Rules.

---

## ADR-004: Bottom-Up Function Ordering (No Forward References)

**Problem:** The compiler must resolve function calls to function definitions. Without forward references, call order matters.

**Decision:** Functions must be defined before they are called (no forward references). Write in bottom-up dependency order: Level 0 utilities → Level N `main()`.

**Reason:**
- Eliminates need for multi-pass resolution or call-graph analysis in the compiler
- Single-pass compilation is simpler, faster, and more deterministic
- Forces authors to think about dependencies before writing code

**Alternatives Considered:**
- Multi-pass compiler — adds complexity disproportionate to benefit for the language size
- Forward declaration stubs — adds boilerplate, easy to forget
- Lazy resolution at runtime — defeats compile-time error checking

**Evidence:** 100% of first compiles fail without dependency planning. After adopting bottom-up ordering, 100% of 10 benchmarks compile on first attempt.

**Status:** Accepted. Permanent.

**Future Impact:** Files beyond ~100 functions / ~1000 LOC become challenging to order correctly. Multi-file programs mitigate this via module imports.

---

## ADR-005: Static Lexical Scoping (Not Dynamic)

**Problem:** How variable names are resolved to bindings.

**Decision:** Static (lexical) scoping. A variable reference resolves to the innermost enclosing scope at definition time. The scope chain is established by the program structure, not the call stack.

**Reason:**
- Most intuitive scoping model for imperative programs
- Enables compile-time scope analysis
- Compatible with the variable lookup cache optimization (ADR-006)
- AI models generate lexically-scoped code more reliably

**Alternatives Considered:**
- Dynamic scoping — would make variable resolution call-stack-dependent, breaking many optimizations
- Lisp-like special variables — would require explicit declaration mechanism
- All names global — simple but impractical for programs of any size

**Evidence:** All 42+ benchmark apps use lexical scoping. Shadowing is well-understood and tested.

**Status:** Accepted. Permanent.

**Future Impact:** The variable lookup cache (ADR-006) depends entirely on lexical scoping. Any future change to dynamic scoping or scope injection would require invalidating the cache design.

---

## ADR-006: Lexical Variable Lookup Cache

**Problem:** `Environment.resolve()` consumed 85.4% of wall-clock execution time in the static analyzer (1.6M calls, 230M chain walks). Variable resolution was the overwhelming performance bottleneck.

**Decision:** Add a per-environment `_resolve_cache: dict[str, Environment]` that stores the binding's owning environment after the first successful resolution. Subsequent lookups from the same environment are O(1).

**Reason:**
- Cache stores binding location, not value — no invalidation needed for `assign`
- Cache is per-environment — shadowing is safe because inner/outer caches are independent
- ~20 lines of Python, no semantic changes, no risk to correctness
- 6× speedup on the worst-case workload

**Alternatives Considered:**
- Per-frame cache — invalidated on every `assign`, ephemeral frames reduce hit rate
- Global name-to-scope table — equivalent to lexical addressing, requires IR changes
- LRU cache — unnecessary for small environment caches (5–20 entries)
- No optimization — static analyzer remains at 373s, effectively unusable

**Evidence:**
- `Environment.resolve` was 85.4% of static analyzer runtime before caching
- Post-cache: 52–64% cache hit rate, ~6× speedup (373s → 19.5s)
- ~11 KB additional memory overhead
- 624/624 tests pass
- All 5 benchmark apps produce byte-identical output
- Negative caching removed after discovering `assign`-can-create-bindings edge case

**Status:** Accepted v0.2.0. Permanent for the current lexical scoping model.

**Future Impact:** See `docs/runtime/lookup_cache/design.md` §6 for conditions that would invalidate the cache (dynamic modules, hot reloading, dynamic scope).

---

## ADR-007: Evidence-First Optimization Policy

**Problem:** How to decide which performance optimizations merit implementation effort.

**Decision:** No optimization shall be implemented without profiler evidence identifying the hotspot and confirming that the optimization would address it. Optimizations must be:
1. Observed (profiler identifies hotspot)
2. Measured (baseline timing recorded)
3. Root-caused (hotspot is the actual bottleneck, not a symptom)
4. Minimal (smallest change that addresses the bottleneck)
5. Benchmarked (before/after comparison)
6. Regression-tested (no semantic changes)

**Reason:**
- Prevents wasted effort on speculative optimizations
- Ensures every optimization has measurable impact
- Prevents premature optimization from adding complexity without benefit

**Alternatives Considered:**
- Ad-hoc optimization — risks investing in nonexistent bottlenecks
- Design-for-performance — conflicts with the "minimal" principle; complexity before evidence

**Evidence:** The variable lookup cache optimization (ADR-006) followed this policy precisely: profiler → hotspot identified → optimization designed → benchmarked → merged. No other optimization has been proposed that meets the evidence bar.

**Status:** Accepted. Permanent.

**Future Impact:** Any proposed optimization must include profiler evidence. See `docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md` — Performance Engineering Workflow.

---

## ADR-008: Standard Library Philosophy

**Problem:** What goes into the standard library and what must be written by users.

**Decision:** The standard library is minimal and stable. It provides:
- Fundamental data types and their operations (string, list, map, set)
- File and path I/O (file, path)
- Serialization (json, csv)
- Utilities (math, convert, time, random, io, system, environment)
- Functions are added only when ≥2 independent benchmarks demonstrate the need

**Reason:**
- Keeps the stdlib small, well-tested, and well-documented
- Prevents feature creep into the stdlib
- Forces evidence-based additions rather than speculative inclusion

**Alternatives Considered:**
- Batteries-included stdlib (Python-style) — would triple the maintenance burden
- No stdlib at all — every program would reimplement string operations

**Evidence:**
- 16 stdlib modules, all documented in `docs/reference/STDLIB_REFERENCE.md`
- Missing functions (split, find, join, sort, list.copy) are confirmed needs across multiple benchmarks but not yet meeting the ≥2 bar for stdlib inclusion after the governance process was established
- All missing-function patterns are documented in `examples/patterns/`

**Status:** Accepted. Stable.

**Future Impact:** Stdlib additions follow the governance process in `PROJECT_MEMORY.md`.

---

## ADR-009: AI-First Development Workflow

**Problem:** How to ensure that AI models can reliably generate correct AILang code.

**Decision:** The entire development process is optimized for AI generation:
1. All project knowledge is documented in single-source-of-truth files (`AGENTS.md`, `PROJECT_MEMORY.md`, `docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md`)
2. These files are auto-consumed by AI tools (Claude Code, Cursor, Windsurf, Copilot)
3. Every engineering lesson discovered in ≥2 independent apps is promoted to permanent documentation
4. The language syntax is designed for unambiguous AI generation (explicit braces, no significant whitespace, no context-sensitive parsing)

**Reason:**
- AILang's primary use case is AI-assisted development
- Every iteration eliminated by upfront planning is an iteration the AI does not need to debug
- Documentation-as-code ensures AI always has access to current knowledge

**Alternatives Considered:**
- Traditional human-first documentation — misses AI-specific needs like structured consumption
- No AI-specialization — would make AILang just another niche language

**Evidence:**
- 100% build+run achieved for all 10 benchmarks after playbook methodology
- Compile iterations: ~0 (was 10/10)
- Runtime iterations: ~0 (was 100% of benchmarks had at least 1)

**Status:** Accepted. Permanent.

**Future Impact:** Any new documentation must be AI-consumable (structured, referenced from AGENTS.md). The Benchmark Feedback Loop ensures continuous improvement of AI guidance.

---

## ADR-010: Consolidate Package Manager Code

**Problem:** `compiler/package/registry.py` and `tools/ail_package_manager/registry.py` are near-identical copies of the same registry client, creating confusion about which is authoritative.

**Decision:** Merge `compiler/package/registry.py` into `tools/ail_package_manager/registry.py`. Remove the `compiler/package/` directory. Wire all package management through `tools/ail_package_manager/`.

**Reason:**
- Two copies create divergence risk (they already differ slightly)
- The `tools/` copy is more complete (typed models, checksum verification)
- The `compiler/` copy is used only by `cmd_publish`
- Single source of truth eliminates maintenance burden

**Alternatives Considered:**
- Keep both copies — ongoing divergence risk
- Move everything to `compiler/package/` — would break the standalone tool pattern

**Evidence:** `compiler/package/registry.py` (264 LOC) vs `tools/ail_package_manager/registry.py` (360 LOC) — the `tools/` version is strictly more complete.

**Status:** Accepted. M77 phase 1.

**Future Impact:** All package management code lives in `tools/ail_package_manager/`. The `compiler/cli/main.py` commands import from there.

---

## ADR-011: `ail new` is the Public API, `ail init` is Internal

**Problem:** User docs (PACKAGES.md) document `ail new` while the design doc (PACKAGE_MANAGER_DESIGN.md) specifies `ail init`.

**Decision:** `ail new` remains the user-facing command for project scaffolding. `ail init` (if kept) is an internal alias used by the package manager tool.

**Reason:**
- `ail new` is documented in PACKAGES.md and has been the public API since v1.0.8
- Changing it would break existing documentation and user muscle memory
- `ail init` exists in `tools/ail_package_manager/init.py` but is not wired to the main CLI
- No breaking change required

**Alternatives Considered:**
- Rename `ail new` to `ail init` — breaking change, documentation churn
- Wire `ail init` to the main CLI as an alias — adds confusion about which to use

**Evidence:** `ail new` appears in 3+ user-facing documents. `ail init` appears only in the design doc and the standalone tool.

**Status:** Accepted. M77 phase 1.

**Future Impact:** `ail new` stays in main CLI dispatch. `ail init` stays in `tools/ail_package_manager/__main__.py` for internal use only.

---

## ADR-012: Local-First, Registry-Ready Architecture

**Problem:** Whether to implement a remote registry server for M77, or design for it but defer.

**Decision:** M77 implements full package management for local path and git dependencies. Registry support is designed but not implemented (server does not exist). The architecture must not block future registry addition.

**Reason:**
- Per PACKAGE_MANAGER_DESIGN.md §3.3, the official registry is out of scope for v1
- Building a registry server is a separate project (infrastructure, hosting, auth)
- Designing for registry-ready architecture means the API surface is stable when a registry is added later
- Local directory registry provides a working publish/install flow for teams

**Alternatives Considered:**
- Build a minimal registry server — scope creep, hosting requirements, auth complexity
- Skip registry design entirely — would require API redesign when registry is added

**Evidence:** The existing `registry.py` already has both `publish_local()` and `publish_remote()` functions. The remote path is implemented but requires a server.

**Status:** Accepted. M77 phase 1.

**Future Impact:** All resolver and installer interfaces accept a `source_type` parameter that can be extended. Registry client code is retained but marked as `@future`.

---

## ADR-013: Semver Range Parsing

**Problem:** The current resolver only handles exact match or `*` (latest). Real package management requires version ranges.

**Decision:** Implement full semver range parsing (>=, ^, ~, exact, range) using a standalone `_parse_version_requirement()` function. No external dependency.

**Reason:**
- `^1.0.0` is the most common constraint format in package managers (Cargo, npm)
- Without ranges, users must pin exact versions, making dependency management brittle
- Semver 2.0 parsing is well-defined and implementable in ~80 lines
- No external dependency (stdlib only) — respects ADR-001 constraint

**Alternatives Considered:**
- Exact-only (current) — too restrictive for real use
- npm-style complex ranges — over-engineered for v1
- Cargo-style ranges — good balance, adopted

**Evidence:** Cargo, npm, and pip all support semver ranges. AILang's design doc (§10) specifies SemVer 2.0.

**Status:** Accepted. M77 phase 2.

**Future Impact:** All version constraints in `ail.toml` support range operators. The resolver uses `_parse_version_requirement()` for all constraint evaluation.

---

## ADR-014: Dependency Conflict Detection

**Problem:** Without conflict detection, `ail install` silently installs whatever version it encounters last, leading to non-reproducible builds.

**Decision:** Implement conflict detection during resolution. When two packages require incompatible versions of the same dependency, emit a clear diagnostic with the conflicting constraints and suggested resolution.

**Reason:**
- Silent version resolution leads to runtime errors that are hard to diagnose
- Clear conflict messages with suggested fixes reduce developer friction
- Conflict detection is O(n) in the number of constraints — negligible performance cost
- Exit code on conflict prevents broken installations

**Alternatives Considered:**
- Silent "last wins" (current behavior) — non-reproducible, hides bugs
- Auto-upgrade to highest compatible — may break packages that depend on specific versions

**Evidence:** Cargo and npm both detect conflicts and report them clearly. npm v7+ made conflict detection the default behavior.

**Status:** Accepted. M77 phase 3.

**Future Impact:** Resolution algorithm tracks all constraints per package name. On conflict: collect all constraints, find intersection, report if empty.

---

## ADR-015: Circular Dependency Detection

**Problem:** Circular dependencies are undefined in AILang (no loops, no lazy evaluation). They must be detected at install time, not at runtime.

**Decision:** Track the resolution path and detect cycles. On cycle, emit diagnostic with the cycle path.

**Reason:**
- AILang has no lazy evaluation — circular deps would cause infinite recursion
- Detection at install time prevents cryptic runtime errors
- Resolution path tracking is O(depth) in memory — negligible cost
- Clear cycle path in diagnostic helps developers understand the problem

**Alternatives Considered:**
- Detect at runtime — too late, wastes developer time
- Prohibit all cycles in packages — too strict, may block valid use cases (e.g., mutually recursive modules within a package)
- Allow cycles with lazy evaluation — language change, out of scope

**Evidence:** Cargo detects circular dependencies at build time. npm detects them at install time. Both report the cycle path.

**Status:** Accepted. M77 phase 4.

**Future Impact:** Resolution maintains a `resolution_path: list[str]` stack. Before recursing into a dep, check if it's already in the path. On cycle: report `CIRCULAR: A → B → C → A`.
