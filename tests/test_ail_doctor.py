"""Unit tests for the ail doctor developer tool."""

import subprocess
import sys
from pathlib import Path


def test_doctor_tool_prints_to_stdout():
    """The ail doctor tool should print report to stdout."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_doctor"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Tool failed: {result.stderr}"

    content = result.stdout
    assert "AILang Doctor Report" in content
    assert "Repository Health Score" in content
    assert "Environment" in content
    assert "Components" in content
    assert "Warnings" in content
    assert "Recommendations" in content


def test_doctor_is_read_only():
    """The doctor tool should be read-only and never modify source files."""
    root = Path(__file__).parent.parent
    all_files_before = set(
        str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()
    )

    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_doctor"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    all_files_after = set(
        str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()
    )

    new_files = all_files_after - all_files_before
    non_generated_new_files = [f for f in new_files if not f.startswith("generated/")]
    assert (
        len(non_generated_new_files) == 0
    ), f"Unexpected new files: {non_generated_new_files}"


def test_doctor_report_sections():
    """The report should contain all required sections."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_doctor"],
        capture_output=True,
        text=True,
    )
    content = result.stdout

    required_sections = [
        "## Environment",
        "## Components",
        "## Warnings",
        "## Errors",
        "## Recommendations",
        "## Version Consistency",
        "## Next Steps",
    ]

    for section in required_sections:
        assert section in content, f"Missing section: {section}"


def test_doctor_score_format():
    """The health score should be in X/100 format."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_doctor"],
        capture_output=True,
        text=True,
    )
    content = result.stdout

    import re

    score_pattern = r"\*\*(\d+)/100\*\*"
    scores = re.findall(score_pattern, content)
    assert len(scores) >= 1, "Expected at least 1 health score"


# ------------------------------------------------------------------
# M132: PyPI install must not falsely report README/LICENSE/CHANGELOG
# as missing.
# ------------------------------------------------------------------


def test_is_pypi_install_detects_source_tree():
    """M132: the real project root is NOT a PyPI install."""
    from tools.ail_doctor.__main__ import is_pypi_install

    repo_root = Path(__file__).parent.parent
    assert is_pypi_install(repo_root) is False, (
        "Real source tree (with compiler/, tools/, stdlib/, pyproject.toml) "
        "must not be classified as a PyPI install"
    )


def test_is_pypi_install_detects_site_packages():
    """M132: a bare site-packages-like directory IS a PyPI install."""
    import tempfile

    from tools.ail_doctor.__main__ import is_pypi_install

    with tempfile.TemporaryDirectory() as tmp:
        bare = Path(tmp)
        # Intentionally NO pyproject.toml
        assert is_pypi_install(bare) is True, (
            "Bare directory with no pyproject.toml must be classified "
            "as a PyPI install"
        )


def test_is_pypi_install_wheel_ships_packages_m132():
    """M132: a real wheel install ships compiler/tools/stdlib into
    site-packages and STILL must be detected as a PyPI install.

    Regression from fresh-release verification: the wheel places
    `compiler/`, `tools/`, `stdlib/`, `ail_platform/` at the site-packages
    root, so those cannot be used as source-tree markers. Only the presence
    of `pyproject.toml` distinguishes a source checkout from a wheel install.
    """
    import tempfile

    from tools.ail_doctor.__main__ import is_pypi_install

    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        # Mirror exactly what a pip install of the wheel produces:
        (site / "compiler").mkdir()
        (site / "tools").mkdir()
        (site / "stdlib").mkdir()
        (site / "ail_platform").mkdir()
        # NO pyproject.toml -> must be classified as a PyPI install.
        assert is_pypi_install(site) is True, (
            "site-packages containing compiler/, tools/, stdlib/ but no "
            "pyproject.toml must be classified as a PyPI install"
        )


def test_check_missing_files_skips_all_pypi_absent_files_m132():
    """M132: NO project files are reported missing on a PyPI install.

    Regression from fresh-release verification: `ail doctor` run from a
    `pip install ailang-lang` site-packages layout (which ships
    compiler/tools/stdlib but no pyproject.toml) previously reported
    README/LICENSE/CHANGELOG/DEVELOPMENT_STATUS/PROJECT_MEMORY/AGENTS as
    missing, even though every one of them is intentionally absent from
    the wheel.
    """
    import tempfile

    from tools.ail_doctor.__main__ import check_missing_files

    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        (site / "compiler").mkdir()
        (site / "tools").mkdir()
        (site / "stdlib").mkdir()
        (site / "ail_platform").mkdir()
        missing = check_missing_files(site)
        assert missing == [], (
            f"PyPI install must report no missing project files; got {missing}"
        )


def test_check_missing_files_still_flags_in_source_tree_m132():
    """M132: a real source checkout still flags genuinely missing files."""
    import tempfile

    from tools.ail_doctor.__main__ import check_missing_files

    repo_root = Path(__file__).parent.parent
    # Use a temp directory that mirrors the source-tree marker layout but
    # contains NONE of the expected project files. This forces every entry
    # to be reported missing.
    with tempfile.TemporaryDirectory() as tmp:
        bare = Path(tmp)
        (bare / "compiler").mkdir()
        (bare / "tools").mkdir()
        (bare / "stdlib").mkdir()
        (bare / "pyproject.toml").write_text("[project]\nname = 'x'\n")
        missing = check_missing_files(bare)
        missing_names = {m["expected_file"] for m in missing}
        # All six should be reported when pyproject.toml (source-tree marker)
        # is present.
        expected = {
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "DEVELOPMENT_STATUS.md",
            "PROJECT_MEMORY.md",
            "AGENTS.md",
        }
        assert missing_names == expected, (
            f"Source-tree mode must flag all six files; got {missing_names}"
        )
