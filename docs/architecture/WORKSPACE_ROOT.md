# Workspace‑Root Resolution (Sprint 3)

## Deterministic precedence

When a CLI or DX tool needs a base directory for relative path resolution it must call the **single** helper:

```python
from compiler.root import resolve_workspace_root
root = resolve_workspace_root(root_arg)  # ``root_arg`` is the optional ``--root`` string
```

The function follows this **exact order**:

1. **Explicit ``--root`` argument** – if the user supplies ``--root <DIR>`` the function returns that absolute path.
2. **Workspace marker** – walks upward from ``Path.cwd()`` looking for ``ail.toml``. The directory containing the marker is considered the *workspace root*.
3. **Fallback** – if no marker is found, the current working directory itself is used.

All commands (`ail order`, `ail rename`, `ail doctor`, `ail context`, `ail benchmark`, `ail testgen`) now import and use this helper; there must be **no other** calls to ``Path.cwd()``, ``get_project_root()`` or ``_find_stdlib().parent`` throughout the codebase.

## Rationale

* Guarantees consistent behaviour regardless of where the user runs the command.
* Provides a clear, documented extension point (`--root`) for advanced workflows.
* Eliminates hidden coupling to the repository layout or site‑packages directory.

## Usage examples

```bash
# Operate relative to the current directory (default)
ail rename old.ail new.ail

# Operate relative to a specific workspace (e.g. a cloned repo located elsewhere)
ail rename old.ail new.ail --root C:/projects/ailang

# Force a repo‑wide rename (searches the entire repository root)
ail rename foo.ail bar.ail --global
```
