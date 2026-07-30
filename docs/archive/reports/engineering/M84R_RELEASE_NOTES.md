# M84R Release Notes

## AILang v1.1.2 — Developer Experience Remediation

This release addresses issues identified by an independent developer during M84 certification.
The goal was not to add features, but to ensure the next developer has a smoother first experience.

### What Changed

**Stdlib modules now work out of the box.**

After `pip install ailang-lang`, standard library modules (io, string, math, json, etc.) are resolved automatically by the compiler. No manual file copying required.

```bash
pip install ailang-lang
ail new demo
cd demo
ail run main.ail   # Works immediately
```

**`ail doctor` no longer crashes.**

The doctor tool now shows user-relevant diagnostics when run from a project:
- Python version check
- `ail` CLI availability
- `ailang` package installation
- Stdlib module availability
- Project structure validation

**`convert.to_number` handles decimals.**

```ail
import convert;

convert.to_number("10.5")   // 10.5
convert.to_number("42")     // 42.0
convert.to_number(42)       // 42.0
```

**`ail install` and `ail add` find your project.**

These commands now correctly detect the project root regardless of working directory.

**`ail heal` accepts file paths.**

```bash
ail heal myfile.ail    # Auto-detects errors and suggests fixes
ail heal forward_reference  # Manual topic lookup still works
```

### Documentation Updates

- Installation guide now leads with `pip install ailang-lang`
- Getting Started guide includes project setup workflow
- Module resolution algorithm fully documented
- Troubleshooting table expanded

### Files Changed

| Category | Files |
|----------|-------|
| Compiler | `session.py`, `main.py`, `builtins.py` |
| Stdlib | `convert.ail` |
| DX Tools | `ail_doctor/__main__.py`, `ail_heal/__main__.py`, `ail_package_manager/__main__.py` |
| Docs | `GETTING_STARTED.md`, `INSTALLATION.md`, `STDLIB_REFERENCE.md`, `MODULE_SYSTEM.md`, `README.md` |

### Backward Compatibility

All changes are backward compatible. No syntax changes, no breaking behavior changes.
Existing programs continue to work without modification.
