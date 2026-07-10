"""AILang Dependency Ordering Assistant - Discovery and parsing."""

from __future__ import annotations

import re
from pathlib import Path

from tools.ail_order.models import FunctionInfo, FileAnalysis


# Keywords to exclude from being considered function calls
AILANG_KEYWORDS = {
    "fn", "let", "if", "else", "return", "import", "as", "true", "false",
    "and", "or", "not",
}

# Stdlib functions (not considered forward refs within file)
STDLIB_FUNCTIONS = {
    "string.concat", "string.equals", "string.uppercase", "string.lowercase",
    "string.length", "string.contains", "string.starts_with", "string.ends_with",
    "string.trim", "string.substring", "string.find", "string.find_from",
    "string.split",
    "math.add", "math.sub", "math.mul", "math.div", "math.abs", "math.min", "math.max",
    "list.new", "list.append", "list.len", "list.get", "list.contains", "list.remove",
    "list.clear", "list.sum", "list.find_by_key",
    "array.new", "array.push", "array.len", "array.get", "array.contains", "array.remove",
    "set.new", "set.add", "set.contains", "set.len", "set.remove", "set.clear",
    "map.new", "map.set", "map.get", "map.has", "map.delete", "map.keys", "map.clear",
    "file.exists", "file.read", "file.write", "file.append", "file.remove", "file.listdir",
    "path.join", "path.basename", "path.dirname", "path.extension", "path.normalize",
    "json.parse", "json.stringify",
    "csv.parse", "csv.parse_header", "csv.stringify",
    "time.now", "time.timestamp", "time.sleep", "time.format",
    "random.int", "random.float", "random.choice",
    "environment.get", "environment.cwd", "environment.args",
    "convert.to_string", "convert.to_int", "convert.to_bool", "convert.to_number",
    "io.write", "io.writeln", "io.println",
    "system.exit",
}


def strip_comment(line: str) -> str:
    """Remove // comment from line, but preserve // inside strings."""
    # Simple approach: find // not inside quotes
    in_string = False
    escape_next = False
    comment_start = -1
    
    for i, ch in enumerate(line):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\":
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
        if not in_string and i < len(line) - 1 and line[i:i+2] == "//":
            comment_start = i
            break
    
    if comment_start >= 0:
        return line[:comment_start]
    return line


def extract_function_name(line: str) -> str | None:
    """Extract function name from fn definition line."""
    stripped = line.strip()
    if not stripped.startswith("fn "):
        return None
    # fn name(params) or fn name(
    match = re.match(r"fn\s+([a-zA-Z_][a-zA-Z0-9_]*)", stripped)
    if match:
        return match.group(1)
    return None


def extract_function_params(line: str) -> list[str]:
    """Extract parameter names from function definition line."""
    stripped = line.strip()
    if not stripped.startswith("fn "):
        return []
    match = re.search(r"fn\s+[a-zA-Z_][a-zA-Z0-9_]*\(([^)]*)\)", stripped)
    if match:
        params_str = match.group(1).strip()
        if params_str:
            return [p.strip() for p in params_str.split(",")]
    return []


def is_fn_def_line(line: str) -> bool:
    """Check if line is a function definition."""
    stripped = line.strip()
    if stripped.startswith("fn ") and "(" in stripped:
        return True
    return False


def is_keyword(name: str) -> bool:
    """Check if name is an AILang keyword."""
    return name in AILANG_KEYWORDS


def extract_calls_from_line(line: str) -> list[str]:
    """Extract function call names from a line of code."""
    calls: list[str] = []
    stripped = strip_comment(line)
    
    # Stdlib method names (only valid when prefixed with module.)
    stdlib_method_names = {
        "concat", "equals", "uppercase", "lowercase", "length", "contains", 
        "starts_with", "ends_with", "trim", "substring", "find", "find_from", "split",
        "new", "push", "len", "get", "append", "remove", "clear", "sum", "find_by_key",
        "set", "has", "delete", "keys", "add", "now", "timestamp", "sleep", "format",
        "int", "float", "choice", "read", "write", "exists", "listdir", "join", 
        "basename", "dirname", "extension", "normalize", "parse", "stringify",
        "parse_header", "to_string", "to_int", "to_bool", "to_number", "writeln", "println",
        "exit",
    }
    
    # Skip if this is a function definition line (handled separately)
    if stripped.strip().startswith("fn "):
        return calls
    
    # Find all func(args) patterns, excluding module. prefix
    i = 0
    while i < len(stripped):
        # Look for identifier followed by (
        if stripped[i].isalpha() or stripped[i] == '_':
            # Extract the identifier
            j = i
            while j < len(stripped) and (stripped[j].isalnum() or stripped[j] == '_'):
                j += 1
            name = stripped[i:j]
            
            # Check if followed by ( (with possible whitespace)
            k = j
            while k < len(stripped) and stripped[k] in ' \t':
                k += 1
            if k < len(stripped) and stripped[k] == '(':
                # This is a function call
                # Skip if preceded by a dot (module.func call)
                if i > 0 and stripped[i-1] == '.':
                    pass  # Skip module.func calls
                elif name not in AILANG_KEYWORDS and name not in stdlib_method_names:
                    calls.append(name)
                i = k + 1
                continue
        
        i += 1
    
    return calls


def discover_functions(content: str) -> list[FunctionInfo]:
    """Discover all function definitions in AILang source."""
    functions: list[FunctionInfo] = []
    lines = content.split("\n")
    
    # Track function ranges
    fn_starts: list[tuple[int, str, int]] = []  # (line, name, brace_count)
    
    for line_num, line in enumerate(lines):
        if is_fn_def_line(line):
            name = extract_function_name(line)
            if name:
                params = extract_function_params(line)
                fn_starts.append((line_num, name, params))
    
    # Find end lines by tracking braces
    i = 0
    while i < len(fn_starts):
        start_line, name, params = fn_starts[i]
        brace_count = 0
        end_line = start_line
        
        for j in range(start_line, len(lines)):
            for ch in lines[j]:
                if ch == "{":
                    brace_count += 1
                elif ch == "}":
                    brace_count -= 1
            end_line = j
            if brace_count == 0 and j > start_line:
                break
        
        # Extract calls within this function
        calls = []
        for j in range(start_line, end_line + 1):
            calls.extend(extract_calls_from_line(lines[j]))
        
        # Check for doc comment on line before
        has_doc = False
        if start_line > 0:
            prev_line = lines[start_line - 1].strip()
            if prev_line.startswith("///"):
                has_doc = True
        
        functions.append(FunctionInfo(
            name=name,
            line=start_line,
            start_line=start_line,
            end_line=end_line,
            parameters=params,
            calls=calls,
            has_doc_comment=has_doc,
        ))
        i += 1
    
    return functions


def analyze_file(filepath: Path) -> FileAnalysis:
    """Analyze a single .ail file for dependency ordering."""
    content = filepath.read_text(encoding="utf-8")
    functions = discover_functions(content)
    
    # Build name to function mapping (for duplicates)
    name_counts: dict[str, int] = {}
    for fn in functions:
        name_counts[fn.name] = name_counts.get(fn.name, 0) + 1
    
    duplicates = [name for name, count in name_counts.items() if count > 1]
    
    return FileAnalysis(
        path=str(filepath),
        functions=functions,
        duplicates=duplicates,
    )


def discover_ail_files(target: Path) -> list[Path]:
    """Discover all .ail files from the given target."""
    if target.is_file() and str(target).endswith(".ail"):
        return [target]
    
    if target.is_dir():
        exclude_dirs = {".venv", ".venv_test", ".git", "__pycache__", "ailang.egg-info", "generated"}
        raw_files = list(target.rglob("*.ail"))
        filtered = [f for f in raw_files if not any(excl in f.parts for excl in exclude_dirs)]
        return sorted(set(filtered))
    
    return []