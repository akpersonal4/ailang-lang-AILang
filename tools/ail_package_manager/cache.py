"""Package cache management — local copy, Git clone, checksum verification."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

from tools.ail_package_manager.manifest import parse_manifest
from tools.ail_package_manager.models import DependencySpec, ProjectManifest


def compute_checksum(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_dir_checksum(directory: Path) -> str:
    """Compute a combined SHA-256 checksum for all files in a directory."""
    hasher = hashlib.sha256()
    for f in sorted(directory.rglob("*")):
        if f.is_file():
            rel = f.relative_to(directory)
            hasher.update(str(rel).encode("utf-8"))
            hasher.update(f.read_bytes())
    return hasher.hexdigest()


def resolve_local_dep(
    dep: DependencySpec, project_root: Path, lib_dir: Path
) -> tuple[ProjectManifest, str]:
    """Resolve a local path dependency.

    Returns (manifest, checksum) of the resolved package.
    Raises ValueError if the path is invalid or has no manifest.
    """
    if not dep.path:
        raise ValueError(f"Dependency '{dep.name}' has no path specified")

    dep_path = (project_root / dep.path).resolve()
    if not dep_path.exists():
        raise ValueError(f"Local dependency path not found: {dep_path}")
    if not dep_path.is_dir():
        raise ValueError(f"Local dependency path is not a directory: {dep_path}")

    manifest_path = dep_path / "ail.toml"
    if not manifest_path.exists():
        raise ValueError(f"No ail.toml found in local dependency: {dep_path}")

    manifest = parse_manifest(manifest_path)
    checksum = compute_dir_checksum(dep_path)
    return manifest, checksum


def clone_git_dep(
    dep: DependencySpec, cache_dir: Path
) -> tuple[ProjectManifest, str, Path]:
    """Clone a Git dependency into the cache directory.

    Returns (manifest, checksum, clone_path).
    Raises ValueError if clone fails or no manifest found.
    """
    if not dep.git:
        raise ValueError(f"Dependency '{dep.name}' has no git URL specified")

    # Create a unique cache directory name from the URL
    url_hash = hashlib.sha256(dep.git.encode("utf-8")).hexdigest()[:16]
    clone_dir = cache_dir / f"{dep.name}-{url_hash}"

    if not clone_dir.exists():
        # Shallow clone
        cmd = ["git", "clone", "--depth", "1"]
        if dep.branch:
            cmd.extend(["--branch", dep.branch])
        elif dep.tag:
            cmd.extend(["--branch", dep.tag])
        cmd.extend([dep.git, str(clone_dir)])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            raise ValueError(f"Git clone timed out for {dep.git}")

        if result.returncode != 0:
            err = result.stderr.strip() or result.stdout.strip() or "unknown error"
            raise ValueError(f"Git clone failed for {dep.git}: {err}")

        # If a specific rev is requested, check it out
        if dep.rev:
            subprocess.run(
                ["git", "checkout", dep.rev],
                cwd=clone_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

    manifest_path = clone_dir / "ail.toml"
    if not manifest_path.exists():
        raise ValueError(f"No ail.toml found in cloned repo: {dep.git}")

    manifest = parse_manifest(manifest_path)
    checksum = compute_dir_checksum(clone_dir)
    return manifest, checksum, clone_dir


def copy_package_to_lib(source_dir: Path, lib_dir: Path, name: str) -> None:
    """Copy a package directory into lib/<name>/."""
    target = lib_dir / name
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source_dir, target)


def clean_lib(lib_dir: Path, keep: set[str]) -> None:
    """Remove packages from lib/ that are not in the keep set."""
    if not lib_dir.exists():
        return
    for item in lib_dir.iterdir():
        if item.name not in keep:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
