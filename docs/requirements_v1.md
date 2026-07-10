# Inventory Management System — Frozen Requirements v1

## 1. Overview

A CLI-based inventory management system built in AILang, implementing full CRUD operations, stock tracking, order management, reporting, and business workflows. Total: 85 files, 8,521 LOC (47 app modules, 4,009 LOC + 38 test files, 4,512 LOC).

## 2. Language Constraints (AILang)

| Constraint | Rule |
|---|---|
| Loops | Recursion only; `while`/`for` do not exist |
| Function scope | All functions at top level; no nested functions |
| Forward references | Callee must be defined before caller; no forward references |
| File ordering | Functions in dependency order (Level 0 utilities → `main()`) |
| `let` | Must have initializer: `let x = value` |
| `return` | Must have value: `return expr` |
| `import` | Top level only; never inside function body |
| Variable names | Unique across all functions; no reuse of `i`, `x`, `result`, `acc` |
| `map.get` | Must guard with `map.has` first (use `helpers_get_map_value_safe`) |
| `list.get` | Must guard with `list.len` check first |
| `string.concat` | Exactly 2 args; use `+` for 3+ strings |
| `&&` (eager) | Both operands always execute; use nested `if` when right depends on left |

## 3. Module Catalog (47 modules, 4,009 LOC)

### Core Infrastructure
| Module | LOC | Lines | Description |
|---|---|---|---|
| `helpers.ail` | 178 | 178 | ID generation, timestamps, safe map access, list contains |
| `storage.ail` | 111 | 111 | JSON-file persistence with CRUD (add, get, update, delete, list, load, save) |
| `pagination.ail` | 88 | 88 | Offset/limit pagination helper |

### Product & Customer
| Module | LOC | Lines | Description |
|---|---|---|---|
| `category.ail` | 35 | 35 | Category CRUD |
| `product.ail` | 50 | 50 | Product CRUD + search by name |
| `customer.ail` | 32 | 32 | Customer CRUD |
| `vendor.ail` | 32 | 32 | Vendor CRUD |
| `supplier.ail` | 76 | 76 | Supplier CRUD + search + top-rated + payment terms filter |
| `warehouse.ail` | 47 | 47 | Warehouse CRUD + search by name/code |

### Inventory & Stock
| Module | LOC | Lines | Description |
|---|---|---|---|
| `stock_movement.ail` | 100 | 100 | Stock movement CRUD, QOH calculation, filter by type |
| `stock_valuation.ail` | 34 | 34 | Valuation set/get/list |
| `stock_transfer.ail` | 95 | 95 | Transfer CRUD + complete + cancel |
| `stock_aging.ail` | 75 | 75 | Aging batch tracking, summary, removal |
| `stock_adjustment.ail` | 117 | 117 | Adjustment CRUD, discrepancies, summary |
| `stock_reservation.ail` | 121 | 121 | Reservation CRUD, fulfill, cancel, availability check |

### Order Management
| Module | LOC | Lines | Description |
|---|---|---|---|
| `order_sales_order.ail` | 112 | 112 | Sales order CRUD + items + confirm |
| `order_purchase_order.ail` | 101 | 101 | Purchase order CRUD + items + receive + verify |
| `returns.ail` | 89 | 89 | Returns CRUD + approve + reject + complete |

### Financial
| Module | LOC | Lines | Description |
|---|---|---|---|
| `invoice.ail` | 53 | 53 | Invoice CRUD + total calculation + number generation |
| `payment.ail` | 72 | 72 | Payment CRUD + list by invoice + total + refund |
| `currency.ail` | 59 | 59 | Currency CRUD + convert + format |
| `tax.ail` | 57 | 57 | Tax CRUD + calculate + list by country |

### Logistics
| Module | LOC | Lines | Description |
|---|---|---|---|
| `shipping.ail` | 58 | 58 | Shipping CRUD + status update + filter by status |
| `batch.ail` | 107 | 107 | Batch CRUD + expiring before + active by product |
| `serial_number.ail` | 78 | 78 | Serial number CRUD + find by serial + list available |

### Business Logic
| Module | LOC | Lines | Description |
|---|---|---|---|
| `reorder.ail` | 96 | 96 | Reorder level management + check + lead time demand |
| `notification.ail` | 78 | 78 | Low stock / out of stock detection |
| `notification_reorder.ail` | 82 | 82 | Reorder notification check + clear + summary |
| `search.ail` | 28 | 28 | Aggregated search across products/customers/vendors |
| `permission.ail` | 90 | 90 | RBAC permission define + check + add/remove action + list roles |
| `workflow.ail` | 122 | 122 | Multi-step approval workflow (create, approve, reject, fulfill, close) |
| `price_history.ail` | 60 | 60 | Price history record + get by product + latest + list |
| `report.ail` | 148 | 148 | Stock report + sales report + profit report |
| `report_trends.ail` | 97 | 97 | Monthly sales trends + top products + category breakdown |
| `dashboard.ail` | 80 | 80 | Dashboard summary + low stock count + top products + recent movements |

### Audit
| Module | LOC | Lines | Description |
|---|---|---|---|
| `audit.ail` | 39 | 39 | Audit log creation + filter (recursive) |
| `audit_trail.ail` | 68 | 68 | Audit trail: list by date range, user, summary, recent |
| `audit_integration.ail` | 89 | 89 | Full audit report + entity summary + recent activity |

### Export & CLI
| Module | LOC | Lines | Description |
|---|---|---|---|
| `export_csv.ail` | 64 | 64 | CSV export for products, customers, vendors, orders |
| `export_json.ail` | 33 | 33 | JSON export for products, customers |
| `data_seed.ail` | 118 | 118 | Comprehensive seed data generator (11 seed functions) |
| `transfer_integration.ail` | 105 | 105 | Transfer with warehouse integration, list, summary |
| `payment_integration.ail` | 83 | 83 | Payment processing, balance, overdue list |

### Entry Point
| Module | LOC | Lines | Description |
|---|---|---|---|
| `main.ail` | 351 | 351 | CLI entry point with 15 commands (init, seed, add, list, search, stock, sell, buy, report, export, transfer, reserve, audit, trend, workflow) |

## 4. Data Storage

- JSON file-based persistence in `data/` directory
- Each collection is a JSON file: `data/{collection_name}.json`
- Storage functions: `storage_add`, `storage_list`, `storage_get_by_id`, `storage_update`, `storage_delete`
- Persistence: every write operation saves to disk immediately
- IDs: generated via `helpers_generate_id(prefix)` using timestamps

## 5. Test Suite (38 test files, 4,512 LOC)

| # | Test File | Subtests |
|---|-----------|----------|
| 1 | `test_audit_integration.ail` | 3 (full report, entity summary, recent activity) |
| 2 | `test_audit_trail.ail` | 5 (date range, user, summary by action, recent, empty) |
| 3 | `test_batch.ail` | 6 (create, missing, list by product, update qty, expiring, active) |
| 4 | `test_currency.ail` | 5 (convert, same currency, format, list, set/get rate) |
| 5 | `test_customer.ail` | 4 (create, missing, get by id, list) |
| 6 | `test_dashboard.ail` | 4 (summary, low stock, top products, recent movements) |
| 7 | `test_data_seed.ail` | 1 (seed all) |
| 8 | `test_export.ail` | 4 (csv products, csv customers, json products, json customers) |
| 9 | `test_invoice.ail` | 5 (create, missing, total, number gen, list by customer) |
| 10 | `test_notification_reorder.ail` | 4 (check all, pending, clear, summary) |
| 11 | `test_notification_search.ail` | 3 (low stock, out of stock, aggregated search) |
| 12 | `test_order_purchase.ail` | 7 (missing, vendor, product, valuation, add item, verify, receive) |
| 13 | `test_order_sales.ail` | 4 (missing, create/get, items, confirm) |
| 14 | `test_pagination.ail` | 5 (basic, page 2, out of range, total pages, page info) |
| 15 | `test_payment.ail` | 5 (create, missing, list by invoice, total, refund) |
| 16 | `test_payment_integration.ail` | 4 (process payment, balance, overdue, not found) |
| 17 | `test_permission.ail` | 6 (define, exists, missing, add action, remove action, list roles) |
| 18 | `test_price_history.ail` | 5 (record, get by product, latest, latest empty, list) |
| 19 | `test_product.ail` | 5 (create, missing, get by id, search, list) |
| 20 | `test_reorder.ail` | 5 (levels, check, missing, list needed, lead time) |
| 21 | `test_report.ail` | 3 (stock, sales, profit) |
| 22 | `test_report_trends.ail` | 3 (monthly sales, top products, category breakdown) |
| 23 | `test_returns.ail` | 6 (create, missing, approve, reject, list by order, complete) |
| 24 | `test_serial_number.ail` | 6 (register, missing, find, list by product, status, list available) |
| 25 | `test_shipping.ail` | 5 (create, missing, status update, list by order, list by status) |
| 26 | `test_stock_adjustment.ail` | 4 (create/get, list by product, discrepancies, summary) |
| 27 | `test_stock_aging.ail` | 3 (record/get batches, summary, remove) |
| 28 | `test_stock_movement.ail` | 3 (create/list by product, QOH, list by type) |
| 29 | `test_stock_reservation.ail` | 5 (create/get, list by order, fulfill, cancel, availability) |
| 30 | `test_stock_transfer.ail` | 4 (missing, create/get, complete, cancel) |
| 31 | `test_stock_valuation.ail` | 3 (missing, set/get, list) |
| 32 | `test_storage.ail` | 7 (empty, add, missing, get by id, update, delete missing, delete) |
| 33 | `test_supplier.ail` | 7 (create, missing, get by id, update, search, top rated, payment terms) |
| 34 | `test_tax.ail` | 5 (create, missing, calculate, list by country, update rate) |
| 35 | `test_transfer_integration.ail` | 4 (create/get, missing, list by warehouse, summary) |
| 36 | `test_vendor.ail` | 4 (create, missing, get by id, list) |
| 37 | `test_warehouse.ail` | 5 (create, missing, get by id, search by name, search by code) |
| 38 | `test_workflow.ail` | 6 (create/get, get by order, manager auto-approve, multi-level, fulfill/close, reject) |

## 6. CLI Commands (via `main.ail`)

| Command | Description |
|---|---|
| `init` | Initialize demo data (2 categories, 4 products, 3 customers, 2 vendors) |
| `seed` | Seed extended data (warehouses, reorder levels, currency rates, tax rates, suppliers, batches, serial numbers, payments, returns, shipments, workflows) |
| `add <type> <json>` | Add entity (product, customer, vendor, category, warehouse) |
| `list <type>` | List entities with optional page/limit |
| `search <query>` | Search across products, customers, vendors |
| `stock` | Stock report |
| `sell <product_id> <customer_id> <qty>` | Create sales order |
| `buy <product_id> <vendor_id> <qty>` | Create purchase order |
| `report <type>` | Reports: sales, profit, stock, trend |
| `export <type>` | Export: csv, json |
| `transfer <product_id> <qty> <from_wh> <to_wh>` | Transfer stock between warehouses |
| `reserve <product_id> <qty>` | Reserve stock |
| `audit` | Audit trail report |
| `trend <type>` | Trend report: monthly, top, category |
| `workflow <action> <workflow_id>` | Workflow actions: approve, reject |

## 7. Validation Checklist

Before running, verify:
1. Required documents read (DEVELOPMENT_STATUS.md, PROJECT_MEMORY.md, AGENTS.md, AILANG_DEVELOPMENT_PLAYBOOK.md, ARCHITECTURE_DECISIONS.md, LANGUAGE_SPEC.md)
2. Dependency graph created (Level 0 → N)
3. Stdlib audited (no manual reimplementation of existing APIs)
4. Guards verified (`map.has` before `map.get`, `list.len` before `list.get`, `&&` safe)
5. Variable names unique across all functions
6. `string.concat` ≤2 args
7. `let` has initializer
8. `return` has value
9. `ail build` passes
10. `ail run` passes with correct output
11. Patterns checked before writing filter/map/reduce/split/find

## 8. Test Command

```
python apps\inventory\tests\runner.py
```

Runs `init` and `seed` setup, then all 38 test suites sequentially. Data directory is cleaned before each run.
