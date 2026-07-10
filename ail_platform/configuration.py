from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ail_platform.manifest import ManifestError, ProjectManifest, find_manifest, get_tool_config, parse_manifest


@dataclass
class ToolConfig:
    """Tool-specific configuration from ail.toml [tools.<name>] section.

    Provides typed access to common configuration fields,
    with raw dict access for tool-specific fields.
    """
    data: dict = field(default_factory=dict)

    def get(self, key: str, default: object = None) -> object:
        return self.data.get(key, default)

    def get_str(self, key: str, default: str = "") -> str:
        value = self.data.get(key, default)
        return str(value) if value is not None else default

    def get_int(self, key: str, default: int = 0) -> int:
        value = self.data.get(key, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        value = self.data.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1")
        return bool(value) if value is not None else default

    def get_list(self, key: str, default: list | None = None) -> list:
        value = self.data.get(key, default)
        if isinstance(value, list):
            return value
        return list(value) if value else (default or [])


def load_tool_config(
    tool_name: str, start_dir: Path | None = None
) -> ToolConfig:
    """Load tool configuration from ail.toml.

    Searches for ail.toml starting from start_dir (or cwd),
    parses it, and extracts the [tools.<tool_name>] section.

    Returns empty ToolConfig if no manifest is found, the section
    doesn't exist, or parsing fails.
    """
    manifest_path = find_manifest(start_dir)
    if manifest_path is None:
        return ToolConfig()

    try:
        manifest = parse_manifest(manifest_path)
    except ManifestError:
        return ToolConfig()

    config = get_tool_config(manifest, tool_name)
    return ToolConfig(data=config)


def merge_config(
    base: ToolConfig, override: ToolConfig | dict | None = None
) -> ToolConfig:
    """Merge two tool configs. override values take precedence.

    Args:
        base: Base configuration (e.g., from ail.toml).
        override: Override configuration (e.g., from CLI flags).

    Returns:
        New ToolConfig with merged values.
    """
    merged = dict(base.data)
    if isinstance(override, ToolConfig):
        merged.update(override.data)
    elif isinstance(override, dict):
        merged.update(override)
    return ToolConfig(data=merged)
