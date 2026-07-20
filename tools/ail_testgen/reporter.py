"""Report generation — JSON and Markdown output."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from tools.ail_testgen.models import CoverageReport


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def generate_json_report(
    coverage: CoverageReport,
    generated_files: list[dict],
    validation: dict | None = None,
    output_dir: Path | None = None,
) -> dict:
    """Build the JSON report structure (does not write to disk)."""
    report: dict[str, Any] = {
        "metadata": {
            "tool": "ail_testgen",
            "version": "0.3.0",
            "timestamp": _now(),
        },
        "summary": {
            "apps_discovered": coverage.apps_total,
            "existing_test_files": coverage.apps_with_tests,
            "tests_generated": sum(
                1 for f in generated_files if f["status"] == "generated"
            ),
            "tests_skipped": sum(
                1 for f in generated_files if f["status"] == "skipped"
            ),
            "errors": sum(1 for f in generated_files if f["status"] == "error"),
            "coverage_pct": coverage.coverage_pct,
        },
        "tests": generated_files,
        "coverage": {
            "apps_tested": coverage.apps_with_tests,
            "apps_untested": coverage.apps_without_tests,
            "untested_apps": coverage.untested_apps,
        },
    }
    if validation:
        report["validation"] = validation
    return report


def generate_markdown_report(
    coverage: CoverageReport,
    generated_files: list[dict],
) -> str:
    """Generate a Markdown report string."""
    lines = [
        "# Test Generation Report",
        "",
        "**Date:** %s" % _now(),
        "**Tool:** ail_testgen (DX-005)",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|:-----:|",
        "| Apps discovered | %d |" % coverage.apps_total,
        "| Apps with tests | %d |" % coverage.apps_with_tests,
        "| Apps without tests | %d |" % coverage.apps_without_tests,
        "| Coverage | %.1f%% |" % coverage.coverage_pct,
        "| Tests generated | %d |"
        % sum(1 for f in generated_files if f["status"] == "generated"),
        "| Tests skipped | %d |"
        % sum(1 for f in generated_files if f["status"] == "skipped"),
        "",
        "---",
        "",
        "## Generated Files",
        "",
        "| File | App | Status | Tests |",
        "|------|:---:|:------:|:-----:|",
    ]

    for f in generated_files:
        lines.append(
            "| `%s` | %s | %s | %d |"
            % (
                f.get("file", ""),
                f.get("app", ""),
                f.get("status", ""),
                f.get("test_count", 0),
            )
        )

    if coverage.untested_apps:
        lines.extend(
            [
                "",
                "---",
                "",
                "## Untested Apps",
                "",
            ]
        )
        for app in coverage.untested_apps:
            lines.append("- %s" % app)

    lines.append("")
    return "\n".join(lines)
