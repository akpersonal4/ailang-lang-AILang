# Contributor Guide

## Welcome

Thank you for your interest in contributing to AILang! This guide explains how to set up your environment, understand the development workflow, and submit high-quality contributions.

## Project Constitution

All contributions must follow the [Project Constitution](PROJECT_CONSTITUTION.md). Key rules:

- **Specification first** — any new feature must begin with a specification
- **TDD mandatory** — write tests before implementation
- **Deterministic behaviour** — never introduce non-determinism
- **No breaking changes without ADR** — architectural decisions require documentation
- **All code tested** — every line of new code must have tests
- **All PRs pass quality gates** — pytest, black, ruff, mypy must all pass

## Setting Up the Development Environment

```bash
# Clone the repository
git clone https://github.com/anomalyco/ailang.git
cd ailang

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install in development mode with all tools
pip install -e .
pip install pytest black ruff mypy
```

## Development Workflow

### 1. Understand the Architecture

Read [COMPILER_ARCHITECTURE.md](COMPILER_ARCHITECTURE.md) to understand the pipeline stages and how they connect.

### 2. Choose an Area

Common areas for contribution:
- **New standard library modules** — add `.ail` wrappers and Python builtins
- **Compiler optimizations** — improve the IR or add optimizer passes
- **Test coverage** — add tests for edge cases
- **Documentation** — improve guides, fix typos, add examples
- **Example programs** — add new `.ail` programs to `examples/`
- **Bug fixes** — see the issue tracker for verified defects

### 3. Write Tests First

All new code must be accompanied by tests. See [TESTING.md](TESTING.md) for the testing guide.

```bash
# Run existing tests to understand the patterns
python -m pytest tests/test_lexer.py -v
```

### 4. Implement

Follow the existing code style:
- Python: PEP 8 with 88-character line limit (black-formatted)
- AILang: see [LANGUAGE_TOUR.md](LANGUAGE_TOUR.md) for syntax conventions

### 5. Run Quality Gates

```bash
python -m pytest           # All tests must pass
black --check .            # No formatting issues
ruff check .               # No lint issues
mypy                       # No type issues
```

### 6. Submit a Pull Request

- Use a descriptive title and summary
- Reference related issues
- Ensure all CI checks pass
- Keep changes focused on a single concern

## Code Style

### Python (compiler code)

- Format with **black** (line length 88)
- Lint with **ruff**
- Type-check with **mypy** (strict mode)
- Follow PEP 8 naming conventions
- Use `__future__ import annotations` in all files

### AILang (examples, apps)

- Use 4-space indentation
- Place opening brace on the same line as the function/if header
- Semicolons at end of statements are optional
- One space before and after operators
- Define functions before they are called (no forward references)
- Use meaningful names for functions and variables

## Testing

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_lexer.py -v

# Run specific test
python -m pytest tests/test_lexer.py::test_lexer_integer -v

# Run with verbose output and no capture
python -m pytest -v -s

# Run benchmarks
python -m pytest tests/test_benchmark.py -v
```

See [TESTING.md](TESTING.md) for the complete testing guide.

## Adding a Standard Library Module

1. Implement the Python function(s) in `compiler/runtime/builtins.py`
2. Register them in the `BUILTINS` dictionary
3. Create `stdlib/modulename.ail` with thin wrappers
4. Add tests in `tests/test_stdlib_modulename.py`
5. Add documentation to `docs/STDLIB_REFERENCE.md`
6. Update the module table in `README.md`
7. Run all quality gates

## Adding an Example Program

1. Create `examples/program_name.ail`
2. Follow the [Getting Started](GETTING_STARTED.md) conventions
3. Ensure it has a `main()` function
4. Test it: `ail run examples/program_name.ail`

## Documentation

Write documentation in Markdown. Place docs in the `docs/` directory. Follow the existing style:
- Use `h1` (`#`) for document titles
- Use `h2` (`##`) for major sections
- Use `h3` (`###`) for subsections
- Use fenced code blocks with language tags
- Reference other docs with relative links

## Pull Request Checklist

Before submitting, verify:

- [ ] Tests pass (`python -m pytest`)
- [ ] Black passes (`black --check .`)
- [ ] Ruff passes (`ruff check .`)
- [ ] Mypy passes (`mypy`)
- [ ] New code has tests
- [ ] Documentation is updated (if applicable)
- [ ] No breaking changes without ADR
- [ ] Commit messages follow conventional commits

## Getting Help

- Open an issue on GitHub
- Check the [documentation index](INDEX.md)
- Read the canonical [Language Specification](../LANGUAGE_SPEC.md)
