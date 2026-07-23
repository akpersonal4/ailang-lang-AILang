# AILang Developer Experience Tool: ail dx-audit
# M86.5D — Developer Experience Audit

"""AILang Developer Experience Audit — reviews CLI and developer workflow.

Reviews:
  - CLI command naming consistency
  - Help output quality
  - Error message quality
  - Documentation discoverability
  - Installation experience

Generates recommendations only. No redesign.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def _find_root() -> Path:
    """Find the AILang repository root."""
    candidate = Path(__file__).resolve().parent.parent.parent
    if (candidate / "pyproject.toml").is_file():
        return candidate
    return Path.cwd()


def _read_file(path: Path) -> str | None:
    """Read file contents safely."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def _run_command(cmd: list[str], cwd: str | None = None, timeout: int = 30) -> dict:
    """Run a command and return stdout, stderr, returncode."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "timeout", "returncode": -1}
    except FileNotFoundError:
        return {"stdout": "", "stderr": "command not found", "returncode": -1}


# =============================================================================
# Audit checks
# =============================================================================


def audit_cli_command_naming(root: Path) -> list[dict]:
    """Review CLI command naming conventions."""
    recommendations = []

    cli_path = root / "compiler" / "cli" / "main.py"
    content = _read_file(cli_path)
    if not content:
        return [{"severity": "error", "message": "Cannot read CLI entry point"}]

    has_hyphenated = "static-analyzer" in content
    has_underscored = "static_analyzer" in content
    if has_hyphenated and has_underscored:
        recommendations.append({
            "severity": "info",
            "area": "naming",
            "message": "static-analyzer and static_analyzer both exist as aliases (acceptable)",
        })

    commands = re.findall(r'"(\w[\w-]*)":\s*cmd_', content)
    for cmd in commands:
        if "_" in cmd and "-" in cmd:
            recommendations.append({
                "severity": "warning",
                "area": "naming",
                "message": f"Command '{cmd}' uses mixed separators",
            })

    return recommendations


def audit_help_output(root: Path) -> list[dict]:
    """Review help output quality."""
    recommendations = []

    result = _run_command(["ail", "help"], cwd=str(root))
    if result["returncode"] != 0:
        recommendations.append({
            "severity": "error",
            "area": "help",
            "message": "'ail help' returned non-zero exit code",
        })
        return recommendations

    output = result["stdout"]
    if not output:
        recommendations.append({
            "severity": "error",
            "area": "help",
            "message": "'ail help' produced no output",
        })
        return recommendations

    if "Usage:" not in output:
        recommendations.append({
            "severity": "warning",
            "area": "help",
            "message": "Help output missing 'Usage:' section",
        })

    if "Commands:" not in output:
        recommendations.append({
            "severity": "warning",
            "area": "help",
            "message": "Help output missing 'Commands:' section",
        })

    if "Examples:" not in output:
        recommendations.append({
            "severity": "info",
            "area": "help",
            "message": "Help output missing 'Examples:' section",
        })

    return recommendations


def audit_error_messages(root: Path) -> list[dict]:
    """Test error message quality for common failure cases."""
    recommendations = []

    error_cases = [
        {
            "cmd": ["ail", "run", "nonexistent.ail"],
            "expect": "should mention file not found",
            "pattern": r"(not found|No such|does not exist|Error)",
        },
        {
            "cmd": ["ail", "build", "nonexistent.ail"],
            "expect": "should mention file not found",
            "pattern": r"(not found|No such|does not exist|Error)",
        },
        {
            "cmd": ["ail", "--nonexistent-flag"],
            "expect": "should mention unknown option",
            "pattern": r"(unknown|Error|usage)",
        },
    ]

    for case in error_cases:
        result = _run_command(case["cmd"], cwd=str(root))
        if result["returncode"] == 0:
            recommendations.append({
                "severity": "warning",
                "area": "errors",
                "message": f"Command {' '.join(case['cmd'])} should fail but returned 0",
            })
        elif result["returncode"] != 0:
            output = result["stderr"] + result["stdout"]
            if output and re.search(case["pattern"], output, re.IGNORECASE):
                pass
            else:
                recommendations.append({
                    "severity": "info",
                    "area": "errors",
                    "message": f"Command {' '.join(case['cmd'])}: error output lacks clear message",
                })

    return recommendations


def audit_documentation_discoverability(root: Path) -> list[dict]:
    """Review documentation discoverability."""
    recommendations = []

    readme_path = root / "README.md"
    readme = _read_file(readme_path)
    if readme:
        if "ail docs" not in readme:
            recommendations.append({
                "severity": "info",
                "area": "discoverability",
                "message": "README.md does not mention 'ail docs' command",
            })
        if "ail context" not in readme:
            recommendations.append({
                "severity": "info",
                "area": "discoverability",
                "message": "README.md does not mention 'ail context' command",
            })
        if "Quick Start" not in readme and "Getting Started" not in readme:
            recommendations.append({
                "severity": "info",
                "area": "discoverability",
                "message": "README.md lacks a Quick Start / Getting Started section",
            })

    getting_started = root / "docs" / "reference" / "GETTING_STARTED.md"
    if not getting_started.is_file():
        recommendations.append({
            "severity": "info",
            "area": "discoverability",
            "message": "docs/reference/GETTING_STARTED.md not found",
        })

    return recommendations


def audit_installation_experience(root: Path) -> list[dict]:
    """Review installation experience."""
    recommendations = []

    pyproject_path = root / "pyproject.toml"
    content = _read_file(pyproject_path)
    if not content:
        return [{"severity": "error", "area": "installation", "message": "pyproject.toml not found"}]

    import tomllib
    data = tomllib.loads(content)

    project = data.get("project", {})
    if not project.get("readme"):
        recommendations.append({
            "severity": "warning",
            "area": "installation",
            "message": "pyproject.toml missing 'readme' field",
        })

    deps = project.get("dependencies", [])
    if not deps:
        recommendations.append({
            "severity": "info",
            "area": "installation",
            "message": "No runtime dependencies declared (only watchdog is needed)",
        })

    optional = project.get("optional-dependencies", {})
    if "dev" not in optional:
        recommendations.append({
            "severity": "info",
            "area": "installation",
            "message": "No 'dev' optional dependency group found",
        })

    scripts = data.get("project.scripts", {})
    if "ail" not in scripts:
        recommendations.append({
            "severity": "error",
            "area": "installation",
            "message": "No 'ail' entry point in pyproject.toml",
        })

    return recommendations


def audit_cli_consistency(root: Path) -> list[dict]:
    """Review overall CLI consistency."""
    recommendations = []

    result = _run_command(["ail", "help"], cwd=str(root))
    if result["returncode"] != 0:
        return [{"severity": "error", "area": "consistency", "message": "ail help failed"}]

    output = result["stdout"]

    help_commands = set()
    for line in output.split("\n"):
        match = re.match(r"\s+(\w[\w-]*)\s{2,}", line)
        if match:
            help_commands.add(match.group(1))

    cli_path = root / "compiler" / "cli" / "main.py"
    cli_content = _read_file(cli_path)
    if cli_content:
        dispatch_commands = set()
        for match in re.finditer(r'"(\w[\w-]*)":\s*cmd_', cli_content):
            cmd = match.group(1)
            if not cmd.startswith("_"):
                dispatch_commands.add(cmd)

        missing_from_help = dispatch_commands - help_commands
        for cmd in sorted(missing_from_help):
            if cmd not in ("help", "version"):
                recommendations.append({
                    "severity": "info",
                    "area": "consistency",
                    "message": f"Command '{cmd}' in dispatch table but missing from help output",
                })

    return recommendations


# =============================================================================
# Report generation
# =============================================================================


def generate_report(root: Path | None = None) -> tuple[str, dict]:
    """Generate the DX audit report.

    Returns (markdown_report, json_data).
    """
    if root is None:
        root = _find_root()

    naming = audit_cli_command_naming(root)
    help_audit = audit_help_output(root)
    error_audit = audit_error_messages(root)
    discoverability = audit_documentation_discoverability(root)
    installation = audit_installation_experience(root)
    consistency = audit_cli_consistency(root)

    all_recommendations = (
        naming + help_audit + error_audit + discoverability + installation + consistency
    )

    severity_counts = {
        "error": sum(1 for r in all_recommendations if r["severity"] == "error"),
        "warning": sum(1 for r in all_recommendations if r["severity"] == "warning"),
        "info": sum(1 for r in all_recommendations if r["severity"] == "info"),
    }

    json_data = {
        "tool": "ail dx-audit",
        "version": "1.0.0",
        "root": str(root),
        "summary": {
            "total_recommendations": len(all_recommendations),
            "errors": severity_counts["error"],
            "warnings": severity_counts["warning"],
            "info": severity_counts["info"],
            "passed": severity_counts["error"] == 0,
        },
        "recommendations": {
            "naming": naming,
            "help": help_audit,
            "errors": error_audit,
            "discoverability": discoverability,
            "installation": installation,
            "consistency": consistency,
        },
    }

    lines = [
        "# Developer Experience Audit Report",
        "",
        "_Generated by `ail dx-audit`_",
        "",
        "## Summary",
        "",
        f"| Category | Recommendations |",
        f"|----------|----------------|",
        f"| CLI naming | {len(naming)} |",
        f"| Help output | {len(help_audit)} |",
        f"| Error messages | {len(error_audit)} |",
        f"| Documentation discoverability | {len(discoverability)} |",
        f"| Installation experience | {len(installation)} |",
        f"| CLI consistency | {len(consistency)} |",
        f"| **Total** | **{len(all_recommendations)}** |",
        "",
        f"**Errors:** {severity_counts['error']} | "
        f"**Warnings:** {severity_counts['warning']} | "
        f"**Info:** {severity_counts['info']}",
        "",
    ]

    areas = [
        ("CLI Naming", naming),
        ("Help Output", help_audit),
        ("Error Messages", error_audit),
        ("Documentation Discoverability", discoverability),
        ("Installation Experience", installation),
        ("CLI Consistency", consistency),
    ]

    for area_name, recs in areas:
        if recs:
            lines.extend([f"## {area_name}", ""])
            for rec in recs:
                icon = {"error": "ERROR", "warning": "WARN", "info": "INFO"}[rec["severity"]]
                lines.append(f"- [{icon}] {rec['message']}")
            lines.append("")

    if not all_recommendations:
        lines.append("No recommendations — CLI and DX are in good shape.")
        lines.append("")

    lines.extend([
        "---",
        "_Report generated by `ail dx-audit`_",
        "",
    ])

    return "\n".join(lines), json_data


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ail dx-audit",
        description="AILang Developer Experience Audit (recommendations only)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write report to file",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="Repository root directory",
    )

    args = parser.parse_args()
    root = Path(args.root) if args.root else None

    report, json_data = generate_report(root)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if args.json:
            out_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
        else:
            out_path.write_text(report, encoding="utf-8")
        print(f"Report written to {out_path}")
    elif args.json:
        print(json.dumps(json_data, indent=2))
    else:
        print(report)

    return 0 if json_data["summary"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
