# Formatter

AILang includes a deterministic source code formatter. One style only — no configuration.

```bash
# Format a file in-place
ail fmt hello.ail

# Check if a file is formatted (exit 0 = yes, 1 = no)
ail fmt --check hello.ail

# Read from stdin, write formatted to stdout
cat hello.ail | ail fmt --stdin
```

## Formatting rules

- **4-space indentation**
- **Opening brace on same line** (`fn foo() {`, `if (cond) {`)
- **`} else {` on one line**
- **Spaces around all binary operators** (`a + b`, `x == y`, `a && b`)
- **Space after `,`** in parameter/argument lists
- **Single blank line between function declarations**
- **Trailing whitespace removed**
- **Newline at EOF**
- **Comments preserved** — inline and standalone comments are retained

Formatting is idempotent: formatting an already-formatted file produces no changes.
