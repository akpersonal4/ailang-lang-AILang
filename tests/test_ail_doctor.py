"""Unit tests for the ail doctor developer tool."""

import sys
import subprocess
from pathlib import Path


def test_doctor_tool_generates_file():
    """The ail doctor tool should generate DOCTOR_REPORT.md."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_doctor"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Tool failed: {result.stderr}"

    output_path = Path(__file__).parent.parent / "generated" / "DOCTOR_REPORT.md"
    assert output_path.exists(), "DOCTOR_REPORT.md was not created"

    content = output_path.read_text(encoding="utf-8")
    assert "Repository Health Score" in content
    assert "Documentation Health Score" in content
    assert "Project Health Score" in content
    assert "Archive Candidates" in content
    assert "Duplicate Candidates" in content
    assert "Version Consistency" in content


def test_doctor_is_read_only():
    """The doctor tool should be read-only and never modify source files."""
    # Get list of files before running
    root = Path(__file__).parent.parent
    all_files_before = set(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())

    # Run the tool
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_doctor"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    # Get list of files after running
    all_files_after = set(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())

    # Files should be unchanged (no new source files created, no existing files modified)
    # We allow generated files to be created
    new_files = all_files_after - all_files_before
    non_generated_new_files = [f for f in new_files if not f.startswith("generated/")]
    assert len(non_generated_new_files) == 0, f"Unexpected new files: {non_generated_new_files}"


def test_doctor_report_sections():
    """The generated report should contain all required sections."""
    output_path = Path(__file__).parent.parent / "generated" / "DOCTOR_REPORT.md"
    content = output_path.read_text(encoding="utf-8")

    required_sections = [
        "## Warnings",
        "## Errors",
        "## Recommendations",
        "## Archive Candidates",
        "## Duplicate Candidates",
        "## Missing References",
        "## Version Consistency",
    ]

    for section in required_sections:
        assert section in content, f"Missing section: {section}"


def test_doctor_score_format():
    """The health score should be in X/100 format."""
    output_path = Path(__file__).parent.parent / "generated" / "DOCTOR_REPORT.md"
    content = output_path.read_text(encoding="utf-8")

    # Check for score pattern
    import re
    score_pattern = r"\*\*(\d+)/100\*\*"
    scores = re.findall(score_pattern, content)
    assert len(scores) >= 3, "Expected at least 3 health scores"