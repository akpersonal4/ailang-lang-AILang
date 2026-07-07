"""Shared CLI argument parsing conventions for DX tools."""

from __future__ import annotations

import argparse
from pathlib import Path


def create_parser(
    prog: str,
    description: str,
) -> argparse.ArgumentParser:
    """Create a standard argument parser with shared conventions."""
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.3.0",
        help="show version and exit",
    )
    return parser


def add_output_args(parser: argparse.ArgumentParser) -> None:
    """Add standard --output-dir argument."""
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: generated/<tool_name>)",
    )


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add common arguments shared across tools."""
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
