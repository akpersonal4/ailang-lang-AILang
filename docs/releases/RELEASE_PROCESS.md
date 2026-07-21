# Release Process

## Versioning

AILang follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes to the language or compiler API
- **MINOR** (0.1.0 → 0.2.0): New features, new stdlib modules, non-breaking enhancements
- **PATCH** (0.1.1 → 0.1.2): Bug fixes, documentation updates, performance improvements

Current version: **0.1.2** (pre-1.0 development phase)

## Release Checklist

### 1. Pre-Release Preparation

- [ ] Review all open issues and PRs for the milestone
- [ ] Ensure all planned features are implemented and tested
- [ ] Run the full test suite and verify all tests pass
- [ ] Run all quality gates (black, ruff, mypy)
- [ ] Update `PROJECT_STATE.json` with current test counts and status
- [ ] Update `CHANGELOG.md` with all changes since the last release
- [ ] Verify example programs all compile and run correctly

### 2. Version Bump

- [ ] Update `version` in `pyproject.toml`
- [ ] Update `version` in `PROJECT_STATE.json`
- [ ] Run tests to verify everything still works after version change

### 3. Documentation

- [ ] Review ALL documentation for accuracy and consistency
- [ ] Update any docs affected by changes in this release
- [ ] Verify all links in documentation are valid
- [ ] Update `DEVELOPMENT_STATUS.md` — move completed milestone to "Recently Completed", update "Current Work"
- [ ] Update `README.md` with current status

### 4. Quality Assurance

- [ ] Run full test suite: `python -m pytest`
- [ ] Run formatter: `black --check .`
- [ ] Run linter: `ruff check .`
- [ ] Run type checker: `mypy`
- [ ] Run all 27 app programs to verify they compile: `ail build apps/*/main.ail`
- [ ] Run benchmark tests: `python -m pytest tests/test_benchmark.py -v`
- [ ] Run stress tests: `python -m pytest tests/test_stress.py -v`
- [ ] Run AI validation tests: `python -m pytest tests/test_ai_validation.py -v`
- [ ] Verify CLI examples: `ail run examples/json_demo.ail`

### 5. Release

- [ ] Create a git tag: `git tag -a v0.1.1 -m "Release v0.1.1"`
- [ ] Push the tag: `git push origin v0.1.1`
- [ ] Create a GitHub Release with:
  - Release title: `v0.1.1`
  - Description: Summary of changes from `CHANGELOG.md`
  - Attach any build artifacts if applicable
- [ ] Verify the GitHub Release page is correct

### 6. Post-Release

- [ ] Update `PROJECT_STATE.json` with the new version
- [ ] Set the next milestone in `DEVELOPMENT_STATUS.md` ("Current Work" → "Recently Completed", new milestone in "Current Work")
- [ ] Communicate the release to contributors
- [ ] Begin work on the next milestone

## Release Cadence

During the pre-1.0 phase:
- **Minor releases**: Every 2-4 weeks, or when a milestone is complete
- **Patch releases**: As needed for bug fixes

After 1.0:
- **Major releases**: When breaking changes are accumulated
- **Minor releases**: Quarterly feature releases
- **Patch releases**: As needed

## Hotfix Process

For critical bugs that cannot wait for the next release:

1. Create a hotfix branch from the latest release tag
2. Apply the fix
3. Run all tests
4. Create a patch release
5. Merge the hotfix branch back into main

## Branch Strategy

```
main          ← Stable, release-ready code
├── develop   ← Integration branch for next release
│   ├── feature/*   ← New features (merge to develop)
│   └── fix/*       ← Bug fixes (merge to develop)
└── hotfix/*   ← Urgent fixes (branch from main, merge to main + develop)
```

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or changes
- `refactor`: Code refactoring (no behavior change)
- `perf`: Performance improvement
- `chore`: Build, CI, tooling changes

Examples:
```
feat(stdlib): add json module with parse and stringify
fix(parser): handle empty function body correctly
docs: add installation guide for Windows
test: add stress test for 10000 LOC programs
```

## Release Artifacts

Current releases are distributed as source code only (via GitHub). Future releases may include:

- PyPI package (`pip install ailang`)
- Pre-built binaries for Windows, Linux, macOS
- Docker images
- VS Code extension

## Current v0.1.2 Release Summary

| Component | Status |
|-----------|--------|
| Compiler pipeline | Complete and validated |
| Standard Library v1.0 | 16 modules, feature-complete |
| Tests | 522 passing |
| Quality gates | All clean |
| Documentation | Canonical specification + full ecosystem guides |
| Examples | 55+ example programs |
| Apps | 27 application programs |
