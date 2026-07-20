# Quickstart

Get from zero to running AILang code in under 5 minutes.

---

## Prerequisites

- **Python 3.11+** installed
- **pip** available in your terminal

---

## Step 1: Install AILang

```bash
pip install ailang-lang
```

Verify:

```bash
ail version
```

---

## Step 2: Create a Project

```bash
ail new my_app
cd my_app
```

This creates:

```
my_app/
├── ail.toml        ← project manifest
├── ail.lock        ← dependency lock file
├── main.ail        ← your entry point
├── README.md
└── data/
    └── sample.json
```

---

## Step 3: Run It

```bash
ail run main.ail
```

Expected output:

```
Welcome to inventory!

Get started by editing main.ail
```

---

## Step 4: Edit Your Code

Open `main.ail` and modify it:

```ailang
import io;

fn main() {
    io.writeln("Hello from AILang!");
}
```

Run again:

```bash
ail run main.ail
```

---

## What Just Happened

| Step | Command | What It Does |
|------|---------|--------------|
| Install | `pip install ailang-lang` | Installs the AILang compiler, runtime, and standard library |
| Create | `ail new my_app` | Scaffolds a project with `ail.toml`, `ail.lock`, and `main.ail` |
| Run | `ail run main.ail` | Compiles and executes your AILang program |

---

## Next Steps

- **Add a dependency:** `ail add math_utils --version 1.0.0`
- **Install dependencies:** `ail install`
- **Run tests:** `ail test`
- **Format code:** `ail fmt main.ail`
- **Check for errors:** `ail build main.ail`

---

## Common First Issues

### "Module not found"

The standard library is bundled. If you see this, ensure you're in the project directory and `ail.toml` exists.

### "No ail.toml found"

Run `ail new <project_name>` to scaffold, or `ail init` in an existing directory.

### "ail: command not found"

Ensure `pip install ailang-lang` succeeded and your Python `Scripts/` or `bin/` directory is in your `PATH`.

---

## Minimal Example (copy-paste)

```bash
pip install ailang-lang
ail new hello
cd hello
ail run main.ail
```

Total time: **< 2 minutes**.
