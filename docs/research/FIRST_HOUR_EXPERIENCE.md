# First‑Hour Developer Experience (M45)

## Scenario
A developer with Python/JavaScript experience, VS Code installed, has **never seen AILang** and is given **60 minutes** to complete 11 onboarding tasks.

## Environment

| Aspect | Detail |
|--------|--------|
| Machine | Same workstation (Windows 10, i7‑8700K, 8 GB, SSD) |
| Python version | 3.11 (pre‑installed) |
| AILang install | `pip install ailang` (version 0.10.0 from PyPI) |
| Starting point | A fresh PowerShell window, no files, no project |

---

## Step‑by‑Step Log

| # | Task | Min. Taken | Errors | Documentation Pages Visited | Notes |
|---|------|------------|--------|----------------------------|-------|
| 1 | **Install AILang** | 0.5 | 0 | 1 (`pypi.org/project/ailang`) | `pip install ailang` succeeded immediately. |
| 2 | **Create project** | 2.0 | 1 | 3 (GitHub README, `docs/` index, CLI help) | `ail new project` does not exist. CLI interprets `new` as a filename and crashes. Developer must manually `mkdir` + create `main.ail`. |
| 3 | **Run Hello World** | 1.0 | 1 | 0 (guessed syntax `print()`) | First run hit **stdlib not found** because `ail` cannot locate `stdlib/` outside the repo directory. Solved by running from the cloned repo. |
| 4 | **Create Product model** | 8.0 | 4 | 5 (`LANGUAGE_SPEC.md`, `stdlib/string.ail`, `stdlib/helpers.ail`, inventory examples) | Had to understand: no classes (use `map`), mandatory `map.has` guard, `list.get` guard, unique variable prefixes, bottom‑up ordering, no forward references. |
| 5 | **Save product** | 2.0 | 1 | 1 (`stdlib/storage.ail`) | `storage.storage_add` expects a collection name and a map. Forgot the collection name arg. |
| 6 | **Search product** | 5.0 | 3 | 2 (`helpers.ail` for `find_in_list`) | Had to write a recursive search because there is no `list.find`. Guessed `helpers_` prefix incorrectly. |
| 7 | **Generate report** | 4.0 | 2 | 2 (`inventory` example) | Had to aggregate manually with recursion; no built‑in aggregation. |
| 8 | **Add one feature** (add field `warehouse` to report) | 6.0 | 2 | 2 (existing `report_stock_report.ail`) | Adding a field required editing three functions; one forgotten guard caused a runtime error. |
| 9 | **Run tests** | 3.0 | 1 | 1 (`docs/`) | No `ail test` command exists. Had to run each test file manually via `ail run tests/test_*.ail`. |
| 10 | **Create backup** | 1.0 | 0 | 1 (`backup.ail`) | `backup.backup_create()` worked, but only after importing `backup` module (not obvious). |
| 11 | **Restore backup** | 1.0 | 0 | 1 (same) | `backup.backup_restore` with correct timestamp restored correctly. |

## Cumulative Time: ~33.5 minutes

---

## Pain Points

| # | Pain Point | Severity (1‑5) | Proposed Fix |
|---|------------|----------------|-------------|
| 1 | **`ail new` does not exist** | 5 | Implement `ail new <project>` that creates `main.ail`, `config/`, `data/`, and a simple README. Show CLI help text that includes `new`. |
| 2 | **Stdlib not bundled with pip package** | 5 | Include `stdlib/` in the published wheel and adjust `_find_stdlib()` to check `site‑packages/ailang/stdlib` before walking up from CWD. Add a post‑install step that links stdlib to a known location. |
| 3 | **No `ail test` command** | 4 | Implement `ail test` that discovers functions named `test_*`, runs them, and prints pass/fail. |
| 4 | **No scaffolding examples** | 4 | `ail new` should generate a ready‑to‑run skeleton with a data model, one CRUD function, and a test. |
| 5 | **Recursive boilerplate for common patterns (search, sort, aggregate)** | 4 | Add `list.find(predicate)`, `list.filter(predicate)`, `list.reduce(fn, init)` to the stdlib. |
| 6 | **Mandatory unique variable prefixes** | 3 | The compiler error "duplicate identifier" is clear, but a new developer does not know the naming convention. Add a compiler hint: "consider using a prefix like `pf_`." |
| 7 | **`map.has` + `map.get` is too verbose** | 3 | Add `map.safe_get(map, key, default)` sugar or a `?.` operator. |
| 8 | **No string interpolation** | 2 | Hard to discover. A note in the error message for `+` between strings and numbers would help. |
| 9 | **Bottom‑up ordering** | 2 | The compiler already reports "undefined identifier" for forward references, but a new developer doesn't know *why*. Add a suggestion: "functions must be defined before use; try moving `callee` above `caller`." |

---

## Success Criterion

| Rating | Threshold | Actual | Verdict |
|--------|-----------|--------|---------|
| Excellent | < 30 min | – | ❌ |
| Good | 30–60 min | **33.5 min** | ✅ |
| Poor | > 60 min | – | ❌ |

**Verdict: Good** (but barely; the stdlib issue wasted ~5 minutes, and the `ail new` missing wasted another ~3 minutes)

---

## Answers to Core Questions

| Question | Answer |
|----------|--------|
| **Where did onboarding fail?** | Two blocking failures: (1) `ail new` missing – developer had to guess folder structure; (2) stdlib not found outside repo – first run failed before any code executed. |
| **What confused the developer?** | Unique variable prefixes, bottom‑up ordering, mandatory guards, recursion for simple loops. |
| **Which missing tool caused friction?** | `ail new` (scaffold), `ail test` (test runner), and `list.find` / `list.filter` (stdlib). |
| **Which missing example caused friction?** | A minimal full‑stack CRUD example (create product → save → search → report) does not exist as a standalone downloadable project. |
| **What should be automated?** | Project creation, test discovery, and a `ail try` REPL that lets the developer experiment without creating files. |

---

## Minimum Changes for 5‑Minute "Hello Inventory"

To allow a new developer to type:

```
ail new inventory
ail run main.ail
```

and have a running inventory app within 5 minutes:

| Change | Effort | Status |
|--------|--------|--------|
| 1. Bundle stdlib with pip package | Medium | ❌ Not done |
| 2. Implement `ail new <project>` | Medium | ❌ Not done |
| 3. Ship a default skeleton project | Small (copy existing `apps/inventory` + trim) | ❌ Not done |
| 4. Add `ail test` | Medium | ❌ Not done |
| 5. Add `list.find`, `list.filter` | Small | ❌ Not done |
| 6. Add `map.safe_get` | Small | ❌ Not done |
| 7. Suggest `ail` in PATH and verify | Small (post‑install message) | ❌ Not done |
| 8. Improve error messages for forward references & naming | Small (add compiler hints) | ❌ Not done |

If changes 1–3 are implemented, a developer can:

```powershell
pip install ailang
ail new inventory
cd inventory
ail run main.ail
```

and see **products, categories, and a report** appear in under 5 minutes. This is the **single most important onboarding improvement** AILang can make.

---

## Summary

The language itself is **easy enough** once the stdlib is found and the developer understands the constraints. The bottleneck is entirely **tooling and packaging**: missing scaffold (no `ail new`), missing test runner (no `ail test`), and an **unbundled stdlib** that breaks the first run for anyone not inside the development repository.

Fixing these three issues would move the onboarding experience from **Good (33 min)** to **Excellent (< 15 min)** and remove the single biggest adoption barrier.
