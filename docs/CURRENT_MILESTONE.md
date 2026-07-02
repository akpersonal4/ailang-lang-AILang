# CURRENT_MILESTONE

## Current Milestone

Parser Refactor

## Goal

Split the monolithic parser into a modular architecture before adding further grammar features.

## Acceptance Criteria

- Parser is split into separate modules: nodes, token_stream, expressions, declarations, statements, recovery, and main entry point.
- Public API is preserved (Parser class, CSTNode, parse_program, parse_expression).
- `parse_return_statement` span inconsistency is fixed.
- All quality gates pass with no behavior changes.

## Tasks

- [x] Extract CSTNode into compiler/parser/nodes.py
- [x] Extract TokenStream into compiler/parser/token_stream.py
- [x] Extract expression parsing into compiler/parser/expressions.py
- [x] Extract declaration parsing into compiler/parser/declarations.py
- [x] Extract statement parsing (block, if/else, return, expression) into compiler/parser/statements.py
- [x] Extract recovery into compiler/parser/recovery.py
- [x] Create main Parser entry point in compiler/parser/parser.py
- [x] Create compiler/parser/__init__.py with re-exports
- [x] Fix parse_return_statement span (current → previous)
- [x] Delete old monolithic compiler/parser.py
- [x] Pass all quality gates

## Completion

100%

## Blockers

None.

## Next Task

Parser finalization: loops (while) and remaining grammar features.