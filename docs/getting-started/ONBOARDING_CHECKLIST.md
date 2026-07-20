# Onboarding Checklist

A step-by-step guide for new developers joining the AILang project.

---

## Day 1: Environment Setup

- [ ] **Install Python 3.11+** — verify with `python --version`
- [ ] **Install AILang** — `pip install ailang-lang`
- [ ] **Verify CLI** — `ail version` should print `AILang v1.1.0`
- [ ] **Run the environment check** — `ail doctor` (look for score > 0/100)
- [ ] **Clone the repo** — `git clone https://github.com/akpersonal4/ailang-lang-AILang.git`
- [ ] **Install dev dependencies** — `pip install -e .` then `pip install pytest black ruff`
- [ ] **Run the test suite** — `ail test` (expect 1074+ passing)

## Day 1: Write Your First Program

- [ ] Create `hello.ail`:
  ```ail
  fn main() {
      print("Hello, AILang!");
      return 0
  }
  ```
- [ ] Run it — `ail run hello.ail`
- [ ] Format it — `ail fmt hello.ail`
- [ ] Check it — `ail check hello.ail`

## Day 2: Learn the Language

- [ ] Read the [Quick Start](QUICK_START.md) (5 min)
- [ ] Read the [Language Tour](../reference/LANGUAGE_TOUR.md) (15 min)
- [ ] Read [AGENTS.md](../../AGENTS.md) — the Hard Rules table is the critical section
- [ ] Browse the [Standard Library Reference](../reference/STDLIB_REFERENCE.md)

### Key Language Rules to Internalize

| Rule | Example |
|------|---------|
| No loops — use recursion | `fn count(n) { if (n == 0) { return 0 }; return 1 + count(n - 1) }` |
| No forward references | Define callee before caller |
| Every `fn` ends with `return <value>` | `return 0` (not `return;`) |
| `let` needs an initializer | `let x = 5` (not `let x;`) |
| `map.get` needs a `map.has` guard | Always check before getting |
| `&&` is eager — no short-circuit | Use nested `if` when right side depends on left |
| `string.concat` takes exactly 2 args | Use `+` for 3+ strings |
| Import at top level only | Never inside a function body |

## Day 2: Learn the Toolchain

- [ ] Try each CLI command at least once:
  - `ail run <file>` — compile and execute
  - `ail check <file>` — pre-flight ordering check
  - `ail build <file>` — build to bytecode
  - `ail fmt <file>` — format code
  - `ail test` — run test suite
  - `ail new <name>` — scaffold a project
  - `ail explain <ERROR_CODE>` — get detailed error help
  - `ail doctor` — environment diagnostics
  - `ail docs LANGUAGE_SPEC` — read the spec in terminal
- [ ] Try `ail explain SEM001` and `ail explain TYP001` — note the quality of error messages

## Day 3: Explore Existing Code

- [ ] Browse `apps/` — 8 reference applications (inventory, expense, todo, employee, etc.)
- [ ] Browse `examples/patterns/` — 10 engineering patterns
- [ ] Read `docs/architecture/ARCHITECTURE_DECISIONS.md` — why AILang is the way it is
- [ ] Read `docs/architecture/M80_TECHNICAL_DEBT_ROADMAP.md` — known technical debt

## Day 3: Make Your First Contribution

- [ ] Pick a small task from the backlog
- [ ] Follow the workflow: Write → `ail fmt` → `ail check` → `ail build` → `ail test` → `ail run`
- [ ] Run `black --check .` and `ruff check .` before committing
- [ ] Submit a PR against `develop`

---

## Quick Reference Card

### Development Pipeline (mandatory order)

```
Write Code → ail fmt → ail check → ail build → ail test → ail run
```

### Useful Commands

| Command | Purpose |
|---------|---------|
| `ail run <file>` | Compile and run |
| `ail check <file>` | Pre-flight validation |
| `ail fmt <file>` | Format code |
| `ail test [dir]` | Run tests |
| `ail explain <CODE>` | Error explanation with examples |
| `ail doctor` | Environment health |
| `ail new <name>` | Scaffold project |
| `ail docs <TOPIC>` | Read docs in terminal |
| `ail heal <topic>` | Auto-fix common patterns |
| `ail rename` | Rename identifiers across files |
| `ail context --json` | Machine-readable language context |
| `ail mcp` | Start MCP server for AI tools |

### Key Documents

| Document | Purpose |
|----------|---------|
| `AGENTS.md` | AI operational rules (start here) |
| `DEVELOPMENT_STATUS.md` | What's done, what's in progress |
| `PROJECT_MEMORY.md` | Project history and decisions |
| `docs/reference/LANGUAGE_SPEC.md` | Canonical language specification |
| `docs/reference/STDLIB_REFERENCE.md` | Standard library API |
| `docs/reference/LANGUAGE_TOUR.md` | Language feature tour |
| `docs/architecture/ARCHITECTURE_DECISIONS.md` | Architecture decisions |
| `docs/architecture/M80_TECHNICAL_DEBT_ROADMAP.md` | Technical debt tracker |

---

## Getting Help

| Need | Where |
|------|-------|
| Error message unclear | `ail explain <ERROR_CODE>` |
| Environment broken | `ail doctor` |
| Language question | `ail docs LANGUAGE_SPEC` |
| Stdlib API | `ail docs STDLIB_REFERENCE` |
| Auto-fix a pattern | `ail heal <topic>` |
| Report a bug | https://github.com/akpersonal4/ailang-lang-AILang/issues |
