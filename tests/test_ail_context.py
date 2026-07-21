"""Tests for the ail context developer tool."""

import json
import subprocess
import sys


def test_context_tool_prints_to_stdout():
    """The ail context tool should print to stdout."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_context"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Tool failed: {result.stderr}"

    content = result.stdout
    assert "AILang Project Context" in content
    assert "Language Rules" in content
    assert "1.1.1" in content


def test_context_is_ai_friendly():
    """The context should be suitable for LLM consumption."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_context"],
        capture_output=True,
        text=True,
    )
    content = result.stdout

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
    assert data["version"] == "1.1.1"
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

    expected_codes = [
        "SEM002",
        "TYP005",
        "TYP006",
        "TYP008",
        "TYP012",
        "TYP013",
        "CMP001",
    ]
    for code in expected_codes:
        assert code in data["diagnostics"], f"Missing diagnostic: {code}"


def test_context_json_no_path_leakage():
    """JSON output must not expose absolute filesystem paths."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_context", "--json"],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)

    json_str = json.dumps(data)

    # No absolute path indicators
    assert "C:\\" not in json_str, "Leaked Windows absolute path"
    assert "/home/" not in json_str, "Leaked Unix home path"
    assert "/Users/" not in json_str, "Leaked macOS user path"
    assert "compiler/docs/" not in json_str, "Leaked repository structure"
    assert "Projects/" not in json_str, "Leaked repository structure"

    # Documentation must have filenames only
    doc = data["documentation"]
    assert "documents" in doc, "Missing documents list"
    assert "AGENTS.md" in doc["documents"]
    assert "LANGUAGE_SPEC.md" in doc["documents"]
    assert "STDLIB_REFERENCE.md" in doc["documents"]

    # Embedded flags must still exist
    assert "agents_embedded" in doc
    assert "language_spec_embedded" in doc
    assert "stdlib_reference_embedded" in doc

    # No path keys remain
    assert "agents" not in doc or isinstance(doc.get("agents"), bool)
    assert "language_spec" not in doc or isinstance(doc.get("language_spec"), bool)
    assert "stdlib_reference" not in doc or isinstance(
        doc.get("stdlib_reference"), bool
    )


def test_context_json_has_retrieval_policy():
    """JSON output should include retrieval_policy."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_context", "--json"],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    assert "retrieval_policy" in data
    policy = data["retrieval_policy"]
    assert "allowed" in policy
    assert "forbidden" in policy
    assert "note" in policy
