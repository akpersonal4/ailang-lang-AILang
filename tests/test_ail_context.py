"""Tests for the ail context developer tool."""

import json
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
    assert "AILang Project Context" in content
    assert "Language Rules" in content
    assert "1.0.4" in content


def test_context_is_ai_friendly():
    """The generated context should be suitable for LLM consumption."""
    output_path = Path(__file__).parent.parent / "generated" / "PROJECT_CONTEXT.md"
    content = output_path.read_text(encoding="utf-8")

    # Check length is reasonable (< 8KB for context windows - still small)
    assert len(content) < 8000, "Context file too large for LLM consumption"

    # Check key sections exist
    assert "Language Rules" in content
    assert "Workflow" in content
    assert "Standard Library" in content
    assert "Diagnostics" in content


def test_context_json_output():
    """The ail context --json should output valid JSON."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_context", "--json"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Tool failed: {result.stderr}"

    data = json.loads(result.stdout)
    assert data["language"] == "AILang"
    assert data["version"] == "1.0.4"
    assert "rules" in data
    assert "workflow" in data
    assert "diagnostics" in data
    assert "stdlib" in data
    assert "types" in data
    assert "operators" in data


def test_context_json_has_all_rules():
    """JSON output should include all language rules."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_context", "--json"],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)

    expected_rules = [
        "no_loops",
        "no_forward_references",
        "no_nested_functions",
        "bottom_up_ordering",
        "let_requires_initializer",
        "return_requires_value",
        "import_top_level_only",
        "unique_variable_names",
        "map_get_needs_guard",
        "list_get_needs_guard",
        "string_concat_two_args",
        "eager_logical_operators",
    ]

    for rule in expected_rules:
        assert rule in data["rules"], f"Missing rule: {rule}"
        assert "enabled" in data["rules"][rule]
        assert "description" in data["rules"][rule]


def test_context_json_workflow():
    """JSON workflow should match official pipeline."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_context", "--json"],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    assert data["workflow"] == ["fmt", "check", "build", "test", "run"]


def test_context_json_has_diagnostics():
    """JSON output should include all diagnostic codes."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_context", "--json"],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)

    expected_codes = ["SEM002", "TYP005", "TYP006", "TYP008", "TYP012", "TYP013", "CMP001"]
    for code in expected_codes:
        assert code in data["diagnostics"], f"Missing diagnostic: {code}"
