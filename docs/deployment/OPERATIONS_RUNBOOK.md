# Operations Runbook — Inventory System

**Date:** 2026-07-10  
**Application:** AILang Inventory System  
**Version:** v1.0.0-RC2  

---

## How to Use This Runbook

Each scenario follows this format:

```
## Symptom

Brief description of what the user sees.

## Cause

Why it happens.

## Resolution

Step-by-step fix.

## Prevention

How to avoid in the future.
```

---

## Scenario 1: Application Won't Start

### Symptom

```
'ail' is not recognized as an internal or external command
```

or

```
ModuleNotFoundError: No module named 'compiler'
```

### Cause

AILang is not installed or not in PATH.

### Resolution

```bash
# Verify Python is installed
python --version
# Expected: Python 3.11.x or later

# Install AILang from repository root
cd <repo-root>
pip install -e .

# Verify installation
ail --help
```

### Prevention

Always run `pip install -e .` from the repo root when setting up a new machine.

---

## Scenario 2: Build Failure

### Symptom

```
$ ail build main.ail
Error: SEM002: Undefined identifier: someFunction
  --> main.ail:25:5
```

### Cause

A compiler error in the AILang source code — typically:
- Undefined identifier (typo)
- Wrong number of function arguments
- Mismatched types
- Import path not found

### Resolution

```bash
# Read the error message carefully — it includes file, line, and column
# Fix the reported error

# Rebuild
ail build main.ail

# If errors persist, check:
#   - All function names are spelled correctly
#   - All imports exist at the specified paths
#   - All variables are declared with 'let'

# For a list of known issues:
cat docs/releases/V1_RC1_KNOWN_LIMITATIONS.md
```

### Prevention

```bash
# Run build check after every change
ail build main.ail

# Run full test suite before deployment
python test_compile.py
```

---

## Scenario 3: Backup Restore

### Symptom

```
Data is missing or corrupted.
ail run main.ail report shows 0 products.
```

### Cause

- Accidental deletion of `data/` directory
- JSON file corruption (system crash during write)
- User error (deleted records)

### Resolution

```bash
# Step 1: Login (required for restore)
ail run main.ail login admin admin123

# Step 2: List available backups
ail run main.ail backups

# Step 3: Restore a specific backup by timestamp
ail run main.ail restore 1623456789

# Step 4: Verify restoration
ail run main.ail report

# Step 5: If no backups exist, start fresh
ail run main.ail init
# Data loss is permanent — this is why backups are critical
```

### Prevention

```bash
# Backup before every session
ail run main.ail backup

# Auto-backup is enabled by default — every storage_save creates
# backups/auto_<collection>.json before overwriting
```

---

## Scenario 4: Corrupted Data File

### Symptom

```
Warning: data/products.json corrupted. Attempting auto-backup recovery...
Warning: Cannot recover products.json. Starting empty.
```

### Cause

- System crash during `storage_save` (power loss, killed process)
- Manual editing of JSON files introduced syntax errors
- Disk full during write

### Resolution

```bash
# Step 1: The system attempted auto-recovery from backups/auto_products.json
# Check if it succeeded:
ail run main.ail report

# Step 2: If collection is empty, check auto-backup integrity
ail run main.ail backups

# Step 3: Restore from manual backup
# See Scenario 3 above

# Step 4: If no backups exist, check data/ directory contents
dir data\
# Look for truncated JSON, extra commas, missing brackets

# Step 5: Use integrity check to assess overall data health
ail run main.ail check
```

### Prevention

The `storage.ail` module creates automatic pre-write backups in `backups/auto_*.json` before every `storage_save`. On next load, if a JSON file is corrupted, the system reads the auto-backup automatically. The auto-backup is always at most one write behind current data.

---

## Scenario 5: Forgotten Password

### Symptom

```
Error: Invalid password
```

### Cause

User forgot the password for their admin account.

### Resolution

```bash
# Step 1: Open the config file
type config\users.json

# Step 2: Find the admin user and view/reset password
# The file contains:
# {
#   "username": "admin",
#   "password": "current_password",
#   "role": "admin"
# }

# Step 3: Change password
# Edit config/users.json with a text editor
# Replace the password value with a new one
# Save the file

# Step 4: Verify login works
ail run main.ail login admin <new_password>
```

### Prevention

Save the admin password in a password manager. The password is stored in plaintext (`config/users.json`) — consider this when choosing a password. Default passwords are documented in FIRST_USER_GUIDE.md.

---

## Scenario 5a: Concurrent Access / Lock File

### Symptom

```
Error: Another session is running. Wait or remove data/.lock
```

### Cause

Two instances of `ail run main.ail` are running simultaneously. The storage module creates a lock file (`data/.lock`) to prevent concurrent writes.

### Resolution

```bash
# Step 1: Wait a few seconds and retry
ail run main.ail report

# Step 2: If the error persists, check for stale lock
dir data\.lock
# The lock auto-expires after 30 seconds

# Step 3: If no other session is running, remove stale lock
del data\.lock

# Step 4: Retry the operation
ail run main.ail report
```

### Prevention

Never run multiple `ail run main.ail` commands at the same time. The lock file prevents data corruption from concurrent writes.

---

## Scenario 5b: CSV Import Failure

### Symptom

```
Error: File not found: imports/products.csv
Error: File is empty: imports/products.csv
```

### Cause

- The CSV file does not exist in the `imports/` directory
- The CSV file is empty (0 bytes)
- The CSV file contains only headers with no data rows

### Resolution

```bash
# Step 1: Verify the import file exists
dir imports\

# Step 2: Check the CSV format
type imports\products.csv
# Expected format:
#   name,price,category,sku
#   Widget,10.99,Electronics,WID-001

# Step 3: Ensure the CSV has column headers in the first row
# The system uses csv.parse_header which requires headers

# Step 4: Ensure the CSV is not empty
# Minimum content: header row followed by at least one data row

# Step 5: Retry the import
ail run main.ail import-products
```

### Prevention

Always validate CSV files before importing. Use the checklist:
- File exists in `imports/`
- File has column headers in first row
- File has at least one data row
- CSV is well-formed (no unescaped quotes, consistent columns)

---

## Scenario 5c: Integrity Check Failure

### Symptom

```
=== INTEGRITY CHECK ===
  [WARN] Product X references non-existent category Y
  [WARN] Movement references non-existent product Z
  [WARN] Product W has negative stock balance: -5
=== END ===
Total warnings: N
```

### Cause

- Data inconsistency introduced by manual JSON edits
- Incomplete data restoration from backup
- Products or categories deleted without updating dependent records
- Stock movements without corresponding inbound/outbound entries

### Resolution

```bash
# Step 1: Read the integrity warning messages carefully
# Each warning identifies the specific issue and affected records

# Step 2: For orphan category references — update or add the missing category
# See FIRST_USER_GUIDE.md for data editing procedures

# Step 3: For orphan movement references — delete or reassign the movement
# Check data/movements.json for the affected product_id

# Step 4: For negative stock — investigate and possibly create
# inbound movements to correct the balance

# Step 5: Re-run integrity check to verify fix
ail run main.ail check

# Step 6: If data is too corrupted, restore from backup
ail run main.ail restore <timestamp>
```

### Prevention

```bash
# Run integrity check regularly (included in daily maintenance)
ail run main.ail check

# Always use the CLI commands to modify data (not manual JSON editing)
# Backup before any manual data manipulation
```

---

## Scenario 6: Failed Upgrade

### Symptom

After copying new `.ail` files:

```
$ ail build main.ail
Error: TYP001: Type mismatch in function call
  --> product.ail:42:15
```

### Cause

New version of the application introduces changes that are incompatible with existing data or calling code.

### Resolution

```bash
# Step 1: Roll back the application code
# Restore previous .ail files from backup

# Step 2: Restore data from backup (if migration was attempted)
# See Scenario 3

# Step 3: Read the upgrade notes carefully
# Check for:
#   - Changed function signatures
#   - New required parameters
#   - Renamed functions or modules
#   - Data format changes

# Step 4: Attempt upgrade again after understanding changes
```

### Prevention

```bash
# Always backup before upgrade
ail run main.ail backup

# Read release notes before upgrading
cat CHANGELOG.md | head -100

# Test in a separate directory first
mkdir ~/test-upgrade
cp -r ~/ailang-inventory/* ~/test-upgrade/
# Perform upgrade in test-upgrade/
# Verify it works before touching production
```

---

## Scenario 7: Slow Performance

### Symptom

```
$ ail run main.ail report
# Takes more than 5 seconds to return
```

### Cause

- Large data volume (thousands of records)
- Recursion overhead in list operations
- Many nested function calls

### Resolution

```bash
# Step 1: Check data volume
wc -l data/*.json
# If any file has >10,000 records, performance may degrade

# Step 2: Check which operation is slow
# Time individual commands
time ail run main.ail report
time ail run main.ail dashboard

# Step 3: If report is slow, data volume is likely the cause
# AILang is designed for ≤2,000 LOC modules with reasonable data volumes

# Step 4: For large datasets, use CSV export and analyze externally
ail run main.ail csv > data-export.csv
# Analyze in Excel, Python, or another tool
```

### Prevention

- Keep record counts under 10,000 per collection for responsive CLI use
- Export and archive old records periodically
- Split very large inventories into separate systems

---

## Scenario 8: Disk Full

### Symptom

```
Error: [Errno 28] No space left on device
```

or

```
ail run main.ail backup fails silently
```

### Cause

The `data/` and `backups/` directories have grown too large.

### Resolution

```bash
# Step 1: Check disk usage
du -sh ~/ailang-inventory/data/
du -sh ~/ailang-inventory/backups/

# Step 2: Clean old backups (keep most recent 5)
ls backups/
rm -rf backups/<oldest-timestamp>

# Step 3: If data/ is large (>100MB), consider archiving
# Export to CSV and archive
ail run main.ail csv > exports/archive-$(date +%s).csv
# Then clear old data and start fresh
```

### Prevention

```bash
# Set a backup retention policy:
# Keep only last 10 manual backups
# Auto-backups are limited to 50 per collection
# Review disk usage monthly
du -sh ~/ailang-inventory/
```

---

## Scenario 9: Impossible Operation

### Symptom

```
You realize the system cannot do what you need.
```

### Common Gaps and Workarounds

#### The system has no GUI
```
┌─ Workaround: Use CSV export and import to/from spreadsheet software
│
└─ ail run main.ail csv  →  open in Excel  →  edit  →  save as CSV  →  import
```

#### The system has no web interface
```
┌─ Workaround: The CLI is the interface. All operations are single-command.
│
└─ Multi-user access is not supported. This is a single-user system.
```

#### The system has no SQL database
```
┌─ Workaround: JSON files are the database. They are human-readable and
│  can be edited with any text editor.
│
└─ For large-scale data (>100K records), export to SQLite or PostgreSQL.
```

#### The system has no reports beyond summary
```
┌─ Workaround: Export data as CSV and generate reports in Excel,
│  Google Sheets, or Python.
│
└─ ail run main.ail csv  →  products.csv, customers.csv, movements.csv
```

---

## Scenario 10: Everything Fails

### Symptom

Multiple errors, data corruption, user cannot operate.

### Nuclear Option

```bash
# Step 1: Preserve evidence
cp -r data data-crash-$(date +%s)

# Step 2: Start completely fresh
rm -rf data/
mkdir data
cp -r backups/<latest>/* data/

# Step 3: If no backup exists, re-seed
ail run main.ail init

# Step 4: Reinstall if needed
pip install -e .  # from repo root

# Step 5: Verify basic operation
ail run main.ail report
```

### When to Call for Help

```
If none of the above resolves the issue,
or if data loss is unacceptable:

Contact: <maintainer-email>
Include:
  - What you were doing when the error occurred
  - The exact error message (screenshot or copy-paste)
  - The contents of data/ directory listing
  - AILang version (ail --version)
```

---

## Quick Reference: Error Messages

| Error Message | Most Likely Cause | See Scenario |
|:--------------|:------------------|:-------------|
| `command not found: ail` | AILang not installed | #1 |
| `No module named 'compiler'` | AILang not installed or wrong Python | #1 |
| `SEM002: Undefined identifier` | Typo in variable/function name | #2 |
| `Warning: ... corrupted. Attempting auto-backup` | JSON file corrupted | #4 |
| `Error: Invalid password` | Wrong credentials | #5 |
| `Error: Another session is running` | Concurrent access / lock file | #5a |
| `Error: File not found: imports/*.csv` | Missing import file | #5b |
| `Error: File is empty: imports/*.csv` | Empty import file | #5b |
| `[WARN] ... references non-existent ...` | Integrity check warning | #5c |
| `[WARN] ... has negative stock balance` | Integrity check warning | #5c |
| `TYP001: Type mismatch` | Incompatible upgrade | #6 |
| `[Errno 28] No space left` | Disk full | #8 |
| `ail run main.ail ... (hangs)` | Large data volume | #7 |
| `RecursionError` | Recursion depth exceeded | See known limitations |
| `Error: Not logged in` | No active session | Login required |
| `Error: Insufficient permissions` | Wrong role for command | Login as admin |

---

## Maintenance Schedule

| Frequency | Task | Duration |
|:----------|:-----|:---------|
| Daily | Backup data | 30 sec |
| Daily | Run report check | 10 sec |
| Weekly | Clean old backups (> 10) | 30 sec |
| Weekly | Export all data as CSV | 1 min |
| Monthly | Verify disk space | 30 sec |
| Monthly | Run test suite | 2 min |
| Per upgrade | Full backup + verify | 5 min |

---

## Monitoring Checklist

```
Daily:
□ ail run main.ail dashboard     — Check for anomalies
□ ail run main.ail backup        — Ensure data safe
□ ail run main.ail check         — Run integrity check

Weekly:
□ python test_compile.py         — Verify system integrity
□ ail run main.ail backups       — Check backup count (< 10)
□ dir /s data\                   — Check data directory size

Monthly:
□ ail build main.ail             — Check for compile errors
□ Review runbook scenarios       — Familiarity check
□ Review config/users.json       — Audit user accounts
```
