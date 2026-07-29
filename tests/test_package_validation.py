"""Tests for M127 P0 package validation improvements.

Covers:
- PackageError structured diagnostics
- Missing manifest
- Missing [project] section
- Invalid package name
- Invalid version
- Invalid authors
- Invalid license
- Invalid description
- Missing entry (warning)
- Exit codes
- CLI formatting
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ail_platform.report_schema import ExitCode
from tools.ail_package_manager.errors import PackageError
from tools.ail_package_manager.manifest import parse_manifest, validate_package_name, validate_version


# =============================================================================
# PackageError structured diagnostics
# =============================================================================


class TestPackageError:
    def test_basic_error(self) -> None:
        err = PackageError(
            reason="Missing [project] section.",
            suggestion='Add a [project] section with name and version.',
        )
        diag = err.format_diagnostic()
        assert "Package Validation Error" in diag
        assert "Missing [project] section." in diag
        assert "Add a [project] section" in diag

    def test_error_with_manifest_path(self) -> None:
        err = PackageError(
            reason="Manifest not found.",
            manifest_path="/project/ail.toml",
        )
        diag = err.format_diagnostic()
        assert "Manifest:" in diag
        assert "/project/ail.toml" in diag

    def test_error_with_location(self) -> None:
        err = PackageError(
            reason="Invalid name.",
            location="[project].name",
        )
        diag = err.format_diagnostic()
        assert "Location:" in diag
        assert "[project].name" in diag

    def test_error_with_detail(self) -> None:
        err = PackageError(
            reason="Parse failed.",
            detail="Expected a string, got integer.",
        )
        diag = err.format_diagnostic()
        assert "Detail:" in diag
        assert "Expected a string" in diag

    def test_str_fallback(self) -> None:
        err = PackageError(
            reason="Something broke.",
            manifest_path="ail.toml",
        )
        msg = str(err)
        assert "Package Validation Error" in msg
        assert "Something broke" in msg
        assert "ail.toml" in msg

    def test_empty_fields(self) -> None:
        err = PackageError(reason="Test")
        diag = err.format_diagnostic()
        assert "Suggestion:" not in diag
        assert "Detail:" not in diag
        assert "Manifest:" not in diag
        assert "Location:" not in diag

    def test_all_fields(self) -> None:
        err = PackageError(
            reason="Test reason.",
            suggestion="Test suggestion.",
            detail="Test detail.",
            manifest_path="/p/ail.toml",
            location="[test]",
        )
        diag = err.format_diagnostic()
        assert diag.count("\n") > 5
        assert "Test reason" in diag
        assert "Test suggestion" in diag
        assert "Test detail" in diag
        assert "/p/ail.toml" in diag
        assert "[test]" in diag


# =============================================================================
# Exit codes
# =============================================================================


class TestExitCodes:
    def test_manifest_not_found_code(self) -> None:
        assert ExitCode.MANIFEST_NOT_FOUND == 10

    def test_invalid_package_name_code(self) -> None:
        assert ExitCode.INVALID_PACKAGE_NAME == 11

    def test_invalid_version_code(self) -> None:
        assert ExitCode.INVALID_VERSION == 12

    def test_invalid_entry_code(self) -> None:
        assert ExitCode.INVALID_ENTRY == 13

    def test_invalid_dependency_code(self) -> None:
        assert ExitCode.INVALID_DEPENDENCY == 14

    def test_missing_manifest_returns_correct_code(self) -> None:
        from tools.ail_package_manager.installer import install

        result = install(project_root=Path("/nonexistent/path"))
        assert result == ExitCode.MANIFEST_NOT_FOUND


# =============================================================================
# Manifest validation
# =============================================================================


class TestManifestValidation:
    def test_missing_manifest_file(self) -> None:
        with pytest.raises(PackageError) as excinfo:
            parse_manifest(Path("/nonexistent/path/ail.toml"))
        assert "Manifest not found" in str(excinfo.value)

    def test_missing_project_section(self, tmp_path: Path) -> None:
        toml_path = tmp_path / "ail.toml"
        toml_path.write_text("[tool]\nkey = 1\n", encoding="utf-8")
        with pytest.raises(PackageError) as excinfo:
            parse_manifest(toml_path)
        diag = excinfo.value.format_diagnostic()
        assert "Missing [project] section" in diag or "validation error" in diag

    def test_missing_project_name(self, tmp_path: Path) -> None:
        toml_path = tmp_path / "ail.toml"
        toml_path.write_text(
            "[project]\nversion = \"1.0.0\"\n", encoding="utf-8"
        )
        with pytest.raises(PackageError) as excinfo:
            parse_manifest(toml_path)
        err = excinfo.value
        assert "Missing" in err.detail or "name" in err.detail

    def test_missing_project_version(self, tmp_path: Path) -> None:
        (tmp_path / "main.ail").write_text("", encoding="utf-8")
        toml_path = tmp_path / "ail.toml"
        toml_path.write_text(
            "[project]\nname = \"my_package\"\n", encoding="utf-8"
        )
        with pytest.raises(PackageError) as excinfo:
            parse_manifest(toml_path)
        err = excinfo.value
        assert "Missing" in err.detail or "version" in err.detail

    def test_invalid_package_name_validation(self, tmp_path: Path) -> None:
        (tmp_path / "main.ail").write_text("", encoding="utf-8")
        toml_path = tmp_path / "ail.toml"
        toml_path.write_text(
            "[project]\nname = \"Bad_Name\"\nversion = \"1.0.0\"\n", encoding="utf-8"
        )
        with pytest.raises(PackageError) as excinfo:
            parse_manifest(toml_path)
        err = excinfo.value
        assert "Invalid package name" in err.detail or "Invalid package name" in str(err)

    def test_invalid_version_validation(self, tmp_path: Path) -> None:
        (tmp_path / "main.ail").write_text("", encoding="utf-8")
        toml_path = tmp_path / "ail.toml"
        toml_path.write_text(
            "[project]\nname = \"my_package\"\nversion = \"abc\"\n", encoding="utf-8"
        )
        with pytest.raises(PackageError) as excinfo:
            parse_manifest(toml_path)
        err = excinfo.value
        assert "Invalid version" in err.detail or "Invalid version" in str(err)

    def test_empty_project_name(self, tmp_path: Path) -> None:
        toml_path = tmp_path / "ail.toml"
        (tmp_path / "main.ail").write_text("", encoding="utf-8")
        toml_path.write_text(
            "[project]\nname = \"\"\nversion = \"1.0.0\"\n", encoding="utf-8"
        )
        with pytest.raises(PackageError) as excinfo:
            parse_manifest(toml_path)
        err = excinfo.value
        assert "Missing or empty" in err.reason or "Missing or empty" in err.detail

    def test_empty_project_version(self, tmp_path: Path) -> None:
        toml_path = tmp_path / "ail.toml"
        (tmp_path / "main.ail").write_text("", encoding="utf-8")
        toml_path.write_text(
            "[project]\nname = \"my_package\"\nversion = \"\"\n", encoding="utf-8"
        )
        with pytest.raises(PackageError) as excinfo:
            parse_manifest(toml_path)
        err = excinfo.value
        assert "Missing or empty" in err.reason or "Missing or empty" in err.detail

    def test_authors_not_list(self, tmp_path: Path) -> None:
        toml_path = tmp_path / "ail.toml"
        (tmp_path / "main.ail").write_text("", encoding="utf-8")
        toml_path.write_text(
            "[project]\nname = \"my_package\"\nversion = \"1.0.0\"\n"
            "authors = \"Alice\"\n",
            encoding="utf-8",
        )
        err = None
        try:
            parse_manifest(toml_path)
        except PackageError as e:
            err = e
        assert err is not None
        assert "authors" in err.detail.lower() or "authors" in err.reason.lower()

    def test_authors_non_string_element(self, tmp_path: Path) -> None:
        toml_path = tmp_path / "ail.toml"
        (tmp_path / "main.ail").write_text("", encoding="utf-8")
        toml_path.write_text(
            "[project]\nname = \"my_package\"\nversion = \"1.0.0\"\n"
            "authors = [42]\n",
            encoding="utf-8",
        )
        err = None
        try:
            parse_manifest(toml_path)
        except PackageError as e:
            err = e
        assert err is not None
        assert "Author" in err.detail or "Author" in err.reason

    def test_license_non_string(self, tmp_path: Path) -> None:
        toml_path = tmp_path / "ail.toml"
        (tmp_path / "main.ail").write_text("", encoding="utf-8")
        toml_path.write_text(
            "[project]\nname = \"my_package\"\nversion = \"1.0.0\"\n"
            "license = true\n",
            encoding="utf-8",
        )
        err = None
        try:
            parse_manifest(toml_path)
        except PackageError as e:
            err = e
        # Boolean license is accepted (boolean is not None and not "" so it triggers
        # the non-string check but the check requires not None AND not ""
        # boolean True != "" is true, so it should error)
        assert err is not None

    def test_description_non_string(self, tmp_path: Path) -> None:
        toml_path = tmp_path / "ail.toml"
        (tmp_path / "main.ail").write_text("", encoding="utf-8")
        toml_path.write_text(
            "[project]\nname = \"my_package\"\nversion = \"1.0.0\"\n"
            "description = 123\n",
            encoding="utf-8",
        )
        err = None
        try:
            parse_manifest(toml_path)
        except PackageError as e:
            err = e
        assert err is not None
        assert "description" in err.detail.lower() or "description" in err.reason.lower()

    def test_entry_warning_on_missing(self, tmp_path: Path, capsys) -> None:
        """Entry warning should be printed, not raised as error."""
        toml_path = tmp_path / "ail.toml"
        toml_path.write_text(
            "[project]\nname = \"my_package\"\nversion = \"1.0.0\"\n"
            "entry = \"nonexistent.ail\"\n",
            encoding="utf-8",
        )
        manifest = parse_manifest(toml_path)
        assert manifest.name == "my_package"
        captured = capsys.readouterr()
        assert "Warning:" in captured.out

    def test_valid_manifest_parses(self, tmp_path: Path) -> None:
        (tmp_path / "main.ail").write_text("", encoding="utf-8")
        toml_path = tmp_path / "ail.toml"
        toml_path.write_text(
            "[project]\nname = \"my_package\"\nversion = \"1.0.0\"\n",
            encoding="utf-8",
        )
        manifest = parse_manifest(toml_path)
        assert manifest.name == "my_package"
        assert manifest.version == "1.0.0"

    def test_manifest_with_all_fields(self, tmp_path: Path) -> None:
        (tmp_path / "main.ail").write_text("", encoding="utf-8")
        toml_path = tmp_path / "ail.toml"
        toml_path.write_text(
            "[project]\nname = \"my_package\"\nversion = \"1.0.0\"\n"
            "description = \"Test project\"\n"
            "authors = [\"Alice\"]\n"
            "license = \"MIT\"\n"
            "entry = \"main.ail\"\n"
            "[language]\nversion = \"1.1.7\"\n",
            encoding="utf-8",
        )
        manifest = parse_manifest(toml_path)
        assert manifest.name == "my_package"
        assert manifest.version == "1.0.0"
        assert manifest.description == "Test project"
        assert manifest.authors == ["Alice"]
        assert manifest.license == "MIT"
        assert manifest.entry == "main.ail"
        assert manifest.language_version == "1.1.7"


# =============================================================================
# CLI formatting test
# =============================================================================


class TestCliFormatting:
    def test_install_no_manifest(self) -> None:
        from tools.ail_package_manager.installer import install

        result = install(project_root=Path("/nonexistent"))
        assert result == ExitCode.MANIFEST_NOT_FOUND
