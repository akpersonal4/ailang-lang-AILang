# CURRENT_MILESTONE

## Current Milestone

AST Builder v1

## Goal

Implement immutable AST node definitions and CST-to-AST transformation according to AST_SPEC.md.

## Acceptance Criteria

- Immutable AST node definitions exist in compiler/ast/nodes.py
- CST-to-AST transformation exists in compiler/ast/builder.py
- Source spans are preserved on AST nodes
- Syntax-only tokens (semicolons, commas, braces, parens) are discarded
- AST unit tests pass
- AST golden snapshot is generated
- All quality gates pass

## Tasks

- [x] Create compiler/ast/ package with package init
- [x] Define immutable AST node dataclasses (Program, Block, VariableDeclaration, FunctionDeclaration, Parameter, ExpressionStatement, ReturnStatement, IfStatement, BinaryExpression, UnaryExpression, CallExpression, Identifier, NumberLiteral, StringLiteral)
- [x] Implement CST-to-AST transformation in ASTBuilder
- [x] Preserve source spans on all AST nodes
- [x] Discard syntax-only tokens (ParameterList, ArgumentList, punctuation)
- [x] Handle else-if chains (lifts nested IfStatement into synthetic Block)
- [x] Add 25 AST unit tests
- [x] Add AST golden snapshot
- [x] Pass all quality gates (59 tests, black, ruff, mypy)

## Completion

100%

## Blockers

None.

## Next Task

Begin semantic analysis.

Do NOT start without CTO approval.