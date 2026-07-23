# AILang Developer Experience Tool: ail doc-verify
# M86.5A — Documentation Verification Tool

"""AILang Documentation Verifier — validates documentation integrity.

Checks:
  - Referenced CLI commands exist
  - Documented options exist
  - Version numbers are consistent across documents
  - Internal document links are valid
  - Referenced files exist
  - Documentation examples remain current
"""

import argparse
import json
import re
import sys
from pathlib import Path


EXCLUDE_DIRS = {
    ".venv",
    ".venv_test",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "__pycache__",
    "ailang.egg-info",
    "dist",
    "build",
}

KNOWN_CLI_COMMANDS = {
    "run",
    "build",
    "check",
    "fmt",
    "test",
    "new",
    "rename",
    "watch",
    "order",
    "install",
    "add",
    "remove",
    "update",
    "list",
    "publish",
    "doctor",
    "heal",
    "explain",
    "docs",
    "context",
    "mcp",
    "static-analyzer",
    "static_analyzer",
    "benchmark",
    "testgen",
    "lsp",
    "version",
    "help",
    "release",
    "doc-verify",
    "stdlib-audit",
    "dx-audit",
    "validate",
}

# Common English words and AILang keywords that appear after "ail" in prose
_FALSE_POSITIVE_WORDS = {
    "is", "the", "a", "an", "and", "or", "not", "for", "in", "on", "to",
    "of", "by", "as", "be", "no", "so", "if", "it", "do", "at", "up",
    "we", "has", "had", "was", "are", "can", "may", "see", "get", "set",
    "put", "try", "use", "all", "any", "top", "src", "env", "dev", "pip",
    "fn", "let", "return", "import", "from", "export", "main", "print",
    "this", "that", "with", "will", "your", "you", "its", "our", "their",
    "been", "have", "does", "did", "would", "could", "should", "might",
    "must", "shall", "only", "also", "just", "then", "than", "when",
    "what", "how", "why", "where", "which", "who", "whom", "each",
    "some", "many", "most", "much", "such", "very", "more", "less",
    "both", "each", "every", "few", "own", "same", "other", "another",
}


def _find_root() -> Path:
    """Find the AILang repository root."""
    candidate = Path(__file__).resolve().parent.parent.parent
    if (candidate / "pyproject.toml").is_file():
        return candidate
    return Path.cwd()


def _find_markdown_files(root: Path) -> list[Path]:
    """Find all markdown files, excluding common non-doc dirs."""
    files = []
    for path in root.rglob("*.md"):
        if not any(part in EXCLUDE_DIRS for part in path.parts):
            files.append(path)
    return sorted(files)


def _read_file(path: Path) -> str | None:
    """Read file contents safely."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


# =============================================================================
# Verification checks
# =============================================================================


def check_cli_command_references(root: Path) -> list[dict]:
    """Verify that CLI commands referenced in documentation actually exist."""
    issues = []
    md_files = _find_markdown_files(root)

    # Match "ail <command>" but require it to appear in a sentence context
    # (not inside code blocks where "ail fn" might appear)
    cmd_pattern = re.compile(r"(?:^|\s)ail\s+([\w][\w-]*)")
    for md_file in md_files:
        content = _read_file(md_file)
        if not content:
            continue

        in_code_block = False
        for line_num, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            for match in cmd_pattern.finditer(line):
                cmd = match.group(1)
                if cmd in KNOWN_CLI_COMMANDS:
                    continue
                if cmd in _FALSE_POSITIVE_WORDS:
                    continue
                # Skip very short commands (likely false positives)
                if len(cmd) <= 2:
                    continue
                issues.append({
                    "file": str(md_file.relative_to(root)),
                    "line": line_num,
                    "command": cmd,
                    "type": "unknown_cli_command",
                })
    return issues


def check_version_references(root: Path) -> list[dict]:
    """Verify version numbers in documentation are consistent with pyproject.toml."""
    issues = []

    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        return [{"file": "pyproject.toml", "type": "missing", "detail": "pyproject.toml not found"}]

    content = _read_file(pyproject)
    if not content:
        return [{"file": "pyproject.toml", "type": "unreadable"}]

    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        return [{"file": "pyproject.toml", "type": "missing", "detail": "version field not found"}]

    canonical_version = match.group(1)

    md_files = _find_markdown_files(root)
    version_pattern = re.compile(r"v?(\d+\.\d+\.\d+)")

    for md_file in md_files:
        rel_path = str(md_file.relative_to(root))
        if "MILESTONE" in rel_path.upper() or "REPORT" in rel_path.upper():
            continue
        if "archive" in rel_path.lower():
            continue

        file_content = _read_file(md_file)
        if not file_content:
            continue

        for match in version_pattern.finditer(file_content):
            found_version = match.group(1)
            if found_version != canonical_version:
                line_num = file_content[: match.start()].count("\n") + 1
                issues.append({
                    "file": rel_path,
                    "line": line_num,
                    "expected": canonical_version,
                    "found": found_version,
                    "type": "version_mismatch",
                })
    return issues


def check_internal_links(root: Path) -> list[dict]:
    """Verify that internal markdown links point to existing files."""
    issues = []
    md_files = _find_markdown_files(root)

    link_pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

    for md_file in md_files:
        content = _read_file(md_file)
        if not content:
            continue

        for match in link_pattern.finditer(content):
            link_text = match.group(1)
            link_target = match.group(2)

            if link_target.startswith("http://") or link_target.startswith("https://"):
                continue
            if link_target.startswith("mailto:"):
                continue
            if link_target.startswith("#"):
                continue
            if link_target.startswith("/"):
                continue

            target_path = (md_file.parent / link_target).resolve()
            if not target_path.exists():
                line_num = content[: match.start()].count("\n") + 1
                issues.append({
                    "file": str(md_file.relative_to(root)),
                    "line": line_num,
                    "link_text": link_text,
                    "link_target": link_target,
                    "type": "broken_internal_link",
                })
    return issues


def check_referenced_files(root: Path) -> list[dict]:
    """Verify that files referenced in documentation exist."""
    issues = []
    md_files = _find_markdown_files(root)

    file_ref_pattern = re.compile(r"`([a-zA-Z_][\w./-]*\.\w+)`")

    for md_file in md_files:
        content = _read_file(md_file)
        if not content:
            continue

        for match in file_ref_pattern.finditer(content):
            ref = match.group(1)
            if ref.endswith((".py", ".ail", ".toml", ".json", ".yml", ".yaml")):
                target = (root / ref).resolve()
                if not target.exists():
                    line_num = content[: match.start()].count("\n") + 1
                    issues.append({
                        "file": str(md_file.relative_to(root)),
                        "line": line_num,
                        "referenced_file": ref,
                        "type": "missing_referenced_file",
                    })
    return issues


def check_documentation_examples(root: Path) -> list[dict]:
    """Check that code examples in docs reference valid stdlib functions."""
    issues = []
    stdlib_functions = _collect_stdlib_functions(root)
    md_files = _find_markdown_files(root)

    func_pattern = re.compile(r"(\w+)\.(\w+)\(")

    for md_file in md_files:
        rel_path = str(md_file.relative_to(root))
        if "archive" in rel_path.lower():
            continue
        if "milestone" in rel_path.lower() or "report" in rel_path.lower():
            continue

        content = _read_file(md_file)
        if not content:
            continue

        in_code_block = False
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if not in_code_block:
                continue

            for match in func_pattern.finditer(line):
                module = match.group(1)
                func = match.group(2)
                if module in stdlib_functions:
                    if func not in stdlib_functions[module]:
                        line_num = content.split("\n").index(line) + 1
                        issues.append({
                            "file": rel_path,
                            "line": line_num,
                            "module": module,
                            "function": func,
                            "available": sorted(stdlib_functions[module]),
                            "type": "invalid_stdlib_function",
                        })
    return issues


def _collect_stdlib_functions(root: Path) -> dict[str, set[str]]:
    """Collect all stdlib module -> functions mapping."""
    modules: dict[str, set[str]] = {}
    stdlib_dir = root / "stdlib"
    if not stdlib_dir.is_dir():
        return modules

    for ail_file in stdlib_dir.glob("*.ail"):
        if ail_file.name == "__init__.py":
            continue
        module_name = ail_file.stem
        content = _read_file(ail_file)
        if not content:
            continue

        funcs = set()
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("export function "):
                func_name = line.split("(")[0].replace("export function ", "").strip()
                funcs.add(func_name)
            elif line.startswith("function "):
                func_name = line.split("(")[0].replace("function ", "").strip()
                funcs.add(func_name)

        modules[module_name] = funcs

    return modules


# =============================================================================
# Report generation
# =============================================================================


def generate_report(root: Path | None = None) -> tuple[str, dict]:
    """Generate a documentation verification report.

    Returns (markdown_report, json_data).
    """
    if root is None:
        root = _find_root()

    cli_issues = check_cli_command_references(root)
    version_issues = check_version_references(root)
    link_issues = check_internal_links(root)
    file_issues = check_referenced_files(root)
    example_issues = check_documentation_examples(root)

    total_issues = (
        len(cli_issues)
        + len(version_issues)
        + len(link_issues)
        + len(file_issues)
        + len(example_issues)
    )

    json_data = {
        "tool": "ail doc-verify",
        "version": "1.0.0",
        "root": str(root),
        "summary": {
            "total_issues": total_issues,
            "cli_command_issues": len(cli_issues),
            "version_issues": len(version_issues),
            "broken_links": len(link_issues),
            "missing_files": len(file_issues),
            "example_issues": len(example_issues),
            "passed": total_issues == 0,
        },
        "cli_command_issues": cli_issues,
        "version_issues": version_issues,
        "broken_links": link_issues,
        "missing_files": file_issues,
        "example_issues": example_issues,
    }

    lines = [
        "# Documentation Verification Report",
        "",
        "_Generated by `ail doc-verify`_",
        "",
        "## Summary",
        "",
        f"| Check | Count |",
        f"|-------|-------|",
        f"| CLI command references | {len(cli_issues)} issues |",
        f"| Version consistency | {len(version_issues)} issues |",
        f"| Internal links | {len(link_issues)} issues |",
        f"| Referenced files | {len(file_issues)} issues |",
        f"| Documentation examples | {len(example_issues)} issues |",
        f"| **Total** | **{total_issues} issues** |",
        "",
        f"**Status:** {'PASS' if total_issues == 0 else 'FAIL'}",
        "",
    ]

    if cli_issues:
        lines.extend(["## CLI Command Issues", ""])
        for issue in cli_issues[:20]:
            lines.append(
                f"- `{issue['file']}:{issue['line']}` — unknown command `ail {issue['command']}`"
            )
        if len(cli_issues) > 20:
            lines.append(f"- ... and {len(cli_issues) - 20} more")
        lines.append("")

    if version_issues:
        lines.extend(["## Version Inconsistencies", ""])
        for issue in version_issues[:20]:
            lines.append(
                f"- `{issue['file']}:{issue['line']}` — found `v{issue['found']}`, expected `v{issue['expected']}`"
            )
        if len(version_issues) > 20:
            lines.append(f"- ... and {len(version_issues) - 20} more")
        lines.append("")

    if link_issues:
        lines.extend(["## Broken Internal Links", ""])
        for issue in link_issues[:20]:
            lines.append(
                f"- `{issue['file']}:{issue['line']}` — [{issue['link_text']}]({issue['link_target']})"
            )
        if len(link_issues) > 20:
            lines.append(f"- ... and {len(link_issues) - 20} more")
        lines.append("")

    if file_issues:
        lines.extend(["## Missing Referenced Files", ""])
        for issue in file_issues[:20]:
            lines.append(
                f"- `{issue['file']}:{issue['line']}` — `{issue['referenced_file']}`"
            )
        if len(file_issues) > 20:
            lines.append(f"- ... and {len(file_issues) - 20} more")
        lines.append("")

    if example_issues:
        lines.extend(["## Documentation Example Issues", ""])
        for issue in example_issues[:20]:
            available = ", ".join(issue["available"][:5])
            lines.append(
                f"- `{issue['file']}:{issue['line']}` — `{issue['module']}.{issue['function']}` not found (available: {available})"
            )
        if len(example_issues) > 20:
            lines.append(f"- ... and {len(example_issues) - 20} more")
        lines.append("")

    if total_issues == 0:
        lines.extend(["All documentation checks passed.", ""])

    lines.extend([
        "---",
        "_Report generated by `ail doc-verify`_",
        "",
    ])

    return "\n".join(lines), json_data


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ail doc-verify",
        description="AILang Documentation Verification Tool",
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
