# Playbook Validation — Kanban App

## Rules Enforced

| Rule | Status | Evidence |
|------|--------|----------|
| No loops (recursion only) | PASS | All iteration via recursive functions (`_iter` suffix) |
| No nested functions | PASS | All 102 `fn` at top level |
| No forward references | PASS | Build passes after reorder |
| Bottom-up ordering | PASS | Level 0 → 5 with physical sort |
| `let` with initializer | PASS | Every `let x = val` |
| `return` with value | PASS | Every `return expr` |
| `import` at top level only | PASS | N/A (single file) |
| Unique variable names | PASS | Variables named by function prefix |
| `map.has` before `map.get` | PASS | Checked in all 10+ map access sites |
| `list.len` before `list.get` | PASS | Checked in all sites |
| `string.concat` ≤2 args | PASS | 3+ strings use `+` operator |
| `&&` safe usage | PASS | N/A (eager `&&` not used where right side depends on left) |

## Stdlib Audit

| API | Used | Notes |
|-----|------|-------|
| `map.new` | Yes | |
| `map.set` | Yes | |
| `map.get` | Yes | Guarded by `map.has` |
| `map.has` | Yes | |
| `map.keys` | Yes | |
| `list.new` | Yes | |
| `list.append` | Yes | |
| `list.len` | Yes | |
| `list.get` | Yes | Guarded |
| `string.concat` | Yes | Only 2-arg form |
| `convert.to_string` | Yes | |
| `print` | Yes | |
| `json.stringify` | Yes | |
| `json.parse` | Yes | |
| `file.write` | Yes | |
| `file.read` | Yes | |
| `random.int` | Yes | In `new_id` |

**Custom implementations (not in stdlib):**
- `find_substring`, `find_delim`, `split_string` — manual split
- `join_strings` — manual join for list of strings
- `filter_matching`, `count_matching` — generic filter/count
- `list_copy` — `list.copy` does not exist
- `is_empty` — generic emptiness check
- `string_in_list_pos/string_in_list_flag` — linear search in list
- `merge_lists` — append source to target

## New Documentation Needs (≥2 apps → Playbook update)

| Finding | Apps | Update Playbook? |
|---------|------|-----------------|
| `list.copy` does not exist | Kanban + prior | YES — add to Pitfalls |
| 100+ functions in one file is max practical | Kanban | YES — recommend multi-file planning |
| `convert.to_string` needed for printing ints | Kanban + prior | Already documented |
