"""Package management commands: add, remove, update, list.

Each command modifies ail.toml or reads the project state.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.ail_package_manager.manifest import (
    find_manifest,
    parse_manifest,
    validate_package_name,
    validate_version,
)


def cmd_add(
    package: str,
    version: str = "*",
    path: str | None = None,
    git: str | None = None,
    tag: str | None = None,
    branch: str | None = None,
    project_dir: Path | None = None,
) -> int:
    """Add a dependency to ail.toml.

    Args:
        package: Package name, or 'name=path=...' or 'name git=...'
        version: Version requirement (default: *)
        path: Local path to package
        git: Git repository URL
        tag: Git tag to pin
        branch: Git branch to track
        project_dir: Project root (default: cwd)

    Returns:
        0 on success, 1 on error.
    """
    if project_dir is None:
        project_dir = Path.cwd()

    manifest_path = find_manifest(project_dir)
    if manifest_path is None:
        print("Error: No ail.toml found. Run 'ail new <project>' first.", flush=True)
        return 1

    # Parse the package spec
    pkg_name, pkg_version, pkg_path, pkg_git, pkg_tag, pkg_branch = _parse_package_spec(
        package, version, path, git, tag, branch
    )

    err = validate_package_name(pkg_name)
    if err:
        print(f"Error: {err}", flush=True)
        return 1

    if pkg_version != "*" and validate_version(pkg_version) is not None:
        # Allow non-semver version requirements like ">=1.0.0"
        pass

    content = manifest_path.read_text(encoding="utf-8")

    # Build the dependency line
    dep_line = _build_dependency_line(
        pkg_name, pkg_version, pkg_path, pkg_git, pkg_tag, pkg_branch
    )

    # Find or create [dependencies] section
    if "[dependencies]" in content:
        # Insert after [dependencies] header
        lines = content.split("\n")
        new_lines = []
        inserted = False
        in_deps = False
        for line in lines:
            new_lines.append(line)
            if line.strip() == "[dependencies]":
                in_deps = True
            elif in_deps and not inserted:
                # Check if next non-empty line is a new section
                if line.strip().startswith("[") and line.strip() != "[dependencies]":
                    # Insert before this section header
                    new_lines.pop()  # Remove the section header we just added
                    new_lines.append(dep_line)
                    new_lines.append("")  # blank line
                    new_lines.append(line)
                    inserted = True
                elif line.strip() == "":
                    continue
                elif not line.strip().startswith("["):
                    # We're in deps content, keep going
                    pass
        if not inserted:
            new_lines.append(dep_line)
        content = "\n".join(new_lines)
    else:
        # Add new [dependencies] section at end
        if not content.endswith("\n"):
            content += "\n"
        content += "\n[dependencies]\n" + dep_line + "\n"

    manifest_path.write_text(content, encoding="utf-8")
    print(
        f"Added dependency: {pkg_name} ({_format_dep_spec(pkg_version, pkg_path, pkg_git, pkg_tag, pkg_branch)})"
    )
    print("Run 'ail install' to install.")
    return 0


def cmd_remove(
    package: str,
    project_dir: Path | None = None,
) -> int:
    """Remove a dependency from ail.toml.

    Args:
        package: Package name to remove
        project_dir: Project root (default: cwd)

    Returns:
        0 on success, 1 on error.
    """
    if project_dir is None:
        project_dir = Path.cwd()

    manifest_path = find_manifest(project_dir)
    if manifest_path is None:
        print("Error: No ail.toml found. Run 'ail new <project>' first.", flush=True)
        return 1

    content = manifest_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    new_lines = []
    removed = False
    in_deps = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped == "[dependencies]":
            in_deps = True
            new_lines.append(line)
            i += 1
            continue

        if in_deps and stripped.startswith("[") and stripped != "[dependencies]":
            in_deps = False

        if in_deps and stripped.startswith(f'"{package}"'):
            removed = True
            i += 1
            continue

        new_lines.append(line)
        i += 1

    if not removed:
        print(f"Error: dependency '{package}' not found in ail.toml", flush=True)
        return 1

    manifest_path.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"Removed dependency: {package}")
    print("Run 'ail install' to update lib/.")
    return 0


def cmd_update(
    package: str | None = None,
    project_dir: Path | None = None,
) -> int:
    """Re-resolve dependencies and update ail.lock.

    For MVP: re-runs the install pipeline to pick up any ail.toml changes.

    Args:
        package: Specific package to update (None = all)
        project_dir: Project root (default: cwd)

    Returns:
        0 on success, 1 on error.
    """
    if project_dir is None:
        project_dir = Path.cwd()

    manifest_path = find_manifest(project_dir)
    if manifest_path is None:
        print("Error: No ail.toml found. Run 'ail new <project>' first.", flush=True)
        return 1

    if package is not None:
        err = validate_package_name(package)
        if err:
            print(f"Error: {err}", flush=True)
            return 1
        print(f"Updating {package}...")

    # Re-resolve by running install
    from tools.ail_package_manager.installer import install

    return install(
        project_root=project_dir,
        no_lock=False,
        offline=False,
        frozen_lockfile=False,
    )


def cmd_list(
    tree: bool = False,
    outdated: bool = False,
    project_dir: Path | None = None,
) -> int:
    """List installed dependencies.

    Args:
        tree: Show dependency tree
        outdated: Show outdated packages
        project_dir: Project root (default: cwd)

    Returns:
        0 on success, 1 on error.
    """
    if project_dir is None:
        project_dir = Path.cwd()

    manifest_path = find_manifest(project_dir)
    if manifest_path is None:
        print("Error: No ail.toml found. Run 'ail new <project>' first.", flush=True)
        return 1

    manifest = parse_manifest(manifest_path)
    lib_dir = project_dir / "lib"

    if not manifest.dependencies:
        print("No dependencies declared in ail.toml.")
        return 0

    print(f"Dependencies ({len(manifest.dependencies)}):")
    print()

    for name, spec in sorted(manifest.dependencies.items()):
        installed = "not installed"
        if lib_dir.is_dir():
            pkg_dir = lib_dir / name
            if pkg_dir.is_dir():
                toml_path = pkg_dir / "ail.toml"
                if toml_path.exists():
                    try:
                        installed_manifest = parse_manifest(toml_path)
                        installed = f"v{installed_manifest.version}"
                    except Exception:
                        installed = "installed (version unknown)"
                else:
                    installed = "installed"

        version_str = spec.version_req if spec.version_req else "*"
        if spec.path:
            version_str = f"path={spec.path}"
        elif spec.git:
            version_str = f"git={spec.git}"
            if spec.tag:
                version_str += f" (tag={spec.tag})"
            elif spec.branch:
                version_str += f" (branch={spec.branch})"

        status = (
            "ok" if installed.startswith("v") or installed == "installed" else installed
        )
        print(f"  {name} {version_str}  [{status}]")

    return 0


def _parse_package_spec(
    package: str,
    version: str,
    path: str | None,
    git: str | None,
    tag: str | None,
    branch: str | None,
) -> tuple[str, str, str | None, str | None, str | None, str | None]:
    """Parse a package spec into (name, version, path, git, tag, branch).

    Supports formats:
        - 'my_package@1.0.0'
        - 'my_package path=/local/path'
        - 'my_package git=https://...'
    """
    name = package
    ver = version

    # Handle name@version
    if "@" in package:
        name, ver = package.rsplit("@", 1)

    # Handle name=path=...
    path_match = re.match(r"^(\S+)\s+path=(\S+)$", package)
    if path_match:
        name = path_match.group(1)
        path = path_match.group(2)
        ver = "*"

    # Handle name git=...
    git_match = re.match(r"^(\S+)\s+git=(\S+)$", package)
    if git_match:
        name = git_match.group(1)
        git = git_match.group(2)
        ver = "*"

    return name, ver, path, git, tag, branch


def _build_dependency_line(
    name: str,
    version: str,
    path: str | None,
    git: str | None,
    tag: str | None,
    branch: str | None,
) -> str:
    """Build a TOML dependency line for ail.toml."""
    if path:
        return f'"{name}" = {{ path = "{path}" }}'
    if git:
        parts = [f'git = "{git}"']
        if tag:
            parts.append(f'tag = "{tag}"')
        if branch:
            parts.append(f'branch = "{branch}"')
        return f'"{name}" = {{ {", ".join(parts)} }}'
    return f'"{name}" = "{version}"'


def _format_dep_spec(
    version: str,
    path: str | None,
    git: str | None,
    tag: str | None,
    branch: str | None,
) -> str:
    """Format a dependency spec for display."""
    if path:
        return f"path={path}"
    if git:
        spec = f"git={git}"
        if tag:
            spec += f" tag={tag}"
        elif branch:
            spec += f" branch={branch}"
        return spec
    return version
