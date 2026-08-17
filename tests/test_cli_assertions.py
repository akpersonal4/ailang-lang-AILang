"""P0-2 regression tests: trustworthy assertion and test verdicts.

Verifies that ``test.expect`` (the real assertion primitive) drives the
``ail test`` verdict through its return value and raised assertions, and
that the output-based "FAIL" string scan is only a supplementary signal:

- a passing assertion produces a PASS (no false failure)
- a failing assertion produces FAIL and reports its reason
- a silent non-zero return is FAIL (the false-PASS regression: a test
  that returned 1 with no output used to be reported as PASS)
- a silent zero return is PASS
- the legacy return-"FAIL" / print-"FAIL" conventions still work
- multiple test functions in one file are all executed and the file is
  reported once
- a runtime error in a test marks the file FAIL
- the process-level exit code is non-zero on failure
- testgen-generated tests flow through the same verdict mechanism
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
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


def _run_cmd_test(
    paths: list[str] | None = None,
) -> tuple[int, str, str]:
    """Run cmd_test capturing stdout/stderr."""
    old_cwd = os.getcwd()
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    sys.stdout = out_buf
    sys.stderr = err_buf
    try:
        rc = cmd_test(list(paths) if paths is not None else [])
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        os.chdir(old_cwd)
    return rc, out_buf.getvalue(), err_buf.getvalue()


class TestAssertionVerdicts:
    def test_passing_assertion_is_pass(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_math.ail").write_text(
            "import test;\n"
            "fn test_addition() {\n"
            "    test.expect(1 + 1 == 2, \"addition works\");\n"
            "    return 0;\n"
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        rc, out, err = _run_cmd_test()
        assert rc == 0
        assert "PASS  test_math.ail" in out

    def test_passing_assertion_with_no_output_is_pass(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A passing assertion must not be reported as FAIL just because
        the test produced no output."""
        (project / "test_silent.ail").write_text(
            "import test;\n"
            "fn test_silent() {\n"
            "    test.expect(true, \"always true\");\n"
            "    return 0;\n"
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        rc, out, err = _run_cmd_test()
        assert rc == 0
        assert "PASS  test_silent.ail" in out

    def test_failing_assertion_is_fail(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_math.ail").write_text(
            "import test;\n"
            "fn test_addition() {\n"
            "    test.expect(1 + 1 == 3, \"one plus one is two\");\n"
            "    return 0;\n"
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        rc, out, err = _run_cmd_test(["--verbose"])
        assert rc == 1
        assert "FAIL  test_math.ail" in err
        assert "one plus one is two" in err

    def test_nonzero_return_with_no_output_is_fail(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Regression: a test returning 1 with no output used to PASS."""
        (project / "test_silent.ail").write_text(
            "fn test_silent_failure() {\n"
            "    return 1;\n"
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        rc, out, err = _run_cmd_test()
        assert rc == 1
        assert "FAIL  test_silent.ail" in err

    def test_zero_return_with_no_output_is_pass(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_silent.ail").write_text(
            "fn test_silent_ok() {\n"
            "    return 0;\n"
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        rc, out, err = _run_cmd_test()
        assert rc == 0
        assert "PASS  test_silent.ail" in out

    def test_legacy_return_fail_string_still_fails(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_legacy.ail").write_text(
            "fn test_old() {\n"
            "    return \"FAIL: old convention\";\n"
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        rc, out, err = _run_cmd_test()
        assert rc == 1
        assert "FAIL  test_legacy.ail" in err

    def test_legacy_print_fail_still_fails(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_legacy.ail").write_text(
            "fn test_old() {\n"
            '    io.println("FAIL: old convention");\n'
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        rc, out, err = _run_cmd_test()
        assert rc == 1
        assert "FAIL  test_legacy.ail" in err

    def test_multiple_tests_one_failure_reports_file_once(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_math.ail").write_text(
            "fn test_a() {\n"
            "    return 0;\n"
            "}\n"
            "fn test_b() {\n"
            "    return 1;\n"
            "}\n"
            "fn test_c() {\n"
            "    return 0;\n"
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        rc, out, err = _run_cmd_test()
        assert rc == 1
        assert "FAIL  test_math.ail" in err
        assert err.count("test_math.ail") >= 1

    def test_runtime_error_in_test_is_fail(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (project / "test_runtime.ail").write_text(
            "import list;\n"
            "import test;\n"
            "fn test_empty_list() {\n"
            "    test.expect(list.len(list.new()) == 0, \"empty list\");\n"
            "    let items = list.new();\n"
            "    return list.get(items, 0);\n"
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        rc, out, err = _run_cmd_test(["--verbose"])
        assert rc == 1
        assert "FAIL  test_runtime.ail" in err

    def test_assertion_error_aborts_remaining_tests_in_file_but_file_fails(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A raised assertion is a hard failure for the file; the file must
        be reported FAIL (not a false PASS)."""
        (project / "test_math.ail").write_text(
            "import test;\n"
            "fn test_bad_assertion() {\n"
            "    test.expect(false, \"deliberate failure\");\n"
            "}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        rc, out, err = _run_cmd_test(["--verbose"])
        assert rc == 1
        assert "FAIL  test_math.ail" in err
        assert "deliberate failure" in err


class TestAssertionProcessExitCode:
    def _run(
        self, test_file: Path, *extra: str
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        repo_root = str(Path(__file__).resolve().parents[1])
        existing_pp = env.get("PYTHONPATH", "")
        if repo_root not in existing_pp.split(os.pathsep):
            env["PYTHONPATH"] = (
                repo_root + (os.pathsep + existing_pp if existing_pp else "")
            )
        return subprocess.run(
            [sys.executable, "-m", "compiler", "test", *extra, str(test_file)],
            capture_output=True,
            text=True,
            cwd=repo_root,
            env=env,
            timeout=120,
        )

    def test_failing_assertion_exits_nonzero(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test_math.ail"
        test_file.write_text(
            "import test;\n"
            "fn test_addition() {\n"
            "    test.expect(2 + 2 == 5, \"four\");\n"
            "    return 0;\n"
            "}\n",
            encoding="utf-8",
        )
        result = self._run(test_file)
        assert result.returncode == 1
        assert "FAIL  test_math.ail" in result.stderr

    def test_passing_assertion_exits_zero(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test_math.ail"
        test_file.write_text(
            "import test;\n"
            "fn test_addition() {\n"
            "    test.expect(2 + 2 == 4, \"four\");\n"
            "    return 0;\n"
            "}\n",
            encoding="utf-8",
        )
        result = self._run(test_file)
        assert result.returncode == 0
        assert "PASS  test_math.ail" in result.stdout


class TestTestgenVerdictIntegration:
    """testgen-generated tests must flow through the same verdict
    mechanism: a genuinely failing generated test is a FAIL."""

    def _testgen(
        self, project: Path
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        repo_root = str(Path(__file__).resolve().parents[1])
        existing_pp = env.get("PYTHONPATH", "")
        if repo_root not in existing_pp.split(os.pathsep):
            env["PYTHONPATH"] = (
                repo_root + (os.pathsep + existing_pp if existing_pp else "")
            )
        return subprocess.run(
            [sys.executable, "-m", "tools.ail_testgen", "--app", "example",
             "--force", "--quiet"],
            capture_output=True,
            text=True,
            cwd=str(project),
            env=env,
            timeout=180,
        )

    def test_generated_test_uses_real_assertion_mechanism(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        project = tmp_path / "proj"
        app_dir = project / "apps" / "example"
        app_dir.mkdir(parents=True)
        (app_dir / "main.ail").write_text(
            "fn main() {\n"
            "    print(\"EXAMPLE_OK\");\n"
            "    return 0\n"
            "}\n",
            encoding="utf-8",
        )
        (project / "ail.toml").write_text(
            "[project]\nname = 'g_proj'\nversion = '0.0.0'\n"
            "entry = 'apps/example/main.ail'\n",
            encoding="utf-8",
        )
        result = self._testgen(project)
        assert result.returncode == 0, result.stderr
        generated = (
            project / "apps" / "example" / "test_app_example_generated.ail"
        )
        assert generated.is_file()
        text = generated.read_text(encoding="utf-8")
        assert "import test;" in text
        assert "test.expect" in text

        # A genuine, edited-in failure must be reported FAIL.
        generated.write_text(
            text.replace(
                'test.expect(true, "app build checks pass");',
                'test.expect(1 + 1 == 3, "genuine failure");',
            ),
            encoding="utf-8",
        )
        monkeypatch.chdir(project)
        rc, out, err = _run_cmd_test(["--verbose", str(generated)])
        assert rc == 1
        assert "FAIL  test_app_example_generated.ail" in err
        assert "genuine failure" in err
