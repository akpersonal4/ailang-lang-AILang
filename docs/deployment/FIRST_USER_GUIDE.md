# First User Guide — Inventory System

**Target:** First successful transaction within 15 minutes.

---

## 1. Login

The system now supports password-based authentication with role-based access control.

```bash
# Login as admin
ail run main.ail login admin admin123
```
**Expected output:**
```
Login successful. Role: admin
Session saved. You can now run other commands.
```

> **Users:** `admin` (password: `admin123`, role: admin) and `staff1` (password: `staff123`, role: staff)
> **Config file:** `config/users.json` — edit to add/remove users
> **Important:** Passwords are stored in plaintext for RC. All mutating commands require an active session.

---

## 2. First Transaction: Add a Product

```bash
cd ~/ailang-inventory
```

The system uses `init` to create demo data. For your first real product, you will use the `product_create` function.

However, since the CLI dispatches commands through `main.ail`, the easiest way to add initial data is:

```bash
# Step 1: Initialize demo data (creates sample products, customers, vendors)
ail run main.ail init
```

**Expected output:**
```
Created 2 categories and 4 products
Created 3 customers
Created 2 vendors
```

To see what was created:

```bash
ail run main.ail report
```

**Expected output:**
```
=== INVENTORY REPORT ===
Products: 4
Categories: 2
Customers: 3
Vendors: 2
Stock Movements: 0
Sales Orders: 0
Purchase Orders: 0
=== END REPORT ===
```

---

## 3. Receive Stock (Inbound Movement)

```bash
# Create a stock movement (inbound)
ail run main.ail stock
```

**Expected output:**
```
Created inbound movement for first product
Created sales order with 1 item
Created purchase order with 1 item
```

This creates:
- A stock movement (50 units inbound) for the first product
- A sales order for the first customer with 2 units of the first product
- A purchase order from the first vendor with 10 units

---

## 4. Check Stock and Dashboard

```bash
# View full report
ail run main.ail report
```

```bash
# View detailed dashboard
ail run main.ail dashboard
```

**Expected output (dashboard):**
```
=== DASHBOARD SUMMARY ===
Products: 4
Categories: 2
Customers: 3
Vendors: 2
Stock Movements: 1
Sales Orders: 1
Purchase Orders: 1
Warehouses: 0
=== END ==
```

---

## 5. Export Data

```bash
# Export products as CSV
ail run main.ail csv
```

**Expected output:**
```
=== PRODUCTS CSV ===
id,name,sku,unit_price,unit
PRD-<ts>0001,Laptop,LAP-001,1200,pcs
PRD-<ts>0002,Mouse,MOU-001,25,pcs
PRD-<ts>0003,Notebook,NTB-001,5,pcs
PRD-<ts>0004,Desk Lamp,LMP-001,45,pcs
=== END ===
```

```bash
# Export products as JSON
ail run main.ail json
```

---

## 6. Search for Products

```bash
# Search across all entities
ail run main.ail search laptop
```

---

## 7. Create a Backup

```bash
# Create a manual backup of all data collections
ail run main.ail backup
```

**Expected output:**
```
Backup created: backups\1623456789.json
```

The backup command reads all JSON files from `data/`, combines them into a single JSON map, and saves to `backups/<timestamp>.json`.

To list available backups:

```bash
ail run main.ail backups
```

**Expected output:**
```
Available backups (N files):
  1623456789.json
  auto_products.json
  ...
```

> **Note:** The `auto_*.json` files are automatic pre-write backups created by `storage.ail` — one per collection, overwritten on each write.

---

## 8. Exit and Restart

```bash
# Exit (just close the terminal)
exit

# Re-open terminal and verify data persists
cd ~/ailang-inventory
ail run main.ail report
```

**Expected output:** Same counts as before. Data persists because it is stored in JSON files.

---

## 9. Restore from Backup

If data is corrupted or lost:

```bash
# List available backups (get the timestamp)
ail run main.ail backups

# Restore specific backup (admin only)
ail run main.ail restore <timestamp>
```

**Example:**
```bash
ail run main.ail restore 1623456789
```

**Expected output:**
```
Restored from: backups\1623456789.json
```

The system also has automatic recovery: if a JSON file in `data/` is corrupted, `storage.ail` automatically attempts recovery from the auto-backup file before falling back to an empty collection.

---

## 10. Advanced Operations

### Create a Stock Adjustment

```bash
ail run main.ail adjust
```

### Stock Reservations

```bash
ail run main.ail reserve
```

### Workflow Approvals

```bash
ail run main.ail workflow
```

### Full Audit Report

```bash
ail run main.ail audit_full
```

---

## 11. Daily Workflow

### Morning (2 min)

```bash
cd ~/ailang-inventory
ail run main.ail dashboard    # Review current state
```

### During the Day (as needed)

```bash
# Add product: use init or manual JSON edit (advanced)
# Receive stock: ail run main.ail stock
# Check reports: ail run main.ail report
# Export data:   ail run main.ail csv
```

### End of Day (1 min)

```bash
ail run main.ail backup        # Backup data
ail run main.ail report        # Final review
```

---

## 12. Quick Reference Card

```
┌──────────────────────────────────────────────────────────────────┐
│                    INVENTORY QUICK REFERENCE                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  login <u> <p>   Login with username and password                │
│  logout          Logout current session                          │
│  init            Seed demo data (products, customers, vendors)   │
│  stock           Create stock movements and orders               │
│  report          Show inventory summary report                   │
│  dashboard       Show detailed dashboard                         │
│  csv             Export products as CSV                          │
│  json            Export products as JSON                         │
│  search <q>      Search across all entities                      │
│  backup          Create data backup                              │
│  restore <ts>    Restore data from backup                    (a) │
│  backups         List available backups                          │
│  check           Run integrity check                             │
│  import-<type>   Import data from CSV (products, customers,      │
│                  vendors, movements)                          (s) │
│  adjust          Create stock adjustment                     (s) │
│  reserve         Create stock reservation                    (s) │
│  warehouse       List warehouses                                 │
│  workflow        Show pending approvals                          │
│  audit_full      Show full audit report                          │
│                                                                  │
│  Legend: (a) admin only, (s) requires staff login                │
│  Data: cd ~/ailang-inventory && ail run main.ail <cmd>           │
│  Build: ail build main.ail                                       │
│  Tests: python test_compile.py                                   │
│                                                                  │
│  Always login before making changes. Backup before major ops.    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 13. Troubleshooting

| Symptom | Likely Cause | Fix |
|:--------|:-------------|:-----|
| `command not found: ail` | AILang not installed | `pip install -e .` from repo root |
| `No such file or directory` | Wrong working directory | `cd ~/ailang-inventory` |
| `ModuleNotFoundError` | AILang not installed in this Python | `pip install -e .` |
| `JSON data is empty` | No data seeded yet | `ail run main.ail init` |
| Build errors | Syntax error in .ail file | Check file for typos |
| Data file corrupted | Unexpected shutdown | Restore from auto-backup or run `restore` |
| `Error: Not logged in` | No active session | `ail run main.ail login <user> <pass>` |
| `Error: Insufficient permissions` | Wrong role for command | Login as admin |
| `Error: User not found` | Wrong username | Check `config/users.json` |

---

## Appendix: All Available Commands

| Command | Description |
|:--------|:------------|
| `login <u> <p>` | Login with username and password |
| `logout` | Logout current session |
| `init` | Initialize demo data (products, customers, vendors) |
| `stock` | Create demo stock movements and orders |
| `report` | Show inventory summary report |
| `csv` | Export products as CSV |
| `json` | Export products as JSON |
| `search <q>` | Search across all entities |
| `seed` | Seed demo data for all modules |
| `reserve` | Create demo stock reservation |
| `adjust` | Create demo stock adjustment |
| `warehouse` | List warehouses |
| `dashboard` | Show dashboard summary |
| `permission` | Demo permission operations |
| `batch` | Demo batch operations |
| `workflow` | Demo workflow operations |
| `audit_full` | Show full audit report |
| `backup` | Create data backup |
| `restore <ts>` | Restore data from backup |
| `backups` | List available backups |
| `import-products` | Import products from CSV |
| `import-customers` | Import customers from CSV |
| `import-vendors` | Import vendors from CSV |
| `import-movements` | Import movements from CSV |
| `check` | Run integrity check |
| `help` | Show help |
