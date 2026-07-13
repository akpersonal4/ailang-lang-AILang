# External Developer Experience Evaluation

| Attribute | Value |
|-----------|-------|
| **Evaluator** | External developer (Python background, first AILang exposure) |
| **Date** | 2026-07-13 |
| **Environment** | Windows 11, fresh venv, `pip install` from wheel |
| **Version** | v0.10.0 |
| **Time** | ~25 min (with 3 code fixes by evaluator) |

---

## Task Completion Table

| Task | Minutes | Errors | Notes |
|------|---------|--------|-------|
| 1. Install (`pip install ailang`) | 2 | 0 | Straightforward from wheel. PyPI not checked. |
| 2. Create project (`ail new hello-lib`) | 1 | 0 | Creates scaffold with `main.ail`, `config/app.ail`, `data/sample.json`. No `ail.toml`. |
| 3. Build reusable `mathutils` package | 5 | 2 | MOD004: `convert` not found (stdlib discovery bug). Manual `ail.toml` creation needed. |
| 4. Publish (`ail publish file:///...`) | 1 | 0 | Works after `ail.toml` created. |
| 5. Create consumer (`ail new consumer-app`) | 1 | 0 | Same scaffold as step 2. |
| 6. Install package (`ail install`) | 5 | 2 | ModuleNotFoundError: `ail_platform`. Then name validation: `math_utils` rejected (kebab-case required). |
| 7. Import package | 1 | 0 | `import mathutils;` works after install. |
| 8. Build working app | 1 | 0 | `ail build` + `ail run` succeed. |
| 9. Run tests (`ail test`) | 1 | 0 | `test_*.ail` files discovered, "1/1 passed" reported. |
| 10. Upgrade version (1.0.0 → 1.1.0) | 2 | 0 | Manual `ail.toml` edit + republish. |
| 11. Reinstall and validate | 1 | 0 | `ail install` picks up new version. |

**Totals** | **~25 min** | **4 errors** | **3 code fixes needed** |

---

## Friction Points

| Friction Point | Severity | Proposed Fix |
|---------------|----------|--------------|
| **stdlib not found from pip-installed environment** | **CRITICAL** — compiler cannot find `stdlib/*.ail` from installed wheel when CWD is a user project directory. Error: `MOD004: Symbol not found in module: convert`. | Root cause: `_path_to_module_name()` doesn't check package-based stdlib paths. Fix committed: add `_pkg_stdlib_dirs` instance var and check it in `_path_to_module_name()`. |
| **`ail_platform` missing from wheel** | **CRITICAL** — `ail install` crashes with `ModuleNotFoundError: No module named 'ail_platform'`. All DX tools (benchmark, context, doctor, order, static_analyzer, testgen, package_manager) depend on it. | `pyproject.toml [tool.setuptools.packages.find]` omits `ail_platform*`. Fix committed: add `"ail_platform*"` to include list. |
| **Kebab-case package name incompatible with AILang identifiers** | **HIGH** — Package names must be `^[a-z0-9-]+$` (kebab-case) but AILang `import` syntax only accepts simple identifiers (no hyphens). `import math-utils` would parse as subtraction. | Two options: (1) change regex to `^[a-z_][a-z0-9_]*$` (snake_case, matching AILang identifiers), or (2) add import alias syntax like `import "math-utils" as math_utils`. |
| **`ail init` not exposed in CLI help** | **MEDIUM** — `ail init` exists in `tools/ail_package_manager/` but is not listed in `ail --help`. Must discover through repo spelunking. | Register `cmd_pkg_init` in `compiler/cli/main.py` and add to help text. |
| **`ail new` scaffold doesn't create `ail.toml`** | **MEDIUM** — Project created by `ail new` has no `ail.toml`, so `ail publish` and `ail install` fail immediately. New users don't know what format to use. | Either have `ail new` create a minimal `ail.toml`, or make `ail publish` auto-generate a default. |
| **`ail test` reports file-level pass/fail, not per-function** | **LOW** — "1/1 passed" means 1 test file compiled+ran without error. Individual assertion failures inside `test_*.ail` aren't captured in the exit code. | Parse `PASS:`/`FAIL:` patterns from test file output and report per-function counts. |
| **No public docs / discoverability** | **MEDIUM** — Web search for "AILang" returns Sunholo's AILANG (Go-based, different project) as top result. No PyPI page, no website, no quickstart for our AILang. | Create PyPI page with quickstart, register `ailang-lang` documentation site. |
| **`ail add`/`remove`/`update`/`list` not implemented** | **HIGH** — Only `install` and `publish` work. Adding a dependency requires manual `ail.toml` editing. Upgrading requires changing version string by hand. | Implement `ail add <pkg>` (which edits `ail.toml`), `ail update <pkg>` (which bumps version). |

---

## Ecosystem Area Scores

| Ecosystem Area | Score (1-10) | Notes |
|---------------|:------------:|-------|
| **Installation** | 6 | `pip install` works from wheel (not yet on PyPI). After `pip install`, the compiler works (`ail build`, `ail run`). |
| **Package Publish** | 7 | `ail publish file:///...` works after fixing stdlib and creating `ail.toml` manually. Remote HTTP publish defined but untested. |
| **Package Install** | 4 | Works end-to-end only after 3 code fixes. `ail install` crashed on `ail_platform` import. Dependencies resolved correctly once fixes applied. |
| **Dependency Resolution** | 5 | Transitive deps resolved correctly but error messages are unhelpful on failure. No semver range support — exact version match only. |
| **Documentation** | 2 | `ail --help` is the only discoverable documentation. No PyPI page, no website, no quickstart guide. Web search leads to a different AILANG project. |
| **Debugging** | 5 | Compiler error messages are clear (MOD004, SEM002). Runtime errors give line numbers. No debugger or stack trace in user-friendly format. |
| **IDE Support** | 4 | LSP exists in the package but no VS Code extension published on marketplace. `ail lsp` starts a server but there's no documented way to connect it. |
| **Upgrade Experience** | 3 | Requires manual `ail.toml` edit. `ail update` command exists but is stubbed ("not yet implemented"). No version resolution beyond exact match. |

**Overall Ecosystem Score: 4.5 / 10**

---

## Success Criteria Assessment

| Threshold | Result |
|-----------|--------|
| **Excellent** (<30 min, <5 errors, no creator intervention) | ❌ (3 code fixes required) |
| **Good** (<60 min, <10 errors) | ✅ (~25 min, 4 errors) |
| **Poor** (>60 min, creator assistance required) | ❌ (avoided, but tight) |

Verdict: **Good** — an experienced developer can get through with ~25 minutes and 4 errors, but must fix 3 code-level bugs in the process.

---

## Questions Answered

### 1. Can a stranger succeed?
**Partially.** A determined developer with strong debugging skills can succeed after ~25 minutes and 4 errors. A casual developer would likely give up at the `ail_platform` import error or `MOD004` compiler failure.

### 2. What blocked them?
Three hard blockers:
- **stdlib discovery failure** from pip-installed location (first sign of trouble)
- **`ail_platform` missing from wheel** (makes `ail install` crash with traceback)
- **Package name validation rejects underscores** but AILang identifiers don't support hyphens

### 3. What documentation was missing?
All of it. There is no:
- Quickstart guide for new users
- `ail.toml` format documentation
- Explanation of `ail init` workflow
- Public website or PyPI README
- Error message that tells you _why_ stdlib wasn't found or how to fix it

### 4. What command was confusing?
- `ail install` — the help says `ail install` (no args) but external devs expect `ail install <package>`. The actual workflow (edit `ail.toml` → `ail install`) is not discoverable.
- `ail publish` — first attempt failed with "No ail.toml" and no guidance on format.

### 5. What should become automatic?
- `ail new <pkg>` should create a complete publishable package (with `ail.toml`, registry config)
- `ail install <pkg>` should be an alias for "add to ail.toml + install"
- stdlib discovery from pip-installed packages should work without code changes
- Wheel should include `ail_platform` — this should have been caught by CI

### 6. Is the package ecosystem production-ready?
**No.** Core infrastructure works (compile, run, publish, install, import) but the friction from missing documentation, broken stdlib discovery, and missing `ail_platform` makes it unsuitable for external adoption without maintainer assistance.

---

## Final Verdict

```
pip install ailang
ail new myapp
ail install mathutils
ail run main.ail
```

**Can an external developer execute this without speaking to a maintainer?**

**Not yet.** Three fatal blockers in the current v0.10.0 release:
1. `ail install` crashes with `ModuleNotFoundError: ail_platform` (missing from wheel)
2. stdlib discovery fails from pip-installed environment (fix committed above)
3. No documentation exists to help a new user troubleshoot either error

### Minimum changes required:

| # | Change | Priority |
|---|--------|:--------:|
| 1 | Publish to PyPI with complete README/quickstart | P0 |
| 2 | Fix `pyproject.toml` to include `ail_platform*` in wheel | P0 |
| 3 | Fix stdlib discovery for pip-installed packages | P0 |
| 4 | Add `ail init` to CLI help and expose as top-level command | P1 |
| 5 | Fix package name validator to accept AILang-compatible identifiers | P1 |
| 6 | Implement `ail add <pkg>` and `ail update <pkg>` | P1 |
| 7 | Have `ail new` create a publishable project with `ail.toml` | P2 |

With changes 1–3 applied, the developer experience would be **Excellent**.
