# Parser Specification

This document defines the parser design contract for the initial AILang parser phase. It is derived from [LANGUAGE_SPEC.md](../../LANGUAGE_SPEC.md) and the grammar in [GRAMMAR.md](GRAMMAR.md).

## Scope
The parser will operate on the token stream produced by the lexer and produce a concrete syntax tree (CST) as its primary output.

## Responsibilities
- Parse the language grammar defined in GRAMMAR.md.
- Report syntax diagnostics using the existing diagnostics subsystem.
- Preserve source spans for syntax nodes when possible.
- Produce a CST that reflects the parsed structure without requiring semantic analysis.

## Parsing Strategy
- The parser will use a recursive-descent strategy that matches the precedence levels in GRAMMAR.md.
- Each nonterminal in the grammar will map to one parser function or method.
- The parser will preserve the grammar's operator precedence and associativity rules explicitly.

## Public API
- The parser entry point will accept a token stream from the lexer.
- The parser will return a CST root node or raise/record syntax diagnostics on failure.
- The parser API should remain independent of the concrete lexer implementation details beyond token types and source locations.

## Diagnostics Integration
- Syntax errors must be reported through the diagnostics subsystem.
- Diagnostics should include the relevant source location when available.
- The parser should support deterministic recovery for common syntax errors where practical.

## Synchronization and Recovery
- On syntax errors, the parser will synchronize to a safe boundary such as a semicolon, a closing brace, or the end of input.
- Recovery should be deterministic and should not invent missing syntax.

## Output Model
- The parser output is a CST.
- The CST should preserve tokens and structural relationships needed for later AST lowering.

## Non-Goals for the Initial Phase
- Semantic analysis
- Type checking
- Evaluation
- Full error recovery beyond basic deterministic recovery
