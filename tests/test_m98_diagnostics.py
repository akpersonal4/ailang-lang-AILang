"""Tests for M98 product hardening diagnostics (WHILE001, LANG001, LANG002, LANG003)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from compiler.compilation import CompilationSession
from compiler.diagnostics import (
    DiagnosticFormatter,
    DiagnosticReporter,
    ErrorCode,
    LANG001_NESTED_FN,
    LANG002_LIST_SET_UNAVAILABLE,
    LANG003_STRING_REPLACE_UNAVAILABLE,
    Severity,
    WHILE001_NO_WHILE_LOOPS,
)


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _compile_source(source: str, experimental_loops: bool = False) -> tuple[CompilationSession, DiagnosticReporter]:
    """Compile AILang source and return session + reporter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        repo_root = _get_repo_root()
        reporter = DiagnosticReporter()
        session = CompilationSession(experimental_loops=experimental_loops)
        session._root = repo_root
        session._resolver = type(session._resolver)(repo_root)
        session.discover(main_file, reporter=reporter)
        session.analyze(reporter)

        return session, reporter


def test_while001_error_code_is_stable() -> None:
    assert WHILE001_NO_WHILE_LOOPS.code == "WHILE001"
    assert "while loops" in WHILE001_NO_WHILE_LOOPS.message


def test_lang001_error_code_is_stable() -> None:
    assert LANG001_NESTED_FN.code == "LANG001"
    assert "Nested functions" in LANG001_NESTED_FN.message


def test_lang002_error_code_is_stable() -> None:
    assert LANG002_LIST_SET_UNAVAILABLE.code == "LANG002"
    assert "list.set()" in LANG002_LIST_SET_UNAVAILABLE.message


def test_lang003_error_code_is_stable() -> None:
    assert LANG003_STRING_REPLACE_UNAVAILABLE.code == "LANG003"
    assert "string.replace()" in LANG003_STRING_REPLACE_UNAVAILABLE.message


def test_diagnostic_formatter_has_next_steps_for_while001() -> None:
    formatter = DiagnosticFormatter()
    steps = formatter.suggest_next_steps("WHILE001")
    assert steps is not None
    assert "ail explain WHILE001" in steps


def test_diagnostic_formatter_has_next_steps_for_lang001() -> None:
    formatter = DiagnosticFormatter()
    steps = formatter.suggest_next_steps("LANG001")
    assert steps is not None
    assert "ail explain LANG001" in steps


def test_diagnostic_formatter_has_next_steps_for_lang002() -> None:
    formatter = DiagnosticFormatter()
    steps = formatter.suggest_next_steps("LANG002")
    assert steps is not None
    assert "ail explain LANG002" in steps


def test_diagnostic_formatter_has_next_steps_for_lang003() -> None:
    formatter = DiagnosticFormatter()
    steps = formatter.suggest_next_steps("LANG003")
    assert steps is not None
    assert "ail explain LANG003" in steps


def test_diagnostic_formatter_has_description_for_while001() -> None:
    formatter = DiagnosticFormatter()
    desc = formatter.get_error_description("WHILE001")
    assert desc is not None
    assert "no while loops" in desc.lower()


def test_diagnostic_formatter_has_description_for_lang001() -> None:
    formatter = DiagnosticFormatter()
    desc = formatter.get_error_description("LANG001")
    assert desc is not None
    assert "nested" in desc.lower()


def test_diagnostic_formatter_has_description_for_lang002() -> None:
    formatter = DiagnosticFormatter()
    desc = formatter.get_error_description("LANG002")
    assert desc is not None
    assert "list.set" in desc.lower()


def test_diagnostic_formatter_has_description_for_lang003() -> None:
    formatter = DiagnosticFormatter()
    desc = formatter.get_error_description("LANG003")
    assert desc is not None
    assert "string.replace" in desc.lower()


def test_format_summary_suggests_docs_for_lang_errors() -> None:
    reporter = DiagnosticReporter()
    from compiler.diagnostics import Diagnostic

    reporter.report(
        Diagnostic(
            Severity.ERROR,
            WHILE001_NO_WHILE_LOOPS,
            "AILang has no while loops.",
            1,
            1,
        )
    )
    formatter = DiagnosticFormatter()
    summary = formatter.format_summary(reporter)
    assert "ail docs AGENTS.md" in summary


# =============================================================================
# Integration tests: while loop detection
# =============================================================================


def test_while_loop_produces_while001() -> None:
    source = """
fn main() {
    let i = 0;
    while (i < 10) {
        i = i + 1;
    }
    return 0;
}
"""
    _, reporter = _compile_source(source)
    codes = {d.error_code.code for d in reporter.diagnostics}
    assert "WHILE001" in codes, f"Expected WHILE001, got: {codes}"


def test_while_loop_at_top_level_produces_while001() -> None:
    source = """
let i = 0;
while (i < 10) {
    i = i + 1;
}
fn main() {
    return 0;
}
"""
    _, reporter = _compile_source(source)
    codes = {d.error_code.code for d in reporter.diagnostics}
    assert "WHILE001" in codes, f"Expected WHILE001, got: {codes}"


# =============================================================================
# Integration tests: nested function detection
# =============================================================================


def test_nested_function_produces_lang001() -> None:
    source = """
fn main() {
    fn helper() {
        return 1;
    }
    let x = helper();
    return x;
}
"""
    _, reporter = _compile_source(source)
    codes = {d.error_code.code for d in reporter.diagnostics}
    assert "LANG001" in codes, f"Expected LANG001, got: {codes}"


# =============================================================================
# Integration tests: list.set() unavailable
# =============================================================================


def test_list_set_produces_lang002() -> None:
    source = """
import list;

fn main() {
    let items = list.new();
    list.set(items, 0, 42);
    return 0;
}
"""
    _, reporter = _compile_source(source)
    codes = {d.error_code.code for d in reporter.diagnostics}
    assert "LANG002" in codes, f"Expected LANG002, got: {codes}"


# =============================================================================
# Integration tests: string.replace() unavailable
# =============================================================================


def test_string_replace_produces_lang003() -> None:
    source = """
import string;

fn main() {
    let s = string.replace("hello world", "world", "AILang");
    return 0;
}
"""
    _, reporter = _compile_source(source)
    codes = {d.error_code.code for d in reporter.diagnostics}
    assert "LANG003" in codes, f"Expected LANG003, got: {codes}"