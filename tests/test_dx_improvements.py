"""Tests for M75.4 DX improvements: diagnostics, context, heal, first-run."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


# =============================================================================
# Diagnostics: next_steps field
# =============================================================================


class TestDiagnosticsNextSteps:
    """Test Diagnostic next_steps field and formatter."""

    def test_diagnostic_has_next_steps_field(self):
        from compiler.diagnostics import Diagnostic, ErrorCode, Severity

        d = Diagnostic(
            severity=Severity.ERROR,
            error_code=ErrorCode("TYP001", "Type mismatch"),
            message="Expected string, got int",
            next_steps="Run `ail heal type_error` for fix suggestions.",
        )
        assert d.next_steps == "Run `ail heal type_error` for fix suggestions."

    def test_diagnostic_next_steps_none_by_default(self):
        from compiler.diagnostics import Diagnostic, ErrorCode, Severity

        d = Diagnostic(
            severity=Severity.ERROR,
            error_code=ErrorCode("TYP001", "Type mismatch"),
            message="Expected string, got int",
        )
        assert d.next_steps is None

    def test_formatter_suggest_next_steps_returns_string(self):
        from compiler.diagnostics import DiagnosticFormatter

        result = DiagnosticFormatter.suggest_next_steps("TYP001")
        assert isinstance(result, str)
        assert "heal" in result.lower() or "type" in result.lower()

    def test_formatter_format_summary(self):
        from compiler.diagnostics import DiagnosticFormatter, DiagnosticReporter, Diagnostic, ErrorCode, Severity

        reporter = DiagnosticReporter()
        reporter.report(Diagnostic(
            severity=Severity.ERROR,
            error_code=ErrorCode("TYP001", "Type mismatch"),
            message="Expected string, got int",
        ))
        reporter.report(Diagnostic(
            severity=Severity.WARNING,
            error_code=ErrorCode("W001", "Unused value"),
            message="Value is never used",
        ))
        summary = DiagnosticFormatter.format_summary(reporter)
        assert "1 diagnostic(s)" in summary
        assert "1 warning(s)" in summary

    def test_formatter_format_summary_no_issues(self):
        from compiler.diagnostics import DiagnosticFormatter, DiagnosticReporter

        reporter = DiagnosticReporter()
        summary = DiagnosticFormatter.format_summary(reporter)
        assert summary == ""


# =============================================================================
# Context tool: recommended_workflows and dx_tools
# =============================================================================


class TestContextWorkflowMetadata:
    """Test that ail context --json includes workflow metadata."""

    def test_json_has_recommended_workflows(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.ail_context", "--json"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Tool failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "recommended_workflows" in data

    def test_json_has_dx_tools(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.ail_context", "--json"],
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        assert "dx_tools" in data

    def test_recommended_workflows_has_new_project(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.ail_context", "--json"],
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        workflows = data["recommended_workflows"]
        assert "new_project" in workflows
        assert "doctor" in workflows["new_project"]
        assert "run" in workflows["new_project"]

    def test_dx_tools_has_doctor(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.ail_context", "--json"],
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        assert "doctor" in data["dx_tools"]
        assert "purpose" in data["dx_tools"]["doctor"]
        assert "recommended_when" in data["dx_tools"]["doctor"]


# =============================================================================
# Heal tool
# =============================================================================


class TestHealTool:
    """Test ail heal tool."""

    def test_heal_lists_topics(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.ail_heal"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "forward_reference" in result.stdout
        assert "type_error" in result.stdout
        assert "env_setup" in result.stdout

    def test_heal_forward_reference_topic(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.ail_heal", "forward_reference"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Forward Reference" in result.stdout
        assert "bottom-up" in result.stdout.lower() or "move" in result.stdout.lower()

    def test_heal_env_setup_topic(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.ail_heal", "env_setup"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "pip install" in result.stdout

    def test_heal_unknown_topic_returns_error(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.ail_heal", "nonexistent_topic"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1


# =============================================================================
# First-run experience
# =============================================================================


class TestFirstRunExperience:
    """Test first-run state management."""

    def test_get_config_dir_returns_path(self):
        from compiler.cli.main import _get_config_dir
        config_dir = _get_config_dir()
        assert isinstance(config_dir, Path)
        assert ".ail" in str(config_dir)

    def test_state_file_persistence(self):
        from compiler.cli.main import _get_config_dir, _load_state, _save_state

        config_dir = _get_config_dir()
        state_file = config_dir / "state.json"

        # Save state
        _save_state({"onboarded": True})

        # Load state
        state = _load_state()
        assert state.get("onboarded") is True

        # Clean up
        if state_file.exists():
            state_file.unlink()


# =============================================================================
# Doctor tool: new checks
# =============================================================================


class TestDoctorNewChecks:
    """Test new ail doctor checks."""

    def test_check_python_version(self):
        from tools.ail_doctor.__main__ import check_python_version
        result = check_python_version()
        assert "current" in result
        assert "required" in result
        assert "ok" in result
        assert isinstance(result["ok"], bool)

    def test_check_stdlib_available(self):
        from tools.ail_doctor.__main__ import check_stdlib_available
        root = Path(__file__).parent.parent
        result = check_stdlib_available(root)
        assert isinstance(result, list)

    def test_check_mcp_available(self):
        from tools.ail_doctor.__main__ import check_mcp_available
        root = Path(__file__).parent.parent
        result = check_mcp_available(root)
        assert "server_exists" in result
        assert "ok" in result

    def test_check_lsp_available(self):
        from tools.ail_doctor.__main__ import check_lsp_available
        root = Path(__file__).parent.parent
        result = check_lsp_available(root)
        assert "server_exists" in result
        assert "ok" in result

    def test_check_vscode_extension(self):
        from tools.ail_doctor.__main__ import check_vscode_extension
        root = Path(__file__).parent.parent
        result = check_vscode_extension(root)
        assert "installed" in result
        assert "ok" in result

    def test_check_ail_package(self):
        from tools.ail_doctor.__main__ import check_ail_package
        result = check_ail_package()
        assert "installed" in result
        assert "ok" in result


# =============================================================================
# Path leakage prevention
# =============================================================================


class TestPathLeakagePrevention:
    """Verify no local filesystem paths leak through public interfaces."""

    def _assert_no_path_leakage(self, text: str, context: str = "") -> None:
        """Assert that text contains no developer-specific filesystem paths."""
        forbidden = [
            "C:\\Users\\",
            "C:\\Users/",
            "/Users/aleckhan",
            "/home/aleckhan",
            "AiLang_New",
            "Projects/AiLang",
            "compiler/docs/",
        ]
        for pattern in forbidden:
            assert pattern not in text, f"Path leakage in {context}: found '{pattern}'"

    def test_context_json_no_path_leakage(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.ail_context", "--json"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        self._assert_no_path_leakage(result.stdout, "ail context --json")

    def test_context_json_has_retrieval_policy(self):
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
        assert "ail docs" in str(policy["allowed"])
        assert "local filesystem access" in str(policy["forbidden"])

    def test_context_markdown_no_path_leakage(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.ail_context"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        self._assert_no_path_leakage(result.stdout, "ail context (markdown)")

    def test_doctor_no_path_leakage(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.ail_doctor"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        self._assert_no_path_leakage(result.stdout, "ail doctor")

    def test_heal_no_path_leakage(self):
        for topic in ["forward_reference", "type_error", "env_setup"]:
            result = subprocess.run(
                [sys.executable, "-m", "tools.ail_heal", topic],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            self._assert_no_path_leakage(result.stdout, f"ail heal {topic}")

    def test_benchmark_metadata_no_absolute_paths(self):
        """Benchmark dataset metadata must not contain absolute paths."""
        import json
        root = Path(__file__).parent.parent
        for meta_file in root.glob("benchmarks/datasets/*/metadata.json"):
            content = meta_file.read_text(encoding="utf-8")
            data = json.loads(content)
            for key in ["description", "path"]:
                if key in data:
                    assert "C:\\" not in data[key], f"Absolute path in {meta_file.name}:{key}"
                    assert "/Users/" not in data[key], f"Absolute path in {meta_file.name}:{key}"
                    assert "/home/" not in data[key], f"Absolute path in {meta_file.name}:{key}"
