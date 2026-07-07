"""Project initialization logic for `ail init`."""

from __future__ import annotations

from pathlib import Path

from tools.ail_package_manager.manifest import validate_package_name, validate_version


_DEFAULT_ENTRY = """\
# {name}
# {description}

import "io"

let main = fn() => {{
    io.writeln("Hello from {name}!")
}}

main()
"""


_DEFAULT_TOML = """\
[project]
name = "{name}"
version = "{version}"
description = "{description}"
entry = "{entry}"

[language]
version = "0.3"
"""


def init_project(
    directory: Path,
    name: str,
    version: str,
    description: str = "",
    entry: str = "main.ail",
    yes: bool = False,
) -> int:
    """Initialize a new AILang project in the given directory.

    Returns 0 on success, 3 on error.
    """
    name = name or directory.name

    # Resolve directory
    target = directory.resolve()

    # Validate inputs
    err = validate_package_name(name)
    if err:
        print(f"Error: {err}")
        return 3

    err = validate_version(version)
    if err:
        print(f"Error: {err}")
        return 3

    # Check if directory already exists and is non-empty
    if target.exists():
        if not target.is_dir():
            print(f"Error: {target} exists and is not a directory")
            return 3
        existing = list(target.iterdir())
        if existing:
            # Filter out hidden files and common VCS directories
            visible = [f for f in existing if not f.name.startswith(".")]
            if visible:
                print(f"Error: {target} is not empty")
                return 3

    # Create directory structure
    target.mkdir(parents=True, exist_ok=True)

    # Determine source directory and entry path
    entry_path = Path(entry)
    if entry_path.parent != Path("."):
        src_dir = target / entry_path.parent
        src_dir.mkdir(parents=True, exist_ok=True)

    # Write ail.toml
    toml_path = target / "ail.toml"
    if not toml_path.exists():
        toml_content = _DEFAULT_TOML.format(
            name=name,
            version=version,
            description=description,
            entry=entry,
        )
        toml_path.write_text(toml_content, encoding="utf-8")
        print(f"  Created: {toml_path}")
    else:
        print(f"  Exists: {toml_path}")

    # Write entry stub
    entry_file = target / entry
    if not entry_file.exists():
        entry_content = _DEFAULT_ENTRY.format(
            name=name,
            description=description,
        )
        entry_file.write_text(entry_content, encoding="utf-8")
        print(f"  Created: {entry_file}")
    else:
        print(f"  Exists: {entry_file}")

    # Write empty ail.lock
    lock_path = target / "ail.lock"
    if not lock_path.exists():
        lock_content = "# ail.lock — Auto-generated. Do not edit manually.\n"
        lock_path.write_text(lock_content, encoding="utf-8")
        print(f"  Created: {lock_path}")
    else:
        print(f"  Exists: {lock_path}")

    print(f"\nInitialized project: {name} v{version}")
    return 0
