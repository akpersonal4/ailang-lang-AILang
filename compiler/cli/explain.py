"""AILang Explain - detailed diagnostics for compiler error codes.

Usage:
    ail explain TYP001
    ail explain SEM002
    ail explain MOD004
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Example:
    broken: str
    fixed: str
    explanation: str


@dataclass
class ErrorExplanation:
    code: str
    description: str
    common_causes: list[str]
    examples: list[Example]
    fixes: list[str]
    related_commands: list[str]
    heal_topic: str | None


ERROR_DATABASE: dict[str, ErrorExplanation] = {
    "TYP001": ErrorExplanation(
        code="TYP001",
        description="Cannot infer type for a variable from its initializer expression.",
        common_causes=[
            "Variable is assigned an expression involving only unknown types (e.g., map.get returns unknown).",
            "Variable is assigned another variable whose type was never determined.",
            "Expression combines incompatible types in a way the type checker cannot resolve.",
        ],
        examples=[
            Example(
                broken='let qty = map.get(product, "qty");\nlet total = qty;',
                fixed='let qty = map.get(product, "qty");\nlet total = qty + 0;',
                explanation="Adding a known int literal (0) lets the type checker infer int.",
            ),
            Example(
                broken="fn get_val() { return unknown_thing; }\nlet x = get_val();",
                fixed="fn get_val() { return 42; }\nlet x = get_val();",
                explanation="Returning a typed literal (42) lets the compiler infer int.",
            ),
        ],
        fixes=[
            "Add a known-type literal to force inference: let x = unknown + 0;",
            "Use convert helpers: let x = convert.to_int(unknown_value);",
            'Ensure upstream functions return typed literals (return 0; return "").',
            "Check function return types with ail explain TYP003.",
        ],
        related_commands=[
            "ail explain TYP003",
            "ail explain TYP005",
            "ail heal type_error",
        ],
        heal_topic="type_error",
    ),
    "TYP002": ErrorExplanation(
        code="TYP002",
        description="Return statement found outside of a function body.",
        common_causes=[
            "A return statement is placed at the top level of a file.",
            "A return statement is placed inside an if/else block at the top level.",
        ],
        examples=[
            Example(
                broken="let x = 1;\nreturn x;",
                fixed="fn main() {\n    let x = 1;\n    return x;\n}",
                explanation="Wrap return statements inside a function.",
            ),
        ],
        fixes=[
            "Move the return statement inside a function body.",
            "If this is meant to be the entry point, wrap in fn main().",
        ],
        related_commands=["ail docs AGENTS.md"],
        heal_topic=None,
    ),
    "TYP003": ErrorExplanation(
        code="TYP003",
        description="Return type mismatch: the returned value does not match the inferred function return type.",
        common_causes=[
            "A function returns different types in different return statements.",
            "The first return establishes the type; later returns conflict.",
        ],
        examples=[
            Example(
                broken='fn get_val() {\n    return 42;\n    return "hello";\n}',
                fixed="fn get_val() {\n    return 42;\n}",
                explanation="All return statements must return the same type.",
            ),
        ],
        fixes=[
            "Ensure all return statements in a function return the same type.",
            "If different branches return different types, restructure the logic.",
        ],
        related_commands=["ail explain TYP001", "ail heal type_error"],
        heal_topic="type_error",
    ),
    "TYP004": ErrorExplanation(
        code="TYP004",
        description="Condition in an if statement must be a boolean expression.",
        common_causes=[
            "Using a non-boolean expression (e.g., number or string) as a condition.",
            "Missing comparison operator (e.g., if (x) instead of if (x > 0)).",
        ],
        examples=[
            Example(
                broken="let x = 5;\nif (x) { print(x); }",
                fixed="let x = 5;\nif (x > 0) { print(x); }",
                explanation="Use an explicit comparison to produce a boolean.",
            ),
        ],
        fixes=[
            "Add an explicit comparison: if (x > 0), if (string.length(s) == 0).",
            "Use map.has() for map key checks: if (map.has(m, key)).",
        ],
        related_commands=["ail docs AGENTS.md"],
        heal_topic=None,
    ),
    "TYP005": ErrorExplanation(
        code="TYP005",
        description="Arithmetic operator used with non-numeric types.",
        common_causes=[
            "Using +, -, *, /, % with string or boolean operands.",
            "Both operands are known non-numeric types (e.g., string + string where result is not string).",
        ],
        examples=[
            Example(
                broken="let a = true;\nlet b = a + 1;",
                fixed="let a = 1;\nlet b = a + 1;",
                explanation="Arithmetic requires numeric operands.",
            ),
        ],
        fixes=[
            "Ensure both operands are numeric (int or float).",
            "Use string.concat() for string concatenation.",
            "Convert types with convert.to_int() or convert.to_number().",
        ],
        related_commands=[
            "ail explain TYP001",
            "ail heal type_error",
            "ail docs STDLIB_REFERENCE.md",
        ],
        heal_topic="type_error",
    ),
    "TYP006": ErrorExplanation(
        code="TYP006",
        description="Comparison operator used with incompatible types.",
        common_causes=[
            "Comparing values of different known types (e.g., int == string).",
            "Comparing values where neither is an unknown type.",
        ],
        examples=[
            Example(
                broken='let a = 1;\nlet b = "hello";\nif (a == b) { }',
                fixed="let a = 1;\nlet c = 2;\nif (a == c) { }",
                explanation="Compare values of the same type.",
            ),
        ],
        fixes=[
            "Ensure both operands are the same type.",
            "Convert types before comparing: convert.to_string(a) == b.",
        ],
        related_commands=["ail explain TYP005", "ail heal type_error"],
        heal_topic="type_error",
    ),
    "TYP007": ErrorExplanation(
        code="TYP007",
        description="Logical operator (&&, ||) requires boolean operands.",
        common_causes=[
            "Using && or || with non-boolean operands.",
            "Missing comparison operator (e.g., a && b instead of a > 0 && b > 0).",
        ],
        examples=[
            Example(
                broken="let x = 5;\nif (x && x > 0) { print(x); }",
                fixed="let x = 5;\nif (x > 0) { print(x); }",
                explanation="Ensure each operand of && is a boolean expression.",
            ),
        ],
        fixes=[
            "Add explicit comparisons to produce boolean values.",
            "Use nested if statements when right operand depends on left (&& is eager).",
        ],
        related_commands=["ail docs AGENTS.md", "ail heal type_error"],
        heal_topic="type_error",
    ),
    "TYP008": ErrorExplanation(
        code="TYP008",
        description="Assignment type mismatch: the right-hand side type does not match the variable's declared type.",
        common_causes=[
            "Reassigning a variable to a value of a different type.",
            "The variable was first assigned an int, then reassigned a string.",
        ],
        examples=[
            Example(
                broken='let x = 1;\nx = "hello";',
                fixed="let x = 1;\nx = 42;",
                explanation="Reassignment must match the original type.",
            ),
        ],
        fixes=[
            "Ensure the reassigned value matches the variable's original type.",
            "Use a new variable instead of reassigning with a different type.",
        ],
        related_commands=["ail explain TYP001", "ail heal type_error"],
        heal_topic="type_error",
    ),
    "TYP009": ErrorExplanation(
        code="TYP009",
        description="Unary minus (-) requires a numeric operand.",
        common_causes=[
            "Using - with a non-numeric type (string, boolean).",
        ],
        examples=[
            Example(
                broken='let s = "hello";\nlet x = -s;',
                fixed="let n = 5;\nlet x = -n;",
                explanation="Unary minus only works with int or float.",
            ),
        ],
        fixes=[
            "Ensure the operand is numeric (int or float).",
        ],
        related_commands=["ail explain TYP005"],
        heal_topic=None,
    ),
    "TYP010": ErrorExplanation(
        code="TYP010",
        description="Logical not (!) requires a boolean operand.",
        common_causes=[
            "Using ! with a non-boolean type.",
        ],
        examples=[
            Example(
                broken="let x = 5;\nif (!x) { print(x); }",
                fixed="let x = 5;\nif (x == 0) { print(x); }",
                explanation="Use a comparison to produce a boolean for negation.",
            ),
        ],
        fixes=[
            "Use an explicit comparison: !(x > 0) or x == 0.",
        ],
        related_commands=["ail explain TYP007"],
        heal_topic=None,
    ),
    "SEM001": ErrorExplanation(
        code="SEM001",
        description="Duplicate declaration: a variable or function with this name already exists in the same scope.",
        common_causes=[
            "Two functions with the same name in the same file.",
            "A variable and a function sharing the same name.",
        ],
        examples=[
            Example(
                broken="fn helper() { return 1; }\nfn helper() { return 2; }",
                fixed="fn helper_1() { return 1; }\nfn helper_2() { return 2; }",
                explanation="Use unique names for all top-level declarations.",
            ),
        ],
        fixes=[
            "Rename the duplicate to a unique name.",
            "Remove the orphaned duplicate declaration.",
        ],
        related_commands=["ail rename", "ail docs AGENTS.md"],
        heal_topic=None,
    ),
    "SEM002": ErrorExplanation(
        code="SEM002",
        description="Forward reference: an identifier is used before it is defined.",
        common_causes=[
            "A function calls another function defined later in the file.",
            "A variable is referenced before its let declaration.",
        ],
        examples=[
            Example(
                broken="fn main() { greet(); }\nfn greet() { print('hello'); }",
                fixed="fn greet() { print('hello'); }\nfn main() { greet(); }",
                explanation="Move the callee above the caller (bottom-up ordering).",
            ),
        ],
        fixes=[
            "Move the referenced function/variable above the one that uses it.",
            "Use bottom-up dependency ordering: Level 0 utilities first, main() last.",
            "Run ail fmt to reorder functions automatically.",
        ],
        related_commands=["ail fmt", "ail docs AGENTS.md", "ail order"],
        heal_topic="forward_reference",
    ),
    "SEM003": ErrorExplanation(
        code="SEM003",
        description="Wrong number of arguments in a function call.",
        common_causes=[
            "Calling a function with more or fewer arguments than expected.",
            "Missing required arguments in a stdlib function call.",
        ],
        examples=[
            Example(
                broken="fn add(a, b) { return a + b; }\nlet x = add(1);",
                fixed="fn add(a, b) { return a + b; }\nlet x = add(1, 2);",
                explanation="Provide exactly the number of arguments the function expects.",
            ),
        ],
        fixes=[
            "Check the function signature and provide the correct number of arguments.",
            "Use ail docs STDLIB_REFERENCE.md to check stdlib function signatures.",
        ],
        related_commands=["ail docs STDLIB_REFERENCE.md", "ail heal type_error"],
        heal_topic="type_error",
    ),
    "MOD001": ErrorExplanation(
        code="MOD001",
        description="Circular import detected: module A imports module B which imports module A.",
        common_causes=[
            "Two modules import each other directly.",
            "A chain of imports creates a cycle.",
        ],
        examples=[
            Example(
                broken="# a.ail imports b.ail\nimport b;\n# b.ail imports a.ail\nimport a;",
                fixed="# Extract shared code into a third module c.ail\nimport c;",
                explanation="Break the cycle by extracting shared code.",
            ),
        ],
        fixes=[
            "Extract shared code into a third module.",
            "Restructure to remove the circular dependency.",
        ],
        related_commands=["ail docs AGENTS.md"],
        heal_topic=None,
    ),
    "MOD003": ErrorExplanation(
        code="MOD003",
        description="Module not found: the imported module does not exist.",
        common_causes=[
            "Typo in the module name.",
            "Module file is missing or in the wrong directory.",
            "Missing stdlib import (e.g., import map; at the top of the file).",
        ],
        examples=[
            Example(
                broken="import mapp;",
                fixed="import map;",
                explanation="Check the module name spelling.",
            ),
        ],
        fixes=[
            "Check the module name spelling.",
            "Ensure the .ail file exists in the same directory.",
            "For stdlib modules, add the import at the top: import map; import list;",
        ],
        related_commands=["ail docs STDLIB_REFERENCE.md", "ail heal missing_import"],
        heal_topic="missing_import",
    ),
    "MOD004": ErrorExplanation(
        code="MOD004",
        description="Symbol not found in module: the function or variable does not exist in the imported module.",
        common_causes=[
            "Typo in the function name after module. prefix.",
            "Function does not exist in the module.",
            "Function was renamed or removed in a newer version.",
        ],
        examples=[
            Example(
                broken='import map;\nlet x = map.sett(m, "k", "v");',
                fixed='import map;\nlet x = map.set(m, "k", "v");',
                explanation="Check the function name spelling.",
            ),
        ],
        fixes=[
            "Check the function name spelling against STDLIB_REFERENCE.md.",
            "Use ail docs STDLIB_REFERENCE.md to list available functions.",
            "Ensure the module is imported before use.",
        ],
        related_commands=["ail docs STDLIB_REFERENCE.md", "ail heal missing_import"],
        heal_topic="missing_import",
    ),
}


def explain(error_code: str) -> str | None:
    """Return a formatted explanation for the given error code, or None if unknown."""
    entry = ERROR_DATABASE.get(error_code.upper())
    if entry is None:
        return None
    return _format_explanation(entry)


def list_codes() -> str:
    """Return a formatted list of all known error codes."""
    lines = ["Known error codes:"]
    lines.append("")
    for code in sorted(ERROR_DATABASE.keys()):
        desc = ERROR_DATABASE[code].description
        lines.append(f"  {code:8s}  {desc}")
    lines.append("")
    lines.append("Usage: ail explain <CODE>")
    return "\n".join(lines)


def _format_explanation(entry: ErrorExplanation) -> str:
    lines = [f"# {entry.code} — {entry.description}"]
    lines.append("")

    lines.append("## Common Causes")
    lines.append("")
    for cause in entry.common_causes:
        lines.append(f"  - {cause}")
    lines.append("")

    if entry.examples:
        lines.append("## Examples")
        lines.append("")
        for i, ex in enumerate(entry.examples, 1):
            lines.append(f"  Example {i}: {ex.explanation}")
            lines.append("")
            lines.append("    Broken:")
            for bline in ex.broken.split("\n"):
                lines.append(f"      {bline}")
            lines.append("")
            lines.append("    Fixed:")
            for fline in ex.fixed.split("\n"):
                lines.append(f"      {fline}")
            lines.append("")

    lines.append("## Fixes")
    lines.append("")
    for fix in entry.fixes:
        lines.append(f"  - {fix}")
    lines.append("")

    if entry.related_commands:
        lines.append("## Related Commands")
        lines.append("")
        for cmd in entry.related_commands:
            lines.append(f"  {cmd}")
        lines.append("")

    if entry.heal_topic:
        lines.append("## Can ail heal help?")
        lines.append("")
        lines.append(f"  Yes — run: ail heal {entry.heal_topic}")
    else:
        lines.append("## Can ail heal help?")
        lines.append("")
        lines.append("  No specific heal topic for this error code.")
        lines.append("  Try: ail docs AGENTS.md")

    return "\n".join(lines)
