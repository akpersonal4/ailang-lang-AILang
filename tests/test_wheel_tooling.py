"""Regression tests for wheel-install fixes (A100 preconditions).

Covered:
- `ail testgen <file>` must not crash with an uncaught ValueError when the
  file lives outside the package location (the fix makes the tool operate
  against the user's CWD-resolved project root).
- `ail benchmark` must fall back to wheel-bundled canonical apps when no
  source checkout is present.
- `ail static-analyzer <file>` must run against a file outside the package
  location.
- `ail rename` must report the directory the user is actually in, not a
  stray ancestor marker.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CANONICAL_APPS = [
    "dice_roller",
    "hangman_game",
    "inventory_mgmt",
    "kanban",
    "static_analyzer",
]

REPO_ROOT = Path(__file__).resolve().parent.parent


def _repo_env() -> dict:
    """Subprocess env that pins tool/compiler resolution to THIS checkout.

    The dev virtualenv contains older installed copies of ``tools``,
    ``compiler``, and ``ail_platform`` in site-packages. When a subprocess
    runs with cwd outside the repo (as these tests do, to simulate a user
    project), plain ``python -m`` would import those stale copies instead of
    the code under test. PYTHONPATH restores the repo's packages.
    """
    import os

    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(REPO_ROOT) + (os.pathsep + existing if existing else "")
    return env


def _write_app(project: Path, name: str = "example.ail") -> Path:
    """Write a small AILang program into *project* and return its path."""
    app = project / name
    app.write_text("fn main() { return 0 }\n", encoding="utf-8")
    return app


# =========================================================================
# ail testgen
# =========================================================================


def test_testgen_single_file_mode_writes_into_project(tmp_path: Path) -> None:
    """A100: `ail testgen <file>` works when the file is not under the
    installed package location.

    Pre-fix, root resolved to the package location and generator's
    ``Path.relative_to(root)`` raised an uncaught ValueError for any file
    outside it.
    """
    project = tmp_path / "proj"
    project.mkdir()
    app = _write_app(project)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.ail_testgen",
            str(app),
            "--output-dir",
            str(project / "tests" / "generated"),
        ],
        capture_output=True,
        text=True,
        cwd=project,
        env=_repo_env(),
        timeout=180,
    )
    assert result.returncode == 0, f"testgen failed: {result.stderr}"
    # M136 P1a fix: testgen now emits ``.ail`` test files (compatible
    # with ``ail test``) instead of pytest ``.py`` files.
    generated = project / "tests" / "generated" / "test_app_example_generated.ail"
    assert generated.is_file(), f"expected generated test file, got: {result.stdout}"


def test_testgen_no_apps_clean_error_in_bare_dir(tmp_path: Path) -> None:
    """A100: `ail testgen` in a directory without apps reports a clean
    error instead of crashing or writing into site-packages."""
    project = tmp_path / "bare"
    project.mkdir()

    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_testgen", "--dry-run"],
        capture_output=True,
        text=True,
        cwd=project,
        env=_repo_env(),
        timeout=120,
    )
    assert "Error: no apps discovered" in result.stdout
    # Must not have written anything next to the CWD's ancestors (home).
    assert not list(project.rglob("TEST_GENERATION_REPORT*"))


# =========================================================================
# ail benchmark
# =========================================================================


def test_benchmark_falls_back_to_bundled_apps(tmp_path: Path) -> None:
    """A100: with no apps/ tree (wheel install), `ail benchmark` discovers
    the canonical apps bundled inside the package."""
    from tools.ail_benchmark.discovery import discover_benchmarks

    project = tmp_path / "proj"
    project.mkdir()

    benchmarks = discover_benchmarks(project, suite="canonical")
    names = sorted(b.name for b in benchmarks)
    assert names == sorted(CANONICAL_APPS), f"got: {names}"
    for benchmark in benchmarks:
        assert benchmark.path.is_file(), f"missing app file: {benchmark.path}"


def test_benchmark_bundled_app_runs_end_to_end(tmp_path: Path) -> None:
    """A100: a bundled app builds and runs via the benchmark runner."""
    from tools.ail_benchmark.discovery import discover_benchmarks
    from tools.ail_benchmark.runner import run_benchmark

    project = tmp_path / "proj"
    project.mkdir()

    benchmarks = discover_benchmarks(project, app_name="dice_roller")
    assert len(benchmarks) == 1
    result = run_benchmark(benchmarks[0], repeat=1, timeout=120, quiet=True)
    assert result.status == "pass", f"benchmark failed: {result.error}"
    assert result.run_stats.avg > 0


# =========================================================================
# ail static-analyzer
# =========================================================================


def test_static_analyzer_runs_on_file_outside_package(tmp_path: Path) -> None:
    """A100: `ail static-analyzer <file>` works for a file that is not
    under the installed package location (sandbox working dir follows the
    analyzed file)."""
    project = tmp_path / "proj"
    project.mkdir()
    app = _write_app(project, "target.ail")

    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_static_analyzer", str(app)],
        capture_output=True,
        text=True,
        cwd=project,
        env=_repo_env(),
        timeout=180,
    )
    assert result.returncode == 0, f"static-analyzer failed: {result.stderr}"
    assert "Analyzed:" in result.stdout
    assert (project / "generated" / "STATIC_ANALYZER_REPORT.json").is_file()


def test_resolve_bundled_app_prefers_live_repo_copy() -> None:
    """The bundled-app resolver must prefer the live apps/ tree in a
    source checkout."""
    from ail_platform.project import (
        bundled_apps_dir,
        get_project_root,
        resolve_bundled_app,
    )

    resolved = resolve_bundled_app("dice_roller")
    assert resolved == get_project_root() / "apps" / "dice_roller" / "main.ail"
    assert resolved.is_file()
    # Bundled copies exist and are distinct from the live tree.
    bundled = bundled_apps_dir()
    assert (bundled / "dice_roller" / "main.ail").is_file()


# =========================================================================
# ail doctor
# =========================================================================


def test_doctor_scopes_scan_to_project_dir(tmp_path: Path) -> None:
    """A100: `ail doctor` scans the user's project, never site-packages."""
    import re

    from tools.ail_doctor.__main__ import generate_report

    project = tmp_path / "proj"
    project.mkdir()
    (project / "README.md").write_text("# Readme\n", encoding="utf-8")
    _write_app(project, "main.ail")

    report = generate_report(scan_root=project)
    assert "AILang Doctor Report" in report
    score_match = re.search(r"\*\*(\d+)/100\*\*", report)
    assert score_match is not None, "expected a health score"
    score = int(score_match.group(1))
    assert score >= 50, (
        f"project scan scored {score}/100; site-packages checks may have leaked"
    )
    assert score != 0


# =========================================================================
# ail rename
# =========================================================================


def test_rename_error_reports_cwd_not_stray_marker(
    tmp_path: Path, monkeypatch
) -> None:
    """A100: rename's 'no ail.toml' error reports the directory the user
    is in, not a stray .ail marker found in an ancestor (e.g. ~/.ail)."""
    import io
    from contextlib import redirect_stderr

    from compiler.cli.main import cmd_rename

    stray = tmp_path / "stray"
    stray.mkdir()
    (stray / ".ail").mkdir()
    inner = stray / "inner"
    inner.mkdir()
    monkeypatch.chdir(inner)

    err = io.StringIO()
    with redirect_stderr(err):
        result = cmd_rename(["foo", "bar"])
    assert result == 5
    assert "no ail.toml found in" in err.getvalue()
    # The reported directory must be where the user is, not the stray
    # ancestor marker directory.
    reported = str(inner.resolve())
    after_prefix = err.getvalue().split("no ail.toml found in", 1)[1]
    assert after_prefix.strip().startswith(reported)
