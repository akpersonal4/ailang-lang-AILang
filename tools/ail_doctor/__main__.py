# AILang Developer Experience Tool: ail doctor
# Repository health checker - read-only diagnostic tool

"""AILang Doctor - repository health checker for AILang project."""

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

from ail_platform.project import get_project_root, read_file_safe


def find_markdown_files(root: Path) -> list[Path]:
    """Find all markdown files in the project (excluding .venv, .git, etc.)."""
    exclude_dirs = {
        ".venv",
        ".venv_test",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
    }
    markdown_files = []
    for path in root.rglob("*.md"):
        if not any(part in exclude_dirs for part in path.parts):
            markdown_files.append(path)
    return sorted(markdown_files)


def find_all_files(root: Path) -> list[Path]:
    """Find all files in the project for repository health analysis."""
    exclude_dirs = {
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
    all_files = []
    for path in root.rglob("*"):
        if path.is_file() and not any(part in exclude_dirs for part in path.parts):
            all_files.append(path)
    return sorted(all_files)


def extract_markdown_links(content: str) -> list[str]:
    """Extract all markdown link targets from content."""
    # Match [text](target) pattern
    pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    matches = re.findall(pattern, content)
    # Filter out email addresses and anchor-only links
    filtered = []
    for link_text, link_target in matches:
        if link_target.startswith("mailto:"):
            continue
        # Skip if target looks like a URL without http (e.g., "url")
        if (
            link_target
            and not link_target.startswith("http")
            and not link_target.startswith("/")
            and "." not in link_target
            and not link_target.endswith(".md")
        ):
            continue
        filtered.append((link_text, link_target))
    return filtered


def check_broken_internal_links(root: Path) -> list[dict]:
    """Check for broken internal markdown links."""
    broken_links = []
    markdown_files = find_markdown_files(root)

    for md_file in markdown_files:
        content = read_file_safe(md_file)
        if not content:
            continue
        for link_text, link_target in extract_markdown_links(content):
            # Only check relative internal links (not URLs, not absolute paths)
            if link_target.startswith("http://") or link_target.startswith("https://"):
                continue
            if link_target.startswith("/"):
                continue

            # Resolve relative to the markdown file's directory
            target_path = (md_file.parent / link_target).resolve()
            if not target_path.exists():
                broken_links.append(
                    {
                        "file": str(md_file.relative_to(root)),
                        "link_text": link_text,
                        "link_target": link_target,
                    }
                )

    return broken_links


def check_missing_files(root: Path) -> list[dict]:
    """Check for missing expected files using common patterns."""
    missing = []
    expected_files = [
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "DEVELOPMENT_STATUS.md",
        "PROJECT_MEMORY.md",
        "AGENTS.md",
    ]

    for expected in expected_files:
        if not (root / expected).exists():
            missing.append({"expected_file": expected})

    return missing


def check_duplicate_files(root: Path) -> list[dict]:
    """Check for duplicate files by content hash."""
    file_hashes = {}
    duplicates = []

    all_files = find_all_files(root)
    for file_path in all_files:
        # Skip very large files
        try:
            if file_path.stat().st_size > 100 * 1024:  # 100KB limit
                continue
        except OSError:
            continue

        content = read_file_safe(file_path)
        if content:
            file_hash = hashlib.md5(content.encode()).hexdigest()
            if file_hash in file_hashes:
                duplicates.append(
                    {
                        "original": str(file_hashes[file_hash].relative_to(root)),
                        "duplicate": str(file_path.relative_to(root)),
                        "hash": file_hash,
                    }
                )
            else:
                file_hashes[file_hash] = file_path

    return duplicates


def check_empty_files(root: Path) -> list[Path]:
    """Find empty files in the project."""
    empty_files = []
    all_files = find_all_files(root)

    for file_path in all_files:
        try:
            if file_path.stat().st_size == 0:
                empty_files.append(file_path.relative_to(root))
        except OSError:
            continue

    return empty_files


def check_large_generated_files(root: Path) -> list[dict]:
    """Find large generated files (>1MB)."""
    large_files = []
    all_files = find_all_files(root)

    for file_path in all_files:
        try:
            size = file_path.stat().st_size
            if size > 1_000_000:  # 1MB
                large_files.append(
                    {
                        "path": str(file_path.relative_to(root)),
                        "size_bytes": size,
                        "size_mb": round(size / 1_000_000, 2),
                    }
                )
        except OSError:
            continue

    return large_files


def check_version_consistency(root: Path) -> list[dict]:
    """Check version consistency across key project files."""
    inconsistencies = []
    versions = {}

    # Check pyproject.toml
    pyproject_content = read_file_safe(root / "pyproject.toml")
    if pyproject_content:
        match = re.search(r'version\s*=\s*"([^"]+)"', pyproject_content)
        if match:
            versions["pyproject.toml"] = match.group(1)

    # Check README.md
    readme_content = read_file_safe(root / "README.md")
    if readme_content:
        match = re.search(r"version-(\d+\.\d+\.\d+)", readme_content)
        if match:
            versions["README.md"] = match.group(1)

    # Check PROJECT_MEMORY.md for version mentions
    pm_content = read_file_safe(root / "PROJECT_MEMORY.md")
    if pm_content:
        match = re.search(r"v(\d+\.\d+\.\d+)", pm_content)
        if match:
            versions["PROJECT_MEMORY.md"] = match.group(1)

    # Check DEVELOPMENT_STATUS.md for version mentions
    ds_content = read_file_safe(root / "DEVELOPMENT_STATUS.md")
    if ds_content:
        match = re.search(r"v(\d+\.\d+\.\d+)", ds_content)
        if match:
            versions["DEVELOPMENT_STATUS.md"] = match.group(1)

    # Check CHANGELOG.md for version mentions
    cl_content = read_file_safe(root / "CHANGELOG.md")
    if cl_content:
        match = re.search(r"v(\d+\.\d+\.\d+)", cl_content)
        if match:
            versions["CHANGELOG.md"] = match.group(1)

    # Check VSCode extension
    vscode_pkg = read_file_safe(root / "extensions" / "vscode-ailang" / "package.json")
    if vscode_pkg:
        try:
            pkg_data = json.loads(vscode_pkg)
            versions["vscode-extension"] = pkg_data.get("version", "")
        except json.JSONDecodeError:
            pass

    # Compare all versions against pyproject.toml (canonical)
    canonical = versions.get("pyproject.toml", "")
    for source, ver in versions.items():
        if source != "pyproject.toml" and ver and ver != canonical:
            inconsistencies.append(
                {
                    "files": ["pyproject.toml", source],
                    "values": [canonical, ver],
                    "type": "version_mismatch",
                }
            )

    return inconsistencies


def check_orphan_documents(root: Path) -> list[Path]:
    """Find orphan markdown documents (never referenced elsewhere)."""
    orphan_docs = []
    markdown_files = find_markdown_files(root)

    # Build set of all linked files
    linked_files = set()
    for md_file in markdown_files:
        content = read_file_safe(md_file)
        if content:
            for _, link_target in extract_markdown_links(content):
                linked_files.add(link_target)

    # Check each markdown file
    for md_file in markdown_files:
        rel_path = str(md_file.relative_to(root))
        if rel_path not in linked_files and rel_path not in [
            "README.md",
            "AGENTS.md",
            "DEVELOPMENT_STATUS.md",
            "PROJECT_MEMORY.md",
            "CHANGELOG.md",
        ]:
            orphan_docs.append(md_file.relative_to(root))

    return orphan_docs


def check_python_version() -> dict:
    """Check Python version compatibility."""
    version = sys.version_info
    required = (3, 11)
    return {
        "current": f"{version.major}.{version.minor}.{version.micro}",
        "required": f"{required[0]}.{required[1]}",
        "ok": version >= required,
    }


def check_stdlib_available(root: Path) -> list[dict]:
    """Check if standard library modules are available."""
    missing = []
    expected = [
        "stdlib/io.ail",
        "stdlib/list.ail",
        "stdlib/map.ail",
        "stdlib/string.ail",
        "stdlib/math.ail",
        "stdlib/json.ail",
        "stdlib/system.ail",
        "stdlib/convert.ail",
        "stdlib/environment.ail",
    ]
    for mod in expected:
        if not (root / mod).exists():
            missing.append({"module": mod})
    return missing


def check_docs_available(root: Path) -> list[dict]:
    """Check if embedded documentation is available."""
    missing = []
    docs_dir = root / "compiler" / "docs"
    expected = ["AGENTS.md", "LANGUAGE_SPEC.md", "STDLIB_REFERENCE.md"]
    for doc in expected:
        if not (docs_dir / doc).exists():
            missing.append({"document": doc})
    return missing


def check_mcp_available(root: Path) -> dict:
    """Check if MCP server is available."""
    mcp_dir = root / "tools" / "ail_mcp"
    server_exists = (mcp_dir / "server.py").exists()
    adapter_exists = (mcp_dir / "context_adapter.py").exists()
    return {
        "server_exists": server_exists,
        "adapter_exists": adapter_exists,
        "ok": server_exists and adapter_exists,
    }


def check_lsp_available(root: Path) -> dict:
    """Check if LSP server is available."""
    lsp_dir = root / "compiler" / "lsp"
    server_exists = (lsp_dir / "server.py").exists()
    return {
        "server_exists": server_exists,
        "ok": server_exists,
    }


def check_ail_on_path() -> dict:
    """Check if 'ail' command is on PATH."""
    ail_path = shutil.which("ail")
    return {
        "found": ail_path is not None,
    }


def check_vscode_extension(root: Path) -> dict:
    """Check if VS Code extension is available."""
    ext_dir = root / "extensions" / "vscode-ailang"
    pkg_file = ext_dir / "package.json"
    if not pkg_file.exists():
        return {"installed": False, "ok": False}
    content = read_file_safe(pkg_file)
    if not content:
        return {"installed": False, "ok": False}
    try:
        pkg = json.loads(content)
        return {
            "installed": True,
            "version": pkg.get("version", "unknown"),
            "ok": True,
        }
    except json.JSONDecodeError:
        return {"installed": True, "version": "parse_error", "ok": False}


def check_ail_package() -> dict:
    """Check if the ailang Python package is installed."""
    try:
        import ailang

        return {
            "installed": True,
            "version": getattr(ailang, "__version__", "unknown"),
            "ok": True,
        }
    except ImportError:
        return {"installed": False, "version": None, "ok": False}


def generate_report() -> str:
    """Generate the DOCTOR_REPORT.md content."""
    root = get_project_root()

    # Gather all check results
    broken_links = check_broken_internal_links(root)
    missing_files = check_missing_files(root)
    duplicate_files = check_duplicate_files(root)
    empty_files = check_empty_files(root)
    large_files = check_large_generated_files(root)
    version_issues = check_version_consistency(root)
    orphan_docs = check_orphan_documents(root)
    python_version = check_python_version()
    stdlib_missing = check_stdlib_available(root)
    docs_missing = check_docs_available(root)
    mcp = check_mcp_available(root)
    lsp = check_lsp_available(root)
    ail_path = check_ail_on_path()
    vscode = check_vscode_extension(root)
    ail_pkg = check_ail_package()

    # Compute scores (simple metric: fewer issues = higher score)
    issues = (
        len(broken_links)
        + len(missing_files)
        + len(duplicate_files)
        + len(empty_files)
        + len(large_files)
        + len(version_issues)
        + len(orphan_docs)
        + len(stdlib_missing)
        + len(docs_missing)
    )
    if not python_version["ok"]:
        issues += 3
    if not mcp["ok"]:
        issues += 2
    if not lsp["ok"]:
        issues += 2
    if not ail_path["found"]:
        issues += 2
    if not vscode["ok"]:
        issues += 1
    if not ail_pkg["ok"]:
        issues += 2

    health_score = max(0, 100 - issues * 2)

    lines = [
        "# AILang Doctor Report",
        "",
        "_Auto-generated by `ail doctor` tool_",
        "",
        "## Repository Health Score",
        "",
        f"**{health_score}/100**",
        "",
        "## Environment",
        "",
        f"- **Python**: {python_version['current']} {'OK' if python_version['ok'] else 'ERROR: need ' + python_version['required'] + '+'}",
        f"- **ail CLI**: {'OK' if ail_path['found'] else 'NOT ON PATH (run: pip install -e .)'}",
        f"- **ailang package**: {'v' + ail_pkg['version'] if ail_pkg['ok'] else 'NOT INSTALLED (run: pip install -e .)'}",
        f"- **VS Code extension**: {'v' + vscode.get('version', '?') if vscode['ok'] else 'NOT INSTALLED'}",
        "",
        "## Components",
        "",
        f"- **MCP server**: {'OK' if mcp['ok'] else 'MISSING'}",
        f"- **LSP server**: {'OK' if lsp['ok'] else 'MISSING'}",
        f"- **Embedded docs**: {'OK' if not docs_missing else 'MISSING: ' + ', '.join(d['document'] for d in docs_missing)}",
        f"- **Standard library**: {'OK' if not stdlib_missing else 'MISSING: ' + ', '.join(d['module'] for d in stdlib_missing)}",
        "",
        "## Warnings",
        "",
    ]

    if orphan_docs:
        lines.append("### Orphan Documents")
        for doc in orphan_docs[:10]:
            lines.append(f"- `{doc}`")
        if len(orphan_docs) > 10:
            lines.append(f"- ... and {len(orphan_docs) - 10} more")
        lines.append("")

    if large_files:
        lines.append("### Large Generated Files")
        for f in large_files:
            lines.append(f"- `{f['path']}` ({f['size_mb']} MB)")
        lines.append("")

    lines.extend(
        [
            "## Errors",
            "",
        ]
    )

    if missing_files:
        lines.append("### Missing Required Files")
        for m in missing_files:
            lines.append(f"- `{m['expected_file']}`")
        lines.append("")

    if broken_links:
        lines.append("### Broken Internal Links")
        for b in broken_links[:10]:
            lines.append(f"- `{b['file']}`: [{b['link_text']}]({b['link_target']})")
        if len(broken_links) > 10:
            lines.append(f"- ... and {len(broken_links) - 10} more broken links")
        lines.append("")

    lines.extend(
        [
            "## Recommendations",
            "",
        ]
    )

    if orphan_docs:
        lines.append(
            "- Consider adding references to orphan documents or archiving them"
        )
    if version_issues:
        lines.append("- Sync version numbers across project files")
    if missing_files:
        lines.append("- Add missing required project files")
    if broken_links:
        lines.append("- Fix broken internal markdown links")
    if duplicate_files:
        lines.append("- Review duplicate files for consolidation or removal")
    if empty_files:
        lines.append("- Remove or populate empty files")
    if large_files:
        lines.append("- Consider splitting or archiving large generated files")
    if not python_version["ok"]:
        lines.append(
            f"- Upgrade Python to {python_version['required']}+ (current: {python_version['current']})"
        )
    if stdlib_missing:
        lines.append(
            "- Run `ail new <project>` to generate stdlib, or copy from existing project"
        )
    if docs_missing:
        lines.append("- Reinstall ailang: `pip install -e .` to restore embedded docs")
    if not mcp["ok"]:
        lines.append("- Ensure tools/ail_mcp/ directory exists with server.py")
    if not lsp["ok"]:
        lines.append("- Ensure compiler/lsp/ directory exists with server.py")
    if not ail_path["found"]:
        lines.append("- Install ail CLI: `pip install -e .` or check PATH")
    if not vscode["ok"]:
        lines.append(
            "- Install VS Code extension: `cd extensions/vscode-ailang && npm install && npm run package`"
        )
    if not ail_pkg["ok"]:
        lines.append("- Install ailang package: `pip install -e .`")

    if not any(
        [
            orphan_docs,
            version_issues,
            missing_files,
            broken_links,
            duplicate_files,
            empty_files,
            large_files,
            stdlib_missing,
            docs_missing,
            not python_version["ok"],
            not mcp["ok"],
            not lsp["ok"],
            not ail_path["found"],
            not vscode["ok"],
            not ail_pkg["ok"],
        ]
    ):
        lines.append("- Repository is healthy!")

    lines.append("")

    lines.extend(
        [
            "## Archive Candidates",
            "",
        ]
    )

    if orphan_docs:
        lines.append("Documents that appear to be orphaned:")
        for doc in orphan_docs[:5]:
            lines.append(f"- `{doc}`")
        if len(orphan_docs) > 5:
            lines.append(f"- ... and {len(orphan_docs) - 5} more")
    else:
        lines.append("No archive candidates identified.")

    lines.extend(
        [
            "",
            "## Duplicate Candidates",
            "",
        ]
    )

    if duplicate_files:
        for d in duplicate_files:
            lines.append(f"- `{d['duplicate']}` duplicates `{d['original']}`")
    else:
        lines.append("No duplicate files identified.")

    lines.extend(
        [
            "",
            "## Missing References",
            "",
        ]
    )

    if missing_files:
        for m in missing_files:
            lines.append(f"- `{m['expected_file']}`")
    else:
        lines.append("No missing required files.")

    lines.extend(
        [
            "",
            "## Version Consistency",
            "",
        ]
    )

    if version_issues:
        for v in version_issues:
            lines.append(f"- Mismatch in {v['files']}: versions {v['values']}")
    else:
        lines.append("All versions consistent.")

    lines.extend(
        [
            "",
            "## Next Steps",
            "",
        ]
    )

    if issues == 0:
        lines.append("Your environment is healthy! Try:")
        lines.append("")
        lines.append("  ail docs AGENTS         # Read the AI agent instructions")
        lines.append(
            "  ail context --json      # Get machine-readable language context"
        )
        lines.append("  ail new myproject       # Create a new project")
    else:
        lines.append("Fix the issues above, then re-run `ail doctor` to verify.")
        lines.append("If problems persist, run `ail heal` for diagnostic guidance.")

    lines.extend(
        [
            "",
            "---",
            "_This report was generated by the `ail doctor` tool._",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    """Main entry point for the ail doctor tool."""
    content = generate_report()
    print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
