# Package Management

AILang packages let you share and reuse code across projects.

---

## Concepts

| Term | Meaning |
|------|---------|
| **Package** | A directory with an `ail.toml` manifest and `.ail` source files |
| **Dependency** | A package your project imports |
| **Registry** | A server that hosts packages for download (local or remote) |
| **Manifest** | `ail.toml` — declares your project name, version, and dependencies |
| **Lock file** | `ail.lock` — records exact resolved versions for reproducibility |

---

## Package Names

Package names must be **snake_case**: lowercase letters, digits, underscores, starting with a letter.

```
✅  my_package
✅  string_utils

❌  my-package    (kebab-case — deprecated)
❌  My_Package    (uppercase)
```

See [PACKAGE_NAMING_POLICY.md](PACKAGE_NAMING_POLICY.md) for full details.

---

## Creating a Package

```bash
ail new my_library
cd my_library
```

This creates `ail.toml`:

```toml
[project]
name = "my_library"
version = "0.1.0"
description = "An AILang project"
entry = "main.ail"

[language]
version = "0.3"
```

Write your library code in `main.ail` (or additional `.ail` files).

---

## Publishing a Package

### Local registry (for testing)

```bash
ail publish --registry file:///tmp/my_registry
```

This packs your project into a `.tar.gz` and uploads it to the local registry directory.

### Remote registry

```bash
ail publish
```

Publishes to the configured registry (default: `https://registry.ailang.dev`).

---

## Installing a Package

### From a local registry

```bash
ail add my_package --path /path/to/my_package
ail install
```

### From a git repository

```bash
ail add my_package --git https://github.com/user/repo.git --tag v1.0.0
ail install
```

### From the remote registry

```bash
ail add my_package --version 1.0.0
ail install
```

---

## Managing Dependencies

### Add a dependency

```bash
ail add math_utils --version 1.0.0
```

This edits `ail.toml`:

```toml
[dependencies]
"math_utils" = "1.0.0"
```

### Remove a dependency

```bash
ail remove math_utils
```

### Update dependencies

```bash
ail update              # re-resolve all
ail update math_utils   # re-resolve one
```

### List installed packages

```bash
ail list
```

Output:

```
Dependencies (1):

  math_utils 1.0.0  [ok]
```

### Install all dependencies

```bash
ail install
```

Reads `ail.toml`, resolves versions, downloads packages to `lib/`, and writes `ail.lock`.

---

## Project Structure After Install

```
my_project/
├── ail.toml
├── ail.lock
├── main.ail
├── lib/
│   └── math_utils/
│       ├── ail.toml
│       └── main.ail
└── ...
```

---

## Importing Packages

Once installed, import packages with `import`:

```ailang
import math_utils;

fn main() {
    let result = math_utils.add(2, 3);
    io.writeln(result);
}
```

---

## Dependency Sources

| Source | Syntax in ail.toml | Example |
|--------|-------------------|---------|
| Registry | `"name" = "version"` | `"math_utils" = "1.0.0"` |
| Local path | `"name" = { path = "..." }` | `"math_utils" = { path = "../math_utils" }` |
| Git repo | `"name" = { git = "..." }` | `"math_utils" = { git = "https://...", tag = "v1.0.0" }` |

---

## Full Workflow Example

```bash
# 1. Create a library
ail new math_utils
cd math_utils
# ... write code in main.ail ...

# 2. Publish to local registry
ail publish --registry file:///tmp/reg

# 3. Create a consumer project
cd ..
ail new my_app
cd my_app

# 4. Add and install the dependency
ail add math_utils --path /tmp/reg/packages/math_utils
ail install

# 5. Use it
# Edit main.ail to import math_utils
ail run main.ail
```

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `ail new <name>` | Create a new project with `ail.toml` |
| `ail init` | Initialize `ail.toml` in current directory |
| `ail add <pkg>` | Add a dependency to `ail.toml` |
| `ail remove <pkg>` | Remove a dependency from `ail.toml` |
| `ail install` | Download and install all dependencies |
| `ail update [pkg]` | Re-resolve dependencies |
| `ail list` | Show installed dependencies |
| `ail publish` | Publish to registry |
