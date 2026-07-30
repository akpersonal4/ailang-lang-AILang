# Package Author Guide

## 1. Overview

AILang packages allow you to organize and distribute reusable code. This guide explains how to create, version, and maintain AILang packages.

## 2. Project Structure

### Basic Package

```
my_package/
├── main.ail           # Entry point (optional for libraries)
├── ail.toml           # Package manifest
├── README.md          # Documentation
├── LICENSE            # License file
├── src/               # Source modules
│   ├── core.ail
│   └── utils.ail
└── tests/             # Test files
    ├── test_core.ail
    └── test_utils.ail
```

### Library Package (No Entry Point)

```
my_library/
├── ail.toml           # Package manifest
├── lib.ail            # Main module (imported by others)
├── README.md
├── LICENSE
└── tests/
    └── test_lib.ail
```

## 3. Package Manifest (ail.toml)

The `ail.toml` file defines your package metadata:

```toml
[project]
name = "my_library"
version = "0.1.0"
description = "A utility library for AILang"
entry = "lib.ail"

[language]
version = "0.3"
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `project.name` | Yes | Package name (snake_case) |
| `project.version` | Yes | Semantic version (x.y.z) |
| `project.description` | Yes | Short description |
| `project.entry` | No | Entry point file (for applications) |
| `language.version` | Yes | Minimum AILang language version |

## 4. Versioning

### Semantic Versioning

AILang follows [Semantic Versioning 2.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

| Change Type | Bump | Example |
|-------------|------|---------|
| Breaking change | MAJOR | 1.0.0 → 2.0.0 |
| New feature (backward compatible) | MINOR | 1.0.0 → 1.1.0 |
| Bug fix (backward compatible) | PATCH | 1.0.0 → 1.0.1 |

### Version Compatibility

- **MAJOR 0.x**: Initial development — breaking changes may occur
- **MAJOR 1.x**: Stable — breaking changes require MAJOR bump

## 5. Dependencies

### Adding Dependencies

```text
ail add my_library
ail add my_library --version 0.2.0
```

### Specifying Version Ranges

```toml
[project]
name = "my_app"
version = "1.0.0"

[dependencies]
my_library = "0.2.0"
std_lib = "*"
```

### Lock File (ail.lock)

The `ail.lock` file is auto-generated. Do not edit it manually:

```text
# ail.lock — Auto-generated. Do not edit manually.
```

It ensures reproducible builds by pinning exact dependency versions.

## 6. Publishing

### Prerequisites

1. Package has a complete `ail.toml`
2. Version is updated (follow semver)
3. All tests pass: `ail test`
4. README and LICENSE are present

### Publishing Steps

```text
# Build the package
ail build main.ail

# Run tests
ail test

# Publish to registry
ail publish --registry <registry_url>
```

### Local Publishing

```text
# Publish to local directory
ail publish --registry file://./registry/
```

## 7. Creating Public APIs

### Exported Functions

Define functions that users of your package will call:

```text
// lib.ail — Public API

// Add two numbers and return the result
fn add(a, b) {
    return math.add(a, b)
}

// Subtract b from a
fn subtract(a, b) {
    return math.sub(a, b)
}
```

### Internal (Private) Functions

Prefix internal functions with an underscore:

```text
// _internal.ail — Internal helpers (not part of public API)

fn _validate_input(value) {
    if (value < 0) {
        return false
    }
    return true
}
```

## 8. Documentation

Every public function should have:

1. A comment describing its purpose
2. Parameter descriptions
3. Return value description

```text
// Calculate the total price including tax
// Parameters:
//   price     - The base price (number)
//   tax_rate  - The tax rate as a decimal (number)
// Returns:
//   The total price including tax
fn calculate_total(price, tax_rate) {
    let tax = math.mul(price, tax_rate);
    return math.add(price, tax)
}
```

## 9. Testing

### Test Files

Name test files with `test_` prefix:

```
tests/test_core.ail
tests/test_utils.ail
```

### Test Structure

```text
// tests/test_core.ail
import lib;

fn test_add_positive() {
    let result = lib.add(2, 3);
    if (result != 5) {
        print("FAIL: add(2, 3) expected 5, got " + convert.to_string(result));
    }
}

fn test_add_negative() {
    let result = lib.add(-2, -3);
    if (result != -5) {
        print("FAIL: add(-2, -3) expected -5, got " + convert.to_string(result));
    }
}

fn main() {
    test_add_positive();
    test_add_negative();
    print("ALL TESTS PASSED");
    return 0
}
```

### Running Tests

```text
# From package root
ail test

# Run specific test file
ail test tests/test_core.ail

# Run with verbose output
ail test --verbose
```

## 10. Best Practices

### Do

- Follow semantic versioning strictly
- Document all public functions
- Include tests for all public APIs
- Run `ail test` before every release
- Use `ail fmt` before committing
- Keep backward compatibility within MAJOR version

### Don't

- Change public API signatures without MAJOR version bump
- Remove exported functions without deprecation notice
- Add dependencies unnecessarily
- Ignore test failures before release
- Edit `ail.lock` manually

## 11. Example Package

### Complete Example

```
example_lib/
├── ail.toml
├── lib.ail
├── README.md
├── LICENSE
└── tests/
    └── test_lib.ail
```

### ail.toml

```toml
[project]
name = "example_lib"
version = "0.1.0"
description = "Example library package"

[language]
version = "0.3"
```

### lib.ail

```text
// Example Library
// Provides string utility functions

import string;

// Reverse a string
fn reverse(input) {
    return string.reverse(input)
}

// Count occurrences of a substring
fn count_occurrences(text, pattern) {
    return string.count(text, pattern)
}

fn make_greeting(name) {
    return string.concat("Hello, ", name)
}