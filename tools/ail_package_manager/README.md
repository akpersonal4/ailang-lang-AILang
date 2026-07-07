# AILang Package Manager

Dependency management for AILang projects.

## Commands

| Command | Description | Status |
|---------|-------------|--------|
| `ail init` | Initialize a new AILang project | ✅ |
| `ail add` | Add a dependency | 📋 |
| `ail remove` | Remove a dependency | 📋 |
| `ail install` | Install all dependencies | ✅ |
| `ail update` | Update dependencies | 📋 |
| `ail list` | List installed dependencies | 📋 |

## Project Manifest (`ail.toml`)

```toml
[project]
name = "my-package"
version = "1.0.0"
description = "A short description"
entry = "src/main.ail"

[language]
version = "0.3"

[dependencies]
string-utils = ">=1.0.0"
local-lib = { path = "../shared-lib" }
my-lib = { git = "https://github.com/user/my-lib.git", tag = "v1.0.0" }
```

## Features

### Local Package Support
Dependencies from local paths are resolved and copied to `lib/<name>/`:
```toml
[dependencies]
my-lib = { path = "../my-lib" }
```

### Git Package Support
Dependencies from Git repositories are shallow-cloned and installed:
```toml
[dependencies]
my-lib = { git = "https://github.com/user/my-lib.git", tag = "v1.0.0" }
```

### Lock File
The `ail.lock` file records the exact resolved dependency tree for reproducible builds:
```toml
input_hash = "sha256-<hash of [dependencies]>"

[[packages]]
name = "my-lib"
version = "1.0.0"
source = "local"
checksum = "sha256-<hex>"
dependencies = []
```

## Exit Codes

| Code | Meaning |
|:----:|---------|
| 0 | Success |
| 1 | Operation failed (resolution, download, checksum mismatch) |
| 3 | Internal error (invalid args, missing manifest, I/O error) |
