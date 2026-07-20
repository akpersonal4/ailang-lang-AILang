"""Tests for package naming policy and ail.toml generation.

Validates that:
- Snake_case package names are accepted
- Kebab-case package names are accepted with deprecation warning
- Invalid names are rejected
- ail new generates ail.toml with correct snake_case name
- Module resolver handles kebab-to-underscore normalization
"""

from __future__ import annotations

from pathlib import Path

from tools.ail_package_manager.manifest import validate_package_name

# =============================================================================
# Package naming validation
# =============================================================================


class TestValidatePackageName:
    """Test the package name validator."""

    def test_snake_case_basic(self) -> None:
        assert validate_package_name("my_package") is None

    def test_snake_case_single_word(self) -> None:
        assert validate_package_name("mathutils") is None

    def test_snake_case_with_numbers(self) -> None:
        assert validate_package_name("my_package_v2") is None

    def test_kebab_case_accepted(self) -> None:
        """Kebab-case is accepted with deprecation warning."""
        assert validate_package_name("my-package") is None

    def test_kebab_case_single_hyphen(self) -> None:
        assert validate_package_name("a-b") is None

    def test_rejects_uppercase(self) -> None:
        assert validate_package_name("My_Package") is not None

    def test_rejects_starts_with_digit(self) -> None:
        assert validate_package_name("1package") is not None

    def test_rejects_empty(self) -> None:
        assert validate_package_name("") is not None

    def test_rejects_special_chars(self) -> None:
        assert validate_package_name("my.package") is not None

    def test_rejects_too_long(self) -> None:
        long_name = "a" * 65
        result = validate_package_name(long_name)
        assert result is not None
        assert "too long" in result

    def test_max_length_valid(self) -> None:
        name = "a" * 64
        assert validate_package_name(name) is None

    def test_single_char(self) -> None:
        assert validate_package_name("x") is None


# =============================================================================
# ail new generates ail.toml
# =============================================================================


class TestAilNewAilToml:
    """Test that ail new creates ail.toml and ail.lock."""

    def test_new_creates_ail_toml(self, tmp_path: Path) -> None:
        """ail new should create ail.toml with snake_case name."""
        import os

        from compiler.cli.main import cmd_new

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = cmd_new(["test_project"])
            assert result == 0

            toml_path = tmp_path / "test_project" / "ail.toml"
            assert toml_path.exists()

            content = toml_path.read_text(encoding="utf-8")
            assert 'name = "test_project"' in content
            assert 'version = "0.1.0"' in content
        finally:
            os.chdir(old_cwd)

    def test_new_creates_ail_lock(self, tmp_path: Path) -> None:
        """ail new should create ail.lock."""
        import os

        from compiler.cli.main import cmd_new

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = cmd_new(["test_project"])
            assert result == 0

            lock_path = tmp_path / "test_project" / "ail.lock"
            assert lock_path.exists()
        finally:
            os.chdir(old_cwd)

    def test_new_hyphen_name_normalizes_to_underscore(self, tmp_path: Path) -> None:
        """ail new with hyphens should use underscores in ail.toml."""
        import os

        from compiler.cli.main import cmd_new

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = cmd_new(["my-project"])
            assert result == 0

            toml_path = tmp_path / "my-project" / "ail.toml"
            assert toml_path.exists()

            content = toml_path.read_text(encoding="utf-8")
            assert 'name = "my_project"' in content
        finally:
            os.chdir(old_cwd)

    def test_new_empty_mode_creates_ail_toml(self, tmp_path: Path) -> None:
        """ail new --empty should also create ail.toml."""
        import os

        from compiler.cli.main import cmd_new

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = cmd_new(["--empty", "minimal"])
            assert result == 0

            toml_path = tmp_path / "minimal" / "ail.toml"
            assert toml_path.exists()
        finally:
            os.chdir(old_cwd)


# =============================================================================
# Module resolver kebab-to-underscore normalization
# =============================================================================


class TestResolverNormalization:
    """Test that the module resolver handles kebab/underscore normalization."""

    def test_resolve_snake_case_package(self, tmp_path: Path) -> None:
        """Resolver finds lib/my_package/ail.toml for import my_package."""
        from compiler.compilation.resolution import ModuleResolver

        lib_dir = tmp_path / "lib" / "my_package"
        lib_dir.mkdir(parents=True)
        (lib_dir / "ail.toml").write_text(
            '[project]\nname = "my_package"\nversion = "0.1.0"\nentry = "main.ail"\n',
            encoding="utf-8",
        )
        (lib_dir / "main.ail").write_text('print("hello")\n', encoding="utf-8")

        resolver = ModuleResolver(tmp_path)
        result = resolver.resolve(("my_package",))
        assert result.name == "main.ail"

    def test_resolve_kebab_dir_with_snake_import(self, tmp_path: Path) -> None:
        """Resolver finds lib/my-package/ail.toml for import my_package."""
        from compiler.compilation.resolution import ModuleResolver

        lib_dir = tmp_path / "lib" / "my-package"
        lib_dir.mkdir(parents=True)
        (lib_dir / "ail.toml").write_text(
            '[project]\nname = "my-package"\nversion = "0.1.0"\nentry = "main.ail"\n',
            encoding="utf-8",
        )
        (lib_dir / "main.ail").write_text('print("hello")\n', encoding="utf-8")

        resolver = ModuleResolver(tmp_path)
        result = resolver.resolve(("my_package",))
        assert result.name == "main.ail"

    def test_resolve_snake_dir_with_kebab_import(self, tmp_path: Path) -> None:
        """Resolver finds lib/my_package/ail.toml for import my-package
        (won't work via parser, but resolver handles the lookup)."""
        from compiler.compilation.resolution import ModuleResolver

        lib_dir = tmp_path / "lib" / "my_package"
        lib_dir.mkdir(parents=True)
        (lib_dir / "ail.toml").write_text(
            '[project]\nname = "my_package"\nversion = "0.1.0"\nentry = "main.ail"\n',
            encoding="utf-8",
        )
        (lib_dir / "main.ail").write_text('print("hello")\n', encoding="utf-8")

        resolver = ModuleResolver(tmp_path)
        result = resolver.resolve(("my-package",))
        assert result.name == "main.ail"
