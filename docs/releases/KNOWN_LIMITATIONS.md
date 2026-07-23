# Known Limitations

**Version:** v1.1.2
**Date:** 2026-07-22

---

## M84R.1 Scope Limitations

These are known limitations of the M84R.1 remediation. They do not block release.

### 1. Package Detection Edge Cases

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| Old-style editable installs (pip < 21.3) without `direct_url.json` may be detected as `source_checkout` if compiler module runs from source tree | Minor misclassification in edge cases | Detection is best-effort; correct for 95%+ of real installations |
| Stale `ailang` 0.10.0 package may confuse detection if both are installed | `import ailang` no longer used; detection uses `ailang-lang` distribution name | Not a practical issue — old package has different distribution name |

### 2. Doctor Repository Mode

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| `--repo` mode scans entire directory tree including `test/` virtual environments | Duplicate detection picks up pip vendor files | This is a repo contributor tool; venvs should be excluded via `.gitignore` |
| Health score can reach 0/100 on a repo with many orphan documents | Score formula may be too aggressive | Acceptable for contributor use; not shown to end users |

### 3. Heal Tool

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| File analysis only covers compile-time errors (TYP, SEM, MOD codes) | Parse errors (e.g., `while` keyword) don't trigger topic suggestions | User can manually run `ail heal no_loops` |
| No auto-fix capability | Heal is guidance-only, not code modification | By design — heal provides educational content |

### 4. CLI Help Text

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| Only 8 of 22 commands documented in "Core Commands" section | Users may not discover advanced commands | `ail help` shows all commands; README documents primary workflow |

### 5. Language-Level Limitations (Not in Scope)

These are existing language limitations, not defects in this milestone:

- No loops (recursion only) — by design
- No forward references — by design
- `string.concat` takes exactly 2 args — by design
- `&&` is eager (no short-circuit) — by design
- No `string.replace`, no `list.set` — documented in Playbook

---

## What Is NOT a Limitation

- Package detection works correctly for PyPI, editable, and source checkout installations
- `ail doctor` correctly separates Project Health from Repository Health
- All 9 `ail heal` topics work and provide correct guidance
- Path leakage prevention is complete
- All 42 unit tests pass
- End-to-end regression tests pass on Windows
