"""Tests for package management commands (add, remove, update, list).

Tests operate on temporary projects to avoid touching the real codebase.
"""

from __future__ import annotations

from pathlib import Path

from tools.ail_package_manager.commands import cmd_add, cmd_list, cmd_remove


def _make_project(tmp_path: Path, name: str = "test_project") -> Path:
    """Create a minimal project with ail.toml."""
    from compiler.cli.main import cmd_new

    import os

    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        cmd_new([name])
    finally:
        os.chdir(old_cwd)

    return tmp_path / name


# =============================================================================
# cmd_add
# =============================================================================


class TestCmdAdd:
    def test_add_simple_dependency(self, tmp_path: Path) -> None:
        project = _make_project(tmp_path)
        result = cmd_add("math_utils", "1.0.0", project_dir=project)
        assert result == 0

        content = (project / "ail.toml").read_text(encoding="utf-8")
        assert '"math_utils" = "1.0.0"' in content

    def test_add_local_path_dependency(self, tmp_path: Path) -> None:
        project = _make_project(tmp_path)
        result = cmd_add("my_lib", path="/local/path", project_dir=project)
        assert result == 0

        content = (project / "ail.toml").read_text(encoding="utf-8")
        assert 'path = "/local/path"' in content

    def test_add_git_dependency(self, tmp_path: Path) -> None:
        project = _make_project(tmp_path)
        result = cmd_add(
            "my_lib",
            git="https://github.com/example/repo.git",
            tag="v1.0.0",
            project_dir=project,
        )
        assert result == 0

        content = (project / "ail.toml").read_text(encoding="utf-8")
        assert 'git = "https://github.com/example/repo.git"' in content
        assert 'tag = "v1.0.0"' in content

    def test_add_rejects_invalid_name(self, tmp_path: Path) -> None:
        project = _make_project(tmp_path)
        result = cmd_add("Bad_Name", "1.0.0", project_dir=project)
        assert result == 1

    def test_add_multiple_dependencies(self, tmp_path: Path) -> None:
        project = _make_project(tmp_path)
        cmd_add("math_utils", "1.0.0", project_dir=project)
        cmd_add("string_utils", "2.0.0", project_dir=project)

        content = (project / "ail.toml").read_text(encoding="utf-8")
        assert '"math_utils" = "1.0.0"' in content
        assert '"string_utils" = "2.0.0"' in content

    def test_add_no_ail_toml(self, tmp_path: Path) -> None:
        result = cmd_add("pkg", project_dir=tmp_path)
        assert result == 1


# =============================================================================
# cmd_remove
# =============================================================================


class TestCmdRemove:
    def test_remove_existing_dependency(self, tmp_path: Path) -> None:
        project = _make_project(tmp_path)
        cmd_add("math_utils", "1.0.0", project_dir=project)

        result = cmd_remove("math_utils", project_dir=project)
        assert result == 0

        content = (project / "ail.toml").read_text(encoding="utf-8")
        assert "math_utils" not in content

    def test_remove_nonexistent_dependency(self, tmp_path: Path) -> None:
        project = _make_project(tmp_path)
        result = cmd_remove("nonexistent", project_dir=project)
        assert result == 1

    def test_remove_one_of_many(self, tmp_path: Path) -> None:
        project = _make_project(tmp_path)
        cmd_add("math_utils", "1.0.0", project_dir=project)
        cmd_add("string_utils", "2.0.0", project_dir=project)

        cmd_remove("math_utils", project_dir=project)

        content = (project / "ail.toml").read_text(encoding="utf-8")
        assert "math_utils" not in content
        assert '"string_utils" = "2.0.0"' in content

    def test_remove_no_ail_toml(self, tmp_path: Path) -> None:
        result = cmd_remove("pkg", project_dir=tmp_path)
        assert result == 1


# =============================================================================
# cmd_list
# =============================================================================


class TestCmdList:
    def test_list_no_dependencies(self, tmp_path: Path) -> None:
        project = _make_project(tmp_path)
        result = cmd_list(project_dir=project)
        assert result == 0

    def test_list_with_dependencies(self, tmp_path: Path) -> None:
        project = _make_project(tmp_path)
        cmd_add("math_utils", "1.0.0", project_dir=project)

        result = cmd_list(project_dir=project)
        assert result == 0

    def test_list_no_ail_toml(self, tmp_path: Path) -> None:
        result = cmd_list(project_dir=tmp_path)
        assert result == 1
