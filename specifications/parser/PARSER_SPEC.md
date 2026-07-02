# Parser Specification

## Scope
This document defines the parser design contract for the initial AILang parser phase. The parser will operate on the token stream produced by the lexer and produce a concrete syntax tree (CST) as its primary output.

## Responsibilities
- Parse the language grammar defined in GRAMMAR.md.
- Report syntax diagnostics using the existing diagnostics subsystem.
- Preserve source spans for syntax nodes when possible.
- Produce a CST that reflects the parsed structure without requiring semantic analysis.

## Public API
- The parser entry point will accept a token stream from the lexer.
- The parser will return a CST root node or raise/record syntax diagnostics on failure.
- The parser API should remain independent of the concrete lexer implementation details beyond token types and source locations.

## Diagnostics Integration
- Syntax errors must be reported through the diagnostics subsystem.
- Diagnostics should include the relevant source location when available.
- The parser should support deterministic recovery for common syntax errors where practical.

## Output Model
- The parser output is a CST.
- The CST should preserve tokens and structural relationships needed for later AST lowering.

## Non-Goals for the Initial Phase
- Semantic analysis
- Type checking
- Evaluation
- Full error recovery beyond basic deterministic recovery
