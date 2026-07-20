"""Lock file (ail.lock) generation and parsing."""

from __future__ import annotations

import hashlib
from pathlib import Path

from tools.ail_package_manager.models import (
    LockFilePackage,
    ResolvedDependency,
)

_LOCK_HEADER = """\
# ail.lock — Auto-generated. Do not edit manually.
version = {version}

# input_hash = sha256 hash of ail.toml
input_hash = "{input_hash}"

"""


def compute_deps_hash(manifest_path: Path) -> str:
    """Compute SHA-256 hash of the [dependencies] section.

    Reads the raw TOML and hashes the dependencies portion.
    """
    text = manifest_path.read_text(encoding="utf-8")
    hasher = hashlib.sha256()
    hasher.update(text.encode("utf-8"))
    return hasher.hexdigest()


def deps_hash_matches(manifest_path: Path, lock_path: Path) -> bool:
    """Check if the manifest hash matches the lock file's stored hash."""
    if not lock_path.exists():
        return False
    current_hash = compute_deps_hash(manifest_path)
    stored_hash = read_input_hash(lock_path)
    return current_hash == stored_hash


def read_input_hash(lock_path: Path) -> str | None:
    """Read the input_hash value from an ail.lock file."""
    if not lock_path.exists():
        return None
    for line in lock_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("input_hash"):
            parts = line.split("=", 1)
            if len(parts) == 2:
                return parts[1].strip().strip('"')
    return None


def generate_lock(resolved: list[ResolvedDependency], manifest_path: Path) -> str:
    """Generate ail.lock content from a resolved dependency list."""
    input_hash = compute_deps_hash(manifest_path)
    lines = [_LOCK_HEADER.format(version=1, input_hash=input_hash)]

    for dep in resolved:
        lines.append("[[package]]")
        lines.append(f'name = "{dep.name}"')
        lines.append(f'resolved_version = "{dep.version}"')
        lines.append(f'source = "{dep.source}"')

        if dep.checksum:
            lines.append(f'checksum = "{dep.checksum}"')

        if dep.dependencies:
            deps_str = ", ".join(dep.dependencies)
            lines.append(f'dependencies = ["{deps_str}"]')
        else:
            lines.append("dependencies = []")

        if dep.path:
            lines.append(f'path = "{dep.path}"')
        if dep.git:
            lines.append(f'git = "{dep.git}"')
        if dep.tag:
            lines.append(f'tag = "{dep.tag}"')
        if dep.checksum and dep.source == "git":
            lines.append(f'commit = "{dep.checksum}"')

        lines.append("")  # blank line between entries

    return "\n".join(lines)


def write_lock(lock_path: Path, content: str) -> None:
    """Write lock file content to disk."""
    lock_path.write_text(content, encoding="utf-8")
    print(f"  Generated: {lock_path}")


def read_lock_packages(lock_path: Path) -> list[LockFilePackage]:
    """Parse an ail.lock file and extract package entries.

    Supports both [[package]] (M77.1) and [[packages]] (legacy) formats.
    """
    if not lock_path.exists():
        return []

    packages: list[LockFilePackage] = []
    current: dict | None = None

    for line in lock_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue

        if stripped in ("[[package]]", "[[packages]]"):
            if current is not None:
                packages.append(_dict_to_package(current))
            current = {}
            continue

        if current is not None and "=" in stripped:
            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip().strip('"')
            current[key] = value

    if current is not None:
        packages.append(_dict_to_package(current))

    return packages


def _dict_to_package(d: dict) -> LockFilePackage:
    """Convert a parsed dict to a LockFilePackage.

    Handles both [[package]] (resolved_version, commit) and
    [[packages]] (version) formats.
    """
    version = d.get("resolved_version", "") or d.get("version", "")
    deps = d.get("dependencies", "[]")
    deps = deps.strip("[]").strip()
    dep_list = (
        [d.strip().strip('"') for d in deps.split(",") if d.strip()] if deps else []
    )

    checksum = d.get("checksum", "")
    commit = d.get("commit", "")
    if not checksum and commit:
        checksum = commit

    return LockFilePackage(
        name=d.get("name", ""),
        version=version,
        source=d.get("source", ""),
        checksum=checksum,
        dependencies=dep_list,
        path=d.get("path"),
        git=d.get("git"),
        tag=d.get("tag"),
    )
