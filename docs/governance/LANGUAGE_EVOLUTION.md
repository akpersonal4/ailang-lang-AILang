# LANGUAGE_EVOLUTION

**Canonical record of every feature request made to AILang, its disposition, and rationale.**

> This document prevents feature creep by requiring every request to be recorded, justified,
> and either accepted or rejected with a written rationale. A feature must be cited by at
> least 3 independent applications before it is even considered for the language itself
> (stdlib additions and bug fixes have a lower bar).

---

## How to Use

1. When a feature is requested, add a row to the table below.
2. State which application(s) need it, the rationale for accepting or rejecting, and the version.
3. Rejected entries remain permanently — they serve as a historical record of *conscious decisions*.
4. Before proposing a new language feature, check this table. If a similar request was rejected, you must provide new evidence (e.g., 3+ new apps that need it) to reopen.

---

## Request Log

| # | Request | Category | Requested By | Accepted? | Rationale | Version |
|---|---------|----------|-------------|-----------|-----------|---------|
| 1 | `string.substring(value, start, end)` | Stdlib | markdown_parser, expr_eval | ✅ Accepted | Genuine stdlib gap — Python `str` has no `.substring()` accessible via `getattr`; multiple apps need substring extraction | 0.1.2 |
| 2 | `env_args` returns user args only (strip CLI plumbing) | Stdlib | All 23 phase11 apps (grep, diff, linter, crm_lite, pos_simulator, etc.) | ✅ Accepted | Original API returned raw `sys.argv` including `run` and script path; every app had to skip indices; stripping is more ergonomic | 0.1.2 |
| 3 | `while` loop | Language | a_star, trie, quick_sort, merge_sort, dfs, bst, binary_search, bfs | ❌ Rejected | Feature creep — AILang deliberately eschews iterative constructs to keep grammar minimal; recursion is the intended iteration mechanism. Revisit only if ≥5 independent apps demonstrate unsolvable problems with recursion alone | — |
| 4 | `for` loop / iterators | Language | grep, diff, file_organizer, dep_graph | ❌ Rejected | Same rationale as `while` — recursion + list operations suffice | — |
| 5 | List literal syntax `[1, 2, 3]` | Language | grep, diff, json_formatter, calculator | ❌ Rejected | No syntax extensions without 3+ apps proving necessity; list can be built with `list.new()` / `list.append()` | — |
| 6 | Map literal syntax `{"key": "val"}` | Language | Phase 8 docs cleanup | ❌ Rejected | No map literal support; use `map.new()` / `map.set()`. Documentation was corrected in Phase 8 | — |
| 7 | Float literal syntax `3.14` | Language | scientific_calculator, grade_calculator, bmi_calculator | ❌ Rejected | Grammar does not support decimal-point literals; documentation corrected in Phase 8 | — |
| 8 | `map.get(map, key, fallback)` / safe-get with default | Stdlib | linter, crm_lite, a_star | ❌ Rejected | Workaround exists: guard with `map.has()` + nested `if`. Short-circuit `||` would make this ergonomic, but language doesn't short-circuit. Revisit if ≥5 apps show the guard pattern is error-prone | — |
| 9 | Short-circuit `&&` / `||` | Runtime | a_star, linter, crm_lite | ❌ Rejected | Both sides of `&&`/`||` are evaluated before the operator is applied. Changing this is a semantics change. Workaround: nested `if` blocks. Revisit if ≥5 apps have correctness bugs from eager evaluation | — |
| 29 | Documentation mismatch: LANGUAGE_SPEC.md claimed short-circuit, runtime evaluates eagerly | Documentation | Mini SQL Engine (B6) | ✅ Resolved | AI benchmark B6 discovered the inconsistency: LANGUAGE_SPEC.md §6.3 claimed short-circuit, but `compiler/ir/builder.py:177-178` eagerly evaluates both operands prior to IR node creation, and `compiler/runtime/interpreter.py:162-165` merely applies Python's `bool(left and right)` to pre-evaluated values. GOVERNANCE.md §6 correctly lists short-circuit as "Rejected Forever". LANGUAGE_SPEC.md corrected to "Eager (no short-circuit)". LANGUAGE_TOUR.md and GETTING_STARTED.md updated with nested-if workaround examples and explicit warnings against guarded-access patterns. Lesson: AI-driven benchmark testing (behavioral observation vs. spec comparison) effectively identifies documentation–implementation inconsistencies in specification-first projects. | 0.1.2 |
| 10 | `file.list_dir(path)` / `file.is_dir(path)` | Stdlib | find utility | ❌ Rejected | `find.ail` works on file paths passed as CLI args instead of scanning directories; not enough apps need directory listing to expand the API surface | — |
| 11 | Chained member access on call results (`list.get(x, 0).strip()`) | Runtime | linter, code_metrics | ❌ Rejected | Runtime cannot chain `.method()` on a call result because the call returns a value, not a reference. Workaround: store in temp variable. Fixing this requires deeper runtime changes | — |
| 12 | `__len__()` as member method accessible via `.` | Runtime | linter (used `line.lstrip().__len__()`) | ❌ Rejected | Python dunder methods are not accessible via AILang member access. Use `string.length()` instead | — |
| 13 | Custom delimiter / quote in `csv` module | Stdlib | csv_formatter, md_formatter | ❌ Rejected | Only RFC 4180 dialect is supported; custom delimiters add complexity. Revisit if ≥5 apps need TSV or pipe-delimited input | — |
| 14 | `json.pretty()` / JSON pretty-print with indentation | Stdlib | json_formatter | ❌ Rejected | Single use-case not sufficient; `json.stringify()` with `_SetEncoder` is adequate. Revisit when ≥3 apps request it | — |
| 15 | CLI pre-commit hook (`ail fmt --check` in hooks) | Devtools | Phase 10 recommendation | ⏳ Deferred | Documented as recommendation; not yet implemented | — |
| 16 | IR optimizer (constant folding, dead code elimination) | Compiler | Roadmap (v0.2.0) | ⏳ Planned | On roadmap for v0.2.0; not yet started | — |
| 17 | Compiler performance profiling | Devtools | Roadmap (v0.2.0) | ⏳ Planned | On roadmap for v0.2.0; reduce compile time for >1000 LOC | — |
| 18 | Package manager | Devtools | Roadmap (Phase 2) | ⏳ Planned | On product roadmap | — |
| 19 | LSP (Language Server Protocol) | Devtools | Roadmap (Phase 2) | ⏳ Planned | On product roadmap | — |
| 20 | IDE plugins | Devtools | Roadmap (Phase 3) | ⏳ Planned | On product roadmap | — |
| 21 | Self-hosting (compiler written in AILang) | Compiler | Roadmap (Phase 3) | ⏳ Planned | On product roadmap | — |
| 22 | JIT compilation | Compiler | Roadmap (Phase 3) | ⏳ Planned | On product roadmap | — |
| 23 | AI integration features | Language | Roadmap (Phase 3) | ⏳ Planned | On product roadmap | — |
| 24 | Significant whitespace | Language | Pre-emptive (design decision) | ❌ Rejected Forever | AILang uses explicit `{}` for blocks; whitespace-sensitive parsing causes brittle parsing, invisible bugs, and poor AI generation reliability | — |
| 25 | Operator overloading | Language | Pre-emptive (design decision) | ❌ Rejected Forever | No user-defined types; overloading adds compiler complexity for zero benefit; functions are the only abstraction mechanism | — |
| 26 | Macros / compile-time code generation | Language | Pre-emptive (design decision) | ❌ Rejected Forever | Macros introduce hidden code paths, complicate error messages, and break determinism guarantees | — |
| 27 | Implicit type conversions | Language | Pre-emptive (design decision) | ❌ Rejected Forever | All conversions must be explicit (`convert.to_int()`, `convert.to_string()`); implicit coercion is a leading source of bugs | — |
| 28 | Multiple inheritance | Language | Pre-emptive (design decision) | ❌ Rejected Forever | AILang has no class or inheritance system; multiple inheritance adds significant complexity without alignment to language goals | — |

---

## Language Change Policy

1. **v0.1.x Language Freeze** — The language specification is frozen. No new keywords, grammar changes, syntax changes, semantic changes, or breaking changes are accepted during v0.1.x. See `docs/governance/GOVERNANCE.md §7`.
2. **No change to the grammar, parser, lexer, compiler pipeline, or runtime semantics** without written rationale and ≥3 independent requesting applications (applies post-freeze).
3. **Stdlib additions** require ≥2 independent applications or a demonstrated stdlib gap (e.g., missing function in a documented module).
4. **Bug fixes** require 1 application demonstrating the defect. No minimum.
5. **Documentation changes** require no minimum.
6. **Every rejection stays in this table permanently.** Features in the "Rejected Forever" category (see `docs/governance/GOVERNANCE.md §6`) are permanently closed and will not be reconsidered.
7. **Breaking changes** require an Architecture Decision Record (ADR) in `docs/ADR-*.md`.

## Stdlib API Stability

| Module | Stability | Since |
|--------|-----------|-------|
| string | Stable | 0.1.0 |
| math | Stable | 0.1.0 |
| list | Stable | 0.1.0 |
| array | Stable (alias for list) | 0.1.0 |
| map | Stable | 0.1.0 |
| set | Stable | 0.1.0 |
| file | Stable | 0.1.0 |
| path | Stable | 0.1.0 |
| json | Stable | 0.1.0 |
| csv | Stable | 0.1.0 |
| time | Stable | 0.1.0 |
| random | Stable | 0.1.0 |
| environment | Stable | 0.1.0 |
| convert | Stable | 0.1.0 |
| io | Stable | 0.1.0 |
| system | Stable | 0.1.0 |

## Related Documents

- [Governance](GOVERNANCE.md) — Proposal process, freeze policy, rejected-forever list, backward compatibility
- [Project Constitution](PROJECT_CONSTITUTION.md) — Immutable rules for AILang development
- [Product Roadmap](PRODUCT_ROADMAP.md) — Forward-looking feature planning
- [CHANGELOG.md](../CHANGELOG.md) — Version history and release notes
- [CONTRIBUTING.md](CONTRIBUTING.md) — How to propose changes
