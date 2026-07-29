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
from tools.ail_package_manager.errors import PackageError
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
        if value.startswith("git+"):
            git_url = value[4:]
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
    raise PackageError(
        reason=f"Invalid dependency value for '{name}': expected string or table.",
        suggestion="Use a version string (e.g. \"1.0.0\"), a path table (e.g. { path = \"../lib\" }), or a git table (e.g. { git = \"https://...\", tag = \"v1.0.0\" }).",
        location=f"dependencies.{name}",
    )


def parse_manifest(path: Path) -> ProjectManifest:
    """Read and validate an ail.toml file. Raises PackageError on validation errors."""
    path_str = str(path)

    if not path.exists():
        raise PackageError(
            reason=f"Manifest not found: {path_str}",
            suggestion="Run 'ail new <project>' to create a new project, or ensure ail.toml exists.",
            manifest_path=path_str,
        )
    if not path.is_file():
        raise PackageError(
            reason=f"Not a file: {path_str}",
            suggestion="Remove the directory or file at this path and create a valid ail.toml file.",
            manifest_path=path_str,
        )

    try:
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        data = tomllib.loads(raw.decode("utf-8"))
    except Exception as e:
        raise PackageError(
            reason=f"Failed to parse manifest: {e}",
            suggestion="Ensure ail.toml contains valid TOML syntax. Check for missing quotes, trailing commas, or unclosed brackets.",
            manifest_path=path_str,
        )

    manifest_dir = path.parent
    errors: list[PackageError] = []

    project = data.get("project")
    if project is None:
        errors.append(
            PackageError(
                reason="Missing [project] section.",
                suggestion='Add a [project] section with name and version. Example:\n\n[project]\nname = "my_project"\nversion = "0.1.0"',
                manifest_path=path_str,
            )
        )
        name = ""
        version = ""
        description = ""
        authors = []
        license_val = ""
        entry = "main.ail"
    else:
        if not isinstance(project, dict):
            errors.append(
                PackageError(
                    reason="[project] section must be a table (key-value pairs).",
                    suggestion="Write [project] as a section header with fields underneath, not as a string or list.",
                    manifest_path=path_str,
                )
            )
            name = ""
            version = ""
            description = ""
            authors = []
            license_val = ""
            entry = "main.ail"
        else:
            name = str(project.get("name", "")) if isinstance(project.get("name"), str) else ""
            version = str(project.get("version", "")) if isinstance(project.get("version"), str) else ""
            description_raw = project.get("description", "")
            description = str(description_raw) if isinstance(description_raw, str) else ""
            authors_raw = project.get("authors", [])
            license_raw = project.get("license", "")
            license_val = str(license_raw) if isinstance(license_raw, str) else ""
            entry_raw = project.get("entry", "main.ail")
            entry = str(entry_raw) if isinstance(entry_raw, str) else "main.ail"

            if not name:
                errors.append(
                    PackageError(
                        reason="Missing or empty [project].name.",
                        suggestion='Set a package name. Example:\nname = "my_project"',
                        manifest_path=path_str,
                        location="[project].name",
                    )
                )
            else:
                err = validate_package_name(name)
                if err:
                    errors.append(
                        PackageError(
                            reason=err,
                            suggestion="Use snake_case: start with a lowercase letter, followed by lowercase letters, digits, or underscores.",
                            manifest_path=path_str,
                            location="[project].name",
                        )
                    )

            if not version:
                errors.append(
                    PackageError(
                        reason="Missing or empty [project].version.",
                        suggestion='Set a version. Example:\nversion = "0.1.0"',
                        manifest_path=path_str,
                        location="[project].version",
                    )
                )
            else:
                err = validate_version(version)
                if err:
                    errors.append(
                        PackageError(
                            reason=err,
                            suggestion="Use MAJOR.MINOR.PATCH format (e.g. 1.0.0). Example:\nversion = \"0.1.0\"",
                            manifest_path=path_str,
                            location="[project].version",
                        )
                    )

            if not isinstance(description_raw, str) and description_raw is not None and description_raw != "":
                errors.append(
                    PackageError(
                        reason=f"Invalid type for [project].description: expected string, got {type(description_raw).__name__}.",
                        suggestion="Set description to a string value. Example:\ndescription = \"My AILang project\"",
                        manifest_path=path_str,
                        location="[project].description",
                    )
                )

            if authors_raw is not None and authors_raw != "":
                if isinstance(authors_raw, list):
                    for i, author in enumerate(authors_raw):
                        if not isinstance(author, str):
                            errors.append(
                                PackageError(
                                    reason=f"Author #{i + 1} must be a string, got {type(author).__name__}.",
                                    suggestion="Each author should be a string. Example:\nauthors = [\"Alice <alice@example.com>\"]",
                                    manifest_path=path_str,
                                    location=f"[project].authors[{i}]",
                                )
                            )
                else:
                    errors.append(
                        PackageError(
                            reason=f"Invalid type for [project].authors: expected a list, got {type(authors_raw).__name__}.",
                            suggestion="Use a list of strings. Example:\nauthors = [\"Alice <alice@example.com>\"]",
                            manifest_path=path_str,
                            location="[project].authors",
                        )
                    )

            if not isinstance(license_raw, str) and license_raw is not None and license_raw != "":
                errors.append(
                    PackageError(
                        reason=f"Invalid type for [project].license: expected string, got {type(license_raw).__name__}.",
                        suggestion="Set license to a string value. Example:\nlicense = \"MIT\"",
                        manifest_path=path_str,
                        location="[project].license",
                    )
                )

            if not isinstance(entry_raw, str):
                errors.append(
                    PackageError(
                        reason=f"Invalid type for [project].entry: expected string, got {type(entry_raw).__name__}.",
                        suggestion="Set entry to a string file path. Example:\nentry = \"main.ail\"",
                        manifest_path=path_str,
                        location="[project].entry",
                    )
                )
            else:
                entry_path = manifest_dir / entry
                if not entry_path.exists():
                    print(
                        f"Warning: entry file not found: {entry} "
                        f"(update [project].entry or create the file)"
                    )

    language = data.get("language")
    language_version = "0.3"
    if language is not None:
        if isinstance(language, dict):
            language_version = str(language.get("version", "0.3"))
        else:
            errors.append(
                PackageError(
                    reason="[language] section must be a table (key-value pairs).",
                    suggestion="Write [language] as a section header with fields underneath. Example:\n[language]\nversion = \"1.1.7\"",
                    manifest_path=path_str,
                )
            )

    dependencies: dict[str, DependencySpec] = {}
    deps_table = data.get("dependencies")
    if deps_table is not None:
        if isinstance(deps_table, dict):
            for dep_name, dep_value in deps_table.items():
                err = validate_package_name(dep_name)
                if err:
                    errors.append(
                        PackageError(
                            reason=f"Dependency '{dep_name}': {err}",
                            suggestion="Use a valid snake_case package name for the dependency.",
                            manifest_path=path_str,
                            location=f"dependencies.{dep_name}",
                        )
                    )
                    continue
                try:
                    dependencies[dep_name] = _parse_dep_value(dep_name, dep_value)
                except PackageError as e:
                    errors.append(e)
        else:
            errors.append(
                PackageError(
                    reason=f"[dependencies] section must be a table, got {type(deps_table).__name__}.",
                    suggestion="Write [dependencies] as a section header with package entries underneath.",
                    manifest_path=path_str,
                )
            )

    if errors:
        detail_lines: list[str] = []
        for i, err in enumerate(errors):
            if i > 0:
                detail_lines.append("---")
                detail_lines.append("")
            detail_lines.append(f"Reason ({i + 1}):")
            detail_lines.append(f"  {err.reason}")
            detail_lines.append("")
            if err.suggestion:
                detail_lines.append("Suggestion:")
                detail_lines.append(f"  {err.suggestion}")
                detail_lines.append("")
        detail_lines.append(f"Manifest: {path_str}")
        raise PackageError(
            reason=f"Manifest has {len(errors)} validation error(s).",
            detail="\n".join(detail_lines),
            suggestion=f"Fix the {len(errors)} issue(s) in {path_str}",
            manifest_path=path_str,
        )

    return ProjectManifest(
        name=name,
        version=version,
        description=description,
        authors=authors_raw if isinstance(authors_raw, list) else [],
        license=license_val,
        entry=entry,
        language_version=language_version,
        dependencies=dependencies,
    )
