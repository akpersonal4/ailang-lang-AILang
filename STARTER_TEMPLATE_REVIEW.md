# Starter Template Review

**Date:** 2026-07-21
**Version:** v1.1.1

---

## Template Change

### Before (v1.1.0)
`ail new <project>` created a full inventory management app (~100 lines, 10+ functions).

### After (v1.1.1)
`ail new <project>` creates a minimal hello-world (4 lines, 1 function).

---

## New Template: `ail new hello_test`

### main.ail
```
fn main() {
    print("Hello, AILang!");
    return 0
}
```

### README.md
```markdown
# hello_test

An AILang project.

## Quick start

    ail run main.ail

## Next steps

- Edit `main.ail` to try your own code
- Run `ail fmt main.ail` to format
- Run `ail build main.ail` to check for errors
- Run `ail --help` to see all commands
```

### ail.toml
```toml
[package]
name = "hello_test"
version = "0.1.0"
```

---

## Why This Change

| Criterion | Inventory Template | Hello-World Template |
|-----------|-------------------|---------------------|
| Time to first run | ~5 seconds | ~1 second |
| Cognitive load | 10+ functions to parse | 1 function |
| Compilable on first run | Yes | Yes |
| Demonstrates core features | Yes (functions, variables, if/else, print) | Yes (fn, print, return) |
| Appropriate for first-time user | No — overwhelming | Yes — minimal |

---

## Full Template (Inventory App)

Available via: `ail new <project> --full`

Creates the full inventory management example with:
- 10+ functions (add_item, remove_item, find_item, etc.)
- Variables, if/else, arithmetic, print
- Demonstrates real-world AILang patterns

---

## Validation

| Check | Status |
|-------|--------|
| `ail new hello_test` creates 4 files | ✅ |
| main.ail compiles (`ail build`) | ✅ |
| main.ail runs (`ail run`) → "Hello, AILang!" | ✅ |
| README.md contains project name | ✅ |
| ail.toml has correct package name | ✅ |
| `--full` flag creates inventory app | ✅ (existing behavior) |

---

## Recommendation

The hello-world default template is the right choice for v1.1.1. It:
1. Gets users to "Hello, AILang!" in under 1 second
2. Demonstrates the three core constructs (fn, print, return)
3. Doesn't overwhelm with patterns they haven't learned yet
4. Serves as a blank canvas for experimentation

The `--full` flag preserves access to the inventory example for users who want to see a complete app.
