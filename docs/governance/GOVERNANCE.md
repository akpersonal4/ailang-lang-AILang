# AILang Governance

**How decisions about the language are made, reviewed, and versioned.**

This document defines the formal process for proposing, reviewing, accepting, or
rejecting changes to AILang. It exists to prevent feature creep, ensure disciplined
evolution, and give every contributor a clear path forward.

---

## 1. Change Categories

Every proposed change falls into one of the following categories, each with its own
process and evidence bar.

| Category | Examples | Evidence Bar |
|----------|----------|-------------|
| **Language feature** | New syntax, new keyword, grammar change, semantics change | ≥3 independent AILang applications that cannot be implemented without it |
| **Stdlib addition** | New function in an existing module, new module | ≥2 independent applications, or a demonstrated stdlib gap |
| **Bug fix** | Correctness defect, crash, non-determinism | 1 application or test demonstrating the defect |
| **Documentation** | Typo fix, clarification, new guide | None (direct approval) |
| **Performance** | Compile time, memory, runtime optimization | Benchmark showing measurable improvement |
| **Devtools** | Formatter, linter, CLI, LSP, extensions | Project lead discretion |
| **Breaking change** | Any change that breaks existing valid programs | ADR (Architecture Decision Record) + project lead approval |

---

## 2. Proposal Process

### 2.1 Pre-Proposal (Discussion)

Before writing a formal proposal, open a **discussion** (GitHub Issue or equivalent)
with a brief description of the requested change. The community and project lead
will give初步 feedback. This saves effort if the change is clearly out of scope.

### 2.2 Formal Proposal

A formal proposal must include:

1. **Summary** — one paragraph describing the change
2. **Motivation** — which applications need it and why existing features are insufficient
3. **Evidence** — source paths of ≥3 (or ≥2 for stdlib) independent AILang applications
4. **Specification** — if a language feature: grammar, semantics, error codes, examples.
   If a stdlib addition: function signatures, behaviour, edge cases.
5. **Backward compatibility** — does it break existing programs? If yes, migration path.
6. **Implementation sketch** — high-level approach (parsing, IR, runtime, etc.)

### 2.3 Evidence Requirements

**Language features** require the proposer to provide:
- At least 3 independent AILang application source files
- Each must be a *real* program (not contrived examples)
- Each must demonstrate that the feature is *necessary*, not merely convenient
- Each must include a statement like: *"This application cannot be implemented
  without feature X because ..."*

**Stdlib additions** require:
- At least 2 independent applications, or
- A documented gap in the existing stdlib (e.g., a function listed in
  `STDLIB_REFERENCE.md` that does not exist in the runtime)

**Evidence is recorded permanently** in `LANGUAGE_EVOLUTION.md` with links to
the requesting applications.

### 2.4 Review Process

```
Discussion → Formal Proposal → Review Period → Decision → Record
```

| Step | Owner | Duration | Outcome |
|------|-------|----------|---------|
| Pre-proposal discussion | Community | Indefinite | Go / No-go |
| Formal proposal submitted | Proposer | — | — |
| Technical review | Compile team | 1 week | Feasibility assessment |
| Application review | Project lead | 1 week | Evidence validation |
| Decision | Project lead | — | Accepted / Rejected / Deferred |
| Record | Project lead | — | Entry in `LANGUAGE_EVOLUTION.md` |

The project lead may:
- **Accept** the proposal as-is
- **Accept with modifications** (e.g., scope reduction)
- **Reject** with written rationale (recorded permanently)
- **Defer** to a future milestone (recorded with target version)

### 2.5 Decision Record

Every decision — accepted or rejected — is recorded in `docs/LANGUAGE_EVOLUTION.md`
with:
- The feature name and category
- Which application(s) requested it
- Whether it was accepted or rejected
- The rationale for the decision
- The version in which it was added (if accepted)

Rejected proposals stay in the table permanently. They may be reopened only with
*new* evidence (additional applications, changed circumstances, industry shifts).

---

## 3. Versioning Policy

AILang follows [Semantic Versioning 2.0.0](https://semver.org/).

| Bump | What it means | Examples |
|------|---------------|----------|
| **MAJOR** (x.0.0) | Breaking change to language or compiler API | Syntax removal, semantics change, API removal |
| **MINOR** (0.x.0) | New functionality, backward-compatible | New stdlib module, new builtin, new devtool |
| **PATCH** (0.0.x) | Bug fixes, documentation, performance | Crash fix, typo, benchmark improvement |

**Pre-1.0** (current: 0.1.x): During initial development, `MINOR` bumps may
include breaking changes with an ADR. After 1.0, breaking changes require a
`MAJOR` bump and a deprecation cycle.

See `docs/RELEASE_PROCESS.md` for the full release checklist.

---

## 4. Backward Compatibility Guarantees

### 4.1 Current Guarantee (Pre-1.0)

While AILang is in the 0.x phase, breaking changes are permitted but must be:
1. Documented in an ADR (`docs/ADR-*.md`)
2. Recorded in `CHANGELOG.md`
3. Given a migration path where possible

### 4.2 Post-1.0 Guarantee

After version 1.0.0, the following are guaranteed:

1. **Source compatibility**: Any valid AILang program that compiles on version N
   will compile on version N+1 (minor/patch) without modification.
2. **Stdlib API stability**: Documented stdlib function signatures will not change
   in minor/patch releases. New functions may be added.
3. **CLI interface**: Documented CLI flags and exit codes will remain stable.
4. **Deprecation cycle**: Breaking changes will be announced at least one minor
   release before they take effect. The deprecated feature will produce a warning
   in the deprecation release and be removed in the next major release.
5. **Error code stability**: Error codes once assigned will never be reassigned.
   Deprecated error codes are marked but not reused.

### 4.3 Exceptions

The following are explicitly **not** covered by backward compatibility:
- Internal compiler APIs (not in public docs)
- Undocumented behaviour
- Generated IR format (not stable between versions)
- `.ail` stdlib wrapper files (may be refactored; public API is the documented
  function signatures)

---

## 5. Feature Lifecycle

```
Proposal → Accepted → Implemented → Documented → Stable → Deprecated → Removed
```

1. **Proposal** — Formal submission (see §2)
2. **Accepted** — Decision recorded in `LANGUAGE_EVOLUTION.md`
3. **Implemented** — Code, tests, and spec complete
4. **Documented** — `STDLIB_REFERENCE.md`, `LANGUAGE_SPEC.md`, or relevant doc updated
5. **Stable** — Feature enters backward-compatibility guarantee
6. **Deprecated** — Scheduled for removal (warning emitted, migration guide provided)
7. **Removed** — Feature deleted in a major release

---

## 6. Rejected Forever

The following language features are **permanently rejected**. They will never be
added to AILang, regardless of how many applications request them. Proposals for
these features will be closed without review.

This list exists so contributors understand these are intentional design choices,
not oversights. No need to argue, campaign, or "prove the need."

| Feature | Rationale |
|---------|-----------|
| **Significant whitespace** | AILang uses explicit braces `{}` for blocks. Whitespace-sensitive languages (Python, YAML) cause brittle parsing, invisible bugs, and poor AI generation reliability. |
| **Operator overloading** | AILang has no user-defined types and no mechanism for custom operators. Overloading would add compiler complexity for zero benefit at this stage. Functions are the only abstraction mechanism. |
| **Macros / compile-time code generation** | Macros introduce hidden code paths, complicate error messages, and break determinism guarantees. AILang values explicitness over syntactic abstraction. |
| **Implicit type conversions** | All conversions must be explicit via `convert.to_int()`, `convert.to_string()`, etc. Implicit coercion is a leading source of bugs in other languages. |
| **Multiple inheritance** | AILang has no class or inheritance system. Multiple inheritance would add significant complexity without alignment to the language's design goals. |
| **List / map / set literals syntax** | No `[1, 2, 3]`, `{"key": "val"}`, or `{1, 2, 3}` literals. Collections are built with `new()` / `append()` / `set()`. Literal syntax was rejected after Phase 8 documentation audit. |
| **Float literal syntax** | No `3.14` decimal literals. All numbers are integers. Phase 8 docs corrected to reflect this limitation. |
| **`while` / `for` loops** | AILang deliberately has no iterative constructs. Recursion is the iteration mechanism. Grammar stays minimal. |
| **Short-circuit `&&` / `||`** | Both operands are always evaluated before the operator is applied. Changing this is a semantic break. Workaround: nested `if` blocks. |

---

## 7. Freeze Policy: v0.1.x Language Freeze

As of AILang v0.1.x, the language specification is **frozen**. No changes to
syntax, grammar, keywords, or semantics will be accepted while the ecosystem
and tooling mature.

### Allowed

| Category | Examples |
|----------|----------|
| Compiler bug fixes | Crash fixes, correctness defects, non-determinism |
| Runtime bug fixes | Interpreter errors, builtin defects, edge cases |
| Documentation improvements | New guides, clarifications, typo fixes, examples |
| Standard library additions | New functions or modules (with evidence, see §2) |
| Tooling | Formatter, linter, LSP, CLI improvements, editor extensions |
| Performance improvements | Compile time, memory, execution speed (benchmark-verified) |

### Not Allowed

| Category | Examples |
|----------|----------|
| New keywords | Any addition to the keyword list |
| Grammar changes | New syntax forms, punctuation changes |
| Syntax changes | Altering existing syntax, adding syntactic sugar |
| Semantic changes | Changing how existing constructs behave |
| Breaking changes | Anything that breaks existing valid `.ail` programs |

### Duration

The freeze remains in effect until v1.0.0 is released. After v1.0.0, language
changes follow the full governance process in §2.

### Why Freeze?

The language has reached a point where stability matters more than expansion.
Freezing the language lets the ecosystem — documentation, tooling, community
programs, real-world usage — grow without chasing a moving target. When the
language does evolve, it will be driven by evidence from actual users, not
theoretical discussions.

---

## 8. Roles & Responsibilities

| Role | Responsibility |
|------|---------------|
| **Project lead** | Final decision authority on all proposals; maintains `LANGUAGE_EVOLUTION.md` |
| **Technical reviewer** | Assesses feasibility, implementation cost, and spec correctness |
| **Proposer** | Submits proposal with evidence; may be any contributor |
| **Community** | Provides feedback during pre-proposal discussion |

---

## 9. Related Documents

| Document | Purpose |
|----------|---------|
| [LANGUAGE_EVOLUTION.md](LANGUAGE_EVOLUTION.md) | Permanent record of every feature request and its disposition |
| [PROJECT_CONSTITUTION.md](PROJECT_CONSTITUTION.md) | Immutable rules for development |
| [RELEASE_PROCESS.md](RELEASE_PROCESS.md) | Version bumping, branching, and release checklist |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Day-to-day developer workflow |
| [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md) | Canonical specification of the language |
| [PRODUCT_ROADMAP.md](PRODUCT_ROADMAP.md) | Long-term feature planning |
