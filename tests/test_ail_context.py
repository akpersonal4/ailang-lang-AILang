"""Tests for the ail context developer tool."""

import subprocess
import sys
from pathlib import Path


def test_context_tool_generates_file():
    """The ail context tool should generate PROJECT_CONTEXT.md."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_context"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Tool failed: {result.stderr}"

    output_path = Path(__file__).parent.parent / "generated" / "PROJECT_CONTEXT.md"
    assert output_path.exists(), "PROJECT_CONTEXT.md was not created"

    content = output_path.read_text(encoding="utf-8")
    assert "Project Overview" in content
    assert "Do Not Change Rules" in content
    assert "v0.2.0" in content
    assert "772 tests" in content


def test_context_is_ai_friendly():
    """The generated context should be suitable for LLM consumption."""
    output_path = Path(__file__).parent.parent / "generated" / "PROJECT_CONTEXT.md"
    content = output_path.read_text(encoding="utf-8")

    # Check length is reasonable (< 8KB for context windows - still small)
    assert len(content) < 8000, "Context file too large for LLM consumption"

    # Check key sections exist
    assert "Language Constraints" in content
    assert "Compiler Architecture" in content
    assert "Runtime Architecture" in content
    assert "Standard Library Summary" in content