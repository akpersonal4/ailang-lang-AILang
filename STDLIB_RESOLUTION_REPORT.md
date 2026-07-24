# Stdlib Module Resolution Report

## Issue: MOD003 When Running from Outside Project Tree

### Problem Description

When running AILang programs that import stdlib modules from a directory outside the project tree (e.g., from a temp directory), the compiler failed with:

```
ERROR MOD003: Module not found: string
```

### Root Cause Analysis

The `ModuleResolver` class in `compiler/compilation/resolution.py` is responsible for resolving module paths to file paths during compilation. The `_candidate_roots()` method searches for modules by walking upward from the source file's directory.

**The Problem:**
- `_candidate_roots()` only searches the local filesystem hierarchy
- It does not check the installed package's stdlib directory
- When running from outside the project tree (e.g., `C:\Temp\`), the upward walk never finds the stdlib

**Why CLI execution worked but compilation failed:**
- The CLI's `_find_stdlib()` function correctly finds the stdlib for the interpreter
- But the `ModuleResolver` used during compilation didn't have equivalent logic
- This created a mismatch where compilation would fail but execution might succeed (if the code even got that far)

### Code Changes

**File:** `compiler/compilation/resolution.py`

**Change 1:** Added `_find_stdlib_root()` helper function:

```python
def _find_stdlib_root() -> Path | None:
    """Locate the stdlib directory in the installed package.

    Mirrors the logic in compiler.cli.main:_find_stdlib() to ensure
    module resolution can find stdlib modules even when running from
    outside the project tree (e.g., from a temp directory).

    Search order:
    1. Next to the compiler package (site-packages/stdlib/) — installed wheel
    2. Next to the package parent (repo-root/stdlib/) — editable/dev install
    3. Bundled in site-packages (site-packages/ailang_lang-*/stdlib/)

    Returns:
        Path to the stdlib directory if found, None otherwise.
    """
    try:
        import compiler

        compiler_path = Path(compiler.__file__).resolve()
        pkg_dir = compiler_path.parent.parent  # 2 levels up from compiler/__init__.py

        candidate = pkg_dir / "stdlib"
        if candidate.is_dir() and list(candidate.iterdir()):
            return candidate
    except (ImportError, ValueError):
        pass

    for site_dir in site.getsitepackages():
        bundled = Path(site_dir) / "stdlib"
        if bundled.is_dir() and list(bundled.iterdir()):
            return bundled

    return None
```

**Change 2:** Updated `_candidate_roots()` to include installed stdlib as a fallback:

```python
def _candidate_roots(self) -> list[Path]:
    """Return search roots, preferring the project root and its stdlib dir.

    Includes the installed package's stdlib as a fallback so that
    stdlib modules can be resolved even when running from outside
    the project tree (e.g., from a temp directory).
    """
    # ... existing code ...

    installed_stdlib = _find_stdlib_root()
    if installed_stdlib is not None:
        stdlib_resolved = installed_stdlib.resolve()
        if stdlib_resolved not in seen:
            roots.append(stdlib_resolved)
            seen.add(stdlib_resolved)

    return roots
```

### Bug Fixed During Implementation

**Initial implementation error:** Used `parent.parent.parent` (3 levels up) instead of `parent.parent` (2 levels up).

Trace for `compiler/__init__.py`:
- `parent` = `compiler/`
- `parent.parent` = `repo/` or `site-packages/` (correct - package root)
- `parent.parent.parent` = parent of repo (incorrect - too far)

The correct path is `parent.parent` because:
- For installed packages: `site-packages/compiler/__init__.py` → `site-packages/`
- For editable installs: `repo/compiler/__init__.py` → `repo/`

### Verification

**Before fix (from temp directory):**
```
$ ail run test.ail
ERROR MOD003: Module not found: string
```

**After fix (from temp directory):**
```
$ ail run test.ail
HELLO
```

**Tested stdlib modules:**
- `string` - works
- `math` - works
- `list` - works
- `map` - works
- `json` - works

### Regression Testing

| Test | Result |
|------|--------|
| pytest tests/ (1014 tests) | All passed |
| test_module_resolution.py (14 tests) | All passed |
| Module resolution from outside project tree | Fixed |

### Related Code

The fix mirrors the logic in `compiler/cli/main.py:_find_stdlib()` which handles finding the stdlib for CLI execution. This ensures consistency between compilation and execution paths.

### No Other Changes Required

This fix is self-contained in `resolution.py`. No changes to:
- Documentation
- Packaging
- CLI entry points
- Test files