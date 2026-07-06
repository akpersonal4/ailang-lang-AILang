# CST Specification

This document defines the concrete syntax tree design for AILang. It is derived from [GRAMMAR.md](GRAMMAR.md) and the parser contract in [PARSER_SPEC.md](PARSER_SPEC.md).

## Purpose
The concrete syntax tree (CST) preserves the full syntactic structure of the source program as parsed from the lexer token stream.

## Node Model
- Each syntax node should expose a kind and a source span.
- Parent-child relationships should be explicit.
- Tokens should remain attached to the nodes that own them where appropriate.
- Each nonterminal production in the grammar will map to one CST node kind; terminals are represented as tokens rather than as separate structural nodes.

## Core Node Kinds
- ProgramNode
- BlockNode
- VariableDeclarationNode
- FunctionDeclarationNode
- ParameterListNode
- ExpressionStatementNode
- IfStatementNode
- BinaryExpressionNode
- UnaryExpressionNode
- IdentifierNode
- NumberLiteralNode
- StringLiteralNode
- TokenNode


## Source Span Tracking
- Every node should carry start and end offsets when available.
- Nodes should preserve the source location of their associated tokens.

## Design Goals
- Preserve syntax structure faithfully.
- Make later AST lowering straightforward.
- Keep the CST simple enough to debug and inspect.
