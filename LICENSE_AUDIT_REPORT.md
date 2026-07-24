# License Audit Report

## License Consistency Investigation

### Observation Reported

Independent validator found:
- Repository: MIT
- PyPI metadata: Apache-2.0

### Investigation

#### Question 1: What is the actual license?

**Finding: Apache-2.0 throughout**

The validator's observation about "Repository: MIT" is incorrect. All actual license references show Apache-2.0.

#### Evidence

| Location | License | Verified |
|----------|---------|----------|
| `LICENSE` file (root) | Apache-2.0 | Yes - full Apache 2.0 license text |
| `pyproject.toml` | `license = { text = "Apache-2.0" }` | Yes |
| `README.md` badge | `Apache 2.0` | Yes |
| PyPI METADATA | `License: Apache-2.0` | Yes |

#### Historical Context

Archived documents reference MIT license. This is because:

1. The project was originally MIT-licensed
2. At some point, the license was changed to Apache-2.0
3. Evidence from `extensions/vscode-ailang/CHANGELOG.md`:
   > License changed from MIT to Apache-2.0

Archived documents were not updated:
- `docs/archive/v0.1.0/RELEASE_PACKAGING_AUDIT.md` - references MIT (archived)
- `docs/archive/v0.1.0/OPEN_SOURCE_READINESS.md` - references MIT (archived)
- `CHANGELOG.md` line 600 - historical note about MIT (not current)

#### Current State

All **current, non-archived** references consistently show Apache-2.0:
- LICENSE file at repository root - Apache-2.0
- pyproject.toml - Apache-2.0
- README.md - Apache 2.0
- PyPI package metadata - Apache-2.0

### Conclusion

**NOT A BUG - License is Consistent**

The license is Apache-2.0 consistently across all locations. The validator's observation about MIT appears to be based on:
1. Historical references in archived documents, or
2. Confusion about past license state

No changes required.

### Dual Licensing

**Is dual licensing intentional?**

No. The project is Apache-2.0 only. The archived MIT references are outdated and should eventually be cleaned up, but they are in `docs/archive/` which is explicitly marked as historical.

### Recommendation

No license changes required. The project is consistently Apache-2.0.

### Optional: Archive Cleanup (Future)

The following archived documents contain outdated license references:
- `docs/archive/v0.1.0/RELEASE_PACKAGING_AUDIT.md`
- `docs/archive/v0.1.0/OPEN_SOURCE_READINESS.md`
- `CHANGELOG.md` (historical note only)

These are in archived directories and their content is explicitly marked as historical. No immediate action required.