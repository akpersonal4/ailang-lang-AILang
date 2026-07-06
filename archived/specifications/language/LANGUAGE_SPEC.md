# Language Specification

This file is the language-level specification root for AILang. It is the source of truth for the lexer and parser design documents in this repository.

## Language Decisions

### Strings Only
AILang supports string literals only. Character literals are not part of the language.

### String Semantics
- String literals are delimited by double quotes.
- Escape sequences are supported for common control characters and the quote and backslash characters.
- The lexer must report unterminated strings and invalid escape sequences.

### Comments
- AILang supports single-line comments beginning with `//`.
- Multi-line comments are not part of the language specification.

### Whitespace
- Whitespace includes spaces, tabs, and newlines.
- Whitespace is ignored between tokens.

### Unicode Policy
- The initial lexer implementation is ASCII-oriented for identifiers, numbers, and punctuation.
- Full Unicode support is not part of the current language specification.

## Syntax Goals
- The language grammar should remain explicit and deterministic.
- The grammar is the source of truth for parser design and implementation.
- The parser must follow the grammar rather than inventing syntax.
