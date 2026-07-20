# AILang Developer Experience Tool: ail heal
# Diagnostic guidance and fix suggestions for common errors

"""AILang Heal - fix suggestions for common AILang compilation errors."""

import sys

HELP_TOPICS = {
    "forward_reference": {
        "title": "Forward Reference Error (SEM002)",
        "description": "A function or variable is used before it is defined.",
        "solution": [
            "AILang requires bottom-up ordering: callees before callers.",
            "",
            "Move the referenced function/variable ABOVE the one that uses it.",
            "",
            "Example (broken):",
            "  fn main() { greet(); }",
            "  fn greet() { print('hello'); }",
            "",
            "Example (fixed):",
            "  fn greet() { print('hello'); }",
            "  fn main() { greet(); }",
            "",
            "Tip: Run `ail fmt` to reorder functions automatically.",
        ],
    },
    "type_error": {
        "title": "Type Error (TYP001-TYP008)",
        "description": "A type mismatch was detected.",
        "solution": [
            "Common causes:",
            "",
            "  TYP001: Wrong argument type in function call",
            "  TYP002: Wrong return type",
            "  TYP003: Wrong operator usage (e.g., string + int)",
            "  TYP004: Unknown function",
            "  TYP005: Missing required argument",
            "  TYP006: Unexpected argument",
            "  TYP007: Map key type mismatch",
            "  TYP008: List element type mismatch",
            "",
            "Fix: Ensure types match the function signature.",
            "For string + int, convert first: string.concat(str, to_string(num))",
            "",
            "Tip: Run `ail docs STDLIB_REFERENCE` to check function signatures.",
        ],
    },
    "missing_import": {
        "title": "Missing Import (SEM004)",
        "description": "A required import is missing.",
        "solution": [
            "Add the import at the top of your file:",
            "",
            "  import io;",
            "  import list;",
            "  import map;",
            "  import string;",
            "  import math;",
            "",
            "Available stdlib modules:",
            "  io, list, map, string, math, json, system, convert, environment, file",
            "",
            "Tip: Run `ail docs STDLIB_REFERENCE` for the full list.",
        ],
    },
    "import_alias": {
        "title": "Import Alias Issue",
        "description": "An import alias is not resolving correctly.",
        "solution": [
            "Import aliases work like this:",
            "",
            "  import math;",
            "  let m = math;",
            "  let pi = m.PI;",
            "",
            "Common issues:",
            "  - Alias must be a simple identifier (no dots)",
            "  - Module must exist at the specified path",
            "  - Use `import <module> as <alias>` or assign after import",
            "",
            "Tip: Run `ail check <file>` to validate imports.",
        ],
    },
    "operator_error": {
        "title": "Operator Error",
        "description": "An operator was used incorrectly.",
        "solution": [
            "AILang operators:",
            "",
            "  Arithmetic: +, -, *, /, %",
            "  Comparison: ==, !=, <, <=, >, >=",
            "  Logical: &&, ||, !",
            "  Assignment: =",
            "",
            "Common issues:",
            "  - Cannot use + with string and number",
            "  - Cannot use * with string and string",
            "  - Use string.concat() for string concatenation",
            "",
            "Tip: Run `ail docs AGENTS` for operator rules.",
        ],
    },
    "no_loops": {
        "title": "No Loops Allowed",
        "description": "AILang does not support while/for loops.",
        "solution": [
            "Use recursion instead of loops:",
            "",
            "  # Instead of: while x > 0 { x = x - 1; }",
            "  fn countdown(x) {",
            "      if x > 0 {",
            "          print(x);",
            "          countdown(x - 1);",
            "      }",
            "  }",
            "",
            "  # Instead of: for i in list { ... }",
            "  fn process_all(items, index) {",
            "      if index < list.len(items) {",
            "          process(list.get(items, index));",
            "          process_all(items, index + 1);",
            "      }",
            "  }",
            "",
            "Tip: See `ail docs AGENTS` for recursion patterns.",
        ],
    },
    "env_setup": {
        "title": "Environment Setup",
        "description": "Setting up the AILang development environment.",
        "solution": [
            "1. Install the ailang package:",
            "     pip install -e .",
            "",
            "2. Verify installation:",
            "     ail --version",
            "",
            "3. Check your environment:",
            "     ail doctor",
            "",
            "4. Read the docs:",
            "     ail docs AGENTS",
            "",
            "5. Get language context:",
            "     ail context --json",
            "",
            "6. Create a new project:",
            "     ail new myproject",
            "",
            "7. Build and run:",
            "     ail build myproject/main.ail",
            "     ail run myproject/main.ail",
        ],
    },
}


def print_help(topic: str | None = None) -> int:
    """Print help for a specific topic or list all topics."""
    if topic:
        if topic not in HELP_TOPICS:
            print(f"Unknown topic: {topic}", file=sys.stderr)
            print(
                f"Available topics: {', '.join(sorted(HELP_TOPICS.keys()))}",
                file=sys.stderr,
            )
            return 1

        info = HELP_TOPICS[topic]
        print(f"# {info['title']}")
        print()
        print(info["description"])
        print()
        for line in info["solution"]:
            print(line)
        return 0

    print("# AILang Heal - Fix Suggestions")
    print()
    print("Usage: ail heal <topic>")
    print()
    print("Available topics:")
    print()
    for name, info in sorted(HELP_TOPICS.items()):
        print(f"  {name:20s}  {info['description']}")
    print()
    print("Examples:")
    print()
    print("  ail heal forward_reference")
    print("  ail heal type_error")
    print("  ail heal env_setup")
    print()
    return 0


def main() -> int:
    """Main entry point for the ail heal tool."""
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        return print_help()

    return print_help(args[0])


if __name__ == "__main__":
    raise SystemExit(main())
