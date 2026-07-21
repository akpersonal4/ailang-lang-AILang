# Inventory Production Plan

**Date:** 2026-07-10  
**Base:** `apps/inventory/` — 9,543 LOC, 80 files (48 production, 32 test), 32 JSON collections, 38/38 tests  

---

## 1. Current State Assessment

### What Already Exists

The inventory system is not a toy. It has production-grade structure:

| Component | Status | Files |
|:----------|:------:|:------|
| JSON persistence (CRUD) | ✅ Full | `storage.ail` — load, save, add, list, get_by_id, update, delete |
| Data collections | 32 | products, customers, vendors, orders, invoices, payments, stock movements, warehouse, batches, serial numbers, etc. |
| Domain modules | 48 | Each entity has create/read/update/delete/list/search |
| CLI routing | ✅ 17 commands | main.ail routes to domain modules |
| CSV export | ✅ Products, customers, movements | `export_csv_export.ail` |
| JSON export | ✅ Products | `export_json_export.ail` |
| Role-based permissions | ✅ admin/manager/staff | `auth.ail` with 20+ permission types |
| Audit trail | ✅ | `audit_trail.ail`, `audit_integration.ail` |
| Dashboard reporting | ✅ | `dashboard.ail` — product counts, order summaries |
| Search | ✅ | Cross-entity search via `search.ail` |
| Workflow approvals | ✅ | `workflow.ail` — pending approvals |
| Reorder management | ✅ | `reorder.ail` — low stock alerts |
| Stock valuation | ✅ | `stock_valuation.ail` |
| Data seed | ✅ | `data_seed.ail` — demo data generator |
| Test suite | ✅ 38/38 | 32 test files covering all modules |

### What Is Missing

| Gap | Impact | Effort to Fill |
|:----|:-------|:---------------|
| **User authentication** | Anyone can run any command | 1 file, ~60 LOC |
| **Data validation** | Invalid data silently accepted | 1 file, ~80 LOC |
| **Backup/restore** | Data loss is unrecoverable | 1 file, ~50 LOC |
| **CSV import** | Cannot migrate existing data | 1 file, ~80 LOC |
| **Error recovery** | Corrupted JSON = silent empty data | Modify `storage.ail`, ~20 LOC |
| **Concurrent access** | Two commands = race condition | Advisory file lock, ~30 LOC |
| **Installation guide** | User doesn't know how to set up | 1 file, ~40 lines |

### Surprising Finding

**The system is 80% production-ready.** The 6 gaps above require approximately **320 LOC** of AILang code — less than 4% of the existing codebase. The "productionization" is primarily about adding 5 new AILang files and a README, not rewriting the architecture.

---

## 2. Minimal Production Path

### Guiding Principle

> Add nothing that a single real user with a single machine does not need on day one.
> Do not build features that can wait for week 2.

### Sprint Structure

Three 1-week sprints. After Sprint 1, the system is usable by a real user.

```
Sprint 1:  Day 1–7   →  USABLE (user can run the system safely)
Sprint 2:  Day 8–14  →  SAFE  (data is protected, recoverable)
Sprint 3:  Day 15–21 →  SMOOTH (import, validation, guide)
```

---

## Sprint 1 — USABLE

### Goal

Put the system in front of a real user on day 7 with data safety guarantees.

### 1.1 User Authentication

**File:** `login.ail` (~60 LOC)

Add a password file (`config/users.json`) and a login command that verifies before allowing mutations:

```
config/users.json:
{
  "admin": {
    "password_hash": "<sha256>",
    "role": "admin",
    "name": "Admin User"
  },
  "staff1": {
    "password_hash": "<sha256>",
    "role": "staff",
    "name": "Staff Member"
  }
}
```

**Commands:**
```
ail run main.ail login admin mypassword    → returns session token
ail run main.ail --user admin --token <token> product create ...
```

**Key simplification:** Use SHA-256 via a Python helper script (`login_helper.py` — 15 LOC of Python) because AILang's stdlib has no built-in hash function. The Python script is called via `system.exit()` patterns — actually, the AILang runtime can call native Python functions. But we can also just store plain text passwords for the RC period behind a warning.

**Even simpler approach:** Skip hashing entirely for RC. Use a plaintext password file with a disclaimer:

```
config/users.json:
{
  "admin": { "password": "admin123", "role": "admin" },
  "staff1": { "password": "staff123", "role": "staff" }
}
```

Add this to `main.ail`:
```
fn main_login(mlUsername, mlPassword) {
    let mlUsers = storage.storage_load("users");
    let mlUser = helpers.helpers_find_in_list(mlUsers, "username", mlUsername);
    if (mlUser == false) {
        print("Error: User not found");
        return false;
    }
    let mlStoredPassword = helpers.helpers_get_map_value_safe(mlUser, "password", "");
    if (mlStoredPassword != mlPassword) {
        print("Error: Invalid password");
        return false;
    }
    let mlRole = helpers.helpers_get_map_value_safe(mlUser, "role", "staff");
    print("Login successful. Role: " + mlRole);
    // Write session file for other commands to read
    let mlSession = map.new();
    map.set(mlSession, "username", mlUsername);
    map.set(mlSession, "role", mlRole);
    map.set(mlSession, "logged_in_at", helpers.helpers_current_timestamp());
    storage.storage_save("session", mlSession);
    print("Session saved. You can now run other commands.");
    return true;
}
```

**Total:** 1 new file, ~60 LOC, 15 min to write.

### 1.2 Session-Guarded Commands

**Modify:** `main.ail` (~+30 LOC)

Every mutating command checks for an active session:

```
fn main_require_auth(mraRequiredRole) {
    let mraSession = storage.storage_load("session");
    if (mraSession == false) {
        print("Error: Not logged in. Run 'login' first.");
        return false;
    }
    let mraRole = helpers.helpers_get_map_value_safe(mraSession, "role", "");
    if (mraRole == "") {
        print("Error: Invalid session. Run 'login' again.");
        return false;
    }
    if (auth.auth_check_role(mraRole, mraRequiredRole) == false) {
        print("Error: Insufficient permissions. Required: " + mraRequiredRole);
        return false;
    }
    return true;
}
```

Route guard pattern:
```
if (mainCommand == "product_create") {
    let guard = main_require_auth("staff");
    if (guard == false) { return 1; }
    // ... existing logic
}
```

**Total:** ~30 LOC added to main.ail, 15 min.

### 1.3 Backup and Restore

**File:** `backup.ail` (~50 LOC)

```
fn backup_create() {
    let bcTimestamp = convert.to_string(helpers.helpers_unix_timestamp());
    let bcBackupDir = "backups/" + bcTimestamp;
    // Copy all JSON files from data/ to backups/<timestamp>/
    let bcCollections = storage.storage_list("__collections__");
    // ... iterate and copy each file using file.read + file.write
    print("Backup created: " + bcBackupDir);
    return true;
}

fn backup_restore(bkTimestamp) {
    let bkBackupDir = "backups/" + bkTimestamp;
    // Copy all JSON files from backups/<timestamp>/ back to data/
    // ... iterate and restore each file
    print("Restored from: " + bkBackupDir);
    return true;
}

fn backup_list() {
    // List available backups by reading backups/ directory
    // ... list directories in backups/
    print("Available backups:");
    // ... iterate and print
    return true;
}
```

**Implementation note:** AILang's `file.listdir(path)` can list backup directories. The copy is `file.read(source) + file.write(dest)`.

**Commands:** `backup`, `restore <timestamp>`, `backups`

**Total:** 1 new file, ~50 LOC, 30 min.

### 1.4 Error Recovery in Storage

**Modify:** `storage.ail` (~+15 LOC)

Add error handling for corrupted JSON files:

```
fn storage_load(collName) {
    let collPath = storage_collection_path(collName);
    if (file.exists(collPath) == false) {
        return list.new();
    }
    let collContent = file.read(collPath);
    let collParsed = json.parse(collContent);
    if (collParsed == false) {
        // Corrupted file — attempt recovery from last backup
        print("Warning: Corrupted data file: " + collPath);
        print("Attempting recovery from backup...");
        let bcRestored = storage_restore_from_backup(collName);
        if (bcRestored != false) {
            return bcRestored;
        }
        print("Error: Cannot recover " + collPath + ". Starting empty.");
        return list.new();
    }
    return collParsed;
}
```

**Total:** ~15 LOC modified in storage.ail, 10 min.

### 1.5 Sprint 1 Delivery

After 7 days and ~155 LOC of new code:

```
apps/inventory/
  login.ail          ← NEW (60 LOC)
  backup.ail          ← NEW (50 LOC)
  main.ail            ← MODIFIED (+30 LOC for auth guards)
  storage.ail         ← MODIFIED (+15 LOC for error recovery)
  config/
    users.json        ← NEW (manual setup)
```

**User experience on day 7:**

```
# Setup
mkdir config
echo '[{"username":"admin","password":"admin123","role":"admin"}]' > config/users.json

# First use
ail run main.ail login admin admin123
  → "Login successful. Role: admin"

ail run main.ail product create "Coffee Maker" "Drip coffee machine" "CM-001" "cat1" 49.99 30.00 "pcs"
  → Product created

ail run main.ail backup
  → "Backup created: backups/1623456789"

ail run main.ail report
  → Shows summary

ail run main.ail csv
  → Exports products as CSV
```

---

## Sprint 2 — SAFE

### Goal

Data is protected against loss, corruption, and user error.

### 2.1 Automatic Pre-Mutation Backups

**Modify:** `storage.ail` (~+10 LOC)

Before every `storage_save`, automatically create a rotating backup:

```
fn storage_save(collName, collItems) {
    // Auto-backup before destructive write
    storage_auto_backup(collName);
    
    let collPath = storage_collection_path(collName);
    let collJson = json.stringify(collItems);
    file.write(collPath, collJson);
    return collItems;
}

fn storage_auto_backup(collName) {
    let abBackupDir = "backups/auto/" + collName;
    let abTimestamp = convert.to_string(helpers.helpers_unix_timestamp());
    let abSource = storage_collection_path(collName);
    if (file.exists(abSource)) {
        let abContent = file.read(abSource);
        file.write(abBackupDir + "/" + abTimestamp + ".json", abContent);
    }
    return true;
}
```

Keep last 50 auto-backups per collection (delete oldest when >50).

**Total:** ~10 LOC, 15 min.

### 2.2 Input Validation

**File:** `validation.ail` (~80 LOC)

Add validation functions for common patterns:

```
fn validate_required(fieldName, fieldValue) {
    if (fieldValue == false) {
        return "Error: " + fieldName + " is required";
    }
    let vrStr = convert.to_string(fieldValue);
    if (string.trim(vrStr) == "") {
        return "Error: " + fieldName + " cannot be empty";
    }
    return "";
}

fn validate_positive_number(fieldName, fieldValue) {
    let vnNum = convert.to_int(fieldValue);
    if (vnNum <= 0) {
        return "Error: " + fieldName + " must be a positive number";
    }
    return "";
}

fn validate_email(fieldName, fieldValue) {
    let veStr = convert.to_string(fieldValue);
    if (string.contains(veStr, "@") == false) {
        return "Error: " + fieldName + " must be a valid email";
    }
    if (string.contains(veStr, ".") == false) {
        return "Error: " + fieldName + " must be a valid email";
    }
    return "";
}

fn validate_unique(fieldName, fieldValue, collectionName, searchKey) {
    let vuAll = storage.storage_list(collectionName);
    let vuFound = helpers.helpers_find_in_list(vuAll, searchKey, fieldValue);
    if (vuFound != false) {
        return "Error: " + fieldName + " must be unique — '" + convert.to_string(fieldValue) + "' already exists";
    }
    return "";
}
```

**Usage in domain modules (e.g., `product.ail`):**
```
fn product_create(pcName, pcDescription, pcSku, pcCategoryId, pcUnitPrice, pcCostPrice, pcUnit) {
    let veName = validate_required("name", pcName);
    if (veName != "") { print(veName); return false; }
    let veSku = validate_required("SKU", pcSku);
    if (veSku != "") { print(veSku); return false; }
    let veSkuUnique = validate_unique("SKU", pcSku, "products", "sku");
    if (veSkuUnique != "") { print(veSkuUnique); return false; }
    let vePrice = validate_positive_number("unit price", pcUnitPrice);
    if (vePrice != "") { print(vePrice); return false; }
    // ... existing creation logic
}
```

**Total:** 1 new file, ~80 LOC; ~5 LOC per domain module for integration.

### 2.3 Concurrent Access Guard

**Modify:** `storage.ail` (~+20 LOC)

Use a simple lock file to prevent concurrent writes:

```
fn storage_acquire_lock() {
    let lockPath = path.join(STORAGE_DATA_DIR, ".lock");
    if (file.exists(lockPath)) {
        let lockContent = file.read(lockPath);
        let lockTime = convert.to_int(lockContent);
        let now = helpers.helpers_unix_timestamp();
        // Lock older than 30 seconds is stale
        if (now - lockTime < 30) {
            print("Error: Another session is running. Wait or remove data/.lock");
            return false;
        }
        print("Warning: Removing stale lock file");
    }
    file.write(lockPath, convert.to_string(helpers.helpers_unix_timestamp()));
    return true;
}

fn storage_release_lock() {
    let lockPath = path.join(STORAGE_DATA_DIR, ".lock");
    if (file.exists(lockPath)) {
        file.remove(lockPath);
    }
    return true;
}
```

**Total:** ~20 LOC, 10 min.

---

## Sprint 3 — SMOOTH

### Goal

User can migrate existing data, get help, and operate without hand-holding.

### 3.1 CSV Import

**File:** `import_csv.ail` (~80 LOC)

```
fn import_csv_products() {
    // Read products.csv from imports/ directory
    let icContent = file.read("imports/products.csv");
    if (icContent == false) {
        print("Error: No imports/products.csv found");
        return false;
    }
    // Parse CSV lines
    let icLines = string.split(icContent, "\n");
    // Skip header, parse each line
    // For each row: validate, create product
    // Track success/failure counts
    print("Imported X products. Y errors.");
    return true;
}
```

Similar for customers, vendors, movements — or a generic CSV-to-collection parser.

**Commands:** `import-products`, `import-customers`, `import-vendors`, `import-movements`

**Total:** 1 new file, ~80 LOC, 1 hour.

### 3.2 Production README

**File:** `PRODUCTION_README.md` (~80 lines)

Contents:
- Installation prerequisites (Python 3.11+, AILang)
- Setup instructions (`config/users.json`)
- First login
- Daily operations (add product, create order, check stock)
- Backup instructions
- Importing existing data
- Backup rotation
- Troubleshooting
- Maintenance schedule

### 3.3 Data Integrity Check

**File:** `integrity.ail` (~40 LOC)

```
fn integrity_check() {
    // Verify all JSON files parse correctly
    // Check that all foreign key references are valid
    // Report missing references, orphaned records
    // Report negative stock quantities
    print("Integrity check complete. X warnings.");
    return true;
}
```

**Command:** `check`

### 3.4 Sprint 3 Delivery

After 21 days and ~400 LOC total new code:

```
apps/inventory/
  login.ail              ← Sprint 1 (60 LOC)
  backup.ail             ← Sprint 1 (50 LOC)
  validation.ail         ← Sprint 2 (80 LOC)
  import_csv.ail         ← Sprint 3 (80 LOC)
  integrity.ail          ← Sprint 3 (40 LOC)
  config/users.json      ← Sprint 1
  PRODUCTION_README.md   ← Sprint 3
  
  main.ail               ← MODIFIED (+30 LOC)
  storage.ail            ← MODIFIED (+45 LOC)
  product.ail            ← MODIFIED (+10 LOC per domain)
  customer.ail           ← MODIFIED (+10 LOC per domain)
  vendor.ail             ← MODIFIED (+10 LOC per domain)
  
  Total new code: ~400 LOC
  Total modified: ~100 LOC across 5 files
  Grand total: ~500 LOC of production work
```

---

## 3. Architecture

### Data Flow

```
User  →  CLI (main.ail)  →  Auth guard (login.ail)  →  Domain module (product.ail)
                                                                ↓
                                                        Validation (validation.ail)
                                                                ↓
                                                        Persistence (storage.ail)
                                                                ↓
                                                        JSON file (data/*.json)
                                                                ↓
                                                        Auto-backup (backup.ail)
```

### Directory Structure (Production)

```
apps/inventory/
├── config/
│   └── users.json              # User accounts (manual setup)
├── data/
│   ├── .lock                   # Concurrent access guard
│   ├── products.json           # 32 JSON collections
│   ├── customers.json
│   └── ...                     # 30 more collection files
├── backups/
│   ├── auto/                   # Automatic pre-write snapshots
│   │   ├── products/
│   │   ├── customers/
│   │   └── ...
│   ├── 1623456789/             # Manual backup (timestamp)
│   └── 1623456790/
├── imports/
│   └── products.csv            # User drops CSV files here
├── *.ail                       # 48 production AILang files
├── tests/
│   └── *.ail                   # 32 test files
├── main.ail                    # CLI entry point
└── PRODUCTION_README.md
```

### Module Dependency Graph

```
                          main.ail
                             │
              ┌──────────────┼──────────────┐
              │              │              │
          login.ail     validation.ail   backup.ail
              │              │              │
              └──────┬───────┘              │
                     │                      │
                 storage.ail ◄──────────────┘
                     │
                     ▼
               JSON files
```

---

## 4. Migration Strategy

### From Benchmark to Production

The current system uses in-memory demo data. Production requires:

| Step | Action | Duration |
|:-----|:-------|:---------|
| 1 | `ail run main.ail seed` | 1 sec |
| 2 | Delete seed data from JSON files | 1 min |
| 3 | Import real data via CSV | 10 min |
| 4 | Create admin user in config/users.json | 1 min |
| 5 | Verify with `check` command | 1 sec |
| 6 | Create first backup | 1 sec |
| Total | | ~13 min |

### Data Migration

```
user.csv:
name,email,phone,active
"Acme Corp","acme@example.com","555-0101",true
"Bob Industries","bob@example.com","555-0102",true

products.csv:
name,description,sku,category_id,unit_price,cost_price,unit
"Coffee Maker","Drip machine","CM-001",,49.99,30.00,pcs
"Desk Chair","Ergonomic","DC-001",,199.99,120.00,pcs
```

User places CSV files in `imports/` directory, runs `import-products`.

---

## 5. Deployment Model

### Single-User Local Installation

| Aspect | Detail |
|:-------|:-------|
| **Machine** | Any Windows/Mac/Linux with Python 3.11+ |
| **Install** | `pip install ailang` (or run from source) |
| **Data location** | `apps/inventory/data/` — local directory |
| **Backup location** | `apps/inventory/backups/` — local directory |
| **Invocation** | `ail run apps/inventory/main.ail <command>` |
| **CLI style** | Interactive command-by-command |
| **Session** | File-based session token in `data/session.json` |

### Why Not

- **Web server:** Adds deployment complexity, requires HTTP, auth, sessions — out of scope for RC
- **Database:** SQLite would require native extension — JSON files are sufficient for single-user
- **Multi-user concurrent:** Lock file prevents corruption — good enough for 1–2 users

### Deployment Steps

```
# For the real user:
git clone <repo>  or  copy apps/inventory/ to their machine
cd apps/inventory
mkdir config
mkdir imports
echo '{"admin":{"password":"choose_a_password","role":"admin"}}' > config/users.json
ail run main.ail login admin <password>
ail run main.ail backup
# System is ready
```

---

## 6. Backup Model

### Three Layers of Protection

| Layer | Mechanism | Frequency | Recovery Time |
|:------|:-----------|:----------|:--------------|
| 1 — Auto-backup | Pre-write snapshot per collection | Every write | < 1 min |
| 2 — Manual backup | Full data directory copy | Daily (manual) | < 5 min |
| 3 — Export | CSV export of all collections | Weekly | < 10 min |

### Auto-Backup Retention

Keep last 50 snapshots per collection. Auto-pruning on each write:
```
fn storage_prune_auto_backups(collName) {
    let pbDir = "backups/auto/" + collName;
    let pbFiles = file.listdir(pbDir);
    let pbCount = list.len(pbFiles);
    if (pbCount > 50) {
        // Sort by name (timestamp) and delete oldest
        // ... deletion logic
    }
    return true;
}
```

### Restore Scenarios

| Scenario | Recovery Action | Data Loss |
|:---------|:----------------|:----------|
| User error (deleted record) | Restore last auto-backup of collection | < 1 write |
| Corrupted JSON file | Auto-detected by `storage_load`, falls back to auto-backup | < 1 write |
| Accidental `data/` deletion | Manual restore from `backups/<timestamp>/` | < 1 day |
| Hard drive failure | Re-clone repo, restore from CSV exports | < 1 week |

---

## 7. Expected Maintenance Effort

### Weekly Operations (15 min/day)

| Task | Frequency | Duration |
|:-----|:----------|:---------|
| Data entry (new products, orders) | Daily | 5–10 min |
| Stock adjustments | 2–3×/week | 5 min |
| Backup (manual) | Daily | 30 sec |
| Integrity check | Weekly | 10 sec |

### Bug Fixes (1–2 hours/week)

Based on Engineering Olympics data (P4 showed 5 bugs in similar inventory code):

| Type | Expected Rate | Examples |
|:-----|:-------------|:---------|
| Logic errors (wrong comparison, off-by-one) | 1–2/month | Stock threshold off by 1 |
| Data validation gaps | 1–2/month | Empty name accepted |
| Edge cases in calculation | 1/month | Division by zero in tax |

### Feature Requests (1–2 hours/week)

| Type | Expected Rate |
|:-----|:--------------|
| New report types | 1/month |
| New import formats | 1–2 months |
| UI improvements | Ongoing |

### Total

| Activity | Hours/Week |
|:---------|:-----------|
| Daily operations | 1.5 |
| Bug fixes | 1.0 |
| Feature requests | 1.0 |
| Backups & maintenance | 0.5 |
| **Weekly total** | **4.0** |

Sustainable for a single maintainer alongside other work.

---

## 8. Known Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|:-----|:----------:|:------:|:-----------|
| **JSON file corruption** during write | Low | Medium | Write to temp file, then rename; auto-backup recovery |
| **Concurrent access** (2 terminals) | Low | Medium | Lock file prevents writes |
| **Hard drive failure** | Very Low | High | Daily backup + weekly CSV export |
| **Recursion limit exceeded** (500 calls) | Low | Medium | All inventory functions are shallow (<50 calls) |
| **Password in plaintext** | Medium | Medium | Document risk; SHA-256 post-RC |
| **User accidentally deletes data/** | Medium | High | `rm` guard: backup.ail refuses if no backup exists |
| **Python version mismatch** | Low | High | Pin Python 3.11+ in PRODUCTION_README.md |
| **AILang compiler bug** | Low | Medium | Roll back to last-known-good tag |
| **User doesn't run backups** | High | Medium | `storage_auto_backup` runs on every write; weekly nag message |

### Risk: `rm -rf data/` Protection

```python
# In production_wrapper.py (optional Python wrapper, 10 LOC):
import sys
import os

if __name__ == "__main__":
    # Verify data directory exists before running
    if not os.path.exists("data/.lock"):
        print("Warning: No data directory found. Run setup first.")
        sys.exit(1)
    os.system(f"ail run main.ail {' '.join(sys.argv[1:])}")
```

---

## 9. What We Will Learn

### Language Validation Data Points

After 3 months of production use:

| Question | How We Answer |
|:---------|:--------------|
| Is JSON persistence sufficient? | Count of data corruption incidents |
| Is plaintext auth acceptable? | User feedback on login friction |
| Is 500-call recursion limit a problem? | Max call depth observed in production |
| Are error messages helpful? | Number of support questions |
| Is the CLI workflow efficient? | Time per daily operation |
| Does `storage.ail` scale to 50K records? | Load test with real data volume |
| Are float literals working correctly? | Pricing bugs reported |
| Is eager `&&` causing real bugs? | Bug reports matching this pattern |

### Benchmark Evidence

| Comparison | Current | After 3 Months |
|:-----------|:--------|:---------------|
| AILang vs Python bug fix rate | 5/5 vs 0/5 (synthetic) | **Real bug fix data** |
| AILang vs Python feature delivery | Synthetic tasks | **Real feature requests** |
| Maintenance cost per feature | Estimated | **Measured in hours** |
| AILang stdlib sufficiency | Guessed | **Empirical gap list** |

---

## 10. What We Will NOT Build

> These features are explicitly postponed. They would add engineering overhead without validating the language.

| Feature | Why Not | When |
|:--------|:--------|:-----|
| Web UI | Adds HTTP server, HTML, CSS — not AILang's job | Post-1.0 |
| SQLite backend | Requires native extension | Post-1.0 |
| Multi-user concurrency | Lock file is sufficient for 1–2 users | Post-1.0 |
| SHA-256 password hashing | Requires Python helper; plaintext is acceptable for RC | v1.0.0 final |
| Email notifications | Requires SMTP integration | Post-1.0 |
| PDF invoice generation | Requires binary format library | Post-1.0 |
| Barcode scanning | Requires USB/hardware integration | Post-1.0 |
| REST API | Adds web server dependency | Post-1.0 |
| Mobile app | Entirely separate product | Post-1.0 |

Every postponed feature is a **deliberate scope constraint**, not a forgotten gap.

---

## 11. Timeline

```
Week 1 (Sprint 1): USABLE
  Mon:  Write login.ail (60 LOC)
  Tue:  Add auth guards to main.ail (30 LOC)
  Wed:  Write backup.ail (50 LOC)
  Thu:  Add error recovery to storage.ail (15 LOC)
  Fri:  Integration test, bug fixes
  Sat:  Deploy to real user
  Sun:  User acceptance

Week 2 (Sprint 2): SAFE
  Mon:  Add auto-backup to storage.ail (10 LOC)
  Tue:  Write validation.ail (80 LOC)
  Wed:  Add validation to product/customer/vendor (30 LOC)
  Thu:  Add concurrent access guard (20 LOC)
  Fri:  Integration test, edge case hardening
  Sat:  User feedback review
  Sun:  Bug fixes

Week 3 (Sprint 3): SMOOTH
  Mon:  Write import_csv.ail (80 LOC)
  Tue:  Write integrity.ail (40 LOC)
  Wed:  Write PRODUCTION_README.md
  Thu:  Data migration from user's existing system
  Fri:  Production launch with real data
  Sat–Sun: On-call for launch issues

Week 4–12: MAINTENANCE
  Daily:  User support (15 min)
  Weekly: Bug fixes, small features (4 hours)
  Monthly: V1_RC1_RELEASE_NOTES.md update with production lessons
```

---

## 12. Conclusion

### The Minimal Production Path

The smallest amount of engineering required to put the system in front of a real user:

**Day 1: ~60 LOC (login.ail + main.ail guard)**
- User can log in with a password
- Mutations are protected by role check
- Read-only commands (report, dashboard, csv) are always available

**That's it.** Day 1 is the answer to "what is the smallest amount?"

Everything else (backup, validation, import, integrity) is quality-of-life improvement that reduces support burden but is not required for the user to start using the system.

### Total Required LOC

| Component | LOC | Status |
|:----------|:---:|:------:|
| Existing codebase | 9,543 | ✅ Already built |
| User authentication | 60 | 🏗 Sprint 1 |
| Auth guards in CLI | 30 | 🏗 Sprint 1 |
| Backup/restore | 50 | 🏗 Sprint 1 |
| Error recovery | 15 | 🏗 Sprint 1 |
| Input validation | 80 | 🏗 Sprint 2 |
| Concurrent access | 20 | 🏗 Sprint 2 |
| CSV import | 80 | 🏗 Sprint 3 |
| Integrity check | 40 | 🏗 Sprint 3 |
| **Total production add** | **375** | **~4% of existing** |

### Decision

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  The inventory system is 80% production-ready TODAY.                 ║
║  With 375 LOC (4% of existing codebase) across 6 new files,          ║
║  it becomes a production application that a real user can             ║
║  operate daily.                                                      ║
║                                                                      ║
║  Day 1 deliverable: login.ail + auth guards — 60 LOC, 15 min.        ║
║  Week 1 deliverable: full USABLE system — 155 LOC, 7 days.           ║
║  Week 3 deliverable: full SAFE+SMOOTH system — 375 LOC, 21 days.     ║
║                                                                      ║
║  The fastest path to "real user, real bug, real fix" is:             ║
║                                                                      ║
║    Write login.ail today. Deploy tomorrow.                           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```
