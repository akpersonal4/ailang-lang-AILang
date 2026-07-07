# AILang Developer Experience Tool: ail doctor
# Repository health checker - read-only diagnostic tool

"""AILang Doctor - repository health checker for AILang project."""

import os
import re
import json
import hashlib
from pathlib import Path


def get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent.parent


def read_file_safe(path: Path) -> str | None:
    """Read a file if it exists, return None otherwise. Returns None for binary/unreadable files."""
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return None
    return None


def find_markdown_files(root: Path) -> list[Path]:
    """Find all markdown files in the project (excluding .venv, .git, etc.)."""
    exclude_dirs = {".venv", ".venv_test", ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "node_modules"}
    markdown_files = []
    for path in root.rglob("*.md"):
        if not any(part in exclude_dirs for part in path.parts):
            markdown_files.append(path)
    return sorted(markdown_files)


def find_all_files(root: Path) -> list[Path]:
    """Find all files in the project for repository health analysis."""
    exclude_dirs = {".venv", ".venv_test", ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "node_modules", "__pycache__", "ailang.egg-info"}
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
        if link_target and not link_target.startswith("http") and not link_target.startswith("/") and "." not in link_target and not link_target.endswith(".md"):
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
                broken_links.append({
                    "file": str(md_file.relative_to(root)),
                    "link_text": link_text,
                    "link_target": link_target,
                })

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
                duplicates.append({
                    "original": str(file_hashes[file_hash].relative_to(root)),
                    "duplicate": str(file_path.relative_to(root)),
                    "hash": file_hash,
                })
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
                large_files.append({
                    "path": str(file_path.relative_to(root)),
                    "size_bytes": size,
                    "size_mb": round(size / 1_000_000, 2),
                })
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
            inconsistencies.append({
                "files": ["pyproject.toml", source],
                "values": [canonical, ver],
                "type": "version_mismatch",
            })

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
        if rel_path not in linked_files and rel_path not in ["README.md", "AGENTS.md", "DEVELOPMENT_STATUS.md", "PROJECT_MEMORY.md", "CHANGELOG.md"]:
            orphan_docs.append(md_file.relative_to(root))

    return orphan_docs


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

    # Compute scores (simple metric: fewer issues = higher score)
    total_issues = len(broken_links) + len(missing_files) + len(duplicate_files) + len(empty_files) + len(large_files) + len(version_issues) + len(orphan_docs)
    health_score = max(0, 100 - total_issues * 2)

    lines = [
        "# AILang Doctor Report",
        "",
        "_Auto-generated by `ail doctor` tool_",
        "",
        "## Repository Health Score",
        "",
        f"**{health_score}/100**",
        "",
        "## Documentation Health Score",
        "",
        f"**{health_score}/100**",
        "",
        "## Project Health Score",
        "",
        f"**{health_score}/100**",
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

    lines.extend([
        "## Errors",
        "",
    ])

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

    lines.extend([
        "## Recommendations",
        "",
    ])

    if orphan_docs:
        lines.append("- Consider adding references to orphan documents or archiving them")
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

    if not any([orphan_docs, version_issues, missing_files, broken_links, duplicate_files, empty_files, large_files]):
        lines.append("- Repository is healthy!")

    lines.append("")

    lines.extend([
        "## Archive Candidates",
        "",
    ])

    if orphan_docs:
        lines.append("Documents that appear to be orphaned:")
        for doc in orphan_docs[:5]:
            lines.append(f"- `{doc}`")
        if len(orphan_docs) > 5:
            lines.append(f"- ... and {len(orphan_docs) - 5} more")
    else:
        lines.append("No archive candidates identified.")

    lines.extend([
        "",
        "## Duplicate Candidates",
        "",
    ])

    if duplicate_files:
        for d in duplicate_files:
            lines.append(f"- `{d['duplicate']}` duplicates `{d['original']}`")
    else:
        lines.append("No duplicate files identified.")

    lines.extend([
        "",
        "## Missing References",
        "",
    ])

    if missing_files:
        for m in missing_files:
            lines.append(f"- `{m['expected_file']}`")
    else:
        lines.append("No missing required files.")

    lines.extend([
        "",
        "## Version Consistency",
        "",
    ])

    if version_issues:
        for v in version_issues:
            lines.append(f"- Mismatch in {v['files']}: versions {v['values']}")
    else:
        lines.append("All versions consistent.")

    lines.extend([
        "",
        "---",
        "_This report was generated by the `ail doctor` tool._",
        "",
    ])

    return "\n".join(lines)


def main() -> int:
    """Main entry point for the ail doctor tool."""
    root = get_project_root()
    output_path = root / "generated" / "DOCTOR_REPORT.md"

    # Ensure generated directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate content
    content = generate_report()

    # Write output
    output_path.write_text(content, encoding="utf-8")
    print(f"Generated: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())