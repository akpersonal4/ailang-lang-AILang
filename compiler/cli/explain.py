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
    "WHILE001": ErrorExplanation(
        code="WHILE001",
        description="AILang has no while loops. Use recursion instead.",
        common_causes=[
            "Using while(condition) { body } syntax from Python/JavaScript/C.",
            "Attempting to write iterative logic.",
        ],
        examples=[
            Example(
                broken="let i = 0;\nwhile (i < 10) {\n    print(i);\n    i = i + 1;\n}",
                fixed="fn count_up(n) {\n    if (n == 0) {\n        return 0;\n    }\n    print(n);\n    return count_up(n - 1);\n}\ncount_up(10);",
                explanation="Replace while with a recursive function that calls itself with a decreasing counter.",
            ),
        ],
        fixes=[
            "Convert the while loop to a recursive function.",
            "Use an if statement as the base case to stop recursion.",
            "Pass decreasing parameters to avoid infinite recursion.",
            "See LANGUAGE_SPEC.md for the recursion pattern.",
        ],
        related_commands=["ail docs AGENTS.md", "ail docs LANGUAGE_SPEC.md"],
        heal_topic=None,
    ),
    "LANG001": ErrorExplanation(
        code="LANG001",
        description="Nested functions are not allowed in AILang. All functions must be at the top level.",
        common_causes=[
            "Defining a function inside another function body.",
            "Python习惯: defining helper functions inside main().",
        ],
        examples=[
            Example(
                broken="fn main() {\n    fn helper() { return 1; }\n    let x = helper();\n}",
                fixed="fn helper() { return 1; }\nfn main() {\n    let x = helper();\n}",
                explanation="Move the inner function to the top level, above the function that calls it.",
            ),
        ],
        fixes=[
            "Move the inner function to the top level of the file.",
            "Use bottom-up ordering: define helper functions before their callers.",
            "Rename functions to avoid name collisions at the top level.",
        ],
        related_commands=["ail docs AGENTS.md", "ail fmt"],
        heal_topic=None,
    ),
    "LANG002": ErrorExplanation(
        code="LANG002",
        description="list.set() does not exist in AILang. Use map.set() or list.append() instead.",
        common_causes=[
            "Trying to set a value at a specific index in a list.",
            "Python habit: my_list[index] = value.",
        ],
        examples=[
            Example(
                broken="import list;\nlet items = list.new();\nlist.set(items, 0, 42);",
                fixed='import map;\nlet m = map.new();\nmap.set(m, "key", 42);',
                explanation="Use map.set() for key-value storage. For lists, use list.append() to add to the end.",
            ),
        ],
        fixes=[
            "Use map.set(key, value) for key-value storage.",
            "Use list.append(value) to add to the end of a list.",
            "For indexed access, use list.get(list, index) to read.",
            "See STDLIB_REFERENCE.md for available list functions.",
        ],
        related_commands=["ail docs STDLIB_REFERENCE.md", "ail explain MOD004"],
        heal_topic=None,
    ),
    "LANG003": ErrorExplanation(
        code="LANG003",
        description="string.replace() does not exist in AILang. Use string.substring() and string.concat() instead.",
        common_causes=[
            "Trying to replace part of a string.",
            "Python habit: my_string.replace(old, new).",
        ],
        examples=[
            Example(
                broken='import string;\nlet s = string.replace("hello world", "world", "AILang");',
                fixed='import string;\nlet before = string.substring("hello world", 0, 6);\nlet after = string.substring("hello world", 11, 11);\nlet s = string.concat(before, "AILang");\ns = string.concat(s, after);',
                explanation="Build modified strings by extracting substrings and concatenating.",
            ),
        ],
        fixes=[
            "Use string.substring() to extract parts before and after the target.",
            "Use string.concat() to join the parts with the replacement.",
            "For simple cases, build a new string from scratch.",
            "See STDLIB_REFERENCE.md for string function details.",
        ],
        related_commands=["ail docs STDLIB_REFERENCE.md", "ail explain MOD004"],
        heal_topic=None,
    ),
    "LANG004": ErrorExplanation(
        code="LANG004",
        description="Import statements are only allowed at the top level, not inside functions or blocks.",
        common_causes=[
            "Placing an import statement inside a function body.",
            "Placing an import statement inside an if/else block.",
        ],
        examples=[
            Example(
                broken='fn main() {\n    import string;\n    let x = string.uppercase("hello");\n}',
                fixed='import string;\n\nfn main() {\n    let x = string.uppercase("hello");\n}',
                explanation="Move the import to the top of the file, outside any function or block.",
            ),
        ],
        fixes=[
            "Move the import statement to the top of the file, before any function definitions.",
            "AILang imports are file-level declarations, not scoped to functions.",
        ],
        related_commands=["ail docs AGENTS.md", "ail docs LANGUAGE_SPEC.md"],
        heal_topic=None,
    ),
    "LEX001": ErrorExplanation(
        code="LEX001",
        description="Unexpected character encountered during lexing. AILang does not allow arbitrary symbols outside of string literals.",
        common_causes=[
            "Using single quotes (') instead of double quotes (\") for strings.",
            "Using a character from an unsupported character set.",
            "A typo or stray character in the source code.",
        ],
        examples=[
            Example(
                broken='print(\'hello\');',
                fixed='print("hello");',
                explanation="AILang only supports double-quoted string literals.",
            ),
        ],
        fixes=[
            "Use double quotes (\") for all string literals.",
            "Remove the unexpected character.",
            "Check for stray characters near the indicated location.",
        ],
        related_commands=["ail docs LANGUAGE_SPEC.md"],
        heal_topic=None,
    ),
    "LEX002": ErrorExplanation(
        code="LEX002",
        description="Unterminated string literal: a string was opened with double quotes but never closed.",
        common_causes=[
            "Missing closing quote at the end of a string.",
            "A multi-line string (AILang does not support multi-line strings).",
        ],
        examples=[
            Example(
                broken='let s = "hello;',
                fixed='let s = "hello";',
                explanation="Add the closing double quote.",
            ),
        ],
        fixes=[
            'Add a closing double quote (") at the end of the string literal.',
            "For long strings, use string.concat() to join multiple string literals.",
        ],
        related_commands=["ail docs LANGUAGE_SPEC.md"],
        heal_topic=None,
    ),
    "LEX003": ErrorExplanation(
        code="LEX003",
        description="Invalid escape sequence in a string literal.",
        common_causes=[
            "Using an unsupported escape sequence like \\x, \\u, or \\0.",
            "Using a backslash without a valid escape character.",
        ],
        examples=[
            Example(
                broken='let s = "hello\\world";',
                fixed='let s = "hello\\\\world";',
                explanation="Use \\\\ to represent a literal backslash.",
            ),
        ],
        fixes=[
            "Use only valid escape sequences: \\n, \\t, \\\\, \\\", \\r, \\b, \\f.",
            "To include a literal backslash, use \\\\.",
        ],
        related_commands=["ail docs LANGUAGE_SPEC.md"],
        heal_topic=None,
    ),
    "LEX004": ErrorExplanation(
        code="LEX004",
        description="Source file is not valid UTF-8. AILang source files must be UTF-8 encoded.",
        common_causes=[
            "The file was saved as UTF-16 (e.g., PowerShell 'echo' redirection on Windows).",
            "The file was saved with a legacy encoding such as ANSI/Latin-1.",
            "The file is a binary file with a .ail extension.",
        ],
        examples=[
            Example(
                broken="Saved as UTF-16 (byte-order-mark at the start of the file)",
                fixed='Re-save as UTF-8: in VS Code use "Save with Encoding" -> UTF-8.',
                explanation="AILang reads every source file as UTF-8. Re-saving as UTF-8 fixes the error.",
            ),
        ],
        fixes=[
            "Re-save the file as UTF-8 using your editor's 'Save with encoding' option.",
            "In PowerShell, use Set-Content -Encoding UTF8 instead of echo redirection.",
        ],
        related_commands=["ail docs LANGUAGE_SPEC.md"],
        heal_topic=None,
    ),
    "PAR001": ErrorExplanation(
        code="PAR001",
        description="Expected a specific token but found something else. The parser could not match the input against the grammar.",
        common_causes=[
            "Missing semicolon at the end of a statement.",
            "Missing closing parenthesis ')'.",
            "Missing closing brace '}'.",
            "Using an expression where a statement is expected, or vice versa.",
            "Bare return; (use return 0; or return \"\"; instead).",
        ],
        examples=[
            Example(
                broken="fn main() {\n    print(\"hello\")\n}",
                fixed="fn main() {\n    print(\"hello\");\n}",
                explanation="AILang requires semicolons at the end of statement lines.",
            ),
            Example(
                broken="fn main() {\n    return;\n}",
                fixed="fn main() {\n    return 0;\n}",
                explanation="return always requires an expression in AILang.",
            ),
        ],
        fixes=[
            "Check the syntax near the indicated location.",
            "Ensure all statements end with a semicolon.",
            "Ensure all parentheses () and braces {} are properly closed.",
            "return always needs an expression: return 0; or return \"\";",
        ],
        related_commands=["ail docs LANGUAGE_SPEC.md", "ail docs GETTING_STARTED"],
        heal_topic=None,
    ),
    "PAR002": ErrorExplanation(
        code="PAR002",
        description="Invalid import path. The import statement has a syntax error.",
        common_causes=[
            "Typo in the module name after 'import'.",
            "Missing module name.",
            "Invalid characters in the module path.",
        ],
        examples=[
            Example(
                broken="import math-utils;",
                fixed="import math_utils;",
                explanation="Use underscores, not hyphens, in module names.",
            ),
        ],
        fixes=[
            "Check the module name spelling after 'import'.",
            "Module names can contain letters, numbers, and underscores.",
            "For stdlib modules, use: import map; import list; import json; etc.",
        ],
        related_commands=["ail docs STDLIB_REFERENCE.md"],
        heal_topic="missing_import",
    ),
    "PAR003": ErrorExplanation(
        code="PAR003",
        description="Expected an identifier (variable or function name) after a keyword.",
        common_causes=[
            "Missing function name after 'fn' keyword.",
            "Missing variable name after 'let' keyword.",
            "Using a reserved word as an identifier.",
        ],
        examples=[
            Example(
                broken="fn () { return 1; }",
                fixed="fn main() { return 1; }",
                explanation="Provide a valid identifier for the function name.",
            ),
        ],
        fixes=[
            "Add a valid identifier (name starting with a letter or underscore).",
            "Avoid using reserved keywords as names.",
        ],
        related_commands=["ail docs LANGUAGE_SPEC.md"],
        heal_topic=None,
    ),
    "TYP011": ErrorExplanation(
        code="TYP011",
        description="Argument count mismatch: the number of arguments in a function call does not match the function's signature.",
        common_causes=[
            "Calling a function with too many or too few arguments.",
            "Missing required arguments in a stdlib function call.",
        ],
        examples=[
            Example(
                broken="import list;\nlet items = list.new();\nlist.get(items);",
                fixed="import list;\nlet items = list.new();\nlist.get(items, 0);",
                explanation="list.get() requires an index as the second argument.",
            ),
        ],
        fixes=[
            "Check the function signature and provide the correct number of arguments.",
            "Use ail docs STDLIB_REFERENCE.md to check stdlib function signatures.",
        ],
        related_commands=["ail docs STDLIB_REFERENCE.md", "ail explain SEM003"],
        heal_topic="type_error",
    ),
    "TYP012": ErrorExplanation(
        code="TYP012",
        description="Argument type mismatch: an argument in a function call has a type that does not match the expected parameter type.",
        common_causes=[
            "Passing a string where a number is expected.",
            "Passing a boolean where a string is expected.",
            "Type inference inconsistency between function declaration and call site.",
        ],
        examples=[
            Example(
                broken='fn add(a, b) { return a + b; }\nlet x = add(1, "2");',
                fixed='fn add(a, b) { return a + b; }\nlet x = add(1, 2);',
                explanation="Both arguments must be the same type (numeric for arithmetic).",
            ),
        ],
        fixes=[
            "Ensure the argument type matches the function parameter type.",
            "Use convert.to_int(), convert.to_string(), etc. to convert types.",
        ],
        related_commands=["ail explain TYP001", "ail heal type_error"],
        heal_topic="type_error",
    ),
    "TYP013": ErrorExplanation(
        code="TYP013",
        description="Non-function callee: attempting to call something that is not a function.",
        common_causes=[
            "Using a variable as a function when it holds a non-function value.",
            "Typo in the function name (falling back to a variable name).",
        ],
        examples=[
            Example(
                broken="let x = 42;\nx();",
                fixed="let x = 42;\nprint(x);",
                explanation="Only functions can be called. x is a number, not a function.",
            ),
        ],
        fixes=[
            "Ensure the name you are calling refers to a function, not a variable.",
            "Check for typos in function names.",
        ],
        related_commands=["ail explain SEM002", "ail docs LANGUAGE_SPEC.md"],
        heal_topic=None,
    ),
    "MOD002": ErrorExplanation(
        code="MOD002",
        description="Duplicate import: the same module is imported more than once.",
        common_causes=[
            "Importing the same module twice in a file.",
            "Copy-paste duplication of import statements.",
        ],
        examples=[
            Example(
                broken="import map;\nimport map;",
                fixed="import map;",
                explanation="Remove the duplicate import. One import per module is sufficient.",
            ),
        ],
        fixes=[
            "Remove the duplicate import statement.",
            "Keep only one import per module at the top of the file.",
        ],
        related_commands=["ail fmt"],
        heal_topic=None,
    ),
    "SEM004": ErrorExplanation(
        code="SEM004",
        description="Unknown stdlib function: the function name does not match any known standard library function.",
        common_causes=[
            "Typo in the stdlib function name (e.g., list.sett instead of list.set).",
            "Using a function that does not exist in the stdlib module.",
            "Calling a stdlib function on the wrong module.",
        ],
        examples=[
            Example(
                broken='import list;\nlet x = list.sett(mylist, "key", "val");',
                fixed='import map;\nlet x = map.set(mymap, "key", "val");',
                explanation="list.sett does not exist; list.set does not accept string keys. Use map.set for key-value storage.",
            ),
        ],
        fixes=[
            "Check the function name spelling against STDLIB_REFERENCE.md.",
            "Use ail docs STDLIB_REFERENCE.md to list available functions.",
            "Verify you are calling the correct module (map vs list).",
        ],
        related_commands=["ail docs STDLIB_REFERENCE.md", "ail explain MOD004"],
        heal_topic="missing_import",
    ),
    "CMP001": ErrorExplanation(
        code="CMP001",
        description="Internal compiler error. This is a bug in the AILang compiler itself.",
        common_causes=[
            "A compiler bug triggered by an unexpected code pattern.",
            "A missing edge case in the compiler's error handling.",
        ],
        examples=[
            Example(
                broken="# This is not a user-facing code issue;\n# CMP001 indicates a compiler bug.",
                fixed="# Report the issue at the AILang repository.",
                explanation="CMP001 is an internal error, not a code error.",
            ),
        ],
        fixes=[
            "This is a compiler bug — please report it at the AILang repository.",
            "Include the source code that triggered the error.",
            "As a workaround, try simplifying the code around the reported location.",
        ],
        related_commands=[],
        heal_topic=None,
    ),
    "LSP000": ErrorExplanation(
        code="LSP000",
        description="LSP server error: the Language Server Protocol server encountered an internal error.",
        common_causes=[
            "The LSP server crashed due to unexpected input.",
            "Memory or resource exhaustion in the editor.",
        ],
        examples=[
            Example(
                broken="# LSP server shows an error popup in VS Code.",
                fixed="Restart the LSP server via VS Code command: 'AILang: Restart Server'",
                explanation="Restarting the LSP server typically resolves transient errors.",
            ),
        ],
        fixes=[
            "Restart the LSP server.",
            "In VS Code, run the 'AILang: Restart Server' command.",
            "If the problem persists, restart VS Code.",
        ],
        related_commands=["ail docs VSCODE_QUICKSTART"],
        heal_topic=None,
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
