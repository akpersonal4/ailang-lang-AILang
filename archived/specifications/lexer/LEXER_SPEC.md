# Lexer Specification

This document defines the lexer contract for AILang. It is subordinate to [../language/LANGUAGE_SPEC.md](../language/LANGUAGE_SPEC.md) and provides the token stream consumed by the parser.

## Token Categories
- Keywords: let, fn, if, else, return
- Identifiers
- Numbers
- Assignment
- Arithmetic operators
- Comparison operators
- Logical operators
- Strings
- Comments
- EOF

## Whitespace and Comments
- Whitespace is ignored between tokens.
- `//` begins a single-line comment.
- Multi-line comments are not supported.

## Source Locations
- Every token exposes line, column, start offset, and end offset.

## Diagnostics
- Invalid characters, unterminated strings, and invalid escapes are reported through the diagnostics subsystem.
