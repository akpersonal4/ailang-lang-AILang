"""Python test runner for inventory system - mirrors AILang runner.py."""

import os
import sys
from pathlib import Path

os.chdir(str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, os.getcwd())

from business.data_seed import seed_all
from core.storage import storage_clear_all

TESTS_DIR = Path(__file__).resolve().parent


def run_test(test_file: str) -> tuple[bool, str]:
    """Run a Python test file by importing and executing its main()."""
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("test_module", test_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        import traceback

        return False, f"ImportError: {e}\n{traceback.format_exc()}"

    try:
        import io

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        result = mod.main()

        captured = sys.stdout.getvalue()
        sys.stdout = old_stdout
    except Exception as e:
        sys.stdout = old_stdout
        import traceback

        return False, f"{type(e).__name__}: {e}\n{traceback.format_exc()}"

    return result == 0, captured


# Setup
print("=== Setup: init ===")
storage_clear_all()
from main import (
    main_demo_create_customers,
    main_demo_create_products,
    main_demo_create_vendors,
)

main_demo_create_products()
main_demo_create_customers()
main_demo_create_vendors()
print("Created 2 categories and 4 products")
print("Created 3 customers")
print("Created 2 vendors")

print("\n=== Setup: seed ===")
seed_all()

import glob

test_files = sorted(glob.glob(str(TESTS_DIR / "test_*.py")))

results = {"pass": 0, "fail": 0, "error": []}
for tf in test_files:
    name = Path(tf).stem.replace("test_", "")
    print(f"\n=== TEST: {name} ===")
    storage_clear_all()
    main_demo_create_products()
    main_demo_create_customers()
    main_demo_create_vendors()
    seed_all()
    passed, output = run_test(tf)
    if passed:
        print(output, end="")
        print("PASS")
        results["pass"] += 1
    else:
        print("FAIL")
        print(output[:2000], end="")
        if len(output) > 2000:
            print(f"\n... ({len(output)} total chars)")
        results["fail"] += 1
        results["error"].append(name)

print(f"\n{'='*50}")
print(f"RESULTS: {results['pass']} passed, {results['fail']} failed")
if results["fail"] > 0:
    print(f"Failed: {', '.join(results['error'])}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED")
