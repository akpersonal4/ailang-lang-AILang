"""AILang Dependency Ordering Assistant - Automatic reordering."""

from __future__ import annotations

import re
from pathlib import Path

from tools.ail_order.models import FileAnalysis, FunctionInfo


def extract_function_blocks(content: str) -> list[tuple[int, int, str]]:
    """Extract function blocks with their start and end line numbers.
    
    Returns list of (start_line, end_line, content) tuples.
    Also includes comments before functions.
    """
    lines = content.split("\n")
    blocks: list[tuple[int, int, str]] = []
    
    in_function = False
    fn_start = -1
    brace_count = 0
    block_lines: list[str] = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if stripped.startswith("fn ") and "(" in stripped and not in_function:
            in_function = True
            fn_start = i
            brace_count = 0
        
        if in_function:
            brace_count += line.count("{") - line.count("}")
            block_lines.append(line)
            
            if brace_count == 0 and block_lines:
                blocks.append((fn_start, i, "\n".join(block_lines)))
                in_function = False
                block_lines = []
    
    # Handle non-function content (imports, let declarations, comments)
    # These should stay in place
    return blocks


def reorder_functions(content: str, levels: dict[int, list[str]]) -> str:
    """Reorder functions according to topological levels.
    
    Preserves:
    - Comments before functions
    - Import statements
    - Let declarations at top level
    - All formatting within functions
    """
    lines = content.split("\n")
    
    # Separate into header (imports/lets/comments) and functions
    header_lines: list[str] = []
    function_blocks: list[tuple[int, int, str]] = []
    
    # Extract function blocks
    func_pattern = re.compile(r"^\s*fn\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(")
    
    for line_num, line in enumerate(lines):
        if func_pattern.match(line):
            # Start of a function - find its extent
            brace_count = 0
            block_start = line_num
            block_lines = []
            
            for j in range(line_num, len(lines)):
                block_lines.append(lines[j])
                brace_count += lines[j].count("{") - lines[j].count("}")
                if brace_count == 0 and j > line_num:
                    function_blocks.append((line_num, j, "\n".join(block_lines)))
                    break
    
    # Header is everything before the first function
    first_fn_line = len(lines)
    for start, _, _ in function_blocks:
        if start < first_fn_line:
            first_fn_line = start
    
    header = "\n".join(lines[:first_fn_line])
    
    # Sort function blocks by level, then by original order within level
    # Build a map of function name to level
    name_to_level: dict[str, int] = {}
    for level, names in levels.items():
        for name in names:
            name_to_level[name] = level
    
    def get_level(block: tuple[int, int, str]) -> int:
        content = block[2]
        match = re.match(r"^\s*fn\s+([a-zA-Z_][a-zA-Z0-9_]*)", content)
        if match:
            name = match.group(1)
            return name_to_level.get(name, 999)
        return 999
    
    # Sort by level (ascending), preserving original order within same level
    function_blocks.sort(key=lambda b: (get_level(b), b[0]))
    
    # Rebuild content
    new_blocks = [header]
    for _, _, block_content in function_blocks:
        new_blocks.append(block_content)
    
    return "\n".join(new_blocks)


def apply_fix(filepath: Path, file_analysis: FileAnalysis) -> bool:
    """Apply automatic reordering to a file.
    
    Returns True if changes were made.
    """
    content = filepath.read_text(encoding="utf-8")
    original = content
    
    new_content = reorder_functions(content, file_analysis.levels)
    
    if new_content != original:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    
    return False


def get_ordered_content(content: str, levels: dict[int, list[str]]) -> str:
    """Get reordered content without writing (for preview)."""
    return reorder_functions(content, levels)