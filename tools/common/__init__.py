"""Shared utilities for AILang Developer Experience tools.

Provides common CLI conventions, filesystem helpers, process execution,
and reporting utilities to eliminate duplication across DX tools.
"""

from tools.common.cli import add_common_args, add_output_args, create_parser
from tools.common.filesystem import (
    discover_apps,
    ensure_output_dir,
    get_project_root,
    list_py_files,
    read_file_safe,
)
from tools.common.hashing import hash_file
from tools.common.process import run_ail_build, run_ail_run, run_subprocess
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
