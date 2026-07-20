"""AILang package manifest (ail.toml) parser and validator.

Thin wrapper around platform.manifest with package-manager-specific
DependencySpec parsing and validation.
"""

from __future__ import annotations

import re
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

from ail_platform.manifest import (
    find_manifest as find_manifest,
)  # noqa: F401  — re-exported for package modules
from tools.ail_package_manager.models import DependencySpec, ProjectManifest

_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_NAME_RE_KEBAB = re.compile(r"^[a-z][a-z0-9-]*[a-z0-9]$")
_MAX_NAME_LENGTH = 64
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def validate_package_name(name: str) -> str | None:
    """Validate a package name. Return error message or None.

    Accepts snake_case identifiers (must start with lowercase letter,
    contain only lowercase alphanumeric and underscores). Kebab-case
    names are accepted with a deprecation warning.
    """
    if len(name) > _MAX_NAME_LENGTH:
        return f"Package name too long ({len(name)} > {_MAX_NAME_LENGTH} chars)"
    if not _NAME_RE.match(name):
        if _NAME_RE_KEBAB.match(name):
            print(
                f"Warning: package name '{name}' uses kebab-case which is deprecated. "
                "Use snake_case instead (e.g. '{0}'.).".format(name.replace("-", "_"))
            )
            return None
        return (
            f"Invalid package name: '{name}'. "
            "Must be snake_case: start with a lowercase letter, "
            "lowercase alphanumeric + underscores, max 64 characters."
        )
    return None


def validate_version(version: str) -> str | None:
    """Validate a semver version string. Return error message or None."""
    if not _SEMVER_RE.match(version):
        return f"Invalid version: '{version}'. Must be MAJOR.MINOR.PATCH (e.g. 1.0.0)"
    return None


def _parse_dep_value(name: str, value) -> DependencySpec:
    """Parse a single dependency value from TOML.

    Supports:
    - Version string: ">=1.0.0"
    - Local path: { path = "../auth" }
    - Git URL string: "git+https://..."
    - Git table: { git = "https://...", tag = "v1.0.0" }
    """
    if isinstance(value, str):
        # git+https:// or git+ssh:// string format
        if value.startswith("git+"):
            git_url = value[4:]  # strip "git+"
            return DependencySpec(name=name, git=git_url, version_req="*")
        return DependencySpec(name=name, version_req=value)
    if isinstance(value, dict):
        if "path" in value:
            return DependencySpec(name=name, path=str(value["path"]), version_req="*")
        git_url = value.get("git", "")
        return DependencySpec(
            name=name,
            git=git_url,
            version_req="*",
            tag=str(value["tag"]) if "tag" in value else None,
            branch=str(value["branch"]) if "branch" in value else None,
            rev=str(value["rev"]) if "rev" in value else None,
        )
    raise ValueError(f"Invalid dependency value for '{name}': expected string or table")


def parse_manifest(path: Path) -> ProjectManifest:
    """Read and validate an ail.toml file. Raises ValueError on validation errors."""
    if not path.exists():
        raise ValueError(f"Manifest not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    try:
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        data = tomllib.loads(raw.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"Failed to parse {path}: {e}")

    errors: list[str] = []

    project = data.get("project", {})
    if not isinstance(project, dict):
        errors.append("[project] section must be a table")

    name = project.get("name", "") if isinstance(project, dict) else ""
    version = project.get("version", "") if isinstance(project, dict) else ""

    if not name:
        errors.append("Missing required field: [project].name")
    else:
        err = validate_package_name(name)
        if err:
            errors.append(err)

    if not version:
        errors.append("Missing required field: [project].version")
    else:
        err = validate_version(version)
        if err:
            errors.append(err)

    description = (
        str(project.get("description", "")) if isinstance(project, dict) else ""
    )
    authors = list(project.get("authors", [])) if isinstance(project, dict) else []
    license_val = str(project.get("license", "")) if isinstance(project, dict) else ""
    entry = (
        str(project.get("entry", "main.ail"))
        if isinstance(project, dict)
        else "main.ail"
    )

    language = data.get("language", {})
    language_version = "0.3"
    if isinstance(language, dict):
        language_version = str(language.get("version", "0.3"))
    else:
        if language is not None:
            errors.append("[language] section must be a table")

    for i, author in enumerate(authors):
        if not isinstance(author, str):
            errors.append(f"Author #{i + 1} must be a string")

    dependencies: dict[str, DependencySpec] = {}
    deps_table = data.get("dependencies", {})
    if isinstance(deps_table, dict):
        for dep_name, dep_value in deps_table.items():
            err = validate_package_name(dep_name)
            if err:
                errors.append(f"Dependency '{dep_name}': {err}")
                continue
            try:
                dependencies[dep_name] = _parse_dep_value(dep_name, dep_value)
            except ValueError as e:
                errors.append(str(e))
    elif deps_table is not None:
        errors.append("[dependencies] section must be a table")

    if errors:
        raise ValueError(
            f"Manifest validation failed for {path}:\n  " + "\n  ".join(errors)
        )

    return ProjectManifest(
        name=name,
        version=version,
        description=description,
        authors=authors,
        license=license_val,
        entry=entry,
        language_version=language_version,
        dependencies=dependencies,
    )
