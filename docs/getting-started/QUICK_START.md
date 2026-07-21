# Quick Start

Get from zero to running AILang code in under 5 minutes.

---

## Prerequisites

- **Python 3.11+** installed and on your PATH

---

## Install

```bash
pip install ailang-lang
```

Verify it worked:

```bash
ail version
```

You should see `AILang v1.1.1`.

---

## Write a Program

Create `hello.ail` with any text editor:

```ail
fn main() {
    print("Hello, AILang!");
    return 0
}
```

Every AILang program needs a `fn main()` entry point. Every function must end with `return <value>`.

---

## Run It

```bash
ail run hello.ail
```

Expected output:

```
Hello, AILang!
```

---

## Next Steps

| What | Command |
|------|---------|
| Check for errors | `ail check hello.ail` |
| Format your code | `ail fmt hello.ail` |
| Scaffold a project | `ail new my_app && cd my_app` |
| Run project tests | `ail test` |
| Diagnose problems | `ail doctor` |
| Read the language docs | `ail docs LANGUAGE_SPEC` |

---

## Common First Issues

| Problem | Fix |
|---------|-----|
| `ail: command not found` | Ensure `pip install ailang-lang` succeeded and your Python `Scripts/` (Windows) or `bin/` (Linux/Mac) is in your PATH |
| `No ail.toml found` | Use `ail run <file>` (not `ail <file>`) |
| `Undefined identifier` | Move the called function above the caller — AILang has no forward references |
| `return;` syntax error | AILang requires a value: `return 0`, not `return;` |
| `while`/`for` syntax error | AILang uses recursion only — no loop constructs |

---

## Minimal Copy-Paste

```bash
pip install ailang-lang
echo 'fn main() { print("Hello, AILang!"); return 0 }' > hello.ail
ail run hello.ail
```
