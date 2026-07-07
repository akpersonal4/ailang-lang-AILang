"""Shared utilities for AILang Developer Experience tools.

Provides common CLI conventions, filesystem helpers, process execution,
and reporting utilities to eliminate duplication across DX tools.
"""

from tools.common.cli import create_parser, add_output_args, add_common_args
from tools.common.filesystem import get_project_root, read_file_safe, ensure_output_dir, discover_apps, list_py_files
from tools.common.hashing import hash_file
from tools.common.process import run_subprocess, run_ail_build, run_ail_run
from tools.common.reporting import write_json_report, write_markdown_report

__all__ = [
    "create_parser",
    "add_output_args",
    "add_common_args",
    "get_project_root",
    "read_file_safe",
    "ensure_output_dir",
    "discover_apps",
    "list_py_files",
    "hash_file",
    "run_subprocess",
    "run_ail_build",
    "run_ail_run",
    "write_json_report",
    "write_markdown_report",
]
