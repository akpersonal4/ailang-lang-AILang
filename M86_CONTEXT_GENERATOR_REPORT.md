# M86 — Context Generator Report

**Status:** COMPLETED  
**Date:** 2026-07-22  

---

## M86F — AI Context Generator v2

### Implementation

**File:** `tools/ail_context/__main__.py`  
**Version:** 1.2.0

### New Modes

| Mode | Flag | Description | Token Usage |
|------|------|-------------|-------------|
| Default | (none) | Human-readable markdown | ~2.5 KB |
| JSON | `--json` | Machine-readable JSON | ~3.0 KB |
| Compact | `--compact` | Minimal token context | ~1.0 KB |
| LLM | `--llm` | LLM-optimized context | ~1.5 KB |
| Full | `--full` | Complete context | ~5.0 KB |

### JSON Enhancements

New fields added to JSON output:
- `compiler_version`: Real compiler version from `compiler.__version__`
- `language_version`: "0.3"
- Project structure analysis via `_get_project_structure()`

### Project Structure Analysis

The `_get_project_structure()` function:
- Reads `ail.toml` for project name/version
- Scans for `.ail` files (up to 50)
- Reports total file count

### Backward Compatibility

- Default mode produces identical output to v1.1.1 (except version string)
- `--json` mode adds new fields but preserves all existing fields
- No breaking changes to existing CLI interface

### Usage Examples

```bash
# Default (human-readable)
ail context

# Machine-readable JSON
ail context --json

# Minimal token context
ail context --compact

# LLM-optimized
ail context --llm

# Complete context
ail context --full

# Write to file
ail context --full -o PROJECT_CONTEXT.md