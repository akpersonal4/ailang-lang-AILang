"""M77.1: Local Package Management — integration tests."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from tools.ail_package_manager.installer import install
from tools.ail_package_manager.lock import (
    generate_lock,
    read_lock_packages,
    deps_hash_matches,
)
from tools.ail_package_manager.manifest import parse_manifest, DependencySpec
from tools.ail_package_manager.models import LockFilePackage
from tools.ail_package_manager.resolver import resolve, ResolvedDependency
from ail_platform.report_schema import ExitCode


def _create_project(
    tmp_path: Path,
    name: str,
    deps: dict[str, DependencySpec] | None = None,
    with_local: list[str] | None = None,
) -> Path:
    """Create a minimal project with ail.toml."""
    project = tmp_path / name
    project.mkdir(parents=True, exist_ok=True)
    manifest = f'[project]\nname = "{name}"\nversion = "0.1.0"\n\n[dependencies]\n'
    if deps:
        for dep_name, spec in deps.items():
            if spec.path:
                manifest += f'{dep_name} = {{ path = "{spec.path}" }}\n'
            elif spec.git:
                manifest += f'{dep_name} = {{ git = "{spec.git}" }}\n'
            else:
                manifest += f'{dep_name} = "{spec.version_req}"\n'
    if with_local:
        for local_name in with_local:
            local_dir = project.parent / local_name
            local_dir.mkdir(exist_ok=True)
            local_manifest = local_dir / "ail.toml"
            local_manifest.write_text(
                f'[project]\nname = "{local_name}"\nversion = "1.0.0"\n',
                encoding="utf-8",
            )
            manifest += f'{local_name} = {{ path = "../{local_name}" }}\n'
    (project / "ail.toml").write_text(manifest, encoding="utf-8")
    return project


class TestLocalDepsInstall:
    """Test that local path dependencies install correctly."""

    def test_single_local_dep(self, tmp_path):
        local_dir = tmp_path / "mylib"
        local_dir.mkdir()
        (local_dir / "ail.toml").write_text(
            '[project]\nname = "mylib"\nversion = "1.0.0"\n',
            encoding="utf-8",
        )
        (local_dir / "test.ail").write_text(
            'fn main() {\n  return 0\n}\n',
            encoding="utf-8",
        )

        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        result = install(project, no_lock=False)
        assert result == ExitCode.SUCCESS
        assert (project / "lib" / "mylib").exists()

    def test_multiple_local_deps(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib1", "mylib2"])
        result = install(project, no_lock=False)
        assert result == ExitCode.SUCCESS
        assert (project / "lib" / "mylib1").exists()
        assert (project / "lib" / "mylib2").exists()

    def test_local_dep_creates_lock(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        result = install(project)
        assert result == ExitCode.SUCCESS
        assert (project / "ail.lock").exists()

    def test_local_dep_copied_not_linked(self, tmp_path):
        local_dir = tmp_path / "mylib"
        local_dir.mkdir()
        (local_dir / "ail.toml").write_text(
            '[project]\nname = "mylib"\nversion = "1.0.0"\n',
            encoding="utf-8",
        )
        (local_dir / "test.ail").write_text(
            'fn main() {\n  return 0\n}\n',
            encoding="utf-8",
        )
        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        result = install(project)
        assert result == ExitCode.SUCCESS
        lib_dest = project / "lib" / "mylib"
        assert lib_dest.exists()
        # Should not be a symlink
        assert not lib_dest.is_symlink()


class TestLockfileFormat:
    """Test lock file format and consistency."""

    def test_lockfile_uses_single_package_header(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        result = install(project)
        assert result == ExitCode.SUCCESS
        lock_content = (project / "ail.lock").read_text(encoding="utf-8")
        assert "[[packages]]" not in lock_content
        assert "[[package]]" in lock_content

    def test_lockfile_has_resolved_version(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        result = install(project)
        assert result == ExitCode.SUCCESS
        lock_content = (project / "ail.lock").read_text(encoding="utf-8")
        assert "resolved_version" in lock_content

    def test_lockfile_deterministic(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        install(project)
        lock1 = (project / "ail.lock").read_text(encoding="utf-8")
        install(project)
        lock2 = (project / "ail.lock").read_text(encoding="utf-8")
        assert lock1 == lock2

    def test_lockfile_changed_after_add_dep(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib1"])
        install(project)
        lock1 = (project / "ail.lock").read_text(encoding="utf-8")
        # Add second dep
        local_dir2 = tmp_path / "mylib2"
        local_dir2.mkdir()
        (local_dir2 / "ail.toml").write_text(
            '[project]\nname = "mylib2"\nversion = "1.0.0"\n',
            encoding="utf-8",
        )
        manifest_path = project / "ail.toml"
        manifest_path.write_text(
            manifest_path.read_text(encoding="utf-8")
            + 'mylib2 = { path = "../mylib2" }\n',
            encoding="utf-8",
        )
        install(project)
        lock2 = (project / "ail.lock").read_text(encoding="utf-8")
        assert lock1 != lock2

    def test_input_hash_present(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        install(project)
        lock_content = (project / "ail.lock").read_text(encoding="utf-8")
        assert "input_hash = " in lock_content


class TestReproducibleInstalls:
    """Test that second install is a no-op."""

    def test_second_install_no_op(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        result1 = install(project)
        assert result1 == ExitCode.SUCCESS
        lib1 = project / "lib" / "mylib"
        mtime1 = lib1.stat().st_mtime_ns
        result2 = install(project)
        assert result2 == ExitCode.SUCCESS
        mtime2 = lib1.stat().st_mtime_ns
        assert mtime1 == mtime2

    def test_clean_removes_unlisted_packages(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib1", "mylib2"])
        install(project)
        assert (project / "lib" / "mylib1").exists()
        assert (project / "lib" / "mylib2").exists()
        # Remove mylib2 from manifest
        manifest_path = project / "ail.toml"
        manifest_path.write_text(
            '[project]\nname = "myapp"\nversion = "0.1.0"\n\n'
            '[dependencies]\nmylib1 = { path = "../mylib1" }\n',
            encoding="utf-8",
        )
        install(project)
        assert (project / "lib" / "mylib1").exists()
        assert not (project / "lib" / "mylib2").exists()


class TestCircularDetection:
    """Test circular dependency detection with diagnostics."""

    def test_direct_cycle(self, tmp_path):
        from tools.ail_package_manager.resolver import _resolve_deps

        project = _create_project(tmp_path, "myapp")
        cache = project / ".ail" / "cache"
        cache.mkdir(parents=True, exist_ok=True)

        # Create local dep "b" at ../b that depends on "a"
        dir_b = tmp_path / "b"
        dir_b.mkdir()
        (dir_b / "ail.toml").write_text(
            '[project]\nname = "b"\nversion = "1.0.0"\n\n'
            '[dependencies]\na = { path = "../a" }\n',
            encoding="utf-8",
        )
        # Create local dep "a" at ../a that depends on "b"
        dir_a = tmp_path / "a"
        dir_a.mkdir()
        (dir_a / "ail.toml").write_text(
            '[project]\nname = "a"\nversion = "1.0.0"\n\n'
            '[dependencies]\nb = { path = "../b" }\n',
            encoding="utf-8",
        )

        # Simulate: we are resolving "b", chain starts with ["b"]
        # b's deps include a, a's deps include b -> cycle
        dep_a = DependencySpec(name="a", version_req="*", path=str(dir_a))
        visited = {"b"}
        chain = ["b"]
        deps = {"a": dep_a}

        with pytest.raises(ValueError, match="Circular"):
            _resolve_deps(
                deps=deps,
                project_root=project,
                manifest_path=project / "ail.toml",
                cache_dir=cache,
                resolved={},
                visited=visited,
                chain=chain,
            )


class TestVerboseOutput:
    """Test verbose installation output."""

    def test_verbose_shows_manifest_path(self, tmp_path, capsys):
        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        result = install(project, verbose=True)
        assert result == ExitCode.SUCCESS
        captured = capsys.readouterr()
        assert "Manifest:" in captured.out
        assert "Project root:" in captured.out


class TestFrozenLockfile:
    """Test frozen lockfile mode."""

    def test_frozen_with_fresh_lock(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        install(project)
        result = install(project, frozen_lockfile=True)
        assert result == ExitCode.SUCCESS

    def test_frozen_stale_lock(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        install(project)
        # Tamper with ail.toml — add a comment to change the hash
        manifest_path = project / "ail.toml"
        manifest_path.write_text(
            manifest_path.read_text(encoding="utf-8") + "\n# added comment\n",
            encoding="utf-8",
        )
        result = install(project, frozen_lockfile=True)
        assert result == ExitCode.LOCKFILE_MISMATCH


class TestExitCodes:
    """Test package-specific exit codes."""

    def test_success(self, tmp_path):
        project = _create_project(tmp_path, "myapp", with_local=["mylib"])
        result = install(project)
        assert result == ExitCode.SUCCESS
        assert ExitCode.RESOLUTION_FAILURE == 1
        assert ExitCode.CIRCULAR_DEPENDENCY == 2
        assert ExitCode.INVALID_MANIFEST == 3
        assert ExitCode.LOCKFILE_MISMATCH == 4
        assert ExitCode.GIT_CLONE_FAILURE == 5
