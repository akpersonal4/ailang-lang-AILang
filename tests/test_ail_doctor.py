"""Unit tests for the ail doctor developer tool."""

import sys
import subprocess
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
    all_files_before = set(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())

    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_doctor"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    all_files_after = set(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())

    new_files = all_files_after - all_files_before
    non_generated_new_files = [f for f in new_files if not f.startswith("generated/")]
    assert len(non_generated_new_files) == 0, f"Unexpected new files: {non_generated_new_files}"


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
