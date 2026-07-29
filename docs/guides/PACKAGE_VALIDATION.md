# Package Validation

## Validation Lifecycle

Package validation occurs at multiple points during the package management workflow:

```
ail init         → validates project name and version before creating ail.toml
ail add          → validates dependency name and manifest existence
ail remove       → validates manifest existence
ail install      → validates manifest, then resolves and validates dependencies
ail update       → validates manifest existence and package name
ail list         → validates manifest and parses it
ail publish      → validates project structure before packaging
```

Each validation step produces a structured diagnostic.

## Diagnostic Format

All validation errors use the `PackageError` class with a deterministic format:

```
Package Validation Error

Reason:
  <what went wrong>

Manifest:
  <path to ail.toml>

Location:
  <which field or section>

Detail:
  <additional context>

Suggestion:
  <how to fix it>
```

Sections that have no content are omitted. The output is deterministic — no Python tracebacks, no implementation details, no non-deterministic content.

## Common Validation Failures

### Missing ail.toml

```
Package Validation Error

Reason:
  No ail.toml found in project root.

Suggestion:
  Run 'ail new <project>' to create a new project, or ensure ail.toml exists in the current directory.
```

### Missing [project] Section

```
Package Validation Error

Reason (1):
  Missing [project] section.

Suggestion:
  Add a [project] section with name and version. Example:

  [project]
  name = "my_project"
  version = "0.1.0"

Manifest: ail.toml
```

### Missing [project].name

```
Package Validation Error

Reason:
  Missing or empty [project].name.

Suggestion:
  Set a package name. Example:
  name = "my_project"

Manifest: ail.toml
Location: [project].name
```

### Invalid Package Name

```
Package Validation Error

Reason:
  Invalid package name: 'My-Package'. Must be snake_case: start with a lowercase letter, lowercase alphanumeric + underscores, max 64 characters.

Suggestion:
  Use snake_case: start with a lowercase letter, followed by lowercase letters, digits, or underscores.

Manifest: ail.toml
Location: [project].name
```

### Invalid Version

```
Package Validation Error

Reason:
  Invalid version: 'abc'. Must be MAJOR.MINOR.PATCH (e.g. 1.0.0).

Suggestion:
  Use MAJOR.MINOR.PATCH format (e.g. 1.0.0). Example:
  version = "0.1.0"

Manifest: ail.toml
Location: [project].version
```

### Invalid [project].authors

```
Package Validation Error

Reason:
  Invalid type for [project].authors: expected a list, got str.

Suggestion:
  Use a list of strings. Example:
  authors = ["Alice <alice@example.com>"]

Manifest: ail.toml
Location: [project].authors
```

### Invalid [project].description

```
Package Validation Error

Reason:
  Invalid type for [project].description: expected string, got int.

Suggestion:
  Set description to a string value. Example:
  description = "My AILang project"

Manifest: ail.toml
Location: [project].description
```

### Entry File Warning

```
Warning: entry file not found: main.ail (update [project].entry or create the file)
```

This is a warning, not an error. The manifest is still valid; the project will run but the entry point won't be found at execution time.

### Missing Dependency Path

```
Package Validation Error

Reason:
  Dependency 'my_lib' has no path specified.

Suggestion:
  Add a path field to the dependency in ail.toml. Example:
  { path = "../my_lib" }

Location: dependencies.my_lib
```

### Local Dependency Not Found

```
Package Validation Error

Reason:
  Local dependency path not found: /project/lib/my_lib

Suggestion:
  Ensure the path exists, or update the dependency path for 'my_lib' in ail.toml.

Location: dependencies.my_lib
```

### Git Clone Failure

```
Package Validation Error

Reason:
  Git clone failed for https://github.com/user/repo.git: ...

Suggestion:
  Check that the repository URL is correct and accessible. For private repositories, ensure you have the right credentials.

Location: dependencies.my_lib
```

### Git Clone Timeout

```
Package Validation Error

Reason:
  Git clone timed out for https://github.com/user/repo.git

Suggestion:
  Check your network connection. For large repositories, consider using a local path dependency instead.

Location: dependencies.my_lib
```

### Missing Manifest in Local Dependency

```
Package Validation Error

Reason:
  No ail.toml found in local dependency: /project/lib/my_lib

Suggestion:
  Each local dependency must be a valid AILang project with an ail.toml file.

Location: dependencies.my_lib
```

## Exit Codes

| Code | Constant | Meaning |
|:----:|----------|---------|
| 0 | `SUCCESS` | Operation completed successfully |
| 1 | `FAILURE` / `RESOLUTION_FAILURE` | Generic failure or resolution failure |
| 2 | `CIRCULAR_DEPENDENCY` | Circular dependency detected |
| 3 | `INVALID_MANIFEST` | Manifest file is missing or invalid |
| 4 | `LOCKFILE_MISMATCH` | Lock file is stale |
| 5 | `GIT_CLONE_FAILURE` | Git clone failed |
| 10 | `MANIFEST_NOT_FOUND` | No ail.toml found in project root |
| 11 | `INVALID_PACKAGE_NAME` | Package name fails validation |
| 12 | `INVALID_VERSION` | Version string fails validation |
| 13 | `INVALID_ENTRY` | Entry file is invalid |
| 14 | `INVALID_DEPENDENCY` | Dependency specification is invalid |

## Troubleshooting

### "Manifest validation failed" with multiple errors

The validator collects all errors before reporting. Fix each listed issue:

1. Check that `[project]` section exists
2. Ensure `name` and `version` are present and valid
3. Check `[dependencies]` section for valid names and formats
4. Ensure `[language]` is a table, not a string or list

### "No ail.toml found"

The package manager looks for `ail.toml` in the current directory. Make sure you are in the project root directory.

### "Exit code 10" vs "Exit code 3"

- **Exit code 10** (`MANIFEST_NOT_FOUND`): The `ail.toml` file does not exist at all.
- **Exit code 3** (`INVALID_MANIFEST`): The `ail.toml` file exists but has validation errors.

## Reference

- `PackageError` class: `tools/ail_package_manager/errors.py`
- Manifest parser and validator: `tools/ail_package_manager/manifest.py`
- Exit code definitions: `ail_platform/report_schema.py`
