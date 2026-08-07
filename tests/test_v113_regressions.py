"""Regression tests for v1.1.13 fixes.

Covers:
- MOD004 for unknown module member calls at compile time (math.mod, list.push)
- CMP001 cascade suppression when a PAR/LEX diagnostic already exists
- LEX004 for non-UTF-8 (UTF-16) source files
- Clean recursion-depth RuntimeError instead of a Python traceback
- Sandbox violation enforced at runtime
- User modules shadowed by stdlib registration do not produce false MOD004
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import pytest

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.errors import RuntimeError as AILangRuntimeError
from compiler.runtime.interpreter import Runtime
from compiler.runtime.sandbox import SandboxPolicy, get_policy, set_policy


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _compile_source(
    source: str, workdir: Path | None = None
) -> tuple[CompilationSession, DiagnosticReporter]:
    """Compile AILang source in a temp dir and return session + reporter."""
    root = workdir or _get_repo_root()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source, encoding="utf-8")

        reporter = DiagnosticReporter()
        session = CompilationSession()
        session._root = root
        session._resolver = type(session._resolver)(root)
        session.discover(main_file, reporter=reporter)
        session.analyze(reporter)

        return session, reporter


def _run_source(source: str) -> Any:
    """Compile and execute AILang source, returning the main result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source, encoding="utf-8")

        root = _get_repo_root()
        session = CompilationSession()
        session._root = root
        session._resolver = type(session._resolver)(root)
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
        return runtime.execute(bundle.module_irs[entry_module])


def test_mod004_unknown_math_member() -> None:
    """math.mod() is not a stdlib export -> MOD004 with available list."""
    _, reporter = _compile_source("import math; fn main() { return math.mod(10, 3) }")
    codes = [d.error_code.code for d in reporter.diagnostics]
    assert "MOD004" in codes
    diag = next(d for d in reporter.diagnostics if d.error_code.code == "MOD004")
    assert "math.mod" in diag.message
    assert "Available functions in module 'math'" in diag.message
    assert "math.abs" in diag.message


def test_mod004_unknown_list_member() -> None:
    """list.push() is not a stdlib export -> MOD004 with full export list."""
    _, reporter = _compile_source(
        "import list; fn main() { let l = list.new(); return list.push(l, 1) }"
    )
    codes = [d.error_code.code for d in reporter.diagnostics]
    assert "MOD004" in codes
    diag = next(d for d in reporter.diagnostics if d.error_code.code == "MOD004")
    assert "list.push" in diag.message
    assert "Available functions in module 'list'" in diag.message


def test_mod004_valid_stdlib_calls_are_clean() -> None:
    """Valid stdlib member calls must not produce MOD004."""
    _, reporter = _compile_source(
        "import math;\nimport list;\nimport string;\n"
        "fn main() {\n"
        "    let l = list.new();\n"
        "    return math.abs(10 - 13) + list.len(l) + string.length(\"hi\")\n"
        "}"
    )
    assert reporter.error_count == 0


def test_parse_error_does_not_cascade_cmp001() -> None:
    """`let x = ;` reports only the parse error (no CMP001 internal failure)."""
    _, reporter = _compile_source("fn main() { let x = ; }")
    codes = [d.error_code.code for d in reporter.diagnostics]
    assert "PAR001" in codes
    assert "CMP001" not in codes


def test_lex004_non_utf8_source() -> None:
    """A UTF-16 source file yields a clean LEX004 diagnostic, no crash."""
    root = _get_repo_root()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text("fn main() { return 1 }\n", encoding="utf-16")

        reporter = DiagnosticReporter()
        session = CompilationSession()
        session._root = root
        session._resolver = type(session._resolver)(root)
        session.discover(main_file, reporter=reporter)

        codes = [d.error_code.code for d in reporter.diagnostics]
        assert "LEX004" in codes
        diag = next(d for d in reporter.diagnostics if d.error_code.code == "LEX004")
        assert "UTF-8" in diag.message


def test_recursion_depth_clean_error() -> None:
    """Deep recursion raises a clean RuntimeError, not a Python traceback."""
    original = get_policy()
    try:
        set_policy(SandboxPolicy(working_dir=_get_repo_root(), enabled=False))
        with pytest.raises(AILangRuntimeError) as exc_info:
            _run_source(
                "fn recurse(n) { if (n <= 0) { return 0 } return recurse(n - 1) }\n"
                "fn main() { return recurse(100000) }"
            )
        err = exc_info.value
        assert err.operation == "call"
        assert "Recursion depth exceeded" in err.reason
        assert "2000" in err.reason
    finally:
        set_policy(original)


def test_sandbox_violation_blocked() -> None:
    """file.read escaping the working directory raises a clean sandbox error."""
    original = get_policy()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            workdir = Path(tmpdir)
            set_policy(SandboxPolicy(working_dir=workdir, enabled=True))
            with pytest.raises(AILangRuntimeError) as exc_info:
                _run_source(
                    "import file; fn main() { return file.read(\"../../../etc/passwd\") }"
                )
            err = exc_info.value
            assert err.operation in ("sandbox", "file.read")
            assert "Sandbox violation" in err.reason
    finally:
        set_policy(original)


def test_sandbox_disabled_allows_external_paths() -> None:
    """With the sandbox disabled, paths outside the working dir are readable."""
    original = get_policy()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            workdir = Path(tmpdir)
            secret = workdir.parent / f"{workdir.name}_secret.txt"
            secret.write_text("s3cr3t", encoding="utf-8")
            set_policy(SandboxPolicy(working_dir=workdir, enabled=False))
            result = _run_source(
                f"import file; fn main() {{ return file.read(\"{secret.as_posix()}\") }}"
            )
            assert result == "s3cr3t"
            secret.unlink()
    finally:
        set_policy(original)


def test_shadowed_stdlib_module_no_false_mod004() -> None:
    """User modules dropped in favor of stdlib must not produce MOD004."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        (tmp_path / "math.ail").write_text(
            "fn add(a, b) { return a + b }\n", encoding="utf-8"
        )
        (tmp_path / "string.ail").write_text(
            "fn add(a, b) { return a - b }\n", encoding="utf-8"
        )
        main_file = tmp_path / "main.ail"
        main_file.write_text(
            "import math;\nimport string;\n\n"
            "fn main() {\n"
            "    print(math.add(1, 2))\n"
            "    print(string.add(3, 1))\n"
            "}\n",
            encoding="utf-8",
        )

        reporter = DiagnosticReporter()
        session = CompilationSession()
        session._root = tmp_path
        session._resolver = type(session._resolver)(tmp_path)
        session.discover(main_file)
        session.analyze(reporter)

        assert reporter.error_count == 0


def test_version_consistency() -> None:
    """The canonical version follows the X.Y.Z scheme (baseline M132)."""
    import re

    from compiler._version import __version__

    assert re.fullmatch(r"1\.\d+\.\d+", __version__), f"Unexpected version: {__version__}"
    assert __version__ != "1.1.12"
