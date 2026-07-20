"""AILang Package Registry — protocol client, metadata, archive format.

Registry protocol (MVP):

  Local directory:
    <registry>/
      packages/
        <name>/
          metadata.json
          <version>.tar.gz

  HTTP registry:
    GET /api/packages/<name>             → metadata JSON
    GET /api/packages/<name>/<version>   → archive .tar.gz
"""

from __future__ import annotations

import hashlib
import io
import json
import tarfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from tools.ail_package_manager.manifest import parse_manifest


def _registry_urljoin(base: str, *parts: str) -> str:
    base = base.rstrip("/")
    for p in parts:
        base = base + "/" + p.lstrip("/")
    return base


class RegistryError(Exception):
    pass


def load_registry_url(project_root: Path) -> str:
    """Read the registry URL from ail.toml [tool.registry] or env var."""
    manifest_path = _find_manifest_in(project_root)
    if manifest_path is None:
        return "https://registry.ailang.dev"

    try:
        raw = manifest_path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        import tomllib

        data = tomllib.loads(raw.decode("utf-8"))
    except Exception:
        return "https://registry.ailang.dev"

    tool = data.get("tool", {})
    if isinstance(tool, dict):
        reg = tool.get("registry", {})
        if isinstance(reg, dict) and "url" in reg:
            return str(reg["url"])

    # Fallback to env var
    import os

    return os.environ.get("AIL_REGISTRY", "https://registry.ailang.dev")


def _find_manifest_in(start: Path) -> Path | None:
    current = start.resolve()
    while True:
        candidate = current / "ail.toml"
        if candidate.is_file():
            return candidate
        if current == current.parent:
            return None
        current = current.parent


def pack_project(project_root: Path) -> tuple[bytes, str]:
    """Pack an AILang project into a .tar.gz archive.

    Returns (archive_bytes, checksum_hex).
    Excludes .ail/, __pycache__/, .git/, .venv/.
    """
    project_root = project_root.resolve()
    manifest_path = project_root / "ail.toml"
    if not manifest_path.exists():
        raise RegistryError("No ail.toml found in project root")

    manifest = parse_manifest(manifest_path)

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        # Add ail.toml
        tar.add(str(manifest_path), arcname="ail.toml")

        # Add source files
        for f in sorted(project_root.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(project_root)
            parts = rel.parts
            # Skip excluded directories
            if any(
                skip in parts
                for skip in (".ail", "__pycache__", ".git", ".venv", "__pycache__")
            ):
                continue
            # Only include .ail, .json, .toml, .md files
            if f.suffix not in (".ail", ".json", ".toml", ".md"):
                continue
            tar.add(str(f), arcname=str(rel))

    data = buf.getvalue()
    checksum = hashlib.sha256(data).hexdigest()
    return data, checksum


def _build_package_metadata(project_root: Path) -> dict[str, Any]:
    """Build package metadata from the project root."""
    manifest_path = project_root / "ail.toml"
    manifest = parse_manifest(manifest_path)

    deps = {}
    for dep_name, dep_spec in manifest.dependencies.items():
        deps[dep_name] = dep_spec.version_req

    return {
        "name": manifest.name,
        "version": manifest.version,
        "description": manifest.description,
        "entry": manifest.entry,
        "language_version": manifest.language_version,
        "dependencies": deps,
    }


def publish_local(project_root: Path, registry_dir: Path) -> None:
    """Publish a package to a local directory registry."""
    project_root = project_root.resolve()
    registry_dir = registry_dir.resolve()

    metadata = _build_package_metadata(project_root)
    name = metadata["name"]
    version = metadata["version"]

    pkg_dir = registry_dir / "packages" / name
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Build metadata.json (merge with existing)
    metadata_path = pkg_dir / "metadata.json"
    existing: dict[str, Any] = {}
    if metadata_path.exists():
        existing = json.loads(metadata_path.read_text(encoding="utf-8"))

    versions = existing.get("versions", {})
    versions[version] = metadata
    existing["name"] = name
    existing["versions"] = versions

    metadata_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    # Write archive
    archive_bytes, checksum = pack_project(project_root)
    archive_path = pkg_dir / f"{version}.tar.gz"
    archive_path.write_bytes(archive_bytes)

    # Update checksum in metadata
    versions[version]["checksum"] = checksum
    metadata_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    print(f"  Published {name} v{version} to {registry_dir}")
    print(f"  Archive: {archive_path}")


def publish_remote(project_root: Path, registry_url: str) -> None:
    """Publish a package to a remote HTTP registry."""
    metadata = _build_package_metadata(project_root)
    name = metadata["name"]
    version = metadata["version"]

    archive_bytes, checksum = pack_project(project_root)
    metadata["checksum"] = checksum

    # POST metadata
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
            f"Registry rejected metadata for {name} v{version}: {e.code} {e.reason}"
        )
    except urllib.error.URLError as e:
        raise RegistryError(f"Could not reach registry {registry_url}: {e.reason}")

    # POST archive
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
            f"Registry rejected archive for {name} v{version}: {e.code} {e.reason}"
        )
    except urllib.error.URLError as e:
        raise RegistryError(f"Could not reach registry {registry_url}: {e.reason}")

    print(f"  Published {name} v{version} to {registry_url}")


def fetch_package_metadata(name: str, registry_url: str) -> dict[str, Any]:
    """Fetch package metadata from the registry."""
    meta_url = _registry_urljoin(registry_url, "api", "packages", name)
    try:
        resp = urllib.request.urlopen(meta_url)
        return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RegistryError(f"Package '{name}' not found in registry")
        raise RegistryError(f"Registry error fetching {name}: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise RegistryError(f"Could not reach registry {registry_url}: {e.reason}")


def download_package_archive(
    name: str, version: str, registry_url: str, dest_dir: Path
) -> str:
    """Download and extract a package archive into dest_dir.

    Returns the checksum from the registry for verification.
    """
    meta_url = _registry_urljoin(registry_url, "api", "packages", name, version)
    try:
        resp = urllib.request.urlopen(meta_url)
        metadata = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RegistryError(f"Package '{name}' v{version} not found in registry")
        raise RegistryError(
            f"Registry error fetching {name} v{version}: {e.code} {e.reason}"
        )
    except urllib.error.URLError as e:
        raise RegistryError(f"Could not reach registry {registry_url}: {e.reason}")

    expected_checksum = metadata.get("checksum", "")

    archive_url = _registry_urljoin(
        registry_url, "api", "packages", name, version, "archive"
    )
    try:
        resp = urllib.request.urlopen(archive_url)
        archive_bytes = resp.read()
    except urllib.error.HTTPError as e:
        raise RegistryError(
            f"Registry error downloading {name} v{version}: {e.code} {e.reason}"
        )
    except urllib.error.URLError as e:
        raise RegistryError(f"Could not reach registry {registry_url}: {e.reason}")

    # Verify checksum
    if expected_checksum:
        actual = hashlib.sha256(archive_bytes).hexdigest()
        if actual != expected_checksum:
            raise RegistryError(
                f"Checksum mismatch for {name} v{version}: "
                f"expected {expected_checksum}, got {actual}"
            )

    # Extract
    import io as _io

    buf = _io.BytesIO(archive_bytes)
    with tarfile.open(fileobj=buf, mode="r:gz") as tar:
        tar.extractall(path=str(dest_dir))

    print(f"  Downloaded {name} v{version} to {dest_dir}")
    return expected_checksum


def download_from_local_registry(
    name: str, version: str, registry_dir: Path, dest_dir: Path
) -> str:
    """Download and extract a package from a local directory registry."""
    pkg_dir = registry_dir / "packages" / name
    if not pkg_dir.exists():
        raise RegistryError(f"Package '{name}' not found in local registry")

    metadata_path = pkg_dir / "metadata.json"
    if not metadata_path.exists():
        raise RegistryError(f"No metadata for '{name}' in local registry")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    versions = metadata.get("versions", {})
    if version not in versions:
        raise RegistryError(
            f"Package '{name}' v{version} not found in local registry. "
            f"Available: {', '.join(sorted(versions.keys()))}"
        )

    expected_checksum = versions[version].get("checksum", "")

    archive_path = pkg_dir / f"{version}.tar.gz"
    if not archive_path.exists():
        raise RegistryError(f"Archive not found: {archive_path}")

    archive_bytes = archive_path.read_bytes()

    # Verify checksum
    if expected_checksum:
        actual = hashlib.sha256(archive_bytes).hexdigest()
        if actual != expected_checksum:
            raise RegistryError(
                f"Checksum mismatch for {name} v{version}: "
                f"expected {expected_checksum}, got {actual}"
            )

    # Extract
    import io as _io

    buf = _io.BytesIO(archive_bytes)
    with tarfile.open(fileobj=buf, mode="r:gz") as tar:
        tar.extractall(path=str(dest_dir))

    print(f"  Downloaded {name} v{version} to {dest_dir}")
    return expected_checksum
