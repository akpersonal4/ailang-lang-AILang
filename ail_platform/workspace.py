from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ail_platform.manifest import (
    ProjectManifest,
    find_manifest,
    get_tool_config,
    parse_manifest,
)
from ail_platform.project import AppInfo, discover_apps, get_project_root


@dataclass
class Workspace:
    """Complete workspace state for a DX tool session.

    Provides a single entry point for all workspace-level queries:
    project root, discovered apps, parsed manifest, tool config.
    """

    root: Path
    apps: list[AppInfo] = field(default_factory=list)
    manifest: ProjectManifest | None = None
    tool_config: dict = field(default_factory=dict)

    @classmethod
    def from_root(
        cls, root: Path | None = None, tool_name: str | None = None
    ) -> Workspace:
        """Discover workspace from a project root.

        Args:
            root: Project root. If None, uses get_project_root().
            tool_name: If provided, extracts tool-specific config from
                       [tools.<tool_name>] in ail.toml.

        Returns:
            Fully populated Workspace.
        """
        if root is None:
            root = get_project_root()

        apps = discover_apps(root)

        manifest_path = find_manifest(root)
        manifest: ProjectManifest | None = None
        if manifest_path is not None:
            try:
                manifest = parse_manifest(manifest_path)
            except Exception:
                manifest = None

        tool_config: dict = {}
        if manifest is not None and tool_name is not None:
            tool_config = get_tool_config(manifest, tool_name)

        return cls(
            root=root,
            apps=apps,
            manifest=manifest,
            tool_config=tool_config,
        )

    @property
    def has_apps(self) -> bool:
        return len(self.apps) > 0

    @property
    def has_manifest(self) -> bool:
        return self.manifest is not None

    def app_by_name(self, name: str) -> AppInfo | None:
        for app in self.apps:
            if app.name == name:
                return app
        return None
