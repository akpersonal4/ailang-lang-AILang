"""Minimal benchmark script matching benchmark.ail.

It seeds the demo data, runs the report, measures elapsed time,
and prints a SHA‑256 hash of the report output.
"""

import hashlib
import time
from contextlib import redirect_stdout
from io import StringIO

# Import the same entry points as the AILang main.
from main import main_report, main_seed


def run_benchmark():
    # Warm‑up is performed by the external runner script.
    # Seed data
    main_seed()
    # Capture report output
    buf = StringIO()
    start = time.time()
    with redirect_stdout(buf):
        main_report()
    elapsed = time.time() - start
    output = buf.getvalue()
    # Compute SHA‑256 of the full report text
    digest = hashlib.sha256(output.encode("utf-8")).hexdigest()
    # Emit in a simple parsable format
    print(f"TIME:{elapsed:.6f}")
    print(f"SHA256:{digest}")
    # Also output the report itself for manual verification if needed
    # (comment out if not desired)
    # print("---REPORT---")
    # print(output)


if __name__ == "__main__":
    run_benchmark()
