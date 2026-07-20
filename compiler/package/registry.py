"""Registry publish protocol for AILang packages.

Supports local directory registries and remote HTTP registries.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import tarfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


class RegistryError(Exception):
    pass


def _registry_urljoin(base: str, *parts: str) -> str:
    base = base.rstrip("/")
    for p in parts:
        base = base + "/" + p.lstrip("/")
    return base


def load_registry_url(project_root: Path) -> str:
    """Read the registry URL from ail.toml [tool.registry] or env var."""
    manifest_path = project_root / "ail.toml"
    if manifest_path.is_file():
        try:
            raw = manifest_path.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                raw = raw[3:]
            import tomllib

            data = tomllib.loads(raw.decode("utf-8"))
        except Exception:
            data = {}
        tool = data.get("tool", {})
        if isinstance(tool, dict):
            reg = tool.get("registry", {})
            if isinstance(reg, dict) and "url" in reg:
                return str(reg["url"])
    return os.environ.get("AIL_REGISTRY", "https://registry.ailang.dev")


def _build_package_metadata(project_root: Path) -> dict[str, Any]:
    """Read package metadata from ail.toml."""
    manifest_path = project_root / "ail.toml"
    if not manifest_path.is_file():
        raise RegistryError("No ail.toml found in project root")

    raw = manifest_path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        import tomllib

        data = tomllib.loads(raw.decode("utf-8"))
    except Exception as e:
        raise RegistryError(f"Failed to parse ail.toml: {e}")

    project = data.get("project", {})
    if not isinstance(project, dict):
        raise RegistryError("Missing [project] section in ail.toml")

    name = project.get("name", "")
    version = project.get("version", "")
    if not name or not version:
        raise RegistryError("Missing name or version in [project] section")

    deps_raw = data.get("dependencies", {})
    dependencies: dict[str, str] = {}
    if isinstance(deps_raw, dict):
        for dep_name, dep_val in deps_raw.items():
            if isinstance(dep_val, str):
                dependencies[dep_name] = dep_val
            elif isinstance(dep_val, dict):
                dependencies[dep_name] = dep_val.get("version", "*")
            else:
                dependencies[dep_name] = "*"

    return {
        "name": name,
        "version": version,
        "description": str(project.get("description", "")),
        "entry": str(project.get("entry", "main.ail")),
        "language_version": str(data.get("language", {}).get("version", "0.3")),
        "dependencies": dependencies,
    }


def pack_project(project_root: Path) -> tuple[bytes, str]:
    """Pack an AILang project into a .tar.gz archive.

    Returns (archive_bytes, sha256_checksum).
    """
    project_root = project_root.resolve()
    _build_package_metadata(project_root)  # validates project exists

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for f in sorted(project_root.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(project_root)
            parts = rel.parts
            if any(skip in parts for skip in (".ail", "__pycache__", ".git", ".venv")):
                continue
            if f.suffix not in (".ail", ".json", ".toml", ".md"):
                continue
            tar.add(str(f), arcname=str(rel))

    data = buf.getvalue()
    checksum = hashlib.sha256(data).hexdigest()
    return data, checksum


def publish_local(project_root: Path, registry_dir: Path) -> None:
    """Publish a package to a local directory registry."""
    metadata = _build_package_metadata(project_root)
    name = metadata["name"]
    version = metadata["version"]

    pkg_dir = registry_dir / "packages" / name
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Merge with existing metadata
    metadata_path = pkg_dir / "metadata.json"
    existing: dict[str, Any] = {"name": name, "versions": {}}
    if metadata_path.exists():
        existing = json.loads(metadata_path.read_text(encoding="utf-8"))
    versions = existing.get("versions", {})

    # Write archive
    archive_bytes, checksum = pack_project(project_root)
    archive_path = pkg_dir / f"{version}.tar.gz"
    archive_path.write_bytes(archive_bytes)

    # Update metadata
    metadata["checksum"] = checksum
    versions[version] = metadata
    existing["name"] = name
    existing["versions"] = versions
    metadata_path.write_text(
        json.dumps(existing, indent=2, sort_keys=True), encoding="utf-8"
    )

    print(f"  Published {name} v{version} to {registry_dir}")
    print(f"  Archive: {archive_path}")


def publish_remote(project_root: Path, registry_url: str) -> None:
    """Publish a package to a remote HTTP registry."""
    metadata = _build_package_metadata(project_root)
    name = metadata["name"]
    version = metadata["version"]

    archive_bytes, checksum = pack_project(project_root)
    metadata["checksum"] = checksum

    # PUT metadata
    meta_url = _registry_urljoin(registry_url, "api", "packages", name, version)
    req = urllib.request.Request(
        meta_url,
        data=json.dumps(metadata).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        raise RegistryError(
            f"Registry rejected metadata for {name} v{version}: " f"{e.code} {e.reason}"
        )
    except urllib.error.URLError as e:
        raise RegistryError(f"Could not reach registry {registry_url}: {e.reason}")

    # PUT archive
    archive_url = _registry_urljoin(
        registry_url, "api", "packages", name, version, "archive"
    )
    req = urllib.request.Request(
        archive_url,
        data=archive_bytes,
        headers={"Content-Type": "application/gzip"},
        method="PUT",
    )
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        raise RegistryError(
            f"Registry rejected archive for {name} v{version}: " f"{e.code} {e.reason}"
        )
    except urllib.error.URLError as e:
        raise RegistryError(f"Could not reach registry {registry_url}: {e.reason}")

    print(f"  Published {name} v{version} to {registry_url}")


def download_local_package(
    name: str, version: str, registry_dir: Path, dest_dir: Path
) -> str:
    """Download and extract a package from a local directory registry.

    Returns the checksum for verification.
    """
    pkg_dir = registry_dir / "packages" / name
    if not pkg_dir.exists():
        raise RegistryError(f"Package '{name}' not found in local registry")

    metadata_path = pkg_dir / "metadata.json"
    if not metadata_path.exists():
        raise RegistryError(f"No metadata for '{name}' in local registry")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    versions = metadata.get("versions", {})
    if version not in versions:
        avail = ", ".join(sorted(versions.keys(), key=_semver_key))
        raise RegistryError(
            f"Package '{name}' v{version} not found. " f"Available: {avail}"
        )

    expected = versions[version].get("checksum", "")
    archive_path = pkg_dir / f"{version}.tar.gz"
    if not archive_path.exists():
        raise RegistryError(f"Archive not found: {archive_path}")

    archive_bytes = archive_path.read_bytes()
    if expected:
        actual = hashlib.sha256(archive_bytes).hexdigest()
        if actual != expected:
            raise RegistryError(
                f"Checksum mismatch for {name} v{version}: "
                f"expected {expected}, got {actual}"
            )

    buf = io.BytesIO(archive_bytes)
    with tarfile.open(fileobj=buf, mode="r:gz") as tar:
        tar.extractall(path=str(dest_dir))

    print(f"  Downloaded {name} v{version} to {dest_dir}")
    return expected


def _semver_key(version: str) -> tuple[int, ...]:
    parts = version.split(".")
    return tuple(int(p) if p.isdigit() else 0 for p in parts[:3])
