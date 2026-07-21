# Implementation Plan — Inventory Management System

## Application: Inventory Management System

An inventory management system with items, categories, suppliers, stock tracking, and reports.

## Features

- Items (SKU, name, description, category, price, quantity, min quantity, supplier)
- Categories (grouping items)
- Suppliers (vendor information)
- Stock transactions (purchase, sale, adjustment)
- Low stock alerts
- Inventory valuation
- Category breakdown reports
- JSON persistence

## Data Structures (all maps)

```
Item:      {id, sku, name, description, category_id, unit_price, quantity, min_quantity, supplier_id}
Category:  {id, name, description}
Supplier:  {id, name, contact, email, phone}
Txn:       {id, item_id, type, quantity, date, note}
Inventory: {items: [Item...], transactions: [Txn...]}
```

## Dependency Map

```
Level 0 (11):  is_empty, current_timestamp_val, new_id, find_substring, find_delim,
               split_helper, split_string, string_in_list_pos, string_in_list_flag,
               list_copy, convert_to_string_val
Level 1 (3):   filter_matching, count_matching, find_in_list_by_field
Level 2 (12):  make_item/category/supplier/transaction, *-to-map, map-to-*
Level 3 (14):  add/remove/find/get item, update_stock, record_txn, query helpers
Level 4 (4):   inventory_to_full_map, full_map_to_inventory, save/load
Level 5 (10):  print_item, print_list, print_report/summary/breakdown
Level 6 (4):   create_demo_categories/suppliers/items/transactions, run_demo
Level 7 (1):   main
```

**Total: ~60 functions**

## Risk Analysis

| Risk | Mitigation |
|------|-----------|
| Forward references | Physical bottom-up ordering by level |
| Map key mismatch | Consistent key names across all `map.set`/`map.get` |
| Variable collision | Unique 2-3 char suffix per function |
| Empty list access | `list.len` guard before `list.get` |
| Missing map key | `map.has` guard before `map.get` |
| `string.concat` 3+ args | Use `+` for 3+ strings |
| Missing stdlib | Stdlib table checked; `list.copy`→custom, `split`→custom |
