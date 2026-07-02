# AST Specification

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
- CST punctuation nodes are not preserved in the AST.
- Parentheses are removed after precedence-aware parsing.
- Token values are preserved in literal and identifier nodes.

## Source Information
- AST nodes may retain source spans for diagnostics and debugging.
- Semantic analysis may attach additional metadata as needed.
