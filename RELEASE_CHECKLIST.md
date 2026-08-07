# AILang Release Checklist

Standard operating procedure for every AILang release (patch, minor, or major).
First captured during the v1.1.16-RC1 audit. Each gate must pass before moving
to the next. The canonical rule set lives in `AGENTS.md`; this document is the
step-by-step execution order.

---

## Phase 0 — Preconditions

- [ ] All milestone deliverables merged and archived (see `docs/archive/`).
- [ ] New version agreed (patch/minor/major) with CTO/Architecture as needed.
- [ ] Read the mandatory docs per `AGENTS.md` §2 before touching internals.

## Phase 1 — Version Bump (single source of truth)

- [ ] Bump `version` in `pyproject.toml`.
- [ ] Regenerate `compiler/_version.py`:
      `python scripts/generate_version.py` (or equivalent).
- [ ] Sync version-dependent fallbacks: `tools/ail_context/__main__.py`,
      `tools/ail_mcp/server.py`, `tools/ail_mcp/context_adapter.py`,
      `tools/ail_mcp/__init__.py`, `extensions/vscode-ailang/package.json`.
- [ ] Sync docs: `docs/reference/LANGUAGE_SPEC.md` header, `PROJECT_MEMORY.md`,
      `DEVELOPMENT_STATUS.md`, `README.md` pip-install line.
- [ ] Add `CHANGELOG.md` entry.
- [ ] Verify all surfaces: `ail --version`, `ail version`, `ail doctor`
      ("All versions consistent"), `ail context --json`.

## Phase 2 — Clean Build

- [ ] Delete `build/` and `ailang_lang.egg-info` (stale artifacts corrupt wheels).
- [ ] `python -m build` (build package installed in dev venv).
- [ ] Record build timestamp (UTC) for both artifacts.

## Phase 3 — Packaging Audit

- [ ] List wheel contents: only `ail_platform/`, `compiler/`, `stdlib/`,
      `tools/`, `dist-info/`.
- [ ] List sdist top level: same, plus packaging metadata.
- [ ] Banned-pattern scan (script): no data files (`*.json` at root), no scratch
      artifacts, no `.venv`, caches, `build/`, `dist/`, stray reports.
- [ ] `twine check <wheel> <sdist>` → PASSED.

## Phase 4 — Fresh Venv + Wheel-Only Install

- [ ] `python -m venv .venv_<rel>` (fresh, outside any source checkout).
- [ ] `.venv_<rel>\Scripts\pip install dist\<pkg>-<ver>.whl` (no `-e`).
- [ ] Confirm installed import resolves to site-packages:
      run from a **neutral directory** with `PYTHONPATH` empty
      (from the repo root, `python` shadows site-packages with the source tree).

## Phase 5 — Install Audit (wheel only, neutral CWD, empty PYTHONPATH)

Every CLI command is exercised against the installed wheel:

- [ ] `ail --version` / `ail version` → expected version
- [ ] `ail doctor` → all consistent
- [ ] `ail context --json` → expected version
- [ ] `ail run <hello>` → exit 0
- [ ] `ail check` / `ail fmt` / `ail build` / `ail order` → pass
- [ ] `ail explain <code>` / `ail docs` → list content
- [ ] `ail test` (scratch project) → pass
- [ ] `ail testgen <file>` (explicit path) → pass
- [ ] `ail new <proj>` → scaffold runs
- [ ] `ail rename` dry-run guard → behaves as designed
- [ ] Note interactive/network commands not smoke-tested: `watch`, `lsp`,
      `mcp`, package-manager commands.
- [ ] Canonical apps from wheel: `ail run apps/<app>/main.ail` for each app
      (pass the app's required args) → exit 0.

## Phase 6 — Regression Audit (source tree)

- [ ] Full test suite: `python -X utf8 -m pytest tests -q --no-header`
      (~13-25 min; run in background and poll). Record exact count.
- [ ] Canonical benchmark: `python -X utf8 -m compiler benchmark` → 5/5 apps OK.
- [ ] No lint/type errors in touched files.

## Phase 7 — Freeze

- [ ] Code frozen. No further changes unless release-blocking.
- [ ] `git status` reviewed; no unintended files staged for the release.
- [ ] Confirm wheel/sdist are the frozen tree (rebuild if any change slipped in).

## Phase 8 — Release Notes

- [ ] Write release notes (`docs/releases/v1.x.y.md` or per naming convention)
      with: summary, bug fixes, validation evidence, known limitations
      (incl. any wheel-install limitations found), artifact SHA256 + timestamps,
      recommendation.
- [ ] Link release notes from `CHANGELOG.md`.
- [ ] If a process gap was found during the audit, document it here or in the
      playbook **before** marking the release done.

## Phase 9 — External Review (release candidates only)

- [ ] Hand the wheel, sdist, and release notes to a **completely new,
      independent reviewer**.
- [ ] Fix only release-blocking defects found; otherwise ship as-is.

## Phase 10 — Publish

- [ ] Tag `v1.<minor>.<patch>` (after external review, only when explicitly
      requested).
- [ ] `twine upload dist/<pkg>-<ver>.whl dist/<pkg>-<ver>.tar.gz`
      (requires credentials; never auto-publish).
- [ ] Update `DEVELOPMENT_STATUS.md`, `PROJECT_MEMORY.md`, README install line
      to the published version.

---

## Known Wheel-Install Limitations (document, do not fix in RC)

- `ail benchmark`, `ail static-analyzer`, `ail testgen` (app-discovery mode)
  resolve the app directory relative to the `ail_platform` package location
  (`site-packages/` under a wheel). Workarounds: `ail testgen <file>`,
  `ail run apps/<app>/main.ail`; full benchmark needs a source checkout.
  Root cause: `ail_platform/project.py::get_project_root()` returns
  `Path(__file__).parent.parent`.
