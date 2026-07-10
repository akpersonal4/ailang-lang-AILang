from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


_KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9-]*[a-z0-9]$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


class ManifestError(Exception):
    """Raised when manifest parsing or validation fails."""


@dataclass
class ProjectManifest:
    """Canonical representation of an ail.toml project manifest."""
    name: str
    version: str
    description: str = ""
    authors: list[str] = field(default_factory=list)
    license: str = ""
    entry: str = "main.ail"
    language_version: str = ""
    dependencies: dict[str, str] = field(default_factory=dict)
    tools: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def from_toml(cls, data: dict) -> ProjectManifest:
        project = data.get("project", {})
        language = data.get("language", {})
        deps = data.get("dependencies", {})
        tools = data.get("tools", {})

        name = project.get("name", "")
        version = project.get("version", "0.1.0")

        return cls(
            name=name,
            version=version,
            description=project.get("description", ""),
            authors=project.get("authors", []),
            license=project.get("license", ""),
            entry=project.get("entry", "main.ail"),
            language_version=language.get("version", ""),
            dependencies=dict(deps),
            tools=dict(tools),
        )

    def to_toml_dict(self) -> dict:
        result: dict = {
            "project": {
                "name": self.name,
                "version": self.version,
            },
        }
        if self.description:
            result["project"]["description"] = self.description
        if self.authors:
            result["project"]["authors"] = self.authors
        if self.license:
            result["project"]["license"] = self.license
        if self.entry != "main.ail":
            result["project"]["entry"] = self.entry
        if self.language_version:
            result["language"] = {"version": self.language_version}
        if self.dependencies:
            result["dependencies"] = dict(self.dependencies)
        if self.tools:
            result["tools"] = dict(self.tools)
        return result


def find_manifest(start_dir: Path | None = None) -> Path | None:
    """Walk up from start_dir (or cwd) looking for ail.toml.

    Returns the path to the first ail.toml found, or None.
    """
    if start_dir is None:
        start_dir = Path.cwd()
    current = start_dir.resolve()
    while True:
        candidate = current / "ail.toml"
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def parse_manifest(path: Path) -> ProjectManifest:
    """Parse and validate an ail.toml file.

    Raises ManifestError if the file is missing or invalid.
    """
    if not path.is_file():
        raise ManifestError(f"Manifest not found: {path}")

    try:
        raw = path.read_bytes()
        data = tomllib.loads(raw.decode("utf-8"))
    except Exception as e:
        raise ManifestError(f"Failed to parse {path}: {e}") from e

    return ProjectManifest.from_toml(data)


def write_manifest(manifest: ProjectManifest, path: Path) -> None:
    """Write a ProjectManifest to ail.toml.

    Uses TOML format matching the canonical schema.
    """
    lines: list[str] = []
    data = manifest.to_toml_dict()

    for section_name, section_data in data.items():
        lines.append(f"[{section_name}]")
        for key, value in section_data.items():
            if isinstance(value, list):
                if not value:
                    continue
                items = ", ".join(repr(v) for v in value)
                lines.append(f'{key} = [{items}]')
            elif isinstance(value, dict):
                lines.append(f"{key} = {{")
                for dk, dv in value.items():
                    lines.append(f'  {dk} = "{dv}"')
                lines.append("}")
            else:
                lines.append(f'{key} = "{value}"')
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def get_tool_config(
    manifest: ProjectManifest, tool_name: str
) -> dict:
    """Extract tool-specific configuration from [tools.<tool_name>].

    Returns empty dict if the section doesn't exist or is empty.
    """
    return dict(manifest.tools.get(tool_name, {}))
