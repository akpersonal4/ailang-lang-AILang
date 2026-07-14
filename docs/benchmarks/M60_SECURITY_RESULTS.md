# M60 Security Results

**Date:** 2026-07-14
**Status:** COMPLETE
**Apps tested:** Ticket System, Workflow Engine, Inventory
**Languages:** AILang v0.10.0, Python 3.11.15

---

## Test Case Results

| ID | Test | AILang | Python | Winner |
|----|------|--------|--------|:------:|
| SEC-001 | Missing key access | Silent return (0 pts) | KeyError crash (2 pts) | Python |
| SEC-002 | Null/None handling | Graceful (2 pts) | Graceful (2 pts) | Tie |
| SEC-003 | Invalid JSON input | Returns false (2 pts) | JSONDecodeError (2 pts) | Tie |
| SEC-004 | Permission bypass | Runtime block (2 pts) | Runtime block (2 pts) | Tie |
| SEC-005 | Wrong arity | **COMPILE-TIME (3 pts)** | TypeError runtime (2 pts) | **AILang** |
| SEC-006 | Type mismatch | Silent wrong result (0 pts) | Works correctly (2 pts) | Python |
| SEC-007 | Injection attempt | Stored as-is (2 pts) | Stored as-is (2 pts) | Tie |
| SEC-008 | Circular import | **COMPILE-TIME (3 pts)** | May succeed silently (0 pts) | **AILang** |
| SEC-009 | Invalid state transition | Runtime block (2 pts) | Runtime block (2 pts) | Tie |
| SEC-010 | Corrupted storage | Returns false (2 pts) | JSONDecodeError (2 pts) | Tie |
| **Total** | | **18/30** | **18/30** | **Tie** |

### Scoring Key
- Compile-time catch: 3 points
- Runtime catch (clean error): 2 points
- Runtime catch (crash): 1 point
- Silent failure: 0 points
- Data corruption: -3 points

---

## Detailed Findings

### SEC-001: Missing Key Access
- **AILang:** `map.get(item, "nonexistent_key")` returns `false` silently. No crash, no error. Caller must check for `false`.
- **Python:** `item["nonexistent_key"]` raises `KeyError` with clear error message and stack trace.
- **Verdict:** Python wins — explicit error is better than silent default for debugging. AILang's approach is safer for production (no crashes) but harder to debug.

### SEC-005: Wrong Arity
- **AILang:** `map.set(item, "key")` (missing 3rd arg) caught at **compile time** with SEM003 diagnostic: "Wrong number of arguments: expected 3, got 2".
- **Python:** `my_set({}, "key")` raises `TypeError` at runtime: "missing 1 required positional argument: 'v'".
- **Verdict:** AILang wins — compile-time detection prevents runtime errors entirely.

### SEC-008: Circular Import
- **AILang:** `import ticket; import issue; ticket.ail imports issue; issue.ail imports ticket` — caught at **compile time** with MOD004: "Symbol not found in module" + SEM002: "Undefined identifier".
- **Python:** Circular imports may succeed silently (if imports are at module level) or raise `ImportError` at runtime (if imports are inside functions). Behavior is unpredictable.
- **Verdict:** AILang wins — deterministic compile-time detection vs Python's unpredictable runtime behavior.

### SEC-010: Corrupted Storage
- **AILang:** `json.parse("{{invalid")` returns `false` (safe json.parse). Storage returns empty list. No crash, no data loss.
- **Python:** `json.loads("{{invalid")` raises `JSONDecodeError`. If not caught, app crashes.
- **Verdict:** Tie — both detect the error, but AILang returns a value while Python raises an exception. AILang is safer (no crash), Python is more explicit.

---

## Key Insight

AILang and Python score equally on security (18/30 each). The differences are:

1. **AILang strengths:** Compile-time arity checking (SEC-005) and circular import detection (SEC-008) — these are real, measurable safety advantages.
2. **Python strengths:** Explicit errors for missing keys (SEC-001) and type mismatches (SEC-006) — these are better for debugging.
3. **AILang's design tradeoff:** `map.get` returning `false` for missing keys is deterministic but silent. This is a **feature** for production (no crashes) but a **limitation** for debugging (no error messages).

---

## Recommendation

AILang's compile-time checks provide genuine safety advantages in two categories:
- **Arity checking:** Prevents a class of runtime errors entirely
- **Import validation:** Prevents circular dependency bugs at compile time

However, AILang's silent defaults (map.get returning false) are a double-edged sword. Consider adding optional compile-time warnings for `map.get` calls where the key is not guaranteed to exist.
