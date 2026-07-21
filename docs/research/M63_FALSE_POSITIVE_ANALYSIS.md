# M63 False Positive Analysis

**Date:** 2026-07-14
**Parent:** [M63 AIL Check Report](M63_AIL_CHECK_REPORT.md)

---

## 1. Test Methodology

### 1.1 Test Applications

| Application | Files | LOC | Description |
|-------------|:-----:|:---:|-------------|
| Ticket System | 7 | 1,371 | M59 Phase 1 benchmark |
| Workflow Engine | 8 | 1,262 | M59 Phase 3 benchmark |
| Inventory | 56 | 4,009 | Full production system |
| **Total** | **71** | **6,642** | — |

### 1.2 Test Procedure

1. Run `ail check` against each application
2. Collect all reported violations
3. Manually verify each violation against the source code
4. Classify as true positive or false positive
5. Calculate false positive rate

---

## 2. Results

### 2.1 Violation Summary

| Application | Files Checked | Violations Reported | True Positives | False Positives |
|-------------|:-------------:|:-------------------:|:--------------:|:---------------:|
| Ticket System | 7 | 0 | 0 | 0 |
| Workflow Engine | 8 | 0 | 0 | 0 |
| Inventory | 56 | 1 | 1 | 0 |
| **Total** | **71** | **1** | **1** | **0** |

### 2.2 False Positive Rate

| Metric | Value |
|--------|:-----:|
| Total violations reported | 1 |
| True positives | 1 |
| False positives | 0 |
| **False positive rate** | **0%** |
| Target | ≤ 5% |
| **Result** | ✅ **PASS** |

---

## 3. True Positive Analysis

### 3.1 Violation Details

```
MISSING_IMPORT:
C:\Users\aleckhan\Projects\AiLang_New\apps\inventory\main.ail:173

  main_reserve()
  calls stock_reservation.reservation_create()

  Suggestion:
    Add: import stock_reservation;
```

### 3.2 Verification

**Step 1: Does the import exist?**

```bash
$ grep "^import" apps/inventory/main.ail
import environment;
import list;
import convert;
import storage;
import helpers;
import product;
import category;
import customer;
import vendor;
import stock_movement;
import order_sales_order;
import order_purchase_order;
import export_csv_export;
import export_json_export;
import warehouse;
import dashboard;
import permission;
import stock_adjustment;
import workflow;
import backup;
```

**Result:** `import stock_reservation;` is **MISSING**.

**Step 2: Does the module file exist?**

```bash
$ ls apps/inventory/stock_reservation.ail
apps/inventory/stock_reservation.ail
```

**Result:** The file **EXISTS**.

**Step 3: Is the function called?**

```bash
$ grep -n "stock_reservation" apps/inventory/main.ail
173:    let mrReservation = stock_reservation.reservation_create("DEMO-ORDER", mrFirstId, 5);
```

**Result:** The function **IS CALLED**.

**Step 4: Would this fail at runtime?**

```bash
$ ail run apps/inventory/main.ail
Runtime error: Undefined identifier: stock_reservation
```

**Result:** Yes, it **WOULD FAIL** at runtime.

### 3.3 Conclusion

This is a **legitimate missing import** that would cause a runtime error. The `ail check` command correctly identified it.

---

## 4. Why No False Positives?

### 4.1 Design Decisions

| Decision | Rationale |
|----------|-----------|
| Only check local file functions | Avoid false positives from external modules |
| Skip stdlib functions | Known good, no need to check |
| Check module file existence | Verify the module actually exists before reporting |
| Require lowercase module names | Avoid false positives from class names |

### 4.2 Conservative Approach

The implementation takes a conservative approach:
- Only reports violations it's **certain** about
- Skips ambiguous cases (e.g., dynamic function calls)
- Verifies file existence before reporting missing imports

---

## 5. Runtime Performance

| Metric | Value |
|--------|:-----:|
| Total files checked | 71 |
| Total runtime | ~1.1 sec |
| Average per file | ~15 ms |
| Target | ≤ 500 ms per file |
| **Result** | ✅ **PASS** |

---

## 6. Conclusion

`ail check` achieves a **0% false positive rate** on the tested applications. The single violation found is a legitimate missing import that would cause a runtime error. The tool is production-ready for pre-flight checks.

---

## 7. Related Documents

- [M63 AIL Check Report](M63_AIL_CHECK_REPORT.md) — Full implementation report
- [M63 Replay Results](M63_REPLAY_RESULTS.md) — M59 benchmark replay
- [M62 AI Correction Analysis](../research/M62_AI_CORRECTION_ANALYSIS.md) — Root cause analysis
