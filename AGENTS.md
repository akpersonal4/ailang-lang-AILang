# AILang — AI Agent Instructions

Auto-consumed by Claude Code, Windsurf, Cursor, Copilot. See `docs/AI_MODEL_GUIDE.md` for per-tool setup.

---

## 1. Mission

Generate correct, idiomatic AILang code that builds and runs on first compile. Eliminate predictable iterations through upfront planning.

---

## 2. Mandatory Reading Order

Before writing any AILang code, read these files in order:

| Order | File |
|:-----:|------|
| 1 | `PROJECT_MEMORY.md` |
| 2 | `docs/AILANG_DEVELOPMENT_PLAYBOOK.md` |
| 3 | `docs/MASTER_ENGINEERING_PROMPT.md` |
| 4 | `LANGUAGE_SPEC.md` |
| 5 | `docs/STDLIB_REFERENCE.md` |
| 6 | `docs/LANGUAGE_TOUR.md` |
| 7 | `README.md` |
| 8 | One existing app from `apps/` |
| 9 | Browse `examples/patterns/` for pre-written recipes |

---

## 3. Engineering Workflow

1. **Plan** — dependency map, stdlib audit, guard audit
2. **Write** — bottom-up (Level 0 utilities → Level N `main()`)
3. **Build** — `ail build <file>`
4. **Run** — `ail run <file>`
5. **Verify** — pass Validation Checklist

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
- **Missing stdlib:** `split`, `find`, `join`, `sort`, `list.copy` don't exist → write custom (see Playbook)
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
