"""Shared utilities for AILang Developer Experience tools.

Provides common CLI conventions, filesystem helpers, process execution,
and reporting utilities to eliminate duplication across DX tools.
"""

from tools.common.cli import create_parser, add_output_args, add_common_args
from tools.common.filesystem import get_project_root, read_file_safe, ensure_output_dir
from tools.common.process import run_subprocess
from tools.common.reporting import write_json_report, write_markdown_report

__all__ = [
    "create_parser",
    "add_output_args",
    "add_common_args",
    "get_project_root",
    "read_file_safe",
    "ensure_output_dir",
    "run_subprocess",
    "write_json_report",
    "write_markdown_report",
]
