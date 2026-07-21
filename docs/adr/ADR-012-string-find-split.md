# ADR-003: String Find and Split as Standard Library Functions

## Status
Accepted (pending merge review)

## Context
During static analyzer optimization (see `docs/archive/benchmarks/APPLICATION_VALIDATION.md`), three new runtime builtins were added to `compiler/runtime/builtins.py`:

- `string_find(s, needle, start)` — substring search returning position index
- `string_split(s, delim)` — string splitting into list
- `system_exit(code)` — process termination with exit code

`system_exit` was pre-existing (in HEAD). `string_find` and `string_split` are new.

Audit question: Are `string.find`, `string.find_from`, and `string.split` genuinely valuable additions to AILang, or were they merely implementation conveniences for the static analyzer benchmark?

## Evidence

### Usage in the static analyzer
Two thin wrappers in `apps/static_analyzer/main.ail`:

```
fn find_substring(text, pat, start_pos) { return string.find_from(text, pat, start_pos) }
fn split_string(text, delim)         { return string.split(text, delim) }
```

These are convenience wrappers that could be inlined.

### Usage across the entire app ecosystem
- **`string.find` / `string.find_from`**: Used by 1 app (static_analyzer) via the wrapper. *But 7 other apps independently implement their own `find_substring` as character-by-character AILang recursion*: hotel_management, inventory_mgmt, kanban, mini_sql, markdown_parser, http_request_parser, hangman_game, wordle_game.

- **`string.split`**: Used by 1 app (static_analyzer) via the wrapper. *But 5 other apps independently implement their own `split_string` as character-by-character AILang recursion*: hotel_management, inventory_mgmt, kanban, mini_sql, http_request_parser.

- **19 of 27 apps** import the `string` module.

### Pre-existing stdlib pattern
`stdlib/string.ail` already wraps common Python string operations:

| Stdlib function | Underlying call |
|----------------|-----------------|
| `string.uppercase` | `value.upper()` |
| `string.contains` | `value.find(needle) != -1` |
| `string.substring` | `string_substring(value, start, end)` |
| `string.length` | `value.__len__()` |
| `string.starts_with` | `value.startswith(prefix)` |
| `string.ends_with` | `value.endswith(suffix)` |
| `string.trim` | `value.strip()` |
| `string.find` (new) | `string_find(value, needle, 0)` |
| `string.find_from` (new) | `string_find(value, needle, start_pos)` |
| `string.split` (new) | `string_split(value, delim)` |

Adding `find`, `find_from`, and `split` is consistent with this established design.

### ADR-008 compliance
ADR-008 requires ≥2 independent benchmarks to demonstrate need before adding to stdlib.

**Before the addition:** 8+ apps across multiple domains (hotel management, mini SQL, markdown parser, HTTP parser, game, kanban board, inventory management, static analyzer) independently reimplemented the same logic by hand. Each reimplementation is character-by-character AILang recursion — a documented performance trap (see Playbook §5, Common Pitfalls).

**Count of independent reimplementations:**
- `find_substring`: 8 apps (7 old + 1 that would benefit)
- `split_string`: 6 apps (5 old + 1 that would benefit)

This satisfies the ≥2 benchmark threshold multiple times over.

## Decision
Keep `string.find`, `string.find_from`, and `string.split` as standard library additions. They fill a documented gap in the string API.

Remove `string_find` and `string_split` from the runtime is not an option: the character-by-character AILang fallback performs at 22,727× overhead vs the Python builtin, which was the root cause of the static analyzer's failure to complete.

## Alternatives considered

### Alternative 1: Do not add, rely on Python member access
The runtime already supports `value.find(needle, start)` via Python member access (`hasattr(receiver, member)` → `getattr`). This works but:
- Not discoverable — no stdlib documentation
- Inconsistent — every other string operation has a named wrapper
- No AILang-level type checking or error handling
- Already partially defeated: 8 apps wrote their own character-by-character fallback despite the mechanism existing

### Alternative 2: Add to stdlib only, not as runtime builtin
`string.find` and `string.split` could be AILang-level functions that call `value.find()` via member access. This would work but:
- The member access path has additional runtime overhead (attribute lookup, method binding)
- Performance impact on the hot path (thousands of calls during static analysis)
- Undermines the purpose: the apps that need this need it *because* character-by-character AILang is too slow

### Alternative 3: Add to stdlib as thin wrappers over runtime builtins (chosen)
This is the approach taken:
- Runtime builtins (`string_find`, `string_split`) provide the fast implementation
- Stdlib wrappers (`string.find`, `string.find_from`, `string.split`) provide the idiomatic AILang API
- Consistent with existing pattern (`string.substring` → `string_substring`)

## Consequences
- 8+ existing apps could replace their character-by-character `find_substring`/`split_string` with `string.find_from`/`string.split`, eliminating a known performance trap
- The `stdlib/string.ail` API is now more complete (find, split, contains, substring, etc.)
- Documentation must be updated: STDLIB_REFERENCE.md to list the new functions, LANGUAGE_SPEC.md if any behavioral notes apply
- No backward compatibility concern: no existing code uses these functions (they didn't exist before)
- The static analyzer can remove its own `find_substring` and `split_string` wrappers in a follow-up cleanup, replacing with direct calls to `string.find_from` and `string.split`
