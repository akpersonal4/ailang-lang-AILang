# M65A Recursion Audit — Recursive Pattern Analysis

**Date:** 2026-07-14
**Status:** COMPLETE
**Parent:** M64 AI-First Development Process Integration

---

## 1. Executive Summary

**175 recursive helpers across 3 benchmark applications consume 2,050 LOC.** The dominant friction source is filter-by-field (52 instances), followed by traversal/print (25 instances) and sum/aggregation (23 instances). Stdlib expansion can eliminate ~46% of recursive helpers and ~41% of LOC without language changes.

| Metric | Inventory | Ticket | Workflow | Total |
|--------|:---------:|:------:|:--------:|:-----:|
| Recursive helpers | 128 | 26 | 21 | **175** |
| LOC inside helpers | 1,471 | 317 | 262 | **2,050** |
| Files with helpers | 47 | 7 | 7 | **61** |
| Avg LOC per helper | 11.5 | 12.2 | 12.5 | **11.7** |

---

## 2. Pattern Distribution

| Pattern | Inventory | Ticket | Workflow | Total | % of Total |
|---------|:---------:|:------:|:--------:|:-----:|:----------:|
| Filter-by-field | 41 | 6 | 5 | **52** | 29.7% |
| Traversal/Print | 14 | 6 | 5 | **25** | 14.3% |
| Sum/Aggregation | 17 | 4 | 2 | **23** | 13.1% |
| Stateful iteration | 14 | 4 | 2 | **20** | 11.4% |
| Find-first | 7 | 2 | 4 | **13** | 7.4% |
| Group-by-key | 7 | 3 | 1 | **11** | 6.3% |
| Search | 6 | 1 | 0 | **7** | 4.0% |
| Exists/Contains | 3 | 1 | 2 | **6** | 3.4% |
| Slice/Take | 6 | 0 | 0 | **6** | 3.4% |
| Map/Transform | 3 | 1 | 0 | **4** | 2.3% |
| Selection Sort | 5 | 0 | 0 | **5** | 2.9% |
| Other | 5 | 2 | 0 | **7** | 4.0% |

---

## 3. Duplicate Pattern Analysis

### 3.1 Filter-by-Field (52 instances)

The single most duplicated pattern. Nearly identical logic: iterate list, compare a map field to a value, append matches to accumulator.

**Representative example:**
```ail
fn user_filter_active_rec(items, idx, acc) {
    if (idx == list.len(items)) { return acc; }
    let item = list.get(items, idx);
    if (map.get(item, "status") == "active") {
        let new_acc = list.append(acc, item);
        return user_filter_active_rec(items, math.add(idx, 1), new_acc);
    }
    return user_filter_active_rec(items, math.add(idx, 1), acc);
}
```

**Duplicate files:** 28 files across Inventory, 3 files across Ticket, 4 files across Workflow

### 3.2 Traversal/Print (25 instances)

Structurally identical: iterate list, print each element, return true.

**Representative example:**
```ail
fn cv_print_comments_rec(items, idx) {
    if (idx == list.len(items)) { return true; }
    let item = list.get(items, idx);
    print("[" + map.get(item, "author_id") + "] " + map.get(item, "content"));
    return cv_print_comments_rec(items, math.add(idx, 1));
}
```

**Duplicate files:** 7 files across Inventory, 1 file across Ticket, 1 file across Workflow

### 3.3 Sum/Aggregation (23 instances)

Iterate list, accumulate a numeric value, return the sum.

**Representative example:**
```ail
fn invoice_calculate_total_rec(items, idx, acc) {
    if (idx == list.len(items)) { return acc; }
    let item = list.get(items, idx);
    let new_acc = math.add(acc, convert.to_int(map.get(item, "line_total")));
    return invoice_calculate_total_rec(items, math.add(idx, 1), new_acc);
}
```

**Duplicate files:** 13 files across Inventory, 2 files across Ticket, 1 file across Workflow

### 3.4 Find-first (13 instances)

Linear scan returning first item where field matches, or return false.

**Representative example:**
```ail
fn storage_find_first_rec(items, key, value, idx) {
    if (idx == list.len(items)) { return false; }
    let item = list.get(items, idx);
    if (map.get(item, key) == value) { return item; }
    return storage_find_first_rec(items, key, value, math.add(idx, 1));
}
```

**Duplicate files:** 7 files across Inventory, 2 files across Ticket, 4 files across Workflow

### 3.5 Group-by-key (11 instances)

Iterate list, accumulate items into a map grouped by a key field.

**Representative example:**
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

**Duplicate files:** 4 files across Inventory, 1 file across Ticket, 1 file across Workflow

### 3.6 Search (7 instances)

Case-insensitive substring match on name field.

**Representative example:**
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

**Duplicate files:** 6 files across Inventory, 1 file across Ticket

---

## 4. Existing Stdlib Coverage

| Pattern | Existing Primitive | Coverage |
|---------|-------------------|:--------:|
| Filter-by-field | `list.filter_by_key(key, value)` | ✅ 100% |
| Find-first | `list.find_by_key(key, value)` | ✅ 100% |
| Exists/Contains | `list.contains(value)` | ⚠ Partial |
| Sum | `list.sum()` | ⚠ Partial |
| Sort | `list.sort_by_key(key)` | ✅ 100% |
| Collect key | `list.collect_key(key)` | ✅ 100% |
| Filter by contains | `list.filter_by_contains(key, substring)` | ✅ 100% |

### Missing Primitives

| Pattern | Missing Primitive | Instances | Est. LOC Reduction |
|---------|-------------------|:---------:|:-------------------:|
| Group-by-key | `list.group_by_key(key)` | 11 | ~150 |
| Sum filtered | `list.sum_by_key(key)` | 17 | ~200 |
| Take/Skip | `list.take(n)`, `list.skip(n)` | 6 | ~70 |
| Search | `list.search_by_name(query)` | 7 | ~100 |
| Exists by key | `list.exists_by_key(key, value)` | 6 | ~70 |
| Map values | `map.values()` | 4 | ~50 |
| Unique | `list.unique()` | 3 | ~35 |
| First or default | `list.first_or_default(default)` | 3 | ~35 |

---

## 5. LOC Distribution by Pattern

| Pattern | Count | Total LOC | Avg LOC |
|---------|:-----:|:---------:|:-------:|
| Filter-by-field | 52 | 624 | 12.0 |
| Traversal/Print | 25 | 215 | 8.6 |
| Sum/Aggregation | 23 | 283 | 12.3 |
| Stateful iteration | 20 | 321 | 16.1 |
| Find-first | 13 | 156 | 12.0 |
| Group-by-key | 11 | 154 | 14.0 |
| Search | 7 | 109 | 15.6 |
| Exists/Contains | 6 | 71 | 11.8 |
| Slice/Take | 6 | 68 | 11.3 |
| Map/Transform | 4 | 49 | 12.3 |
| Selection Sort | 5 | 57 | 11.4 |
| Other | 7 | 93 | 13.3 |

---

## 6. Key Observations

1. **Filter-by-field accounts for 30% of all recursive helpers.** A single generic `list.filter_by_key` could replace ~52 functions.

2. **The search pattern is duplicated 7 times** across Inventory and Ticket. A generic `list.search_by_name` could replace 5 of these.

3. **Two independent selection sort implementations** exist in `dashboard.ail` and `report_trends.ail` with identical structure.

4. **`helpers_list_contains_rec` and `auth_list_contains_rec` are exact functional duplicates** — both check if a value exists in a flat list.

5. **The sum/aggregation pattern appears 23 times**. Most differ only in which field is summed. A generic `list.sum_by_key` could reduce this significantly.

6. **47 of 55 non-test .ail files (85%)** in Inventory contain at least one recursive helper, meaning recursion is pervasive across the entire application.

7. **All 175 recursive helpers use the same boilerplate**: `list.len` for base case, `list.get` for element access, `math.add(index, 1)` for advancement. This is the direct cost of recursion-only iteration.

---

## 7. Related Documents

- [M62 AI Correction Analysis](M62_AI_CORRECTION_ANALYSIS.md) — Root cause analysis
- [M62 Root Cause Table](M62_ROOT_CAUSE_TABLE.md) — Every cycle classified
- [M63 AIL Check Report](M63_AIL_CHECK_REPORT.md) — Pre-flight ordering check
- [M63 Replay Results](M63_REPLAY_RESULTS.md) — M59 replay data
