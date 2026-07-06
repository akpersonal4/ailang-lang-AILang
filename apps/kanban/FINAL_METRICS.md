# Final Metrics — Kanban App

## Code Metrics

| Metric | Value |
|--------|-------|
| Total lines | 1012 |
| Non-blank lines | 894 |
| Function count | 102 |
| Characters | ~28,000 |
| Levels of abstraction | 6 (0-5) |

## Build Performance

| Metric | Value |
|--------|-------|
| Compile attempts | 2 |
| Compile time (pass) | 1.0s |
| Runtime | 0.73s |

## Error Metrics

| Type | Count | Root Cause |
|------|-------|------------|
| Build errors | 7 | All forward references |
| Runtime errors | 0 | — |
| Logic errors | 0 | — |

## Function Breakdown by Level

| Level | Count | Description |
|:-----:|:-----:|-------------|
| 0 | 15 | String/list/map utilities, ID generation |
| 1 | 4 | Filter, count, search |
| 2 | 19 | Task + Column constructors and operations |
| 3 | 35 | Board operations, display, reporting |
| 4 | 6 | JSON persistence (save/load) |
| 5 | 23 | Demo data, `main` orchestration |
| **Total** | **102** | |

## Code Quality

| Pattern | Count |
|---------|-------|
| Recursive calls | ~80 |
| `map.has` guards | 10+ |
| `list.len` checks | 5+ |
| Self-terminating recursion | All |
| Tail position returns | Most |

## Risk Mitigation

| Risk | Mitigated? | How |
|------|-----------|-----|
| Forward references | Yes | Reordered functions bottom-up |
| Map key mismatches | Yes | Consistent key naming (`id`, `title`, `priority`, etc.) |
| Variable collision | Yes | Unique prefix per function (`_cdb`, `_dem`, etc.) |
| Empty list access | Yes | `list.len` guarded before `list.get` |
| Missing map keys | Yes | `map.has` before `map.get` everywhere |
| `string.concat` over 2 args | Yes | Used `+` for 3+ strings |
