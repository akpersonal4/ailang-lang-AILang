"""Dependency resolution — resolves ail.toml dependencies to a flat dependency tree."""

from __future__ import annotations

from pathlib import Path

from tools.ail_package_manager.cache import clone_git_dep, resolve_local_dep
from tools.ail_package_manager.lock import (
    deps_hash_matches,
    read_lock_packages,
)
from tools.ail_package_manager.models import (
    DependencySpec,
    ProjectManifest,
    ResolvedDependency,
)
from tools.ail_package_manager.registry import (
    RegistryError,
    fetch_package_metadata,
    load_registry_url,
)


def _fetch_local_package_meta(name: str, registry_dir: Path) -> dict:
    """Fetch package metadata from a local directory registry."""
    import json

    meta_path = registry_dir / "packages" / name / "metadata.json"
    if not meta_path.exists():
        raise RegistryError(f"Package '{name}' not found in local registry")
    return json.loads(meta_path.read_text(encoding="utf-8"))


def resolve(
    project_root: Path,
    manifest: ProjectManifest,
    manifest_path: Path,
    lock_path: Path,
    cache_dir: Path,
    use_lock: bool = True,
) -> list[ResolvedDependency]:
    """Resolve all dependencies into a flat dependency list.

    If a valid lock file exists and use_lock is True, replay from lock.
    Otherwise, resolve from scratch.

    Returns a list of ResolvedDependency in dependency order
    (dependencies before dependents).
    """
    if use_lock and deps_hash_matches(manifest_path, lock_path):
        return _resolve_from_lock(project_root, lock_path, manifest_path, cache_dir)

    return _resolve_fresh(project_root, manifest, manifest_path, cache_dir)


def _resolve_from_lock(
    project_root: Path,
    lock_path: Path,
    manifest_path: Path,
    cache_dir: Path,
) -> list[ResolvedDependency]:
    """Replay dependency resolution from an existing lock file."""
    lock_packages = read_lock_packages(lock_path)
    resolved = []

    for pkg in lock_packages:
        rd = ResolvedDependency(
            name=pkg.name,
            version=pkg.version,
            source=pkg.source,
            checksum=pkg.checksum,
            dependencies=pkg.dependencies,
            path=pkg.path,
            git=pkg.git,
        )
        resolved.append(rd)

    return resolved


def _resolve_fresh(
    project_root: Path,
    manifest: ProjectManifest,
    manifest_path: Path,
    cache_dir: Path,
) -> list[ResolvedDependency]:
    """Resolve dependencies from scratch."""
    resolved: dict[str, ResolvedDependency] = {}
    _resolve_deps(
        deps=manifest.dependencies,
        project_root=project_root,
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        resolved=resolved,
        visited=set(),
        chain=None,
    )

    # Topological sort: dependencies before dependents
    return _topological_sort(resolved)


def _resolve_deps(
    deps: dict[str, DependencySpec],
    project_root: Path,
    manifest_path: Path,
    cache_dir: Path,
    resolved: dict[str, ResolvedDependency],
    visited: set[str],
    chain: list[str] | None,
    constraints: dict[str, list[str]] | None = None,
) -> None:
    """Recursively resolve a set of dependencies.

    Raises ValueError on circular dependency, version conflict, or resolution failure.
    """
    if chain is None:
        chain = []
    if constraints is None:
        constraints = {}

    for dep_name, dep_spec in deps.items():
        if dep_name in chain:
            cycle = " -> ".join(chain + [dep_name])
            raise ValueError(f"Circular dependency detected: {cycle}")

        if dep_name in visited:
            # Already resolved — check for version conflict
            if dep_spec.version_req != "*" and dep_name in resolved:
                existing = resolved[dep_name]
                if existing.version != dep_spec.version_req:
                    prior = constraints.get(dep_name, [])
                    prior_str = ", ".join(prior) if prior else "unknown"
                    raise ValueError(
                        f"Version conflict for '{dep_name}': "
                        f"already resolved to {existing.version} (from {prior_str}), "
                        f"but {dep_spec.version_req} is required"
                    )
            continue

        visited.add(dep_name)
        chain.append(dep_name)

        # Track constraints for conflict detection
        constraint_str = dep_spec.version_req
        if dep_spec.path:
            constraint_str = f"path={dep_spec.path}"
        elif dep_spec.git:
            constraint_str = f"git={dep_spec.git}"
        constraints.setdefault(dep_name, []).append(constraint_str)

        if dep_spec.path:
            _resolve_local_dep(
                dep_spec,
                project_root,
                cache_dir,
                resolved,
                visited,
                chain,
                constraints,
            )
        elif dep_spec.git:
            _resolve_git_dep(
                dep_spec,
                cache_dir,
                resolved,
                visited,
                chain,
                constraints,
            )
        else:
            # Registry dependency
            registry_url = load_registry_url(project_root)
            is_local = registry_url.startswith(("file://", "/", ".", "\\"))
            local_registry_dir: Path | None = None
            if is_local:
                raw = registry_url
                if raw.startswith("file:///"):
                    raw = raw[8:]
                elif raw.startswith("file://"):
                    raw = raw[7:]
                local_registry_dir = Path(raw).resolve()

            try:
                if local_registry_dir is not None:

                    meta = _fetch_local_package_meta(dep_name, local_registry_dir)
                else:
                    meta = fetch_package_metadata(dep_name, registry_url)
            except RegistryError as e:
                raise ValueError(
                    f"Could not resolve registry dependency '{dep_name}': {e}"
                )

            versions = meta.get("versions", {})
            if not versions:
                raise ValueError(
                    f"Package '{dep_name}' has no published versions in registry"
                )

            # Use the requested version or the latest
            requested = dep_spec.version_req
            if requested == "*":
                requested = sorted(versions.keys(), key=_semver_key)[-1]
            elif requested not in versions:
                raise ValueError(
                    f"Package '{dep_name}' v{requested} not found. "
                    f"Available: {', '.join(sorted(versions.keys(), key=_semver_key))}"
                )

            version_meta = versions[requested]
            resolved[dep_name] = ResolvedDependency(
                name=dep_name,
                version=requested,
                source="registry",
                checksum=version_meta.get("checksum", ""),
                dependencies=list(version_meta.get("dependencies", {}).keys()),
            )

            # Resolve transitive dependencies from the registry metadata
            transitive_deps = {}
            for tdep_name, tdep_ver in version_meta.get("dependencies", {}).items():
                transitive_deps[tdep_name] = DependencySpec(
                    name=tdep_name,
                    version_req=tdep_ver if isinstance(tdep_ver, str) else "*",
                )

            if transitive_deps:
                _resolve_deps(
                    deps=transitive_deps,
                    project_root=project_root,
                    manifest_path=manifest_path,
                    cache_dir=cache_dir,
                    resolved=resolved,
                    visited=visited,
                    chain=chain,
                    constraints=constraints,
                )

        chain.pop()


def _resolve_local_dep(
    dep_spec: DependencySpec,
    project_root: Path,
    cache_dir: Path,
    resolved: dict[str, ResolvedDependency],
    visited: set[str],
    chain: list[str],
    constraints: dict[str, list[str]] | None = None,
) -> None:
    """Resolve a local path dependency and its transitive deps."""
    dep_manifest, checksum = resolve_local_dep(dep_spec, project_root, cache_dir)

    resolved[dep_spec.name] = ResolvedDependency(
        name=dep_spec.name,
        version=dep_manifest.version,
        source="local",
        path=None,
        checksum=checksum,
        dependencies=list(dep_manifest.dependencies.keys()),
    )

    # Resolve transitive dependencies
    _resolve_deps(
        deps=dep_manifest.dependencies,
        project_root=project_root,
        manifest_path=None,
        cache_dir=cache_dir,
        resolved=resolved,
        visited=visited,
        chain=chain,
        constraints=constraints,
    )


def _resolve_git_dep(
    dep_spec: DependencySpec,
    cache_dir: Path,
    resolved: dict[str, ResolvedDependency],
    visited: set[str],
    chain: list[str],
    constraints: dict[str, list[str]] | None = None,
) -> None:
    """Resolve a Git dependency and its transitive deps."""
    dep_manifest, checksum, clone_path = clone_git_dep(dep_spec, cache_dir)

    resolved[dep_spec.name] = ResolvedDependency(
        name=dep_spec.name,
        version=dep_manifest.version,
        source="git",
        git=dep_spec.git,
        tag=dep_spec.tag,
        checksum=checksum,
        dependencies=list(dep_manifest.dependencies.keys()),
    )

    # Resolve transitive dependencies using the cloned repo as project_root
    parent_dir = clone_path.parent
    _resolve_deps(
        deps=dep_manifest.dependencies,
        project_root=parent_dir,
        manifest_path=None,
        cache_dir=cache_dir,
        resolved=resolved,
        visited=visited,
        chain=chain,
        constraints=constraints,
    )


def _semver_key(version: str) -> tuple[int, int, int]:
    """Convert a semver string to a sortable tuple."""
    parts = version.split(".")
    return tuple(int(p) if p.isdigit() else 0 for p in parts[:3]) + (0,) * (
        3 - len(parts)
    )


def _topological_sort(
    resolved: dict[str, ResolvedDependency],
) -> list[ResolvedDependency]:
    """Sort resolved dependencies so dependencies come before dependents."""
    sorted_list: list[ResolvedDependency] = []
    visited: set[str] = set()

    def visit(name: str) -> None:
        if name in visited:
            return
        visited.add(name)
        dep = resolved.get(name)
        if dep is None:
            return
        for child_name in dep.dependencies:
            visit(child_name)
        sorted_list.append(dep)

    for name in resolved:
        visit(name)

    return sorted_list
