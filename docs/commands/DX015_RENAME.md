# DX-015 — Repository Rename Tool (`ail rename`)

## Usage

```bash
ail rename <old_name> <new_name> [options]
```

## Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview changes without modifying files |
| `--diff` | Show unified diff of all changes |
| `--strings` | Also rename matching string literal values |
| `--no-verify` | Skip compiler verification after rename |

## Exit Codes

| Code | Meaning |
|:----:|---------|
| 0 | Rename completed and verified |
| 1 | Error during rename (rolled back) |
| 2 | No references found for old_name |
| 4 | Invalid new_name (not a valid identifier) |

## Examples

```bash
# Basic rename
ail rename supplier vendor_partner

# Preview
ail rename --dry-run supplier vendor_partner

# Preview with diff
ail rename --diff supplier vendor_partner

# Include string literals
ail rename --strings supplier vendor_partner

# Skip verification
ail rename --no-verify supplier vendor_partner
```

## Safety

- Every rename creates a rollback bundle in `.ail/rename/<timestamp>/`
- The bundle contains original (`.orig`) backups of all modified files
- If any write fails, all already-written files are restored automatically
- After rename, the compiler verifies the result via `ail build`
- If verification fails, exit code 3 is returned
