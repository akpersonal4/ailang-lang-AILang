# First Deployment — Inventory System

**Date:** 2026-07-10  
**Version:** v1.0.0-RC1  
**User:** Single operator on single machine

---

## 1. Architecture

### Deployment Diagram

```
┌─────────────────────────────────────────────────────┐
│                   User's Machine                      │
│                                                       │
│   ┌──────────────┐     ┌──────────────────────────┐  │
│   │   Terminal    │────▶│   ail run main.ail      │  │
│   │   (CLI)       │     │   <command> [args]       │  │
│   └──────────────┘     └──────────┬───────────────┘  │
│                                   │                   │
│                                   ▼                   │
│   ┌──────────────────────────────────────────────┐   │
│   │              Inventory Codebase               │   │
│   │   main.ail → auth.ail → storage.ail → ...    │   │
│   └──────────────────────┬───────────────────────┘   │
│                          │                           │
│                          ▼                           │
│   ┌──────────────────────────────────────────────┐   │
│   │              JSON Data Files                   │   │
│   │   data/products.json                          │   │
│   │   data/customers.json                         │   │
│   │   data/invoices.json       (32 collections)   │   │
│   └──────────────────────┬───────────────────────┘   │
│                          │                           │
│                          ▼                           │
│   ┌──────────────────────────────────────────────┐   │
│   │              Backup Directory                  │   │
│   │   backups/<timestamp>/                       │   │
│   └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Constraints

| Constraint | Reason |
|:-----------|:-------|
| Single machine | No network dependencies, no server process |
| CLI only | No GUI framework needed |
| JSON files | No database server, no SQL |
| No cloud | Data stays on user's machine |
| No Docker/Podman/K8s | Zero container infrastructure |

### Technology Stack

| Layer | Technology | Justification |
|:------|:-----------|:--------------|
| Language | AILang v1.0.0-RC1 | Target of validation |
| Runtime | Python 3.11+ | AILang interpreter host |
| Data | JSON files (flat file) | Single-user, no concurrent writes |
| CLI | Terminal | No UI framework needed |
| Installer | Python script | Cross-platform, no dependencies |

---

## 2. Installation Steps

### Prerequisites

```
- Python 3.11 or later
- pip (Python package manager)
- 50 MB free disk space
- Read/write permission on installation directory
```

### Step 1 — Install AILang

```bash
# Option A: From source (recommended for RC)
git clone <repository-url> ailang
cd ailang
pip install -e .

# Option B: From PyPI (if published)
pip install ailang

# Verify installation
ail --help
# Expected output: "Usage: ail build|run|fmt|lsp|..."
```

### Step 2 — Run Installer

```bash
# The installer creates the inventory application directory
python tools/install_inventory.py

# Or manually:
mkdir -p ~/ailang-inventory/data
mkdir -p ~/ailang-inventory/backups
mkdir -p ~/ailang-inventory/imports
cp -r apps/inventory/*.ail ~/ailang-inventory/
```

### Step 3 — Verify Installation

```bash
cd ~/ailang-inventory

# Run the self-test
ail run main.ail help

# Expected output:
# Usage: ail run main.ail <command>
# Commands:
#   init       - Initialize demo data
#   stock      - Create demo stock movements and orders
#   report     - Show inventory summary report
#   csv        - Export products as CSV
#   json       - Export products as JSON
#   dashboard  - Show dashboard summary
#   search <q> - Search across all entities
#   ...
```

### Step 4 — Initialize Data Directory

```bash
# Create initial data directory structure
mkdir -p data
mkdir -p backups
mkdir -p imports
```

### Step 5 — Seed Demo Data (Optional)

```bash
# Create sample products, customers, vendors
ail run main.ail init
# Expected: "Created 2 categories and 4 products"
#            "Created 3 customers"
#            "Created 2 vendors"

# Create sample stock movements and orders
ail run main.ail stock

# Verify data persisted
ail run main.ail report
# Expected: Shows product/customer/vendor counts
```

### Expected Time

| Step | Duration |
|:-----|:---------|
| Install Python (if needed) | 5 min |
| Install AILang | 2 min |
| Run installer | < 10 sec |
| Verify installation | 1 min |
| Seed demo data | 1 min |
| **Total first-time setup** | **~9 min** |

---

## 3. Directory Layout

```
~/ailang-inventory/                 # Application root
├── main.ail                        # Entry point (CLI dispatcher)
├── helpers.ail                     # Shared utilities
├── storage.ail                     # JSON persistence layer
├── auth.ail                        # Role-based permissions
├── audit.ail                       # Audit trail
├── backup.ail                      # Backup/restore (*)
├── login.ail                       # User authentication (*)
├── validation.ail                  # Input validation (*)
├── import_csv.ail                  # CSV import (*)
├── integrity.ail                   # Data integrity check (*)
├── product.ail                     # Product CRUD
├── customer.ail                    # Customer CRUD
├── vendor.ail                      # Vendor CRUD
├── supplier.ail                    # Supplier management
├── category.ail                    # Category management
├── order_sales_order.ail           # Sales orders
├── order_purchase_order.ail        # Purchase orders
├── invoice.ail                     # Invoice generation
├── payment.ail                     # Payment tracking
├── payment_integration.ail         # Payment integrations
├── stock_movement.ail              # Stock movements (in/out)
├── stock_adjustment.ail            # Stock adjustments
├── stock_transfer.ail              # Stock transfers
├── stock_reservation.ail           # Stock reservations
├── stock_valuation.ail             # Stock valuation
├── stock_aging.ail                 # Stock aging analysis
├── reorder.ail                     # Reorder levels/alerts
├── notification.ail                # Notifications
├── notification_reorder.ail        # Reorder notifications
├── shipping.ail                    # Shipping management
├── returns.ail                     # Returns processing
├── serial_number.ail               # Serial number tracking
├── batch.ail                       # Batch/lot tracking
├── warehouse.ail                   # Warehouse management
├── currency.ail                    # Currency/multi-currency
├── tax.ail                         # Tax rates
├── price_history.ail               # Price change history
├── permission.ail                  # Permission system
├── pagination.ail                  # Pagination utilities
├── search.ail                      # Cross-entity search
├── dashboard.ail                   # Dashboard summary
├── report_stock_report.ail         # Stock reports
├── report_sales_report.ail         # Sales reports
├── report_profit_report.ail        # Profit reports
├── report_trends.ail               # Trend analysis
├── export_csv_export.ail           # CSV export
├── export_json_export.ail          # JSON export
├── data_seed.ail                   # Demo data seed
├── audit_trail.ail                 # Audit log
├── audit_integration.ail           # Audit integration
├── workflow.ail                    # Workflow approvals
├── transfer_integration.ail        # Transfer integration
├── data/                           # JSON data files (auto-created)
│   ├── products.json
│   ├── customers.json
│   ├── invoices.json
│   └── ... (32 collections total)
├── backups/                        # Backup snapshots (auto-created)
│   └── auto/                       # Automatic pre-write backups
│       ├── products/
│       ├── customers/
│       └── ...
├── imports/                        # CSV import directory
│   └── products.csv               # User drops files here
├── tests/                          # Test suite
│   ├── test_product.ail
│   ├── test_stock_movement.ail
│   └── ... (32 test files)
└── test_compile.py                 # Compile & run smoke test

(*) Files marked with * are planned but not yet built.
```

---

## 4. Backup Locations

### What Gets Backed Up

| Path | Content | Criticality |
|:-----|:--------|:------------|
| `data/*.json` | All business data | Critical — restore target |
| `config/users.json` | User accounts (if created) | Medium |

### What Does NOT Get Backed Up

| Path | Reason |
|:-----|:-------|
| `*.ail` | Source code — version controlled |
| `tests/` | Test code — version controlled |
| `backups/` | Previous backups — no recursive backup |

### Backup Storage

| Type | Location | Retention |
|:-----|:---------|:----------|
| Manual backup | `backups/<timestamp>/` | Until manually deleted |
| Auto-backup | `backups/auto/<collection>/` | Last 50 per collection |
| CSV export | `exports/` (manual) | Until manually deleted |

### Recommended Backup Schedule

| Frequency | Action |
|:----------|:-------|
| **Every session** | Run `ail run main.ail backup` before quitting |
| **Before any mutation** | System auto-saves pre-write snapshots |
| **Weekly** | Export all collections as CSV |
| **Before upgrade** | Full manual backup |

---

## 5. Recovery Steps

### Scenario 1: Corrupted Single JSON File

```bash
# 1. Identify the corrupted file
ail run main.ail check
# Expected: Warning about corrupted file

# 2. The system attempts auto-recovery from backups/auto/
# If recovery succeeds, data is restored with < 1 write of loss

# 3. If auto-recovery fails, manually restore from backup
# (Copy from backups/<timestamp>/<collection>.json to data/)
```

### Scenario 2: Entire data/ Directory Lost

```bash
# 1. Restore from latest manual backup
# Copy backups/<latest_timestamp>/* to data/

# 2. Verify integrity
ail run main.ail report
# Expected: Shows expected counts
```

### Scenario 3: Application Won't Start

```bash
# 1. Verify AILang installation
ail --version

# 2. Check for compiler errors
ail build main.ail

# 3. If build fails, reinstall AILang
pip install -e .  # from repo root

# 4. If build succeeds but runtime fails, restore data from backup
```

---

## 6. Upgrade Process

### Upgrading AILang Version

```bash
# 1. Backup current data
ail run main.ail backup

# 2. Export all data as CSV (safety net)
ail run main.ail csv > exports/pre-upgrade-products.csv

# 3. Upgrade AILang
pip install --upgrade ailang

# 4. Verify application still works
ail build main.ail
python test_compile.py

# 5. Verify data integrity
ail run main.ail report
```

### Upgrading Application Code

```bash
# 1. Backup data
ail run main.ail backup

# 2. Replace .ail files with new versions
cp <new-version>/inventory/*.ail ~/ailang-inventory/

# 3. Run tests
ail build main.ail
python test_compile.py

# 4. Verify data
ail run main.ail report
```

### Rollback

```bash
# 1. Restore previous .ail files from backup/version control
# 2. Restore data from backup
# 3. Verify
ail build main.ail
ail run main.ail report
```

---

## 7. Quick Reference

### Common Commands

| Command | Action |
|:--------|:-------|
| `ail run main.ail help` | Show available commands |
| `ail run main.ail init` | Seed demo data |
| `ail run main.ail report` | Show inventory summary |
| `ail run main.ail dashboard` | Show detailed dashboard |
| `ail run main.ail csv` | Export products as CSV |
| `ail run main.ail backup` | Create data backup |
| `ail run main.ail check` | Verify data integrity |
| `ail build main.ail` | Check for compile errors |
| `python test_compile.py` | Run full test suite |

### File Paths

| Item | Path |
|:-----|:-----|
| Application root | `~/ailang-inventory/` |
| Data files | `~/ailang-inventory/data/` |
| Backups | `~/ailang-inventory/backups/` |
| Imports | `~/ailang-inventory/imports/` |
| Test suite | `~/ailang-inventory/tests/` |

---

## 8. Deployment Verification

Run these commands to verify the deployment is complete:

```bash
echo "=== Step 1: Directory Structure ==="
ls -la *.ail | wc -l
echo "Expected: 48+ .ail files"

echo "=== Step 2: Build Check ==="
ail build main.ail
echo "Expected: No errors, exit code 0"

echo "=== Step 3: Help Command ==="
ail run main.ail help
echo "Expected: Shows command list"

echo "=== Step 4: Test Suite ==="
python test_compile.py
echo "Expected: ALL TESTS PASSED"
```

### Verification Checklist

```
□ Python 3.11+ installed
□ ail command available (ail --version)
□ Inventory directory exists with 48+ .ail files
□ data/ directory exists
□ backups/ directory exists
□ imports/ directory exists
□ ail build main.ail succeeds
□ ail run main.ail help shows command list
□ python test_compile.py passes
□ ail run main.ail init succeeds
□ ail run main.ail report shows counts
```
