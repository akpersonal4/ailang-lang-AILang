# CURRENT_MILESTONE

## Current Milestone

Validation Sprint 2

## Status

Complete

## What Was Validated

Ten compiler validation examples were written and executed through the official CLI
to stress-test the language and surface compiler bugs.

Each example validates a specific subset of AILang language features:

| Example             | Features Validated                                    |
|---------------------|-------------------------------------------------------|
| word_counter        | functions, variables, arithmetic, return, print       |
| text_search         | functions, if/else, string equality, return, print    |
| config_loader       | functions, variables, return, print                   |
| json_parser         | functions, if/else, comparisons, return, print        |
| csv_reader          | functions, variables, return, print                   |
| ini_parser          | functions, if/else, comparisons, return, print        |
| markdown_parser     | functions, if/else, string equality, return, print    |
| file_copy           | functions, if/else, comparisons, return, print        |
| http_client         | functions, if/else, string equality, return, print    |
| dir_tree            | functions, if/else, comparisons, return, print        |

## Naming

These programs are intentionally called **Compiler Validation Examples**, not
"real applications". They use hardcoded input data because AILang does not yet
have a standard library.

Real applications (JSON parsers that read files, HTTP clients that open sockets,
file copy utilities that read bytes) become possible once the standard library
is introduced in Phase 2.

## Bug Found and Fixed

| Bug | Location | Fix |
|-----|----------|-----|
| CLI auto-printed return value of main() | compiler/cli/main.py | Removed print(result); output must come from print() builtins only |

Regression test: `test_regression_main_return_value_not_printed_by_cli`

## Quality Gates

- pytest: 158 passed
- black: clean
- ruff: clean
- mypy: clean

## Next Milestone

Standard Library (Phase 2)

Prerequisites for real applications:
- File I/O: open, read, write, close
- String operations: len, contains, split, startsWith, charAt
- Dynamic collections (arrays/lists)

Do NOT start without CTO approval.
