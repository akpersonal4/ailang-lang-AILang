#!/usr/bin/env python3
"""Install the AILang Inventory System for a single user.

Usage:
    python tools/install_inventory.py                    # Default install
    python tools/install_inventory.py --target ~/inventory  # Custom path
    python tools/install_inventory.py --verify           # Verify existing install
    python tools/install_inventory.py --help             # This message

Target: less than 60 seconds to install.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────

DEFAULT_TARGET = os.path.join(Path.home(), "ailang-inventory")
REQUIRED_DIRS = ["data", "backups", "imports", "exports"]

INSTALLER_VERSION = "1.0.0-RC1"

# ── Paths ──────────────────────────────────────────────────────────

# This script lives at tools/install_inventory.py
# The inventory source is at apps/inventory/
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
INVENTORY_SRC = REPO_DIR / "apps" / "inventory"

# ── Helpers ────────────────────────────────────────────────────────

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def ok(msg):
    print(f"{GREEN}✓{RESET} {msg}")


def warn(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")


def fail(msg):
    print(f"{RED}✗{RESET} {msg}")


def header(msg):
    print(f"\n{BOLD}{CYAN}{msg}{RESET}")
    print("─" * 50)


# ── Checks ─────────────────────────────────────────────────────────

def check_python():
    """Verify Python 3.11+ is available."""
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 11):
        fail(f"Python 3.11+ required, found {v.major}.{v.minor}.{v.micro}")
        print("  Install Python 3.11+ from https://python.org")
        return False
    ok(f"Python {v.major}.{v.minor}.{v.micro}")
    return True


def check_ail():
    """Verify `ail` CLI is available."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "compiler.cli.main", "--help"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            ok("AILang CLI available")
            return True
        else:
            warn("AILang CLI not responding as expected")
            return False
    except FileNotFoundError:
        fail("AILang not found. Run: pip install -e .")
        return False
    except subprocess.TimeoutExpired:
        fail("AILang CLI timed out")
        return False


def check_inventory_source():
    """Verify the inventory source files exist."""
    main_file = INVENTORY_SRC / "main.ail"
    if not main_file.exists():
        fail(f"Inventory source not found at {INVENTORY_SRC}")
        print("  Make sure you are running this script from the repository root.")
        return False

    ail_files = list(INVENTORY_SRC.glob("*.ail"))
    ok(f"Inventory source found: {len(ail_files)} .ail files")
    return True


# ── Installation ───────────────────────────────────────────────────

def create_directories(target):
    """Create required directories under target."""
    for d in REQUIRED_DIRS:
        path = os.path.join(target, d)
        os.makedirs(path, exist_ok=True)
    ok(f"Directories created in {target}")


def copy_source(target):
    """Copy all .ail files from source to target."""
    target_path = Path(target)
    count = 0
    for f in INVENTORY_SRC.glob("*.ail"):
        shutil.copy2(f, target_path / f.name)
        count += 1
    ok(f"Copied {count} .ail files" if count > 0 else "No .ail files copied")

    # Copy config/ directory (users.json)
    config_src = INVENTORY_SRC / "config"
    config_dst = target_path / "config"
    if config_src.exists():
        os.makedirs(config_dst, exist_ok=True)
        for f in config_src.iterdir():
            shutil.copy2(f, config_dst / f.name)
        ok("Copied config/")

    # Also copy test files
    test_src = INVENTORY_SRC / "tests"
    test_dst = target_path / "tests"
    if test_src.exists():
        os.makedirs(test_dst, exist_ok=True)
        test_count = 0
        for f in test_src.glob("*.ail"):
            shutil.copy2(f, test_dst / f.name)
            test_count += 1
        ok(f"Copied {test_count} test .ail files" if test_count > 0 else "No test files copied")

    # Copy test_compile.py
    compile_test_src = INVENTORY_SRC / "test_compile.py"
    if compile_test_src.exists():
        shutil.copy2(compile_test_src, target_path / "test_compile.py")
        ok("Copied test_compile.py")

    # Copy runner.py
    runner_src = INVENTORY_SRC / "tests" / "runner.py"
    if runner_src.exists():
        os.makedirs(target_path / "tests", exist_ok=True)
        shutil.copy2(runner_src, target_path / "tests" / "runner.py")
        ok("Copied tests/runner.py")

    return count


def create_config(target):
    """Create default config/users.json."""
    config_dir = os.path.join(target, "config")
    os.makedirs(config_dir, exist_ok=True)

    users_file = os.path.join(config_dir, "users.json")
    if not os.path.exists(users_file):
        default_users = [
            {
                "username": "admin",
                "password": "admin123",
                "role": "admin",
                "name": "Admin User"
            },
            {
                "username": "staff1",
                "password": "staff123",
                "role": "staff",
                "name": "Staff Member"
            }
        ]
        with open(users_file, "w") as f:
            json.dump(default_users, f, indent=2)
        ok(f"Created default config/users.json")
        warn("Default passwords: admin/admin123, staff1/staff123 — change after first login")
    else:
        ok(f"Config file already exists: {users_file}")


def create_backup_dir(target):
    """Ensure backup directory structure exists."""
    backup_dir = os.path.join(target, "backups", "auto")
    os.makedirs(backup_dir, exist_ok=True)
    ok("Backup directories ready")


def create_readme(target):
    """Create a README in the install target."""
    readme_path = os.path.join(target, "README.txt")
    content = f"""AILang Inventory System
{'=' * 50}
Installed:  {datetime.now().isoformat()}
Version:    {INSTALLER_VERSION}
Source:     {INVENTORY_SRC}

Commands:
  ail run main.ail help     Show available commands
  ail run main.ail init     Seed demo data
  ail run main.ail report   Show inventory summary

Data:     data/
Backups:  backups/
Imports:  imports/

Documentation:
  {REPO_DIR}/docs/deployment/FIRST_DEPLOYMENT.md
  {REPO_DIR}/docs/deployment/FIRST_USER_GUIDE.md
  {REPO_DIR}/docs/deployment/OPERATIONS_RUNBOOK.md
"""
    with open(readme_path, "w") as f:
        f.write(content)
    ok("Created README.txt")


# ── Verification ───────────────────────────────────────────────────

def verify_build(target):
    """Run `ail build main.ail` to verify the application compiles."""
    main_file = os.path.join(target, "main.ail")
    if not os.path.exists(main_file):
        fail("main.ail not found in target")
        return False

    result = subprocess.run(
        [sys.executable, "-m", "compiler.cli.main", "build", main_file],
        capture_output=True, text=True, timeout=30,
        cwd=target
    )
    if result.returncode == 0:
        ok("ail build main.ail — SUCCESS")
        return True
    else:
        fail("ail build main.ail — FAILED")
        print(result.stderr[:500])
        return False


def verify_help(target):
    """Run the help command and verify it works."""
    result = subprocess.run(
        [sys.executable, "-m", "compiler.cli.main", "run", os.path.join(target, "main.ail"), "help"],
        capture_output=True, text=True, timeout=30,
        cwd=target
    )
    if result.returncode == 0 and "Usage:" in result.stdout:
        ok("ail run main.ail help — SUCCESS")
        return True
    else:
        fail("ail run main.ail help — FAILED")
        print(result.stderr[:500])
        return False


def verify_compile_test(target):
    """Run test_compile.py and verify it passes."""
    test_file = os.path.join(target, "test_compile.py")
    if not os.path.exists(test_file):
        warn("test_compile.py not found — skipping")
        return True

    result = subprocess.run(
        [sys.executable, test_file],
        capture_output=True, text=True, timeout=60,
        cwd=target
    )
    if result.returncode == 0 and "ALL TESTS PASSED" in result.stdout:
        ok("test_compile.py — ALL TESTS PASSED")
        return True
    else:
        fail("test_compile.py — FAILED")
        print(result.stdout[-500:])
        print(result.stderr[-500:])
        return False


# ── Main ───────────────────────────────────────────────────────────

def print_banner():
    print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════╗{RESET}
{BOLD}{CYAN}║      AILang Inventory System Installer     ║{RESET}
{BOLD}{CYAN}║           v{INSTALLER_VERSION}                ║{RESET}
{BOLD}{CYAN}╚══════════════════════════════════════════╝{RESET}
""")


def install(target):
    """Full installation sequence."""
    header("Pre-flight Checks")
    checks_pass = all([
        check_python(),
        check_ail(),
        check_inventory_source(),
    ])
    if not checks_pass:
        fail("Pre-flight checks failed. Aborting.")
        sys.exit(1)

    header(f"Installing to {target}")
    create_directories(target)
    file_count = copy_source(target)
    create_config(target)
    create_backup_dir(target)
    create_readme(target)

    if file_count == 0:
        fail("No files were copied. Aborting.")
        sys.exit(1)

    header("Verification")
    verify_build(target)
    verify_help(target)
    verify_compile_test(target)

    header("Installation Summary")
    ok(f"Target:     {target}")
    ok(f"Files:      {file_count} .ail files + tests")
    ok(f"Data:       {os.path.join(target, 'data')}")
    ok(f"Backups:    {os.path.join(target, 'backups')}")
    ok(f"Config:     {os.path.join(target, 'config', 'users.json')}")
    warn("Default admin password is 'admin123' — change immediately")
    print()
    print(f"  {BOLD}Quick start:{RESET}")
    print(f"    cd {target}")
    print(f"    ail run main.ail help")
    print(f"    ail run main.ail init")
    print(f"    ail run main.ail report")
    print()


def verify_existing(target):
    """Verify an existing installation."""
    header(f"Verifying installation at {target}")
    checks_pass = all([
        check_python(),
        check_ail(),
    ])
    if not checks_pass:
        fail("Verification checks failed.")
        sys.exit(1)

    # Check directories
    all_dirs_exist = True
    for d in REQUIRED_DIRS:
        path = os.path.join(target, d)
        if os.path.isdir(path):
            ok(f"Directory exists: {d}/")
        else:
            warn(f"Directory missing: {d}/")
            all_dirs_exist = False

    # Check main.ail
    main_file = os.path.join(target, "main.ail")
    if os.path.exists(main_file):
        ok("main.ail found")
    else:
        fail("main.ail missing")
        sys.exit(1)

    verify_build(target)
    verify_help(target)
    verify_compile_test(target)

    if all_dirs_exist:
        ok("Installation verified successfully")
    else:
        warn("Some directories are missing — run install again to create them")


def main():
    print_banner()

    target = DEFAULT_TARGET
    mode = "install"

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--target" and i + 1 < len(args):
            target = os.path.abspath(args[i + 1])
            i += 2
        elif args[i] == "--verify":
            mode = "verify"
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                target = os.path.abspath(args[i + 1])
                i += 2
            else:
                i += 1
        elif args[i] == "--help" or args[i] == "-h":
            print(__doc__)
            sys.exit(0)
        else:
            print(f"Unknown argument: {args[i]}")
            sys.exit(1)

    if mode == "install":
        if os.path.exists(target):
            print(f"  {YELLOW}Target directory already exists: {target}{RESET}")
            response = input("  Overwrite? (y/N): ").strip().lower()
            if response != "y":
                print("  Aborted.")
                sys.exit(0)
        install(target)
    elif mode == "verify":
        if not os.path.exists(target):
            fail(f"Target directory not found: {target}")
            sys.exit(1)
        verify_existing(target)


if __name__ == "__main__":
    main()
