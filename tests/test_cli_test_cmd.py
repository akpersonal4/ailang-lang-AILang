"""Tests for `ail test` test_* function auto-execution (J-2)."""

from __future__ import annotations

from pathlib import Path

import pytest

from compiler.cli.main import cmd_test


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """Create a minimal AILang project for `ail test`."""
    root = tmp_path / "proj"
    root.mkdir()
    (root / "ail.toml").write_text(
        "[project]\nname = 'x'\nversion = '0.1.0'\n", encoding="utf-8"
    )
    return root


class TestAutoExecuteTestFunctions:
    def test_passing_test_functions_return_success(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_math.ail").write_text(
            "fn test_addition() {\n"
            '    if (1 + 1 == 2) { return "PASS: addition" } '
            'else { return "FAIL: addition" }\n'
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        assert cmd_test([]) == 0

    def test_failing_assertion_detected(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_math.ail").write_text(
            "fn test_addition() {\n"
            '    if (1 + 1 == 3) { return "PASS: addition" } '
            'else { return "FAIL: addition" }\n'
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        assert cmd_test([]) == 1

    def test_failure_via_print_detected(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_math.ail").write_text(
            "fn test_addition() {\n"
            "    io.println(\"FAIL: addition\");\n"
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        assert cmd_test([]) == 1

    def test_crashing_test_function_marks_failure(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_empty.ail").write_text(
            "import list;\n"
            "fn test_empty_list() {\n"
            "    let items = list.new();\n"
            "    return list.get(items, 0);\n"
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        assert cmd_test([]) == 1

    def test_multiple_test_functions_all_executed(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_math.ail").write_text(
            "fn test_a() {\n"
            '    if (1 + 1 == 2) { return "PASS: a" } '
            'else { return "FAIL: a" }\n'
            "}\n"
            "fn test_b() {\n"
            '    if (5 - 3 == 2) { return "PASS: b" } '
            'else { return "FAIL: b" }\n'
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        assert cmd_test([]) == 0

    def test_legacy_main_convention_still_runs(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_legacy.ail").write_text(
            "fn main() {\n"
            '    io.println("PASS: legacy");\n'
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        assert cmd_test([]) == 0

    def test_legacy_main_failure_still_detected(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_legacy.ail").write_text(
            "fn main() {\n"
            '    io.println("FAIL: legacy");\n'
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        assert cmd_test([]) == 1
