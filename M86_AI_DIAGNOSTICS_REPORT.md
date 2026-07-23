# M86 — AI Diagnostics Report

**Status:** COMPLETED  
**Date:** 2026-07-22  

---

## M86A — Intelligent Diagnostics

### Implementation

**File:** `compiler/diagnostics.py`

**New fields on `Diagnostic` dataclass:**
- `confidence: Confidence | None` — Deterministic confidence level
- `documentation_ref: str | None` — Reference to documentation section
- `possible_fix: str | None` — Specific fix suggestion

### Diagnostic Format Before/After

**Before:**
```
SEM002
Undefined identifier
```

**After:**
```
main.ail:42:7  ERROR SEM002: Undefined identifier "foo"

Possible Fix:
  Move function "foo" above "main"

Did you mean: "foobar"?
Confidence: HIGH

Documentation: LANGUAGE_SPEC.md §8.3 — Forward References

Suggested next steps:
  ail docs AGENTS.md
  ail fmt
```

### Documentation Reference Mapping

| Error Code | Reference |
|------------|-----------|
| TYP001 | LANGUAGE_SPEC.md §8.4 — Type System |
| TYP003 | LANGUAGE_SPEC.md §8.4 — Return Types |
| SEM001 | LANGUAGE_SPEC.md §8.3 — Declarations |
| SEM002 | LANGUAGE_SPEC.md §8.3 — Forward References |
| SEM004 | STDLIB_REFERENCE.md — Standard Library |
| MOD003 | STDLIB_REFERENCE.md — Module Reference |

### Determinism

All diagnostics are purely deterministic — no AI models, no random factors, no heuristics that produce non-deterministic output.

---

## M86B — Machine Readable Diagnostics

### Verification

`ail check --json` and `ail build --json` already produce correct machine-readable JSON output.

**Example JSON output:**
```json
{
  "file": "main.ail",
  "line": 42,
  "column": 7,
  "code": "SEM002",
  "message": "Undefined identifier",
  "severity": "error",
  "suggestion": "foobar",
  "confidence": "HIGH",
  "documentation_ref": "LANGUAGE_SPEC.md §8.3 — Forward References",
  "possible_fix": "Move function \"foo\" above \"main\""
}
```

### JSON Schema (ail check --json)

```json
{
  "type": "object",
  "properties": {
    "passed": {"type": "boolean"},
    "errors": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file": {"type": "string"},
          "line": {"type": ["integer", "null"]},
          "column": {"type": ["integer", "null"]},
          "code": {"type": "string"},
          "message": {"type": "string"},
          "severity": {"type": "string"},
          "suggestion": {"type": ["string", "null"]},
          "confidence": {"type": ["string", "null"]},
          "documentation_ref": {"type": ["string", "null"]},
          "possible_fix": {"type": ["string", "null"]}
        }
      }
    },
    "total_errors": {"type": "integer"}
  }
}
```

---

## M86C — AI-Friendly Compiler Suggestions

### Suggestion Engine Methods

| Method | Purpose | Deterministic |
|--------|---------|---------------|
| `find_suggestion(unknown, known)` | Basic spell-check suggestion | Yes (difflib) |
| `find_suggestion_with_confidence(unknown, known)` | Suggestion with confidence level | Yes (difflib) |
| `check_common_mistake(name)` | Known stdlib mistake patterns | Yes (dict lookup) |
| `find_module_suggestion(module)` | Closest stdlib module name | Yes (difflib) |
| `find_function_suggestion(func)` | Closest stdlib function name | Yes (difflib) |

### Common Mistake Patterns (48 patterns)

| Wrong | Correct | Confidence |
|-------|---------|------------|
| `string.len` | `string.length` | HIGH |
| `json.load` | `json.parse` | HIGH |
| `print` | `io.println` | HIGH |
| `str` | `convert.to_string` | HIGH |
| `int` | `convert.to_int` | HIGH |
| `len` | `string.length / list.len / array.len` | HIGH |

### No AI Models

All suggestion matching uses `difflib.get_close_matches()` with deterministic cutoff thresholds.