# AILang — AI Agent Instructions

> **Derived from:** `LANGUAGE_SPEC.md` (canonical source of truth)
> **If this document conflicts with LANGUAGE_SPEC.md, the spec wins.**

Auto-consumed by Claude Code, Windsurf, Cursor, Copilot. See `docs/guides/AI_MODEL_GUIDE.md` for per-tool setup.

---

## 1. Mission

Generate correct, idiomatic AILang code that builds and runs on first compile. Eliminate predictable iterations through upfront planning.

---

## 2. Mandatory Reading Order

### 2.1 Before Writing AILang Code

Before writing any AILang code, read these files in order:

| Order | File |
|:-----:|------|
| 1 | `DEVELOPMENT_STATUS.md` |
| 2 | `PROJECT_MEMORY.md` |
| 3 | `AGENTS.md` (this file) |
| 4 | `docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md` |
| 5 | `docs/architecture/ARCHITECTURE_DECISIONS.md` |
| 6 | `docs/reference/LANGUAGE_SPEC.md` |

> Developers first need to know **what is happening today** before learning **how the language works**.

### 2.1a Benchmark Evidence (read when working on benchmarks)

When working on engineering benchmarks, B2–B6, or inventory comparison:

| Order | File |
|:----:|------|
| 1 | `docs/ENGINEERING_BENCHMARK_PLAN.md` — B1–B7 methodology |
| 2 | `docs/benchmarks/INVENTORY_SCALABILITY_BENCHMARK.md` — 8,515 LOC AILang inventory system |
| 3 | `docs/benchmarks/INVENTORY_PYTHON_COMPARISON.md` — Empirical AILang vs Python head-to-head |
| 4 | `docs/benchmarks/INVENTORY_BENCHMARK_HARNESS.md` — B2–B6 execution protocol (exact prompts, models, stopping conditions) |

### 2.2 Before Modifying Runtime/Compiler Internals

Before modifying any file in:
- `compiler/runtime/`
- `compiler/interpreter/`
- `environment.py`
- The semantic analyzer
- Scope handling

AI MUST read these files in order:

| Order | File |
|:-----:|------|
| 1 | `docs/architecture/ARCHITECTURE_DECISIONS.md` |
| 2 | `docs/runtime/optimizations.md` |
| 3 | `docs/runtime/lookup_cache/design.md` |
| 4 | `docs/runtime/lookup_cache/implementation.md` |

**Never remove or redesign an optimization without understanding the architectural decision that introduced it.**

---

## 3. Engineering Workflow

### Official Development Pipeline

```
Write Code
    ↓
ail fmt
    ↓
ail check
    ↓
ail build
    ↓
ail test
    ↓
ail run
```

**This pipeline is mandatory for all v1.x development.**

### Why This Pipeline?

- `ail check` detects forward references, missing imports, and ordering violations **before compilation**
- If violations exist, execution stops with actionable fixes
- Developers spend time fixing business logic, not syntax ordering mistakes

### Workflow Steps

1. **Canonical First** — Before creating a new document, search for an existing canonical document. Extend it if appropriate. Only create if genuinely new responsibility.
2. **Plan** — dependency map, stdlib audit, guard audit
3. **Write** — bottom-up (Level 0 utilities → Level N `main()`)
4. **Check** — `ail check <file>` (auto-run by `ail run` and `ail test`)
5. **Build** — `ail build <file>`
6. **Run** — `ail run <file>`
7. **Verify** — pass Validation Checklist

### Skip Auto-Check (Rare)

If you need to bypass the pre-flight check:

```bash
ail run --no-check <file>
ail test --no-check <file_or_dir>
```

**Only use when:** You're testing a specific compile error and need to bypass the check.

---

## 4. Hard Rules

| Rule | Detail |
|------|--------|
| No loops | Use recursion only (`while`/`for` don't exist) |
| No nested functions | All functions at top level |
| No forward references | Callee must be defined before caller |
| Bottom-up ordering | Write in dependency order (Level 0 → main) |
| `let` needs initializer | `let x = value`, never `let x;` |
| `return` needs value | `return expr`, never `return;` |
| `import` at top level only | Never inside a function body |
| Unique variable names | No reuse of `i`, `x`, `result`, `acc` across functions |
| `map.get` needs `map.has` guard | Always check key existence first |
| `list.get` needs `list.len` check | Guard against empty list access |
| `string.concat` takes exactly 2 args | Use `+` for 3+ strings |
| `&&` is eager | Both operands always execute. Use nested `if` when right side depends on left |

---

## 5. Common Pitfalls

- **Forward reference:** `Undefined identifier: X` → move X before its caller
- **Missing stdlib:** `sort`, `list.copy` don't exist → write custom (see Playbook)
- **Wrong map key:** Keys mismatch between `map.set` and `map.get` → audit key names
- **Variable collision:** `let i = 0` in multiple functions → use unique names
- **File too large:** ~100 functions / 1000+ LOC → forward reference ordering becomes error-prone; plan to split early

---

## 6. Validation Checklist

| # | Check |
|:-:|-------|
| 1 | Required documents read (§2) |
| 2 | Dependency graph created (Level 0 → N) |
| 3 | Stdlib audited (no manual reimplementation of existing APIs) |
| 4 | Guards verified (`map.has` before `map.get`, `list.len` before `list.get`, `&&` safe) |
| 5 | Variable names unique across all functions |
| 6 | `string.concat` has ≤2 args (use `+` for 3+) |
| 7 | `let` has initializer (`let x = value`) |
| 8 | `return` has value (`return expr`) |
| 9 | `ail build` passes |
| 10 | `ail run` passes with correct output |
| 11 | Patterns checked before writing filter/map/reduce/split/find |

### Benchmark Feedback Loop

After each benchmark or new app: new lesson? → appeared in ≥2 independent apps? → **yes** → update Playbook → update AGENTS.md (only if universally applicable). Single-app findings stay in benchmark report only.

---

## 7. Deliverables

- Working `.ail` file(s) that build and run
- All Validation Checklist items pass
- If new lesson discovered: documented in Playbook before considering work complete

---

## 8. Feature Governance

Every new feature proposal **must** answer these six questions:

1. **Which mission objective does it support?**
2. **Which measured pain point does it solve?**
3. **Can existing tooling solve it instead?**
4. **Does it increase language expressiveness?**
5. **Does it reduce determinism?**
6. **Would this feature still make sense if AI code generation did not exist?**

**Q6 lens**: If the answer is *No* (AI-specific optimization) it likely belongs in AILang. If the answer is *Yes* (every language eventually needs this) it faces much stronger scrutiny — it may push AILang toward becoming a generic language rather than an AI-first business language.

### Decision Matrix

| Result Pattern | Outcome |
|---|---|
| Q1–Q3 positive, Q4–Q6 negative | ✅ Approve for v1.x |
| Q4 or Q5 positive with strong evidence | ⚠ ADR + CTO review |
| Q4 or Q5 positive without evidence | ❌ Reject |
| Q6 positive but feature is ecosystem/tooling | ✅ Allow with review |
| Universal feature with weak mission alignment | 🔬 Move to v2.0 research |

### Governance Tracks

Proposals fall into one of two tracks, each with its own review process.

#### Language Features

Changes to syntax, semantics, types, or execution model.

**Examples:** loops, generics, async, pattern matching, reflection, operator overloading, algebraic types.

**Review:** Q1–Q6, strict, ADR required.

#### Tooling Features

Non-language additions to the developer experience.

**Examples:** `ail test`, `ail rename`, `ail fmt`, `ail watch`, `ail new`, `ail mcp`, VS Code extension, LSP features.

**Review:** Q1–Q3 only, lightweight maintainer approval.

### Review Ownership

| Domain | Reviewer | Gate |
|---|---|---|
| Language feature | CTO + Architecture | ADR required |
| Tooling feature | Maintainer | Issue comment |
| Runtime/compiler internal | Architecture | ADR required |

### Approval Stage

> Feature proposals must be reviewed and approved **before implementation begins**.

This is not a post-hoc justification exercise. A rejected proposal costs a document. An implemented feature that should have been rejected costs months of debt.

### Alignment

The project remains tightly aligned with:

> **AI-assisted, deterministic, low-maintenance business software development.**

Features that damage determinism, add unmeasured complexity, or solve no observed pain point are out of scope for v1.x.