# ail doctor — Developer Experience Tool

> Standalone utility that checks repository health for the AILang project.

## Purpose

The `ail doctor` tool performs read-only health checks on the AILang repository and generates `generated/DOCTOR_REPORT.md` with findings. It follows the same pattern as `cargo check`, `go vet`, and `flutter doctor` — **reporting issues without modifying files**.

## Usage

```bash
# Run from project root
python -m tools.ail_doctor
```

## Checks Performed

### Repository Health
- **Missing files** — Required project files (README.md, LICENSE, etc.)
- **Duplicate files** — Files with identical content hashes
- **Empty files** — Zero-byte files in the repository
- **Large generated files** — Files over 1MB in size
- **Unexpected files** — Files that don't belong in the project structure

### Documentation Health
- **Broken internal links** — Markdown links pointing to non-existent files
- **Orphan documents** — Markdown files never referenced elsewhere

### Version Consistency
- Compares version in:
  - `pyproject.toml`
  - `README.md`
  - VS Code extension `package.json`

## Output

The tool generates `generated/DOCTOR_REPORT.md` containing:

1. **Repository Health Score**
2. **Documentation Health Score**
3. **Project Health Score**
4. **Warnings** — Non-critical issues
5. **Errors** — Critical problems
6. **Recommendations** — Suggested actions
7. **Archive Candidates** — Orphaned documents
8. **Duplicate Candidates** — Files with matching content
9. **Missing References** — Expected but missing files
10. **Version Consistency** — Cross-file version comparison

## Design

- **Standalone** — Lives in `tools/ail_doctor/`, no compiler integration
- **Read-only** — Never modifies source files or documentation
- **No external dependencies** — Uses only Python standard library