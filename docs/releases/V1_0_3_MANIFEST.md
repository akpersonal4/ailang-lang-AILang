# v1.0.3 Release Manifest

| File | Reason for inclusion | Sprint |
|------|----------------------|--------|
| `compiler/cli/main.py` | CLI now runs type‑checker and catches internal errors (CMP001) | Sprint 2 |
| `compiler/root.py` | Centralised workspace‑root resolver (`resolve_workspace_root`) | Sprint 3 |
| `compiler/types/types.py` | Added `LIST_TYPE` primitive | Sprint 1 |
| `compiler/types/checker.py` | Enforced `TYP005`/`TYP006` diagnostics for illegal arithmetic/comparison | Sprint 1 |
| `compiler/exceptions.py` | `InternalCompilerError` class for uniform internal‑error handling | Sprint 2 |
| `tests/test_type_errors.py` | Regression test for illegal arithmetic/comparison | Sprint 1 |
| `tests/test_ir_crash.py` | Regression test for IR‑builder `ValueError` → CMP001 | Sprint 2 |
| `tests/test_path_resolution.py` | Path‑resolution matrix (relative/absolute, `--root`, `--global`) | Sprint 3 |
| `pyproject.toml` | Bumped version to **1.0.3** | Sprint 1 |
| `README.md` | Updated version badge and release‑notes link | Documentation |
| `docs/architecture/WORKSPACE_ROOT.md` | Specification of deterministic workspace‑root precedence | Sprint 3 |
| `docs/milestones/M69_8_RELEASE_SYNC.md` | Summary of the release‑sync process | Documentation |
| `CHANGELOG.md` | Added “v1.0.3 – M69 Stabilisation Release” entry | Documentation |
| `CONTRIBUTING.md` | Updated “Release” section with new workflow | Documentation |
| `docs/releases/V1_0_3_MANIFEST.md` | This manifest (self‑documenting release contents) | Documentation |
