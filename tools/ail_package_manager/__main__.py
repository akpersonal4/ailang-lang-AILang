"""AILang Package Manager — dependency management for AILang projects."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ail_platform.report_schema import ExitCode
from tools.ail_package_manager.init import init_project
from tools.ail_package_manager.installer import install
from tools.ail_package_manager.registry import (
    RegistryError,
    load_registry_url,
    publish_local,
    publish_remote,
)


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


def cmd_publish(args: argparse.Namespace) -> int:
    """Pack and publish the current project to a registry."""
    project_root = Path.cwd()
    registry_arg = args.registry

    if registry_arg:
        registry_url = registry_arg
    else:
        registry_url = load_registry_url(project_root)

    try:
        if registry_url.startswith(("file://", "/", ".")):
            local_path = registry_url
            if local_path.startswith("file://"):
                local_path = local_path[7:]
            publish_local(project_root, Path(local_path).resolve())
        else:
            publish_remote(project_root, registry_url)
        return ExitCode.SUCCESS
    except (RegistryError, ValueError) as e:
        print(f"Publish error: {e}", file=sys.stderr)
        return ExitCode.FAILURE


def cmd_add(args: argparse.Namespace) -> int:
    from tools.ail_package_manager.commands import cmd_add as do_add

    return do_add(
        package=args.package,
        version=args.version or "*",
        path=args.path,
        git=args.git,
        tag=args.tag,
        branch=args.branch,
    )


def cmd_remove(args: argparse.Namespace) -> int:
    from tools.ail_package_manager.commands import cmd_remove as do_remove

    return do_remove(package=args.package)


def cmd_install(args: argparse.Namespace) -> int:
    return install(
        project_root=Path.cwd(),
        no_lock=args.no_lock,
        offline=args.offline,
        frozen_lockfile=args.frozen_lockfile or args.frozen,
        verbose=args.verbose,
    )


def cmd_update(args: argparse.Namespace) -> int:
    from tools.ail_package_manager.commands import cmd_update as do_update

    return do_update(package=args.package)


def cmd_list(args: argparse.Namespace) -> int:
    from tools.ail_package_manager.commands import cmd_list as do_list

    return do_list(tree=args.tree, outdated=args.outdated)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AILang Package Manager — dependency management for AILang projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ail publish
    publish_parser = subparsers.add_parser(
        "publish", help="Publish package to registry"
    )
    publish_parser.add_argument(
        "--registry",
        default=None,
        help="Registry URL (default: from ail.toml [tool.registry] or AIL_REGISTRY env var)",
    )

    # ail init
    init_parser = subparsers.add_parser("init", help="Initialize a new AILang project")
    init_parser.add_argument(
        "directory", nargs="?", default=None, help="Target directory (default: current)"
    )
    init_parser.add_argument(
        "--name", default=None, help="Project name (default: directory name)"
    )
    init_parser.add_argument(
        "--version", default="0.1.0", help="Initial version (default: 0.1.0)"
    )
    init_parser.add_argument("--description", default=None, help="Project description")
    init_parser.add_argument(
        "--entry", default="main.ail", help="Entry point (default: main.ail)"
    )
    init_parser.add_argument(
        "--yes", "-y", action="store_true", help="Accept all defaults"
    )

    # ail add
    add_parser = subparsers.add_parser("add", help="Add a dependency")
    add_parser.add_argument(
        "package", help="Package name (e.g. my_package, my_package@1.0.0)"
    )
    add_parser.add_argument(
        "--version", "-V", default=None, help="Version requirement (default: *)"
    )
    add_parser.add_argument("--path", default=None, help="Local path to package")
    add_parser.add_argument("--git", default=None, help="Git repository URL")
    add_parser.add_argument("--tag", default=None, help="Git tag")
    add_parser.add_argument("--branch", default=None, help="Git branch")
    add_parser.add_argument(
        "--dev", action="store_true", help="Add as dev dependency (future)"
    )

    # ail remove
    remove_parser = subparsers.add_parser("remove", help="Remove a dependency")
    remove_parser.add_argument("package", help="Package name to remove")

    # ail install
    install_parser = subparsers.add_parser("install", help="Install all dependencies")
    install_parser.add_argument(
        "--no-lock", action="store_true", help="Skip lock file creation"
    )
    install_parser.add_argument(
        "--offline", action="store_true", help="Fail if network access required"
    )
    install_parser.add_argument(
        "--frozen-lockfile", action="store_true", help="Fail if lock file would change"
    )
    install_parser.add_argument(
        "--frozen", action="store_true", help="Alias for --frozen-lockfile"
    )
    install_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed installation output"
    )

    # ail update
    update_parser = subparsers.add_parser("update", help="Update dependencies")
    update_parser.add_argument(
        "package", nargs="?", default=None, help="Package to update (default: all)"
    )

    # ail list
    list_parser = subparsers.add_parser("list", help="List installed dependencies")
    list_parser.add_argument("--tree", action="store_true", help="Show dependency tree")
    list_parser.add_argument(
        "--outdated", action="store_true", help="Show outdated packages"
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return ExitCode.SUCCESS

    command_map = {
        "publish": cmd_publish,
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
        return ExitCode.INTERNAL_ERROR

    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
