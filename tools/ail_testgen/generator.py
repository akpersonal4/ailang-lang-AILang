"""Generation stage — produce pytest test files from TestCase models."""

from __future__ import annotations

from pathlib import Path

from ail_platform.project import resolve_project_root
from tools.ail_testgen.models import AUTO_HEADER, TestCase, TestCategory
from tools.common.filesystem import ensure_output_dir
from tools.common.hashing import hash_file


def _relative_app_path(root: Path, source_file: Path) -> str:
    """Return the app path relative to the project root.

    Falls back to the absolute path when the file lives outside the project
    (e.g. a single-file mode invocation on a file in another directory), so
    the generated pytest can still locate it.
    """
    try:
        return str(source_file.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(source_file.resolve()).replace("\\", "/")


def _generate_pytest_source(root: Path, cases: list[TestCase]) -> str:
    """Generate the full Python source for a test file covering one app."""
    app_name = cases[0].app_name
    rel_path = _relative_app_path(root, cases[0].source_file)
    lines: list[str] = [
        AUTO_HEADER,
        '"""Auto-generated tests for %s."""' % app_name,
        "",
        "import sys",
        "import subprocess",
        "from pathlib import Path",
        "",
        "",
        "PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent",
        "",
        "",
        "def _app_path() -> str:",
        '    """Return the path to the AILang source file."""',
        '    return str(PROJECT_ROOT / "%s")' % rel_path,
        "",
        "",
        "def _run_ail(args=None):",
        '    """Run the AILang program and return (exit_code, stdout, stderr)."""',
        '    cmd = [sys.executable, "-m", "compiler", "run", _app_path()]',
        "    if args:",
        "        cmd.extend(args)",
        "    result = subprocess.run(cmd, capture_output=True, text=True)",
        "    return result.returncode, result.stdout, result.stderr",
        "",
    ]

    for case in cases:
        desc = case.description or ""
        lines.append("")
        lines.append("")
        lines.append("def %s() -> None:" % case.test_name)
        lines.append('    """%s"""' % desc)

        if case.category == TestCategory.BUILD:
            lines.append("    result = subprocess.run(")
            lines.append(
                '        [sys.executable, "-m", "compiler", "build", _app_path()],'
            )
            lines.append("        capture_output=True, text=True,")
            lines.append("    )")
            lines.append(
                '    assert result.returncode == %d, "Build failed: %%s" %% result.stderr'
                % case.expected_exit_code
            )

        elif case.category == TestCategory.RUN:
            lines.append("    code, out, err = _run_ail()")
            lines.append(
                '    assert code == %d, "Run failed: %%s" %% err'
                % case.expected_exit_code
            )
            lines.append('    assert len(out) > 0, "Expected non-empty output"')

    lines.append("")
    return "\n".join(lines)


def generate_all(
    cases: list[TestCase],
    output_dir: Path,
    force: bool = False,
    root: Path | None = None,
) -> list[dict]:
    """Generate pytest test files for all TestCase objects.

    Produces one file per app containing all its test cases.
    Skips existing files unless force=True.

    Args:
        cases: TestCase objects to turn into files.
        output_dir: Where generated tests are written.
        force: Overwrite existing files.
        root: Project root used for relative paths in generated tests.
            Defaults to the CWD-resolved project root (never the installed
            package location), which keeps `ail testgen` working on a wheel.

    Returns a list of result dicts with file/status/hash/test_count.
    """
    if root is None:
        root = resolve_project_root()
    output_dir = ensure_output_dir(output_dir)

    seen: dict[str, list[TestCase]] = {}
    for case in cases:
        seen.setdefault(case.app_name, []).append(case)

    results: list[dict] = []
    for app_name, app_cases in seen.items():
        output_path = output_dir / ("test_app_%s_generated.py" % app_name)

        if output_path.exists() and not force:
            results.append(
                {
                    "file": str(output_path.relative_to(root)),
                    "app": app_name,
                    "status": "skipped",
                    "reason": "already exists (use --force to overwrite)",
                    "test_count": len(app_cases),
                }
            )
            continue

        source = _generate_pytest_source(root, app_cases)
        output_path.write_text(source, encoding="utf-8")
        digest = hash_file(output_path)
        results.append(
            {
                "file": str(output_path.relative_to(root)),
                "app": app_name,
                "status": "generated",
                "hash": digest,
                "test_count": len(app_cases),
            }
        )

    return results
