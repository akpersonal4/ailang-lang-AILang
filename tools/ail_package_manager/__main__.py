"""AILang Package Manager — dependency management for AILang projects.

Exit codes:
    0 = Success
    1 = Operation failed (resolution, download, checksum)
    3 = Internal error (invalid args, missing manifest, I/O error)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.ail_package_manager.init import init_project
from tools.ail_package_manager.installer import install
from tools.ail_package_manager.manifest import find_manifest, parse_manifest


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def cmd_init(args: argparse.Namespace) -> int:
    directory = Path(args.directory) if args.directory else Path.cwd()
    return init_project(
        directory=directory,
        name=args.name or directory.name,
        version=args.version,
        description=args.description or "",
        entry=args.entry,
        yes=args.yes,
    )


def cmd_add(args: argparse.Namespace) -> int:
    manifest_path = find_manifest(Path.cwd())
    if manifest_path is None:
        print("Error: No ail.toml found in current or parent directories", file=sys.stderr)
        return 3
    print(f"ail add: {args.package} (not yet implemented)")
    return 1


def cmd_remove(args: argparse.Namespace) -> int:
    manifest_path = find_manifest(Path.cwd())
    if manifest_path is None:
        print("Error: No ail.toml found in current or parent directories", file=sys.stderr)
        return 3
    print(f"ail remove: {args.package} (not yet implemented)")
    return 1


def cmd_install(args: argparse.Namespace) -> int:
    return install(
        project_root=Path.cwd(),
        no_lock=args.no_lock,
        offline=args.offline,
        frozen_lockfile=args.frozen_lockfile,
    )


def cmd_update(args: argparse.Namespace) -> int:
    manifest_path = find_manifest(Path.cwd())
    if manifest_path is None:
        print("Error: No ail.toml found in current or parent directories", file=sys.stderr)
        return 3
    pkg = args.package
    print(f"ail update {pkg or '(all)'} (not yet implemented)")
    return 1


def cmd_list(args: argparse.Namespace) -> int:
    manifest_path = find_manifest(Path.cwd())
    if manifest_path is None:
        print("Error: No ail.toml found in current or parent directories", file=sys.stderr)
        return 3
    print("ail list (not yet implemented)")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AILang Package Manager — dependency management for AILang projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ail init
    init_parser = subparsers.add_parser("init", help="Initialize a new AILang project")
    init_parser.add_argument("directory", nargs="?", default=None, help="Target directory (default: current)")
    init_parser.add_argument("--name", default=None, help="Project name (default: directory name)")
    init_parser.add_argument("--version", default="0.1.0", help="Initial version (default: 0.1.0)")
    init_parser.add_argument("--description", default=None, help="Project description")
    init_parser.add_argument("--entry", default="main.ail", help="Entry point (default: main.ail)")
    init_parser.add_argument("--yes", "-y", action="store_true", help="Accept all defaults")

    # ail add
    add_parser = subparsers.add_parser("add", help="Add a dependency")
    add_parser.add_argument("package", help="Package name, path=..., or git=...")
    add_parser.add_argument("--tag", default=None, help="Git tag")
    add_parser.add_argument("--branch", default=None, help="Git branch")
    add_parser.add_argument("--rev", default=None, help="Git commit hash")
    add_parser.add_argument("--dev", action="store_true", help="Add as dev dependency (future)")
    add_parser.add_argument("--save-exact", action="store_true", help="Save exact version")

    # ail remove
    remove_parser = subparsers.add_parser("remove", help="Remove a dependency")
    remove_parser.add_argument("package", help="Package name to remove")

    # ail install
    install_parser = subparsers.add_parser("install", help="Install all dependencies")
    install_parser.add_argument("--no-lock", action="store_true", help="Skip lock file creation")
    install_parser.add_argument("--offline", action="store_true", help="Fail if network access required")
    install_parser.add_argument("--frozen-lockfile", action="store_true", help="Fail if lock file would change")

    # ail update
    update_parser = subparsers.add_parser("update", help="Update dependencies")
    update_parser.add_argument("package", nargs="?", default=None, help="Package to update (default: all)")

    # ail list
    list_parser = subparsers.add_parser("list", help="List installed dependencies")
    list_parser.add_argument("--tree", action="store_true", help="Show dependency tree")
    list_parser.add_argument("--outdated", action="store_true", help="Show outdated packages")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    command_map = {
        "init": cmd_init,
        "add": cmd_add,
        "remove": cmd_remove,
        "install": cmd_install,
        "update": cmd_update,
        "list": cmd_list,
    }

    handler = command_map.get(args.command)
    if handler is None:
        print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
        return 3

    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
