# M65A Stdlib Gap Analysis — Missing Collection Primitives

**Date:** 2026-07-14
**Status:** COMPLETE
**Parent:** M65A Recursion Audit

---

## 1. Executive Summary

**7 new stdlib primitives could eliminate ~46% of recursive helpers and ~41% of LOC.** The largest gains come from `list.group_by_key` (11 instances, ~150 LOC) and `list.sum_by_key` (17 instances, ~200 LOC). All proposals pass governance Q1-Q3.

| Proposed Primitive | Instances | Est. LOC Reduction | Governance |
|-------------------|:---------:|:-------------------:|:----------:|
| `list.group_by_key(key)` | 11 | ~150 | ✅ Approved |
| `list.sum_by_key(key)` | 17 | ~200 | ✅ Approved |
| `list.take(n)` | 3 | ~35 | ✅ Approved |
| `list.skip(n)` | 3 | ~35 | ✅ Approved |
| `list.search_by_name(query)` | 5 | ~75 | ✅ Approved |
| `list.exists_by_key(key, value)` | 6 | ~70 | ✅ Approved |
| `map.values()` | 4 | ~50 | ✅ Approved |

**Total estimated impact:** 49 instances, ~615 LOC reduction

---

## 2. Existing Stdlib Inventory

### 2.1 list.* (18 functions)

| Function | Parameters | Description | Status |
|----------|-----------|-------------|:------:|
| `list.new()` | — | Create empty list | ✅ |
| `list.append(values, value)` | list, any | Append value | ✅ |
| `list.len(values)` | list | Get length | ✅ |
| `list.get(values, index)` | list, int | Get element | ✅ |
| `list.contains(values, value)` | list, any | Check membership | ✅ |
| `list.remove(values, value)` | list, any | Remove first occurrence | ✅ |
| `list.clear(values)` | list | Clear all elements | ✅ |
| `list.sum(values)` | list | Sum all elements | ✅ |
| `list.sort(values)` | list | Sort ascending | ✅ |
| `list.sort_by_key(values, key)` | list, string | Sort by dict key | ✅ |
| `list.copy(values)` | list | Shallow copy | ✅ |
| `list.find(values, key, value)` | list, string, any | Find first by key | ✅ |
| `list.find_by_key(values, key, value)` | list, string, any | Alias for find | ✅ |
| `list.filter(values, key, value)` | list, string, any | Filter by key | ✅ |
| `list.filter_by_key(values, key, value)` | list, string, any | Alias for filter | ✅ |
| `list.filter_by_contains(values, key, substring)` | list, string, string | Filter by substring | ✅ |
| `list.collect_key(values, key)` | list, string | Collect key values | ✅ |

### 2.2 map.* (9 functions)

| Function | Parameters | Description | Status |
|----------|-----------|-------------|:------:|
| `map.new()` | — | Create empty dict | ✅ |
| `map.set(values, key, value)` | dict, any, any | Set key-value | ✅ |
| `map.get(values, key)` | dict, any | Get value | ✅ |
| `map.has(values, key)` | dict, any | Check key exists | ✅ |
| `map.delete(values, key)` | dict, any | Delete key | ✅ |
| `map.keys(values)` | dict | Get all keys | ✅ |
| `map.clear(values)` | dict | Clear all pairs | ✅ |
| `map.get_or_default(values, key, default)` | dict, any, any | Get with default | ✅ |
| `map.safe_get(values, key, default)` | dict, any, any | Alias for get_or_default | ✅ |

---

## 3. Missing Primitives — Governance Analysis

### 3.1 `list.group_by_key(key)`

**Purpose:** Group list items by a key field, returning a map of key → list of items.

**Governance Q1-Q3:**

| Question | Answer |
|----------|--------|
| Q1: Supports mission objective? | ✅ Yes — reduces recursive boilerplate for grouping patterns |
| Q2: Solves measured pain point? | ✅ Yes — 11 instances across 6 files, ~150 LOC |
| Q3: Can existing tooling solve it? | ❌ No — no existing primitive handles grouping |

**Instances eliminated:** 11
**Estimated LOC reduction:** ~150
**Estimated BRE:** 8.5×

**Example before:**
```ail
fn trend_group_sales_rec(items, idx, acc) {
    if (idx == list.len(items)) { return acc; }
    let item = list.get(items, idx);
    let key = map.get(item, "product_id");
    if (map.has(acc, key)) {
        let current = convert.to_int(map.get(map.get(acc, key), "quantity"));
        let new_qty = math.add(current, convert.to_int(map.get(item, "quantity")));
        let updated = map.set(map.get(acc, key), "quantity", convert.to_string(new_qty));
        let new_acc = map.set(acc, key, updated);
        return trend_group_sales_rec(items, math.add(idx, 1), new_acc);
    }
    let new_entry = map.set(map.new(), "quantity", map.get(item, "quantity"));
    let new_acc = map.set(acc, key, new_entry);
    return trend_group_sales_rec(items, math.add(idx, 1), new_acc);
}
```

**Example after:**
```ail
let grouped = list.group_by_key(items, "product_id");
```

---

### 3.2 `list.sum_by_key(key)`

**Purpose:** Sum numeric values of a key field across all list items.

**Governance Q1-Q3:**

| Question | Answer |
|----------|--------|
| Q1: Supports mission objective? | ✅ Yes — reduces recursive boilerplate for aggregation patterns |
| Q2: Solves measured pain point? | ✅ Yes — 17 instances across 13 files, ~200 LOC |
| Q3: Can existing tooling solve it? | ❌ No — `list.sum()` only works on flat number lists, not dict values |

**Instances eliminated:** 17
**Estimated LOC reduction:** ~200
**Estimated BRE:** 10×

**Example before:**
```ail
fn invoice_calculate_total_rec(items, idx, acc) {
    if (idx == list.len(items)) { return acc; }
    let item = list.get(items, idx);
    let new_acc = math.add(acc, convert.to_int(map.get(item, "line_total")));
    return invoice_calculate_total_rec(items, math.add(idx, 1), new_acc);
}
```

**Example after:**
```ail
let total = list.sum_by_key(items, "line_total");
```

---

### 3.3 `list.take(n)` and `list.skip(n)`

**Purpose:** Take first N items or skip first N items from a list.

**Governance Q1-Q3:**

| Question | Answer |
|----------|--------|
| Q1: Supports mission objective? | ✅ Yes — reduces recursive boilerplate for slice patterns |
| Q2: Solves measured pain point? | ✅ Yes — 6 instances across 4 files, ~70 LOC |
| Q3: Can existing tooling solve it? | ⚠ Partially — `pagination.slice` exists but is app-specific |

**Instances eliminated:** 6
**Estimated LOC reduction:** ~70
**Estimated BRE:** 7×

**Example before:**
```ail
fn dashboard_take_rec(items, n, idx, acc) {
    if (idx == n) { return acc; }
    if (idx == list.len(items)) { return acc; }
    let new_acc = list.append(acc, list.get(items, idx));
    return dashboard_take_rec(items, n, math.add(idx, 1), new_acc);
}
```

**Example after:**
```ail
let first_five = list.take(items, 5);
let rest = list.skip(items, 5);
```

---

### 3.4 `list.search_by_name(query)`

**Purpose:** Search list items by case-insensitive substring match on name field.

**Governance Q1-Q3:**

| Question | Answer |
|----------|--------|
| Q1: Supports mission objective? | ✅ Yes — reduces recursive boilerplate for search patterns |
| Q2: Solves measured pain point? | ✅ Yes — 5 instances across 5 files, ~75 LOC |
| Q3: Can existing tooling solve it? | ⚠ Partially — `list.filter_by_contains` exists but requires explicit key |

**Instances eliminated:** 5
**Estimated LOC reduction:** ~75
**Estimated BRE:** 7.5×

**Example before:**
```ail
fn customer_search_rec(items, query, idx, acc) {
    if (idx == list.len(items)) { return acc; }
    let item = list.get(items, idx);
    let name = string.lowercase(map.get(item, "name"));
    if (string.contains(name, string.lowercase(query))) {
        let new_acc = list.append(acc, item);
        return customer_search_rec(items, query, math.add(idx, 1), new_acc);
    }
    return customer_search_rec(items, query, math.add(idx, 1), acc);
}
```

**Example after:**
```ail
let results = list.search_by_name(items, "query");
```

---

### 3.5 `list.exists_by_key(key, value)`

**Purpose:** Check if any item in the list has a matching key value (short-circuit on first match).

**Governance Q1-Q3:**

| Question | Answer |
|----------|--------|
| Q1: Supports mission objective? | ✅ Yes — reduces recursive boilerplate for exists patterns |
| Q2: Solves measured pain point? | ✅ Yes — 6 instances across 5 files, ~70 LOC |
| Q3: Can existing tooling solve it? | ⚠ Partially — `list.find_by_key` returns the item but doesn't short-circuit |

**Instances eliminated:** 6
**Estimated LOC reduction:** ~70
**Estimated BRE:** 7×

**Example before:**
```ail
fn permission_check_rec(actions, target, idx) {
    if (idx == list.len(actions)) { return false; }
    if (list.get(actions, idx) == target) { return true; }
    return permission_check_rec(actions, target, math.add(idx, 1));
}
```

**Example after:**
```ail
let has_permission = list.exists_by_key(permissions, "action", "read");
```

---

### 3.6 `map.values()`

**Purpose:** Return a list of all values in a map.

**Governance Q1-Q3:**

| Question | Answer |
|----------|--------|
| Q1: Supports mission objective? | ✅ Yes — reduces recursive boilerplate for map-to-list patterns |
| Q2: Solves measured pain point? | ✅ Yes — 4 instances across 2 files, ~50 LOC |
| Q3: Can existing tooling solve it? | ❌ No — no existing primitive returns map values |

**Instances eliminated:** 4
**Estimated LOC reduction:** ~50
**Estimated BRE:** 6×

**Example before:**
```ail
fn trend_map_to_list_rec(keys, map_data, idx, acc) {
    if (idx == list.len(keys)) { return acc; }
    let key = list.get(keys, idx);
    let value = map.get(map_data, key);
    let new_acc = list.append(acc, value);
    return trend_map_to_list_rec(keys, map_data, math.add(idx, 1), new_acc);
}
```

**Example after:**
```ail
let values = map.values(grouped);
```

---

## 4. Implementation Effort

| Primitive | Native Builtin | AILang Wrapper | Test Cases | Total Effort |
|-----------|:--------------:|:--------------:|:----------:|:------------:|
| `list.group_by_key` | ~50 LOC | ~20 LOC | ~10 | ~80 LOC |
| `list.sum_by_key` | ~30 LOC | ~15 LOC | ~8 | ~53 LOC |
| `list.take` | ~25 LOC | ~10 LOC | ~6 | ~41 LOC |
| `list.skip` | ~25 LOC | ~10 LOC | ~6 | ~41 LOC |
| `list.search_by_name` | ~40 LOC | ~15 LOC | ~8 | ~63 LOC |
| `list.exists_by_key` | ~30 LOC | ~10 LOC | ~6 | ~46 LOC |
| `map.values` | ~20 LOC | ~10 LOC | ~5 | ~35 LOC |

**Total implementation effort:** ~359 LOC
**Total LOC reduction:** ~615 LOC
**Net benefit:** +256 LOC (implementation is smaller than removal)

---

## 5. Recommended Implementation Order

| Priority | Primitive | Rationale |
|:--------:|-----------|-----------|
| 1 | `list.group_by_key` | Highest impact (150 LOC), 11 instances |
| 2 | `list.sum_by_key` | Highest impact (200 LOC), 17 instances |
| 3 | `list.exists_by_key` | High impact (70 LOC), 6 instances, short-circuit semantics |
| 4 | `list.take` + `list.skip` | Medium impact (70 LOC), 6 instances, simple implementation |
| 5 | `list.search_by_name` | Medium impact (75 LOC), 5 instances, case-insensitive |
| 6 | `map.values` | Medium impact (50 LOC), 4 instances, simple implementation |

---

## 6. Related Documents

- [M65A Recursion Audit](M65A_RECURSION_AUDIT.md) — Pattern analysis
- [M62 AI Correction Analysis](M62_AI_CORRECTION_ANALYSIS.md) — Root cause analysis
- [M62 Root Cause Table](M62_ROOT_CAUSE_TABLE.md) — Every cycle classified
