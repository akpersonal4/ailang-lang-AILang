# AST Specification

This document defines the abstract syntax tree design for AILang. It is derived from the CST design in [CST_SPEC.md](CST_SPEC.md) and the grammar in [GRAMMAR.md](GRAMMAR.md).

## Purpose
The abstract syntax tree (AST) is the simplified representation used after parsing and before semantic analysis.

## Design Goals
- Remove syntactic noise such as punctuation and grouping tokens.
- Preserve only semantics-relevant structure.
- Keep the AST suitable for later semantic analysis and code generation.

## Core Node Kinds
- ProgramNode
- BlockNode
- VariableDeclarationNode
- FunctionDeclarationNode
- ParameterNode
- ExpressionStatementNode
- BinaryExpressionNode
- UnaryExpressionNode
- IdentifierNode
- NumberLiteralNode
- StringLiteralNode

## Transform Rules
- Each CST node is lowered to a corresponding AST node when the syntax is semantically relevant.
- CST punctuation nodes are not preserved in the AST.
- Parentheses are removed after precedence-aware parsing.
- Token values are preserved in literal and identifier nodes.
- Operator precedence is encoded in the AST structure by the parser's precedence-aware descent.

## Source Information
- AST nodes may retain source spans for diagnostics and debugging.
- Semantic analysis may attach additional metadata as needed.
