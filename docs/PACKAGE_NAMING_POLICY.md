# Package Naming Policy

| Attribute | Value |
|-----------|-------|
| **Status** | Approved |
| **Decision** | snake_case package names |
| **ADR** | Implicit (ADR-013) |
| **Date** | 2026-07-13 |

---

## Decision

Package names **must** use **snake_case**: lowercase letters, digits, and underscores, starting with a letter.

```
✅  my_package
✅  string_utils
✅  math_utils_v2
✅  json_parser

❌  my-package      (kebab-case — deprecated, migrated automatically)
❌  My_Package      (uppercase)
❌  1package        (starts with digit)
❌  my.package      (special characters)
```

---

## Rationale

AILang's lexer defines identifiers as `[a-zA-Z_][a-zA-Z0-9_]*`. Hyphens (`-`) are tokenized as the minus operator, making `import my-package` a parse error.

Package names must be importable. Therefore package names must be valid AILang identifiers.

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **A) snake_case** | Matches AILang identifiers, zero parser changes, widely used (Python, Rust) | Less visually distinct from function names | **Selected** |
| B) kebab-case with import alias | Matches npm/Go conventions | Requires new import syntax (`import "my-pkg" as ...`), parser change, two naming systems | Rejected |
| C) package name ≠ import name | Maximum flexibility | Confusing — same name means different things in different contexts | Rejected |

---

## Validation

| Field | Regex | Example |
|-------|-------|---------|
| Package name | `^[a-z][a-z0-9_]*$` | `my_package` |
| Max length | 64 characters | — |

Enforced by:
- `tools/ail_package_manager/manifest.py:validate_package_name()`
- `ail_platform/manifest.py:_SNAKE_CASE_RE`

---

## Migration (kebab-case)

Kebab-case names in existing `ail.toml` files are **accepted with a deprecation warning**:

```
Warning: package name 'my-package' uses kebab-case which is deprecated.
Use snake_case instead (e.g. 'my_package'.).
```

The module resolver normalizes kebab-to-underscore when looking up packages in `lib/`, so existing kebab-case directories continue to resolve.

### Migration steps

1. Open `ail.toml`
2. Replace `"name = "my-package""` with `"name = "my_package""`
3. Rename `lib/my-package/` to `lib/my_package/` (optional — resolver handles both)

---

## Examples

```toml
[project]
name = "my_package"
version = "1.0.0"
```

```toml
[dependencies]
"string_utils" = "1.0.0"
"math_helpers" = { path = "../math_helpers" }
"http_client" = { git = "https://github.com/example/client.git", tag = "v2.0.0" }
```
