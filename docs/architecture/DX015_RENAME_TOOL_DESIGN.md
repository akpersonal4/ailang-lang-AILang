# DX-015 — Repository Rename Tool

**Status:** Design Proposal — v0.10.0 (M23)  
**Type:** P0 Developer Experience Tool  
**Requirement:** Benchmark B4–B6 identified rename/reorganize as the highest-AI-friction refactoring operation  

---

## 1. Problem

In the Inventory benchmark (B4), the AI needed to rename `supplier` → `vendor_partner` across 28 `.ail` files containing 4,009 LOC of AILang. The AI performed this rename by:

1. Reading every file to find `supplier` references
2. Replacing each occurrence one at a time
3. Introducing 3 errors (missed references) that required two additional compile–fix cycles
4. Total cost: 5 extra AI turns + 3 compile iterations

**Same operation in a typed language with a rename-refactoring tool:** 1 command, 0 errors, 0 extra turns.

**Goal:** `ail rename` performs a complete, safe, verifiable rename of a user-defined identifier across the entire repository in a single command. AI never needs to manually trace symbol references again.

---

## 2. Non-Goals

| Not in scope | Reason |
|-------------|--------|
| Rename across multiple repositories | Single-repo only. Cross-repo is an edge case with no current benchmarks |
| Rename within standard library | Stdlib is immutable to `ail rename`. User cannot break `list`, `map`, `string`, etc. |
| Interactive rename (`--ask`) | AI-driven workflow means batch rename with preview. Interactive mode is human-focused and adds UI complexity |
| Rename of map keys / string literals | Map keys are runtime strings, not identifiers. See §6 |
| Move / extract / inline refactoring | These are distinct refactoring operations. DX-015 is rename-only |
| IDE integration | The `ail` CLI is the integration point. VS Code/JetBrains extensions are future work |

---

## 3. CLI Specification

```
ail rename <old_name> <new_name> [options]
```

### Positional Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `old_name` | Current identifier to rename | `supplier` |
| `new_name` | New identifier | `vendor_partner` |

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--dry-run` | Show what would change without modifying files | `false` |
| `--diff` | Print unified diff of changes | `false` |
| `--no-verify` | Skip `ail build` verification after rename | `false` |
| `--verbose` | List every file and every occurrence processed | `false` |
| `--strings` | Also rename matching string literals (map keys, etc.) | `false` |

### Exit Codes

| Code | Meaning |
|:----:|---------|
| 0 | Rename completed and verified |
| 1 | Rename would be unsafe (ambiguous identifier, etc.) |
| 2 | Identifier not found in repo |
| 3 | Build verification failed after rename |
| 4 | Invalid new_name (not a valid AILang identifier) |

### Examples

```bash
# Quick rename with auto-verify
ail rename supplier vendor_partner

# Preview before applying
ail rename supplier vendor_partner --dry-run --diff

# Aggressive rename with string literal matching
ail rename supplier vendor_partner --strings

# Rename without build verification (for bulk operations)
ail rename supplier vendor_partner --no-verify
```

---

## 4. Symbol Graph Traversal

The rename tool builds a **repository-wide symbol graph** from parsed AILang source. This graph maps each identifier occurrence to its defining binding.

### Graph Structure

```
SymbolGraph:
  identifiers:           # All user-defined identifiers
    "supplier":
      - { file: "src/entities/supplier.ail", line: 12, kind: "function", name: "supplier" }
      - { file: "src/entities/supplier.ail", line: 34, kind: "parameter", name: "items" }  # NOT a reference
      - { file: "src/catalog/supplier_map.ail", line: 8, kind: "call", target: "supplier" }
      - { file: "src/catalog/supplier_map.ail", line: 22, kind: "string", value: "supplier_id" }  # only with --strings
    ...

  bindings:              # Mapping from definition site → occurrences
    "entities/supplier.ail:12":     # Function `supplier` definition
      - call: "catalog/supplier_map.ail:8"
      - call: "catalog/import.ail:15"
      - recur: "entities/supplier.ail:19"   # Recursive self-call
    ...
```

### Referenced Identifier Kinds

| Kind | Example | Include in rename? |
|------|---------|:------------------:|
| Function declaration | `fn supplier(...) { }` | Yes |
| Function call | `supplier(data)` | Yes |
| Variable/let binding | `let supplier_id = ...` | Yes |
| Variable reference | `process(supplier_id)` | Yes |
| Function parameter | `fn process(supplier) { }` | Yes |
| Import target | `import supplier_lib` | Yes (if import refers to user module) |
| Map key literal | `map.set(data, "supplier_id", val)` | Only with `--strings` |
| String literal | `let name = "supplier"` | Only with `--strings` |
| Comment | `// supplier helper` | Never |

### Graph Building Algorithm

```
build_symbol_graph(repo_root):
  files = find_all_ail_files(repo_root)
  for each file in files:
    parse(file) → AST
    traverse AST:
      if node is FunctionDeclaration:
        record_binding("function", node.name, file, node.span)
      elif node is CallExpression:
        record_reference("call", node.target, file, node.span)
      elif node is LetStatement:
        record_binding("variable", node.name, file, node.span)
      elif node is VariableReference:
        record_reference("varref", node.name, file, node.span)
      elif node is LiteralString and --strings:
        record_reference("string", match_identifier(node.value), file, node.span)
      ...

  return graph
```

### Identifier Resolution (No Shadowing)

AILang's no-shadowing rule makes symbol graph building deterministic:

1. Every identifier refers to exactly one binding site in its scope
2. No shadowing, no overloading, no forward references within a file
3. Import resolution uses the module system (fully qualified paths)
4. Uniqueness of variable names across functions means a rename is unambiguous

The resolver simply finds all occurrences of `old_name` across all binding kinds and reference kinds, collects them into a changeset, and applies the diff.

### Atomic File Rewriting

Each file modification is an atomic operation:

1. Read file into memory
2. Apply all replacements for this file (sorted by position descending to preserve offsets)
3. Write modified content to `.ail.rename.tmp`
4. Rename `.ail.rename.tmp` → `.ail` (atomic on same filesystem)
5. On failure of any single file: abort all changes, restore originals from backup

---

## 5. Operation Guarantees

### Safety Properties

| Property | Guarantee |
|----------|-----------|
| No silent truncation | Every file is either fully renamed or fully unchanged. No partial writes |
| No double-rename | The symbol graph is built before any file is modified. Renaming is done as a batch operation, not sequentially with overlapping passes |
| No identifier collision | `new_name` is verified to not collide with any existing identifier in scope. If collision is detected, `ail rename` exits with code 1 |
| No stdlib corruption | Stdlib identifiers (`list`, `map`, `string`, `fn`, `let`, `if`, `return`, `import`) are excluded from the search. Renaming `list` would error with "stdlib identifiers cannot be renamed" |
| No hidden corruptions | After rename, `ail build` runs on the full repository. If verification fails, the rename is not committed to disk |

### Identifier Validity Check

`new_name` must satisfy the AILang identifier grammar:

```ebnf
identifier = letter, { letter | digit | "_" } ;
letter = "a" | ... | "z" | "A" | ... | "Z" ;
```

Additional checks:
- Must not be a keyword (`fn`, `let`, `if`, `return`, `import`, `for`, `in`)
- Must not be a stdlib module name (`list`, `map`, `string`, `int`)
- Must not start with `__` (reserved for compiler use)

---

## 6. Rollback Strategy

### Automatic Rollback File

Before modifying any file, `ail rename` creates a **rollback bundle** at:

```
.ail/rename/<timestamp>/
  manifest.json          # Metadata: old_name, new_name, start_time, files_changed
  backups/
    src/entities/supplier.ail.orig
    src/catalog/supplier_map.ail.orig
    ...
  diff/
    rename.diff           # Unified diff format for manual inspection
```

### Rollback Bundle Contents

`manifest.json`:
```json
{
  "command": "ail rename supplier vendor_partner",
  "old_name": "supplier",
  "new_name": "vendor_partner",
  "timestamp": "2026-07-10T14:30:00Z",
  "status": "succeeded",
  "verification": "passed",
  "files_modified": [
    "src/entities/supplier.ail",
    "src/catalog/supplier_map.ail",
    "src/catalog/import.ail"
  ]
}
```

### Undo Command

```bash
ail rename --undo .ail/rename/20260710T143000/
```

The undo command:
1. Reads the manifest to determine which files were changed
2. Restores each `.orig` backup over the modified file
3. Removes the rollback directory

### Restore Strategy

| Failure Mode | Restore Action |
|-------------|---------------|
| Build verification fails after rename | Automatic restore from `.orig` backups |
| Rename tool crashes mid-operation | On restart, `.ail/rename/<timestamp>/manifest.json` is checked. If `status` is `pending`, the bundle is restored on next `ail rename` startup |
| File I/O error during write | Roll back all files already written. Abort with error message |
| User rejects rename after preview | No files modified. No action needed |

### Rollback Guarantees

- The rollback bundle is created **before** any source file is modified
- Source files are safe because `.orig` backups are written atomically (same filesystem, same directory)
- No data loss: the `.orig` files contain the pre-rename content
- The rollback directory is in `.ail/rename/` which is gitignored (see DX-012)

---

## 7. Integration with Git

### Git-Aware Mode

When the repository is a Git working tree (always the case for AILang), `ail rename` provides additional safety:

1. **Before rename:** `git stash` any uncommitted changes? No — that would disrupt the user's workflow. Instead, `ail rename` works on the working tree files directly, and Git tracks the changes naturally.

2. **After rename:** The changes appear as unstaged modifications in `git status`. The user can review with `git diff` and commit with `git add` + `git commit`.

3. **Commit suggestion:** `ail rename` prints the suggested commit command:

```
--- Rename complete ---
Files modified: 3
Verification: PASSED
Suggested commit:
  git add -A && git commit -m "refactor: rename supplier -> vendor_partner"
```

### Authoritative Source

The working tree is the authoritative source. `ail rename` reads from and writes to working tree files. Git is the version control layer on top — `ail rename` does not call Git directly but is compatible with any VCS.

---

## 8. Benchmark Impact Estimate

### Time Savings

| Operation | Current (Manual) | With `ail rename` |
|-----------|:----------------:|:-----------------:|
| Simple rename (1 file, 5 references) | 2 minutes | <1 second |
| Cross-file rename (3 files, 15 refs) | 8 minutes | <2 seconds |
| Inventory-scale rename (28 files, 200+ refs) | 25 minutes | <5 seconds |
| Extra compile cycles from missed refs | 2–3 cycles | **Eliminated** |
| AI turns for rename (B4) | 5 extra turns | **Eliminated** |

### Risk and Mitigation

| Risk | Severity | Mitigation |
|------|:--------:|------------|
| Symbol graph misses a reference | Medium | Build verification catches it. Add test coverage for rare patterns |
| String literal false positive (--strings) | Low | Default is off. User must opt in with `--strings` |
| New identifier matches existing function | Low | Pre-verification check. Exit with code 1 if collision detected |
| Rename breaks an import path | Medium | Import path renaming is handled separately (see §10 Rejected) |
| Large repo performance | Low | Symbol graph is built in a single pass. File writes are batched |

---

## 9. Implementation Plan

### Phase 1: Core Engine

| Component | Description | LOC |
|-----------|-------------|:---:|
| Symbol graph builder | Parse all `.ail` files, collect binding/reference map | ~150 |
| Identifier resolution | Match `old_name` against all references | ~50 |
| Diff generator | Compute unified diff for preview | ~80 |
| File rewriter | Atomic file modification with offset-safe rewriting | ~100 |
| Rollback manager | Create/restore `.orig` backup bundles | ~80 |

### Phase 2: CLI

| Component | Description | LOC |
|-----------|-------------|:---:|
| Argument parser | `argparse` for subcommand + options | ~60 |
| Output formatter | Dry-run display, diff output, progress | ~80 |
| Verification runner | Invoke `ail build` on the repo subprocess | ~40 |

### Phase 3: Safety

| Component | Description | LOC |
|-----------|-------------|:---:|
| Name validation | Valid identifier check, keyword/stdlib exclusion | ~40 |
| Collision detection | Verify `new_name` doesn't shadow existing | ~30 |
| Integrity check | Verify all files parsed before rename | ~20 |

### Estimated Total: ~730 LOC (Phase 1–3)

### Testing Strategy

| Test type | Coverage |
|-----------|----------|
| Unit: symbol graph builder | Function, variable, parameter, call, import references |
| Unit: file rewriter | Single-file, multi-file, overlapping replacements |
| Unit: rollback manager | Backup creation, restore, crash recovery |
| Integration: full rename | Rename function, variable, parameter across 3+ files |
| Integration: safety checks | Collision detection, invalid name, stdlib protection |
| Integration: `--dry-run` | Verify no files modified in preview mode |
| Integration: `--strings` | String literal matching and replacement |
| Benchmark: Inventory rename | Time `ail rename supplier vendor_partner` end-to-end |

---

## 10. Rejected Alternatives

| Alternative | Reason |
|-------------|--------|
| sed-based rename | `sed -i 's/supplier/vendor_partner/g'` would rename partial matches (`suppliers` → `vendor_partners`), string values, and comments. Unsafe |
| AST-based rename (modify CST, regenerate) | Regenerating source from CST loses formatting. AILang code is hand-readable. Text-based rename preserves formatting |
| LSP rename request | LSP would require a running language server. The CLI tool must work without a daemon |
| Symbol file (`.ail_symbols`) | Writing a persistent symbol file adds sync complexity. Building the symbol graph on-the-fly is fast enough for rename operations |
| Cross-module rename for stdlib | Stdlib is shared code. Renaming `list.append` to `list.add` would break every repository. Stdlib immutability is a safety invariant |

---

## 11. Decision

**Verdict:** ACCEPT.

`ail rename` solves a measured, benchmark-identified AI-friction point: multi-file identifier rename produces 3+ errors per operation and costs 5+ AI turns. A dedicated rename tool eliminates:

- All missed reference errors (build verification catches them)
- 5+ extra AI turns per rename operation
- 25 minutes of developer time for Inventory-scale renames
- 2–3 additional compile–fix cycles

The implementation is self-contained (~730 LOC), does not modify the compiler pipeline, and provides automatic rollback. The `--dry-run` and `--diff` flags give the AI a preview mechanism for verification before applying destructive changes to the repository.
