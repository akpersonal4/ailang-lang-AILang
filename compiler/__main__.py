"""AILang package entry point.

Usage (preferred — after `pip install -e .`):
    ail run <file>
    ail build <file>
    ail version

Also works via:
    python -m compiler run <file>
    python -m compiler build <file>
    python -m compiler version
"""

from __future__ import annotations

from compiler.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
