# Testing Guide

## Overview

AILang uses pytest for all testing. Tests are located in the `tests/` directory and cover every component of the compiler pipeline, standard library modules, examples, and application programs.

## Running Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run a specific test file
python -m pytest tests/test_lexer.py

# Run a specific test
python -m pytest tests/test_lexer.py::test_lexer_integer

# Run tests matching a keyword
python -m pytest -k "json"

# Run with live stdout (no capture)
python -m pytest -v -s

# Run with timeout guard
python -m pytest --timeout=60

# Run tests excluding slow stress tests
python -m pytest --ignore=tests/test_stress.py --ignore=tests/test_benchmark.py
```

## Test Organization

```
tests/
├── test_lexer.py                  # Lexer unit tests
├── test_parser.py                 # Parser unit tests
├── test_ast_builder.py            # CST → AST conversion
├ test_ir_builder.py               # AST → IR conversion
├── test_semantic.py               # Semantic analysis
├── test_type_checker.py           # Type checking
├── test_runtime.py                # Runtime interpreter
├── test_session.py                # Compilation session
├── test_source.py                 # Source model
├── test_diagnostics.py            # Error reporting
├── test_member_access.py          # Member access expressions
├── test_imports.py                # Import resolution
├── test_module_resolution.py      # Module path resolution
├── test_module_integration.py     # Multi-module compilation
├── test_cli.py                    # CLI integration tests
├── test_validation.py             # Validation examples
├── test_validation_comprehensive.py # Comprehensive validation
├── test_benchmark.py              # Compile/runtime/memory benchmarks
├── test_stress.py                 # Stress tests (large programs)
├── test_ai_validation.py          # AI-generated program tests
├── test_stdlib_collections.py     # List/map/set/array tests
├── test_stdlib_csv.py             # CSV module tests
├── test_stdlib_environment.py     # Environment module tests
├── test_stdlib_file.py            # File module tests
├── test_stdlib_json.py            # JSON module tests
├── test_stdlib_path.py            # Path module tests
├── test_stdlib_random.py          # Random module tests
└── test_stdlib_time.py            # Time module tests
```

## Test Patterns

### Unit Test Pattern

Tests use pytest's standard assert style:

```python
def test_function_name() -> None:
    """Description of what is being tested."""
    result = function_under_test(args)
    assert result == expected_value
```

### Compiler Pipeline Test Pattern

Tests that compile and run AILang programs use the `_compile_and_run` helper:

```python
from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.interpreter import Runtime

def _compile_and_run(source: str) -> int:
    """Compile and run an AILang program, return main() result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        session = CompilationSession()
        session._root = repo_root
        session._resolver = type(session._resolver)(repo_root)
        session.discover(main_file)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        assert reporter.error_count == 0

        bundle = session.build_ir()
        runtime = Runtime(bundle)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        entry_module = next(
            name for name in bundle.module_irs if name.endswith("main")
        )
        return int(runtime.execute(bundle.module_irs[entry_module]))
```

### Determinism Test Pattern

```python
def test_deterministic() -> None:
    """Program produces same result across 5 runs."""
    results = []
    for _ in range(5):
        results.append(_compile_and_run(source))
    for r in results:
        assert r == expected
```

### Benchmark Test Pattern

```python
def test_compile_time() -> None:
    """Measure compile time with perf_counter."""
    start = time.perf_counter()
    session = _compile_ail_source(source, repo_root)
    elapsed = time.perf_counter() - start
    assert elapsed < threshold
```

### Memory Test Pattern

```python
def test_memory_usage() -> None:
    """Measure peak memory with tracemalloc."""
    tracemalloc.start()
    try:
        _compile_ail_source(source, repo_root)
        _current, peak = tracemalloc.get_traced_memory()
        peak_mb = peak / (1024 * 1024)
        assert peak_mb < threshold_mb
    finally:
        tracemalloc.stop()
```

## Writing New Tests

### For a New Language Feature

1. Add unit tests for the specific component (lexer, parser, AST, semantic)
2. Add a validation test in `test_validation.py` or `test_validation_comprehensive.py`
3. Ensure edge cases are covered (empty inputs, extreme values, error paths)

### For a New Stdlib Module

1. Create `tests/test_stdlib_modulename.py`
2. Test each function with valid and invalid inputs
3. Add a round-trip test (parse → stringify → parse)
4. Add integration tests with file I/O if applicable
5. Add CLI test to `test_cli.py`

### For a Bug Fix

1. First write a test that reproduces the bug
2. Verify the test fails
3. Fix the bug
4. Verify the test passes
5. Add the test to the regression tests section

## Test Data

- Inline source strings are preferred over external fixture files
- Small AILang programs are embedded directly in test functions
- Temporary directories are used for file I/O tests
- `tempfile.TemporaryDirectory` is used to ensure cleanup

## Continuous Integration

All quality gates must pass before merging:
- **pytest**: 360+ tests, all passing
- **black**: Code formatting check
- **ruff**: Lint check
- **mypy**: Type check (strict mode)

Run all quality gates:

```bash
python -m pytest
black --check .
ruff check .
mypy
```

## Test Categories

| Category | Description | Typical Threshold |
|----------|-------------|-------------------|
| Unit | Single component tests | < 1s each |
| Validation | End-to-end program compilation | < 1s each |
| Compile benchmark | Compile time measurement | < 5-60s (LOC-dependent) |
| Runtime benchmark | Execution time measurement | < 5-30s |
| Memory benchmark | Peak memory measurement | < 200-500 MB |
| Stress | Large programs, deep recursion | < 10s each |
| AI validation | AI-generated program tests | < 1s each |

## Common Issues

| Issue | Solution |
|-------|----------|
| Tests pass locally but fail in CI | Ensure deterministic test environment |
| Memory test fails | Adjust threshold or run on dedicated machine |
| Stress test timeout | Increase timeout or reduce stress level |
| Import error in test | Ensure `pip install -e .` was run |
| Teardown error on Windows | Run with `-p no:cacheprovider` or use WSL |
