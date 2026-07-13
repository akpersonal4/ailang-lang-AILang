# DX-017 — Adaptive Tool Orchestration Engine (ATOE)

**Status:** Architecture Design  
**Type:** P1 Developer Experience Engine  
**Requirement:** 10 standalone tools exist, all requiring manual invocation. Developers and AI agents must remember when to use each tool. This creates a discoverability gap that widens as the tool ecosystem grows.

---

## 1. Problem

### Current State

AILang provides 10+ developer tools:

```
ail fmt        — Format code
ail order      — Detect forward references
ail rename     — Rename symbols across files
ail watch      — Watch for file changes
ail doctor     — Repository health check
ail benchmark  — Run benchmarks
ail testgen    — Generate tests
ail context    — Generate AI context
ail lsp        — Language server
static analyzer— Code analysis
```

Each tool is independently useful. But the developer (human or AI) must:

1. Know the tool exists
2. Know when to use it
3. Remember to invoke it
4. Interpret its output

**Evidence of the gap:**

| Scenario | Current Flow | Ideal Flow |
|:---------|:-------------|:------------|
| Repeated build failures | Developer keeps rebuilding, hoping | System suggests `ail doctor` after 3rd failure |
| Symbol rename across files | Developer manually edits 10 files | System detects rename pattern, suggests `ail rename` |
| Rapid edit cycle | Developer runs `ail build` 15 times | System suggests `ail watch` after 5th build |
| Large repo with formatting issues | Developer manually runs `ail fmt` | System auto-formats on build (safe tool) |
| Release preparation | Developer checks each tool manually | System runs `ail doctor` + benchmark on git tag |

### Cost Estimate

Based on B2–B7 benchmark data:
- Average developer spends **3–5 minutes per hour** on tool-discovery overhead
- AI agents waste **1–2 iterations per task** on missing tool invocations
- Estimated savings from orchestration: **15–25% reduction in edit-compile-fix cycles**

---

## 2. Architecture

### 2.1 Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ATOE (Adaptive Tool Orchestration Engine)       │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   │
│  │  Observer    │  │  Matcher    │  │  Suggester  │                   │
│  │  Layer       │──│  Layer      │──│  Layer      │──▶ Recommendations │
│  └──────┬───────┘  └──────┬──────┘  └──────┬──────┘                   │
│         │                 │                │                           │
│         ▼                 ▼                ▼                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   │
│  │ Event Queue │  │ Rule Engine │  │ Executor    │                   │
│  │ (ring buf)  │  │ (priority)  │  │ (mode gate) │                   │
│  └─────────────┘  └─────────────┘  └─────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐   ┌──────────────┐   ┌────────────────────────────┐
│ Compiler     │   │ File System  │   │ Tool Registry              │
│ Diagnostics  │   │ Events       │   │ (known tools, safety class) │
└──────────────┘   └──────────────┘   └────────────────────────────┘
```

### 2.2 Layers

#### Layer 1: Observer

Collects raw observations from three sources:

| Source | Data Collected | Collection Method |
|:-------|:---------------|:------------------|
| **Compiler diagnostics** | Error codes, file locations, error counts, build duration | Hook into `DiagnosticReporter` after each compile |
| **File system** | File creation, deletion, modification; directory structure changes | `watchdog` events (shared with DX-016 watch mode) |
| **Build history** | Build timestamps, success/failure, edit intervals | In-memory ring buffer (last 100 events), persisted to `.ail/atote_history.json` |

**Observation record structure:**

```python
@dataclass
class Observation:
    timestamp: float          # Unix timestamp
    source: str               # "compiler" | "filesystem" | "build"
    event_type: str           # "diagnostic" | "file_change" | "build_start" | "build_end"
    payload: dict             # Event-specific data
```

#### Layer 2: Matcher

Evaluates observations against trigger rules. Each rule produces:

```python
@dataclass
class Match:
    rule_id: str              # Unique rule identifier
    confidence: float         # 0.0–1.0
    observation_ids: list[str]  # Evidence
    context: dict             # Relevant state (file paths, error codes, etc.)
```

**Matching pipeline:**

```
Observation arrives
  → Filter irrelevant observations (noise reduction)
  → Apply each trigger rule (parallel, independent)
  → Deduplicate (same rule, same evidence → merge)
  → Rank by confidence
  → Pass top-K matches to Suggester
```

#### Layer 3: Suggester

Converts matches into user-facing suggestions:

```python
@dataclass
class Suggestion:
    code: str                 # "DX101" — unique suggestion code
    message: str              # Human-readable suggestion
    confidence: float         # 0.0–1.0
    suggested_command: str    # Exact CLI command to run
    estimated_time_saved: str # "~2 minutes"
    safety_class: str         # "safe" | "dangerous"
    auto_executable: bool     # Can run in AUTO mode?
```

**Suggestion deduplication:**
- Same suggestion code within 60 seconds → suppress (throttle)
- Same suggestion code, same file, same error → suppress after 3rd occurrence (user is ignoring it)
- Different suggestion codes → all shown, ranked by confidence

### 2.3 Integration with Existing Pipeline

```
Before ATOE:                    After ATOE:

ail build main.ail              ail build main.ail
  → Lexer                         → Lexer
  → Parser                        → Parser
  → AST Builder                   → AST Builder
  → Semantic Analyzer             → Semantic Analyzer
  → Type Checker                  → Type Checker
  → IR Builder                    → IR Builder
  → Print diagnostics           → Print diagnostics
                                  → ATOE.evaluate()
                                    → Print suggestions (SUGGEST mode)
                                    → Or ask user (INTERACTIVE mode)
                                    → Or auto-run (AUTO mode)
```

**Zero compiler pipeline modification.** ATOE hooks into the output of the existing pipeline via:
- A post-compile callback in `CompilationSession`
- A file-system watcher event handler (shared with watch mode)
- An optional Git hook for release triggers

---

## 3. Trigger Registry

### 3.1 Category 1 — Compiler Diagnostic Triggers

#### TRIGGER-D001: Repeated SEM002 (Undefined Identifier)

| Field | Value |
|:------|:-------|
| **Detection rule** | ≥3 occurrences of SEM002 within 60 seconds, same file |
| **Confidence** | 0.75 |
| **False positive risk** | Medium — developer may be actively writing new code |
| **Suggested action** | `ail doctor --check imports` |
| **Time saved** | ~2 minutes (scanning imports manually) |
| **Safety class** | Safe (read-only) |
| **Auto-executable** | No (requires context) |

#### TRIGGER-D002: Repeated MOD004 (Module Not Found)

| Field | Value |
|:------|:-------|
| **Detection rule** | ≥2 occurrences of MOD004 within 30 seconds |
| **Confidence** | 0.85 |
| **False positive risk** | Low — module resolution is deterministic |
| **Suggested action** | `ail doctor --check modules` |
| **Time saved** | ~3 minutes (tracing import paths) |
| **Safety class** | Safe |
| **Auto-executable** | Yes |

#### TRIGGER-D003: Forward Reference Pattern (SEM002 on callee before definition)

| Field | Value |
|:------|:-------|
| **Detection rule** | SEM002 where the undefined identifier is a function name that exists later in the file |
| **Confidence** | 0.90 |
| **False positive risk** | Very low — forward references are a known pattern |
| **Suggested action** | `ail order --fix main.ail` |
| **Time saved** | ~5 minutes (manual reordering) |
| **Safety class** | Dangerous (modifies file order) |
| **Auto-executable** | No |

#### TRIGGER-D004: Duplicate Symbol (SEM003 or MOD002)

| Field | Value |
|:------|:-------|
| **Detection rule** | Any SEM003 (duplicate variable) or MOD002 (duplicate import) |
| **Confidence** | 0.95 |
| **False positive risk** | Very low — duplicate detection is exact |
| **Suggested action** | `ail rename --dedup <symbol>` |
| **Time saved** | ~1 minute (finding the duplicate) |
| **Safety class** | Safe (rename with --dry-run) |
| **Auto-executable** | No (--dry-run only) |

#### TRIGGER-D005: Type Mismatch (TYP001)

| Field | Value |
|:------|:-------|
| **Detection rule** | Any TYP001 diagnostic |
| **Confidence** | 0.60 |
| **False positive risk** | Medium — type errors require human judgment |
| **Suggested action** | `ail doctor --check types` |
| **Time saved** | ~1 minute (context switch) |
| **Safety class** | Safe |
| **Auto-executable** | No |

#### TRIGGER-D006: Parser Error (PAR001–PAR012)

| Field | Value |
|:------|:-------|
| **Detection rule** | Any PAR* diagnostic |
| **Confidence** | 0.50 |
| **False positive risk** | Medium — syntax errors are usually clear from the error message |
| **Suggested action** | `ail fmt --check main.ail` (if formatting issue) |
| **Time saved** | ~30 seconds |
| **Safety class** | Safe |
| **Auto-executable** | Yes (--check mode) |

#### TRIGGER-D007: Float Literal Usage Pattern

| Field | Value |
|:------|:-------|
| **Detection rule** | LEX004 suppressed, but float literals found in source (post-fix) |
| **Confidence** | 0.40 (deprecated — float literals now supported) |
| **False positive risk** | High — float literals are now valid syntax |
| **Suggested action** | None (legacy trigger, kept for backward compatibility) |
| **Time saved** | N/A |
| **Safety class** | N/A |
| **Auto-executable** | No |

---

### 3.2 Category 2 — Repository Pattern Triggers

#### TRIGGER-R001: Large-Scale File Change

| Field | Value |
|:------|:-------|
| **Detection rule** | ≥10 files changed within 5 minutes |
| **Confidence** | 0.65 |
| **False positive risk** | Medium — could be a bulk import or generated code |
| **Suggested action** | `ail doctor --check all` |
| **Time saved** | ~5 minutes (reviewing each file) |
| **Safety class** | Safe |
| **Auto-executable** | Yes |

#### TRIGGER-R002: New Module Added

| Field | Value |
|:------|:-------|
| **Detection rule** | New `.ail` file created with `import` statement |
| **Confidence** | 0.70 |
| **False positive risk** | Low — new files typically need formatting |
| **Suggested action** | `ail fmt <new_file>` |
| **Time saved** | ~30 seconds |
| **Safety class** | Safe |
| **Auto-executable** | Yes |

#### TRIGGER-R003: Repository Growth

| Field | Value |
|:------|:-------|
| **Detection rule** | Repository crossed 50, 100, 200, or 500 `.ail` files threshold |
| **Confidence** | 0.80 |
| **False positive risk** | Low — thresholds are clear indicators |
| **Suggested action** | `ail doctor --check scalability` or enable incremental compilation |
| **Time saved** | ~10 minutes (manual performance audit) |
| **Safety class** | Safe |
| **Auto-executable** | Yes (enable incremental) |

#### TRIGGER-R004: Unformatted Files Detected

| Field | Value |
|:------|:-------|
| **Detection rule** | `ail fmt --check` (run by CI or manually) returns non-zero |
| **Confidence** | 0.95 |
| **False positive risk** | Very low — formatter check is deterministic |
| **Suggested action** | `ail fmt` (format all unformatted files) |
| **Time saved** | ~2 minutes (manual formatting) |
| **Safety class** | Safe |
| **Auto-executable** | Yes |

#### TRIGGER-R005: Mixed Import Styles

| Field | Value |
|:------|:-------|
| **Detection rule** | Files using both absolute and relative imports inconsistently |
| **Confidence** | 0.55 |
| **False positive risk** | Medium — import style preferences vary |
| **Suggested action** | `ail doctor --check imports` |
| **Time saved** | ~2 minutes |
| **Safety class** | Safe |
| **Auto-executable** | No |

---

### 3.3 Category 3 — Behavioral Triggers

#### TRIGGER-B001: Rapid Build Loop

| Field | Value |
|:------|:-------|
| **Detection rule** | ≥5 `ail build` invocations within 180 seconds |
| **Confidence** | 0.85 |
| **False positive risk** | Low — rapid builds strongly indicate iterative development |
| **Suggested action** | `ail watch main.ail` |
| **Time saved** | ~30 seconds per build (setup overhead) |
| **Safety class** | Safe |
| **Auto-executable** | Yes (start watch mode in background) |

#### TRIGGER-B002: Repeated Build Failure

| Field | Value |
|:------|:-------|
| **Detection rule** | ≥3 consecutive `ail build` failures with different errors |
| **Confidence** | 0.70 |
| **False positive risk** | Medium — could be learning the language |
| **Suggested action** | `ail static_analyzer main.ail` |
| **Time saved** | ~5 minutes (manual code review) |
| **Safety class** | Safe |
| **Auto-executable** | No (user needs to understand the analysis) |

#### TRIGGER-B003: Repeated Same-Error Build Failure

| Field | Value |
|:------|:-------|
| **Detection rule** | ≥3 consecutive `ail build` failures with the same error code |
| **Confidence** | 0.90 |
| **False positive risk** | Low — same error means the fix attempt failed |
| **Suggested action** | `ail doctor --check <error_code>` |
| **Time saved** | ~3 minutes (troubleshooting) |
| **Safety class** | Safe |
| **Auto-executable** | No |

#### TRIGGER-B004: Manual Symbol Rename Detected

| Field | Value |
|:------|:-------|
| **Detection rule** | File changes that: (a) remove a function definition, (b) add a function definition with a similar name, and (c) update call sites within 60 seconds |
| **Confidence** | 0.65 |
| **False positive risk** | Medium — could be add+delete rather than rename |
| **Suggested action** | `ail rename <old_name> <new_name> --dry-run` |
| **Time saved** | ~5 minutes (manual rename across files) |
| **Safety class** | Safe (--dry-run only) |
| **Auto-executable** | No |

#### TRIGGER-B005: Long Compile Time

| Field | Value |
|:------|:-------|
| **Detection rule** | Single build taking >5 seconds (baseline: ~0.2s for inventory) |
| **Confidence** | 0.75 |
| **False positive risk** | Low — unusual build times indicate a problem |
| **Suggested action** | `ail doctor --check performance` |
| **Time saved** | ~10 minutes (manual profiling) |
| **Safety class** | Safe |
| **Auto-executable** | Yes |

#### TRIGGER-B006: Test Addition Without Running

| Field | Value |
|:------|:-------|
| **Detection rule** | New `test_` function added to `tests/` but test suite not run within 5 minutes |
| **Confidence** | 0.60 |
| **False positive risk** | Medium — developer may be writing tests before running |
| **Suggested action** | `python -m pytest tests/ -q` |
| **Time saved** | ~30 seconds (context switch to test runner) |
| **Safety class** | Safe |
| **Auto-executable** | No (test may intentionally fail) |

#### TRIGGER-B007: Zero Test Coverage on New Module

| Field | Value |
|:------|:-------|
| **Detection rule** | New module file created with 5+ functions but no corresponding test file within 10 minutes |
| **Confidence** | 0.45 |
| **False positive risk** | High — developer may be in active development |
| **Suggested action** | `ail testgen --app <module>` |
| **Time saved** | ~5 minutes (writing initial tests) |
| **Safety class** | Safe |
| **Auto-executable** | No |

---

### 3.4 Category 4 — Release Triggers

#### TRIGGER-T001: Git Tag Created

| Field | Value |
|:------|:-------|
| **Detection rule** | New Git tag matching `v*` pattern |
| **Confidence** | 0.95 |
| **False positive risk** | Very low — tags are intentional |
| **Suggested action** | `ail doctor --check all` + benchmark suite + release checklist |
| **Time saved** | ~15 minutes (manual release checklist) |
| **Safety class** | Safe |
| **Auto-executable** | Yes (doctor + benchmark) |

#### TRIGGER-T002: CHANGELOG.md Modified

| Field | Value |
|:------|:-------|
| **Detection rule** | `CHANGELOG.md` file changed |
| **Confidence** | 0.70 |
| **False positive risk** | Medium — changelog updates don't always mean release |
| **Suggested action** | `ail doctor --check version` |
| **Time saved** | ~2 minutes (version consistency check) |
| **Safety class** | Safe |
| **Auto-executable** | Yes |

#### TRIGGER-T003: Version Bump Detected

| Field | Value |
|:------|:-------|
| **Detection rule** | `pyproject.toml` version field changed |
| **Confidence** | 0.80 |
| **False positive risk** | Low — version bumps are deliberate |
| **Suggested action** | Verify CHANGELOG.md updated, verify tests pass, run `ail doctor` |
| **Time saved** | ~5 minutes |
| **Safety class** | Safe |
| **Auto-executable** | Yes (doctor only) |

---

## 4. Confidence Model

### 4.1 Formula

Each match has a base confidence derived from the rule definition. The final confidence is adjusted by:

```
final_confidence = base_confidence * recency_factor * frequency_factor * context_factor
```

### 4.2 Factors

| Factor | Calculation | Range |
|:-------|:------------|:------|
| **Recency** | `max(0, 1 - (seconds_ago / 300))` — decays over 5 minutes | 0.0 – 1.0 |
| **Frequency** | `min(1, occurrence_count / threshold)` — more occurrences = higher confidence | 0.0 – 1.0 |
| **Context** | Varies by trigger — e.g., same file as previous error = +0.1 | 0.8 – 1.2 |
| **Suppression** | User has dismissed same suggestion ≥3 times → `0.0` (blacklist for session) | 0.0 or 1.0 |

### 4.3 Thresholds

| Confidence Range | Action |
|:----------------:|:-------|
| 0.90 – 1.00 | Show immediately (high certainty) |
| 0.70 – 0.89 | Show after current output (moderate certainty) |
| 0.50 – 0.69 | Show only in detailed mode (`--verbose`) |
| 0.00 – 0.49 | Suppress (insufficient evidence) |

### 4.4 Suppression Rules

- If user dismisses the same suggestion code 3+ times in a session → suppress for rest of session
- If user runs the suggested tool manually → suppress (user already knows)
- If the exact same suggestion was shown within 60 seconds → suppress (throttle)
- If the trigger condition no longer applies → suppress (stale)

---

## 5. Operating Modes

### 5.1 Mode Selection

| Mode | Flag | Behavior |
|:----:|:----:|:---------|
| **OFF** | `--suggest off` or `AILANG_SUGGEST=0` | No suggestions. Zero overhead. |
| **SUGGEST** | `--suggest` or `AILANG_SUGGEST=1` (default) | Print suggestions to stderr after compiler output |
| **INTERACTIVE** | `--interactive` or `AILANG_SUGGEST=2` | Ask "Run suggested tool? [Y/n]" for each suggestion |
| **AUTO** | `--auto-orchestrate` or `AILANG_SUGGEST=3` | Auto-run safe tools (fmt, doctor, watch). Never auto-run dangerous tools. |

### 5.2 Mode Gates

Each suggestion carries a `safety_class` that gates auto-execution:

| Safety Class | AUTO Mode | INTERACTIVE Mode | SUGGEST Mode | OFF Mode |
|:-------------|:---------:|:----------------:|:------------:|:--------:|
| Safe (read-only) | ✅ Auto-run | ✅ Ask | ✅ Show | ❌ |
| Safe (write, reversible) | ✅ Auto-run with `--dry-run` | ✅ Ask | ✅ Show | ❌ |
| Dangerous (write, irreversible) | ❌ Never | ✅ Ask with warning | ✅ Show with warning | ❌ |

### 5.3 Mode Configuration

```toml
# ail.toml
[orchestration]
mode = "suggest"           # off | suggest | interactive | auto
auto_safe_tools = true     # In AUTO mode, auto-run safe tools?
verbose = false            # Show low-confidence suggestions?
history_file = ".ail/atote_history.json"

[orchestration.suppress]
# Suppress specific triggers
trigger_codes = ["TRIGGER-B007", "TRIGGER-D005"]
# Suppress for specific files
file_patterns = ["tests/*", "generated/*"]
```

### 5.4 Environment Variables

| Variable | Values | Description |
|:---------|:-------|:------------|
| `AILANG_SUGGEST` | `0` (off), `1` (suggest), `2` (interactive), `3` (auto) | Mode override |
| `AILANG_SUGGEST_VERBOSE` | `0` / `1` | Show low-confidence suggestions |
| `AILANG_SUGGEST_LOG` | path | Log suggestions to file for analysis |

---

## 6. Implementation

### 6.1 File Structure

```
compiler/
└── orchestration/
    ├── __init__.py              # Public API: evaluate(), configure()
    ├── engine.py                # ATOE orchestration engine (main loop)
    ├── observer.py              # Event collection from compiler, FS, history
    ├── matcher.py               # Trigger rule evaluation
    ├── suggester.py             # Suggestion formatting and delivery
    ├── executor.py              # Tool execution (mode-gated)
    ├── history.py               # Event ring buffer + persistence
    ├── triggers.py              # All trigger rule definitions
    ├── models.py                # Data classes (Observation, Match, Suggestion)
    └── config.py                # Configuration parsing (ail.toml + env vars)
```

### 6.2 Key Implementation Details

```python
# engine.py — Main orchestration loop

class ATOEEngine:
    def __init__(self, config: ATOEConfig):
        self.config = config
        self.history = EventHistory(capacity=100)
        self.observer = Observer(self.history)
        self.matcher = Matcher(triggers.ALL_RULES)
        self.suggester = Suggester(config)

    def evaluate(self, context: CompileContext) -> list[Suggestion]:
        """Called after each compilation."""
        # 1. Record observation
        self.observer.record_compile(context)

        # 2. Match against rules
        matches = self.matcher.match_all(self.history.recent())

        # 3. Filter by confidence
        matches = [m for m in matches if m.confidence >= self.config.min_confidence]

        # 4. Deduplicate and throttle
        matches = self._deduplicate(matches)
        matches = self._throttle(matches)

        # 5. Generate suggestions
        suggestions = [self.suggester.suggest(m) for m in matches]

        # 6. Gate by mode
        return self._gate_by_mode(suggestions)
```

```python
# history.py — Ring buffer with persistence

class EventHistory:
    """Thread-safe ring buffer of recent observations, persisted to JSON."""

    def __init__(self, capacity: int = 100, persist_path: str | None = None):
        self.capacity = capacity
        self.persist_path = persist_path
        self._events: list[Observation] = []
        self._load()

    def record(self, event: Observation) -> None:
        self._events.append(event)
        if len(self._events) > self.capacity:
            self._events.pop(0)
        self._save()

    def recent(self, seconds: int = 300) -> list[Observation]:
        """Return events from the last N seconds."""
        cutoff = time.time() - seconds
        return [e for e in self._events if e.timestamp >= cutoff]

    def count(self, event_type: str, seconds: int = 60) -> int:
        return sum(1 for e in self.recent(seconds) if e.event_type == event_type)
```

```python
# matcher.py — Rule evaluation

class Matcher:
    """Evaluates observations against trigger rules."""

    def __init__(self, rules: list[TriggerRule]):
        self.rules = rules

    def match_all(self, events: list[Observation]) -> list[Match]:
        matches = []
        for rule in self.rules:
            match = rule.evaluate(events)
            if match is not None:
                matches.append(match)
        return matches
```

```python
# triggers.py — Individual trigger rules

class RepeatedBuildLoop(TriggerRule):
    """TRIGGER-B001: ≥5 builds within 180 seconds."""

    id = "TRIGGER-B001"
    base_confidence = 0.85

    def evaluate(self, events: list[Observation]) -> Match | None:
        builds = [e for e in events
                  if e.event_type == "build_end"
                  and e.timestamp > time.time() - 180]
        if len(builds) >= 5:
            return Match(
                rule_id=self.id,
                confidence=self.base_confidence,
                observation_ids=[e.id for e in builds],
                context={"build_count": len(builds)}
            )
        return None
```

### 6.3 Integration Points

| Integration | Location | Change Required |
|:------------|:---------|:----------------|
| Post-compile hook | `CompilationSession.compile()` | Add `ATOEEngine.evaluate(context)` call after compilation, before returning |
| File watcher | `watch.py` | Add file events to ATOE history |
| Git hook | `.git/hooks/post-commit` | Call `ail doctor --check` on commit |
| LSP | `lsp/handlers.py` | Add ATOE suggestions to LSP diagnostics |

**Minimal compiler change:** The ATOE engine is a single additional call at the end of `CompilationSession.compile()`:

```python
# In compilation/session.py:
class CompilationSession:
    def compile(self, ...):
        # ... existing compilation pipeline ...
        reporter = DiagnosticReporter()
        self.discover(...)
        self.analyze(reporter)
        bundle = self.build_ir()

        # NEW: ATOE evaluation
        if self.atote_enabled:
            suggestions = self.atote.evaluate(
                CompileContext(
                    diagnostics=reporter.diagnostics,
                    duration=time.time() - start_time,
                    file_count=len(self._graph.modules),
                )
            )
            for s in suggestions:
                print(s.format(), file=sys.stderr)

        return bundle
```

---

## 7. Performance Impact

### 7.1 Overhead Budget

| Operation | Budget | Measurement |
|:----------|:-------|:------------|
| Event recording | < 1ms | `time.time()` + list append |
| Rule evaluation (20 rules) | < 5ms | Linear scan of event buffer |
| History persistence | < 5ms | JSON dump of ~100 events |
| Suggestion formatting | < 1ms | String formatting |
| **Total per build** | **< 12ms** | Negligible vs 219ms baseline |

### 7.2 OFF Mode Overhead

When ATOE is disabled (`AILANG_SUGGEST=0`), the engine is not instantiated and no code paths are added. **Zero overhead.**

### 7.3 The 12ms Budget

At 12ms per build, the overhead is ~5% of the inventory build time (219ms) and < 1% of the 10,000 LOC stress test build time (1.88s). This is acceptable for SUGGEST and INTERACTIVE modes. AUTO mode may add additional execution time for auto-run tools.

---

## 8. Safety & Security

### 8.1 Invariant: Determinism

AILang's compilation is deterministic (SHA-256 identical rebuilds). The ATOE must not break this:

| Risk | Mitigation |
|:-----|:------------|
| Suggestions affect compilation | Suggestions are purely advisory — they never modify the compiler pipeline |
| History affects output | History is only used for suggestions, never for IR generation |
| AUTO mode modifies files | Only safe, reversible tools are auto-executed; dangerous tools require user confirmation |

### 8.2 Invariant: Never Modify Without Permission

| Mode | Write Permission |
|:-----|:-----------------|
| OFF | Never |
| SUGGEST | Never |
| INTERACTIVE | Only with explicit user confirmation |
| AUTO | Only for safe, reversible tools (fmt, doctor). Never for rename, delete, or destructive operations. |

### 8.3 Invariant: Visible Actions

Every auto-executed action in AUTO mode prints what it did:

```
[ATOE] Auto-ran: ail fmt main.ail (3 files formatted)
[ATOE] Auto-ran: ail doctor --check modules (no issues found)
[ATOE] Auto-ran: ail watch main.ail (watch mode started in background)
```

### 8.4 Blacklist

The following actions are **never** auto-executed, even in AUTO mode:

- `ail rename` without `--dry-run`
- `ail order --fix` (modifies source order)
- `test_compile.py` (runs with side effects)
- Any command with `--force` flag
- Any command that deletes files
- Any command that overwrites data

---

## 9. User Experience

### 9.1 SUGGEST Mode Output

```
$ ail build main.ail
Build succeeded (0.22s)

[DX101] ⚡ Rapid build loop detected (8 builds in 2 minutes)
         Suggested: ail watch main.ail
         Estimated time saved: ~30s per build

[DX105] 📦 New module detected: reports/monthly_report.ail
         Suggested: ail fmt reports/monthly_report.ail
         Estimated time saved: ~30s
```

### 9.2 INTERACTIVE Mode Output

```
$ ail build main.ail
Build succeeded (0.22s)

[DX101] ⚡ Rapid build loop detected (8 builds in 2 minutes)
         Suggested: ail watch main.ail
         Run now? [Y/n]: y
         ✓ ail watch main.ail started in background

[DX105] 📦 New module detected: reports/monthly_report.ail
         Suggested: ail fmt reports/monthly_report.ail
         Run now? [Y/n]: n
         Dismissed.
```

### 9.3 AUTO Mode Output

```
$ ail build main.ail
Build succeeded (0.22s)

[ATOE] Auto-ran: ail fmt reports/monthly_report.ail (1 file formatted)
[ATOE] Auto-ran: ail watch main.ail (watch mode started in background)

[DX101] ⚡ Rapid build loop detected (8 builds in 2 minutes)
         Auto-enabled: ail watch main.ail
```

### 9.4 Suppression

```
$ ail build main.ail
Build succeeded (0.22s)
$ ail build main.ail
Build succeeded (0.23s)
# (suggestion not repeated — throttled to once per 60s)

# User can also run ail build --no-suggest to suppress all suggestions
```

---

## 10. Testing Strategy

### 10.1 Test Categories

| Test Type | Count | What It Tests |
|:----------|:-----:|:--------------|
| Unit — trigger rules | 20 | Each rule independently with mock event data |
| Unit — confidence model | 5 | Recency, frequency, suppression calculations |
| Unit — history buffer | 3 | Capacity, persistence, thread safety |
| Integration — full pipeline | 5 | ATOE integration with CompilationSession |
| Integration — mode gating | 4 | OFF/SUGGEST/INTERACTIVE/AUTO behavior |
| Integration — safety | 3 | Never auto-execute dangerous tools |
| Acceptance — smoke | 2 | ATOE loads, runs, produces output |
| **Total** | **42** | |

### 10.2 Key Test Cases

```python
def test_repeated_build_loop_trigger():
    """TRIGGER-B001: 5 builds in 180 seconds triggers suggestion."""
    history = EventHistory()
    for i in range(5):
        history.record(Observation(
            timestamp=time.time() - (i * 30),  # Every 30 seconds
            source="build",
            event_type="build_end",
            payload={"success": True}
        ))
    matcher = Matcher([RepeatedBuildLoop()])
    matches = matcher.match_all(history.recent())
    assert len(matches) == 1
    assert matches[0].rule_id == "TRIGGER-B001"

def test_auto_mode_never_executes_dangerous():
    """AUTO mode gates dangerous tools."""
    engine = ATOEEngine(config=ATOEConfig(mode="auto"))
    dangerous_suggestion = Suggestion(
        code="DX999",
        message="Rename symbol",
        suggested_command="ail rename old new",
        safety_class="dangerous",
        auto_executable=False,
    )
    result = engine._gate_by_mode([dangerous_suggestion])
    assert len(result) == 1  # Still shown
    assert result[0].action == "show"  # Not auto-run

def test_suggestion_deduplication():
    """Same suggestion within 60s is suppressed."""
    engine = ATOEEngine(config=ATOEConfig(mode="suggest"))
    s = Suggestion(code="DX101", message="test", ...)
    engine._last_shown["DX101"] = time.time() - 10  # 10 seconds ago
    assert engine._is_throttled(s) == True

def test_zero_overhead_in_off_mode():
    """OFF mode instantiates no engine."""
    session = CompilationSession(atote_enabled=False)
    assert session.atote is None
```

---

## 11. Rollout Plan

### Phase 1: Foundation (Week 1–2)

| Deliverable | Effort | Description |
|:------------|:-------|:------------|
| `orchestration/models.py` | 1 hour | Data classes: Observation, Match, Suggestion |
| `orchestration/history.py` | 2 hours | Ring buffer with JSON persistence |
| `orchestration/config.py` | 1 hour | ail.toml parsing + env vars |
| **Phase 1 total** | **4 hours** | |

### Phase 2: Core Engine (Week 3–4)

| Deliverable | Effort | Description |
|:------------|:-------|:------------|
| `orchestration/observer.py` | 2 hours | Compiler hook, FS event adapters |
| `orchestration/matcher.py` | 3 hours | Rule evaluation, confidence calculation |
| `orchestration/triggers.py` | 4 hours | 15 trigger rules (all categories) |
| `orchestration/suggester.py` | 2 hours | Formatting, deduplication, throttling |
| `orchestration/executor.py` | 2 hours | Mode gating, tool invocation |
| `orchestration/engine.py` | 3 hours | Main orchestrator, connection to compiler |
| **Phase 2 total** | **16 hours** | |

### Phase 3: Integration (Week 5)

| Deliverable | Effort | Description |
|:------------|:-------|:------------|
| Compiler hook | 2 hours | Single call in `CompilationSession.compile()` |
| ail.toml integration | 1 hour | Parse orchestration config |
| CLI flags | 1 hour | `--suggest`, `--interactive`, `--auto-orchestrate` |
| Watch mode integration | 1 hour | Share file events |
| **Phase 3 total** | **5 hours** | |

### Phase 4: Testing & Release (Week 6)

| Deliverable | Effort | Description |
|:------------|:-------|:------------|
| Unit tests (20) | 4 hours | Trigger rules, confidence, history |
| Integration tests (12) | 4 hours | Pipeline, mode gating, safety |
| Acceptance tests (10) | 2 hours | Smoke tests, edge cases |
| Documentation | 2 hours | Update ARCHITECTURE_DECISIONS.md, RELEASE docs |
| **Phase 4 total** | **12 hours** | |

### Total: ~37 hours / ~1 person-week

---

## 12. Benchmark Expectations

### 12.1 Expected Improvements

| Metric | Before ATOE | After ATOE (estimated) | Source |
|:-------|:-----------:|:----------------------:|:-------|
| **Build-fix cycles per feature** | 4.0 (B2 avg) | **3.2** (−20%) | Trigger B001, B002, B003 reduce repeated failures |
| **Time to discover tool** | 2 min (estimated) | **0 min** (automatic) | Triggers surface tools contextually |
| **Release prep time** | 30 min | **15 min** (−50%) | Trigger T001 automates checklist |
| **Manual renames** | Var. | **Reduced** | Trigger B004 catches manual rename patterns |
| **Unformatted code** | Var. | **Near zero** | Trigger R004 auto-formats on build |
| **Developer satisfaction** | Unknown | **Improved** | Fewer context switches |

### 12.2 Risk to Benchmarks

| Risk | Mitigation |
|:-----|:------------|
| ATOE breaks deterministic builds | ATOE never modifies compiler pipeline; suggestions are post-compile |
| ATOE slows down benchmarks | OFF mode = zero overhead; ON mode < 12ms |
| ATOE changes benchmark behavior | Benchmarks run with ATOE disabled; no impact on existing measurements |
| ATOE false positives confuse users | Confidence threshold, throttling, suppression; user can disable |

---

## 13. Comparison with Existing Systems

| Feature | AILang ATOE | GitHub Copilot | IDE Linters | CI/CD Pipelines |
|:--------|:-----------:|:--------------:|:-----------:|:----------------:|
| Triggers on compiler diagnostics | ✅ | ❌ | ✅ | ❌ |
| Triggers on behavioral patterns | ✅ | ❌ | ❌ | ❌ |
| Suggests tools, not just fixes | ✅ | ❌ | ❌ | ❌ |
| Offline (no cloud dependency) | ✅ | ❌ | ✅ | ❌ |
| Confidence model | ✅ | ✅ (ML) | ❌ | ❌ |
| Safety-gated auto-execution | ✅ | N/A | ✅ | ✅ |
| Zero overhead when disabled | ✅ | N/A | ✅ | N/A |

---

## 14. Future Extensions

| Extension | Trigger | Complexity | Notes |
|:----------|:--------|:-----------|:-------|
| AI-generated suggestions | All triggers | High | Use LLM to generate contextual suggestions beyond rules |
| Collaborative suggestions | Shared history | High | Multiple developers → shared pattern detection |
| Self-tuning thresholds | History analysis | Medium | Adjust confidence thresholds based on user acceptance rate |
| Plugin trigger system | Custom triggers | Medium | Third-party tools register their own trigger rules |
| Time-series anomaly detection | Build duration | High | Detect gradual performance degradation |
| Cross-project patterns | Multi-repo | High | Learn from patterns across projects |

---

## 15. Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    EXPERIMENTAL                              ║
║                                                              ║
║  The ATOE architecture is sound, the triggers are            ║
║  well-specified, and the implementation is feasible          ║
║  (~37 hours / 1 person-week).                               ║
║                                                              ║
║  However, this is the FIRST tool that observes user          ║
║  behavior rather than code structure. The confidence         ║
║  model and suppression rules need real-world validation      ║
║  before they can be declared stable.                         ║
║                                                              ║
║  RECOMMENDATION:                                             ║
║  1. Release behind --experimental-orchestrate flag          ║
║  2. Default mode: OFF (opt-in via AILANG_SUGGEST=1)         ║
║  3. After 3 months of real usage, evaluate:                  ║
║     - False positive rate (< 20% target)                     ║
║     - User acceptance rate (> 50% target)                    ║
║     - Build time overhead (< 50ms target)                    ║
║  4. If targets met, promote to stable with SUGGEST as default║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### Rationale for EXPERIMENTAL (not APPROVE or REJECT)

| Vote | Reason |
|:-----|:--------|
| **APPROVE** | Architecture is well-defined. Triggers are concrete, not speculative. Implementation cost is low. Integration risk is near zero (post-compile hook, no pipeline changes). |
| **EXPERIMENTAL** | Confidence model has never been validated in production. Suppression rules are heuristic. User tolerance for suggestions is unknown. AUTO mode safety needs real-world testing. |
| **REJECT** | Would not reject — the problem is real (10 tools → discoverability gap) and the proposed solution is minimal. |

---

## 16. Quick Reference

### Key Numbers

| Metric | Value |
|:-------|:------|
| Implementation effort | ~37 hours |
| Lines of code (estimated) | ~800 (Python) |
| Files created | 8 (compiler/orchestration/) |
| Files modified | 2 (CompilationSession, CLI main) |
| Overhead per build | < 12ms |
| Trigger rules | 20 (15 specified, 5 reserved) |
| Operating modes | 4 (OFF, SUGGEST, INTERACTIVE, AUTO) |
| Safety classes | 3 (safe-read, safe-write, dangerous) |
| Tests | 42 |

### CLI Flags

| Flag | Mode |
|:-----|:------|
| `--no-suggest` | OFF (per-invocation override) |
| *(default)* | SUGGEST |
| `--interactive` | INTERACTIVE |
| `--auto-orchestrate` | AUTO |

### Environment Variables

```
AILANG_SUGGEST=0    # OFF
AILANG_SUGGEST=1    # SUGGEST (default)
AILANG_SUGGEST=2    # INTERACTIVE
AILANG_SUGGEST=3    # AUTO
```
