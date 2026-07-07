# Standard Library Gap Analysis

**Date:** 2026-07-05  
**Applications Reviewed:** 21  
**Threshold:** Functions appearing in 3+ independent applications  

---

## Executive Summary

After analyzing all 21 applications, several common patterns emerged that could benefit from standardized stdlib functions. The most significant gaps are in list iteration and aggregation utilities, which currently require verbose recursive helper patterns.

---

## Duplicate Helper Functions

### 1. Display/Iterate Pattern (7 applications)

**Pattern:** Iterating over a list and displaying each item

```ail
fn display_*_helper(items, i) {
    if (i >= list.len(items)) { return false }
    let item = list.get(items, i);
    print(...);
    display_*_helper(items, i + 1)
}
```

**Applications:**
- banking_ledger (display_account_helper)
- contact_book (display_contacts_helper)
- inventory (display_inventory_helper)
- random_data_generator (display_helper)
- todo_manager (display_helper)
- invoice_generator (print_lines_helper)
- csv_analyzer (display_rows_helper)

**Recommendation:** Add `list.iter(items, func)` or `list.foreach(items, func)`

---

### 2. Sum/Reduce Pattern (3 applications)

**Pattern:** Summing numeric values across a list

```ail
fn sum_*_helper(items, i) {
    if (i >= list.len(items)) { return 0 }
    return list.get(items, i) + sum_*_helper(items, i + 1)
}
```

**Applications:**
- csv_analyzer (sum_scores_helper)
- employee_management (process_payroll_helper - sum-like)
- student_management (sum_scores_helper)

**Recommendation:** Add `list.sum(items)` for numeric lists

---

### 3. Find-By-Property Pattern (3 applications)

**Pattern:** Finding an item by matching a property value

```ail
fn find_*_helper(items, key, i) {
    if (i >= list.len(items)) { return false }
    let item = list.get(items, i);
    if (map.get(item, "property") == key) { return item }
    return find_*_helper(items, key, i + 1)
}
```

**Applications:**
- contact_book (find_by_name_helper)
- banking_ledger (find by index pattern)
- student_management (find_best_name Helper)

**Recommendation:** Add `list.find(items, property, value)` or `list.find_by(items, func)`

---

## Repeated Algorithms

### 4. Map-as-Record Pattern (12 applications)

**Pattern:** Using maps as data structures with consistent property access

```ail
let item = map.new();
map.set(item, "name", name);
map.set(item, "value", value);
list.append(items, item);
```

**Applications:** All data management, business logic, and productivity apps

**Recommendation:** This is idiomatic; no change needed. But could add `map.new_with(props)` helper.

---

### 5. Recursive Index-Based Iteration (15+ applications)

**Pattern:** Manual index-based iteration due to no loop constructs

```ail
fn *_helper(items, i, ...) {
    if (i >= list.len(items)) { return ... }
    let item = list.get(items, i);
    ...
    return *_helper(items, i + 1, ...)
}
```

**Applications:** 15+ including banking_ledger, contact_book, csv_analyzer, employee_management, etc.

**Recommendation:** This is fundamental to the language design (no loops). Document as standard pattern.

---

## Repeated Parsing Logic

### 6. Number Base Conversion (1 application)

**Pattern:** Converting numbers to different bases using division and modulo

**Applications:** number_base

**Recommendation:** Currently only 1 application. Not meeting threshold. Add `math.base(n, radix)` could be future enhancement.

---

## Repeated String Manipulation

### 7. Case-Insensitive Search (1 application)

**Pattern:** Converting to lowercase before searching

```ail
fn contains_ignore_case(text, pattern) {
    return string.contains(string.lowercase(text), string.lowercase(pattern))
}
```

**Applications:** text_search

**Recommendation:** Currently only 1 application. Could add `string.icontains(text, pattern)`.

---

### 8. String Concatenation for Building Output (6 applications)

**Pattern:** Building strings via concatenation in loops

**Applications:** password_generator, number_base, invoice_generator

**Recommendation:** Currently works but could add `string.join(list)` in future.

---

## Repeated File Utilities

### 9. File Existence Check Pattern (5 applications)

**Pattern:** Check existence before operation

```ail
if (!file.exists(path)) {
    print("File not found");
    return false
}
let content = file.read(path);
```

**Applications:** config_reader, file_copy, file_search, json_formatter, log_analyzer

**Recommendation:** Currently only 5 but spread across different error handling. Could add a helper that returns error value or use option types.

---

## Recommended New Stdlib APIs

### Meeting Threshold (3+ occurrences):

| Function | Module | Description | Frequency |
|----------|--------|-------------|-----------|
| `list.iter(items, func)` | list | Iterate over list applying function | 7 |
| `list.sum(items)` | list | Sum all numeric values in list | 3 |
| `list.find(items, property, value)` | list | Find first item where property equals value | 3 |

### Below Threshold but Noted:

| Function | Module | Description | Frequency |
|----------|--------|-------------|-----------|
| `map.new_with(name, age, ...)` | map | Create map with initial properties | 1 |
| `string.icontains(text, pattern)` | string | Case-insensitive substring search | 1 |
| `string.join(separator, items)` | string | Join list of strings | 1 |
| `math.base(n, radix)` | math | Convert number to different base string | 1 |

---

## Implementation Recommendations

### list.iter (High Priority)
```ail
fn display_all(items) {
    list.iter(items, fn(item) {
        print(map.get(item, "name"));
    });
}
```

### list.sum (Medium Priority)
```ail
fn total(items) {
    return list.sum(items);
}
```

### list.find (Medium Priority)
```ail
fn find_contact(contacts, name) {
    return list.find(contacts, "name", name);
}
```

---

## Current Stdlib Coverage Assessment

| Module | Completeness | Notes |
|--------|--------------|-------|
| string | ✅ Complete | All spec functions implemented |
| math | ✅ Complete | All spec functions implemented |
| list | ✅ Complete | All spec functions implemented |
| array | ✅ Complete | Alias for list |
| map | ✅ Complete | All spec functions implemented |
| set | ✅ Complete | All spec functions implemented |
| file | ✅ Complete | All spec functions implemented |
| path | ✅ Complete | All spec functions implemented |
| json | ✅ Complete | All spec functions implemented |
| csv | ✅ Complete | All spec functions implemented |
| time | ✅ Complete | All spec functions implemented |
| random | ✅ Complete | All spec functions implemented |
| environment | ✅ Complete | All spec functions implemented |
| convert | ✅ Complete | Extra `to_number` added |
| io | ⚠️ Redundant | Wraps print unnecessarily |
| system | ⚠️ Incomplete | `exit` doesn't actually exit |

---

## Priority Actions

1. **Immediate:** Fix `system.exit()` to actually terminate the process
2. **Near-term:** Consider `list.iter`, `list.sum`, `list.find` for v0.2.0
3. **Future:** Evaluate `string.icontains`, `string.join` for convenience