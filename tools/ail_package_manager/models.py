"""Data models for the AILang package manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ProjectManifest:
    name: str
    version: str
    description: str = ""
    authors: list[str] = field(default_factory=list)
    license: str = ""
    entry: str = "main.ail"
    language_version: str = "0.3"
    dependencies: dict[str, DependencySpec] = field(default_factory=dict)

    @property
    def entry_path(self) -> str:
        return self.entry


@dataclass
class DependencySpec:
    name: str
    version_req: str = "*"
    path: Optional[str] = None
    git: Optional[str] = None
    tag: Optional[str] = None
    branch: Optional[str] = None
    rev: Optional[str] = None
    dev: bool = False


@dataclass
class LockFilePackage:
    name: str
    version: str
    source: str
    checksum: str = ""
    dependencies: list[str] = field(default_factory=list)
    path: Optional[str] = None
    git: Optional[str] = None
    tag: Optional[str] = None


@dataclass
class LockFile:
    version: int = 1
    input_hash: str = ""
    packages: list[LockFilePackage] = field(default_factory=list)


@dataclass
class ResolvedDependency:
    name: str
    version: str
    source: str
    path: Optional[Path] = None
    git: Optional[str] = None
    tag: Optional[str] = None
    checksum: str = ""
    dependencies: list[str] = field(default_factory=list)
    transitive_of: list[str] = field(default_factory=list)
