# AILang Developer Experience Tool: ail stdlib-audit
# M86.5B — Standard Library Audit

"""AILang Standard Library Audit — validates stdlib integrity.

Checks:
  - Exported symbols are consistent
  - No duplicate APIs across modules
  - No undocumented public APIs
  - No missing documentation for public functions
  - No broken examples in documentation
  - No deprecated interfaces
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
}


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


def _find_markdown_files(root: Path) -> list[Path]:
    """Find all markdown files."""
    files = []
    for path in root.rglob("*.md"):
        if not any(part in EXCLUDE_DIRS for part in path.parts):
            files.append(path)
    return sorted(files)


# =============================================================================
# Stdlib parsing
# =============================================================================


def parse_stdlib_modules(root: Path) -> dict[str, dict]:
    """Parse all stdlib .ail files and extract function signatures.

    Returns {module_name: {functions: {name: {params, line}}, exported: set}}
    """
    stdlib_dir = root / "stdlib"
    if not stdlib_dir.is_dir():
        return {}

    modules = {}
    for ail_file in sorted(stdlib_dir.glob("*.ail")):
        module_name = ail_file.stem
        content = _read_file(ail_file)
        if not content:
            continue

        functions = {}
        exported = set()

        for line_num, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()
            match_export = re.match(r"export\s+fn\s+(\w+)\(([^)]*)\)", stripped)
            match_fn = re.match(r"fn\s+(\w+)\(([^)]*)\)", stripped)

            if match_export:
                name = match_export.group(1)
                params = match_export.group(2).strip()
                functions[name] = {"params": params, "line": line_num}
                exported.add(name)
            elif match_fn:
                name = match_fn.group(1)
                params = match_fn.group(2).strip()
                functions[name] = {"params": params, "line": line_num}
                # In stdlib, all fn declarations are effectively exported
                exported.add(name)

        modules[module_name] = {
            "functions": functions,
            "exported": exported,
            "file": str(ail_file.relative_to(root)),
        }

    return modules


# =============================================================================
# Audit checks
# =============================================================================


def check_exported_symbols(modules: dict[str, dict]) -> list[dict]:
    """Verify exported symbols are properly defined."""
    issues = []
    for mod_name, mod_data in modules.items():
        for func_name in mod_data["exported"]:
            if func_name not in mod_data["functions"]:
                issues.append({
                    "module": mod_name,
                    "symbol": func_name,
                    "type": "exported_not_defined",
                })
    return issues


def check_duplicate_apis(modules: dict[str, dict]) -> list[dict]:
    """Check for duplicate function names across modules."""
    func_map: dict[str, list[str]] = {}
    issues = []

    for mod_name, mod_data in modules.items():
        for func_name in mod_data["functions"]:
            if func_name not in func_map:
                func_map[func_name] = []
            func_map[func_name].append(mod_name)

    for func_name, mod_list in func_map.items():
        if len(mod_list) > 1:
            issues.append({
                "function": func_name,
                "modules": mod_list,
                "type": "duplicate_api",
            })
    return issues


def check_documentation_coverage(
    modules: dict[str, dict], root: Path
) -> list[dict]:
    """Check that all public (exported) functions appear in documentation."""
    issues = []

    md_files = _find_markdown_files(root)
    doc_content = ""
    for md_file in md_files:
        content = _read_file(md_file)
        if content:
            doc_content += content + "\n"

    for mod_name, mod_data in modules.items():
        for func_name in mod_data["exported"]:
            pattern = re.compile(
                rf"{re.escape(mod_name)}\.{re.escape(func_name)}", re.IGNORECASE
            )
            if not pattern.search(doc_content):
                issues.append({
                    "module": mod_name,
                    "function": func_name,
                    "type": "undocumented_public_api",
                })

    return issues


def check_broken_doc_examples(root: Path, modules: dict[str, dict]) -> list[dict]:
    """Check code examples in stdlib documentation for correctness."""
    issues = []
    all_functions = {}
    for mod_name, mod_data in modules.items():
        for func_name in mod_data["functions"]:
            all_functions[f"{mod_name}.{func_name}"] = mod_data["functions"][func_name]

    md_files = _find_markdown_files(root)
    func_pattern = re.compile(r"(\w+)\.(\w+)\(")

    for md_file in md_files:
        rel_path = str(md_file.relative_to(root))
        if "archive" in rel_path.lower():
            continue
        content = _read_file(md_file)
        if not content:
            continue

        in_code_block = False
        for line_num, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if not in_code_block:
                continue

            for match in func_pattern.finditer(line):
                full = f"{match.group(1)}.{match.group(2)}"
                if full in all_functions:
                    pass
                elif match.group(1) in modules:
                    issues.append({
                        "file": rel_path,
                        "line": line_num,
                        "reference": full,
                        "type": "broken_doc_example",
                    })

    return issues


def check_deprecated_interfaces(modules: dict[str, dict]) -> list[dict]:
    """Check for functions marked as deprecated or containing deprecation notices."""
    issues = []
    for mod_name, mod_data in modules.items():
        ail_file = Path(mod_data["file"])
        content = _read_file(ail_file)
        if not content:
            continue

        for line_num, line in enumerate(content.split("\n"), 1):
            stripped = line.strip().lower()
            if "deprecated" in stripped or "removed in" in stripped:
                match = re.match(r"(?:export\s+)?function\s+(\w+)", line.strip())
                if match:
                    issues.append({
                        "module": mod_name,
                        "function": match.group(1),
                        "line": line_num,
                        "notice": line.strip(),
                        "type": "deprecated_interface",
                    })
    return issues


# =============================================================================
# Report generation
# =============================================================================


def generate_report(root: Path | None = None) -> tuple[str, dict]:
    """Generate the standard library audit report.

    Returns (markdown_report, json_data).
    """
    if root is None:
        root = _find_root()

    modules = parse_stdlib_modules(root)

    export_issues = check_exported_symbols(modules)
    duplicate_issues = check_duplicate_apis(modules)
    doc_issues = check_documentation_coverage(modules, root)
    example_issues = check_broken_doc_examples(root, modules)
    deprecated_issues = check_deprecated_interfaces(modules)

    total_issues = (
        len(export_issues)
        + len(duplicate_issues)
        + len(doc_issues)
        + len(example_issues)
        + len(deprecated_issues)
    )

    total_functions = sum(len(m["functions"]) for m in modules.values())
    total_exported = sum(len(m["exported"]) for m in modules.values())

    json_data = {
        "tool": "ail stdlib-audit",
        "version": "1.0.0",
        "root": str(root),
        "summary": {
            "modules": len(modules),
            "total_functions": total_functions,
            "exported_functions": total_exported,
            "total_issues": total_issues,
            "passed": total_issues == 0,
        },
        "modules": {
            name: {
                "file": data["file"],
                "function_count": len(data["functions"]),
                "exported_count": len(data["exported"]),
                "functions": sorted(data["functions"].keys()),
                "exported": sorted(data["exported"]),
            }
            for name, data in modules.items()
        },
        "export_issues": export_issues,
        "duplicate_issues": duplicate_issues,
        "documentation_issues": doc_issues,
        "example_issues": example_issues,
        "deprecated_issues": deprecated_issues,
    }

    lines = [
        "# Standard Library Audit Report",
        "",
        "_Generated by `ail stdlib-audit`_",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Modules | {len(modules)} |",
        f"| Total functions | {total_functions} |",
        f"| Exported functions | {total_exported} |",
        f"| Export issues | {len(export_issues)} |",
        f"| Duplicate APIs | {len(duplicate_issues)} |",
        f"| Undocumented APIs | {len(doc_issues)} |",
        f"| Broken examples | {len(example_issues)} |",
        f"| Deprecated interfaces | {len(deprecated_issues)} |",
        f"| **Total issues** | **{total_issues}** |",
        "",
        f"**Status:** {'PASS' if total_issues == 0 else 'FAIL'}",
        "",
        "## Module Inventory",
        "",
        "| Module | Functions | Exported |",
        "|--------|-----------|----------|",
    ]

    for name in sorted(modules.keys()):
        data = modules[name]
        lines.append(
            f"| `{name}` | {len(data['functions'])} | {len(data['exported'])} |"
        )

    lines.append("")

    if export_issues:
        lines.extend(["## Export Issues", ""])
        for issue in export_issues:
            lines.append(
                f"- `{issue['module']}` — exported `{issue['symbol']}` not defined"
            )
        lines.append("")

    if duplicate_issues:
        lines.extend(["## Duplicate APIs", ""])
        for issue in duplicate_issues:
            mods = ", ".join(f"`{m}`" for m in issue["modules"])
            lines.append(f"- `{issue['function']}()` defined in {mods}")
        lines.append("")

    if doc_issues:
        lines.extend(["## Undocumented Public APIs", ""])
        for issue in doc_issues[:30]:
            lines.append(f"- `{issue['module']}.{issue['function']}()`")
        if len(doc_issues) > 30:
            lines.append(f"- ... and {len(doc_issues) - 30} more")
        lines.append("")

    if example_issues:
        lines.extend(["## Broken Documentation Examples", ""])
        for issue in example_issues[:20]:
            lines.append(
                f"- `{issue['file']}:{issue['line']}` — `{issue['reference']}`"
            )
        if len(example_issues) > 20:
            lines.append(f"- ... and {len(example_issues) - 20} more")
        lines.append("")

    if deprecated_issues:
        lines.extend(["## Deprecated Interfaces", ""])
        for issue in deprecated_issues:
            lines.append(
                f"- `{issue['module']}.{issue['function']}()` (line {issue['line']}): {issue['notice']}"
            )
        lines.append("")

    if total_issues == 0:
        lines.append("All standard library checks passed.")
        lines.append("")

    lines.extend([
        "---",
        "_Report generated by `ail stdlib-audit`_",
        "",
    ])

    return "\n".join(lines), json_data


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ail stdlib-audit",
        description="AILang Standard Library Audit Tool",
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
