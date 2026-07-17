"""Installation engine — orchestrates resolution, caching, lock generation."""

from __future__ import annotations

import shutil
from pathlib import Path

from ail_platform.report_schema import ExitCode
from tools.ail_package_manager.cache import (
    clone_git_dep,
    copy_package_to_lib,
    resolve_local_dep,
)
from tools.ail_package_manager.lock import generate_lock, write_lock
from tools.ail_package_manager.manifest import find_manifest, parse_manifest
from tools.ail_package_manager.registry import (
    download_from_local_registry,
    download_package_archive,
    load_registry_url,
    RegistryError,
)
from tools.ail_package_manager.resolver import resolve


def install(
    project_root: Path,
    no_lock: bool = False,
    offline: bool = False,
    frozen_lockfile: bool = False,
    verbose: bool = False,
) -> int:
    """Install all dependencies declared in ail.toml."""
    manifest_path = find_manifest(project_root)
    if manifest_path is None:
        print("Error: No ail.toml found")
        return ExitCode.INTERNAL_ERROR

    if verbose:
        print(f"Manifest: {manifest_path}")

    try:
        manifest = parse_manifest(manifest_path)
    except ValueError as e:
        print(f"Error: {e}")
        return ExitCode.INTERNAL_ERROR

    if not manifest.dependencies:
        print("No dependencies to install")
        return ExitCode.SUCCESS

    lib_dir = project_root / "lib"
    cache_dir = project_root / ".ail" / "cache"
    lock_path = project_root / "ail.lock"

    lib_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Project root: {project_root}")
        print(f"Lib dir: {lib_dir}")
        print(f"Cache dir: {cache_dir}")
        print(f"Lock file: {lock_path}")

    if frozen_lockfile and lock_path.exists():
        print("Checking lock file consistency...")
        if verbose:
            from tools.ail_package_manager.lock import deps_hash_matches
            if deps_hash_matches(manifest_path, lock_path):
                print("  Lock file is fresh")
            else:
                print("  Warning: Lock file is stale")

    if verbose:
        deps = manifest.dependencies
        for name, spec in deps.items():
            source = spec.path or spec.git or "registry"
            print(f"  {name}: {spec.version_req} (source: {source})")

    print(f"Resolving dependencies for '{manifest.name}'...")

    try:
        resolved = resolve(
            project_root=project_root,
            manifest=manifest,
            manifest_path=manifest_path,
            lock_path=lock_path,
            cache_dir=cache_dir,
            use_lock=not frozen_lockfile,
        )
    except ValueError as e:
        print(f"Resolution error: {e}", file=__import__("sys").stderr)
        return ExitCode.FAILURE

    if frozen_lockfile and lock_path.exists():
        from tools.ail_package_manager.lock import deps_hash_matches
        if not deps_hash_matches(manifest_path, lock_path):
            print("Error: Lock file is stale (--frozen-lockfile)", file=__import__("sys").stderr)
            return ExitCode.LOCKFILE_MISMATCH

    installed_names: set[str] = set()
    for dep in resolved:
        if verbose:
            print(f"  Installing {dep.name} v{dep.version} ({dep.source})...")
        else:
            print(f"  Installing {dep.name} v{dep.version} ({dep.source})...")

        if dep.source == "local":
            source_spec = manifest.dependencies.get(dep.name)
            if source_spec and source_spec.path:
                source_path = (project_root / source_spec.path).resolve()
                if verbose:
                    print(f"    Copying from {source_path}")
                copy_package_to_lib(source_path, lib_dir, dep.name)

        elif dep.source == "git":
            dep_spec = manifest.dependencies.get(dep.name)
            if dep_spec and dep_spec.git:
                if verbose:
                    print(f"    Cloning {dep_spec.git}")
                try:
                    _manifest, _checksum, clone_path = clone_git_dep(dep_spec, cache_dir)
                    copy_package_to_lib(clone_path, lib_dir, dep.name)
                except ValueError as e:
                    print(f"  Error installing {dep.name}: {e}", file=__import__("sys").stderr)
                    return ExitCode.FAILURE

        elif dep.source == "registry":
            if offline:
                print(f"  Error: {dep.name} requires network (--offline)", file=__import__("sys").stderr)
                return ExitCode.FAILURE
            registry_url = load_registry_url(project_root)
            dest = lib_dir / dep.name
            try:
                if registry_url.startswith(("file://", "/", ".", "\\")):
                    raw = registry_url
                    if raw.startswith("file:///"):
                        raw = raw[8:]
                    elif raw.startswith("file://"):
                        raw = raw[7:]
                    registry_dir = Path(raw).resolve()
                    if verbose:
                        print(f"    Downloading from local registry: {registry_dir}")
                    download_from_local_registry(
                        dep.name, dep.version, registry_dir, dest
                    )
                else:
                    if verbose:
                        print(f"    Downloading from {registry_url}")
                    download_package_archive(
                        dep.name, dep.version, registry_url, dest
                    )
            except RegistryError as e:
                print(f"  Error installing {dep.name}: {e}", file=__import__("sys").stderr)
                return ExitCode.FAILURE

        installed_names.add(dep.name)

    from tools.ail_package_manager.cache import clean_lib
    clean_lib(lib_dir, installed_names)

    if not no_lock:
        lock_content = generate_lock(resolved, manifest_path)
        write_lock(lock_path, lock_content)
        if verbose:
            print(f"Lock file updated: {lock_path}")

    print(f"\nInstalled {len(resolved)} packages")
    return ExitCode.SUCCESS
