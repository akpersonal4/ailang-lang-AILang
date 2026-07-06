# Lexer Specification

This document is the lexer-facing specification for AILang. It is subordinate to [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md) and provides the lexical contract that the parser consumes.

## Scope
This document defines the lexical rules for the initial AILang lexer implementation.

## Token Inventory
The lexer must recognize the following token categories:

| Category | Tokens | Status |
| --- | --- | --- |
| Keywords | `let`, `fn`, `if`, `else`, `return` | ✅ |
| Identifiers | identifier | ✅ |
| Numbers | integer | ✅ |
| Assignment | `=` | ✅ |
| Arithmetic | `+`, `-`, `*`, `/`, `%` | ✅ |
| Comparison | `==`, `!=`, `<`, `<=`, `>`, `>=` | ✅ |
| Logical | `&&`, `||`, `!` | ✅ |
| Strings | `"..."` | ✅ |
| Comments | `//` | ✅ |
| EOF | EOF | ✅ |

## Character Literal Decision
AILang will use string literals only. Character literals are not a distinct language feature and are intentionally not supported.

## Identifier Rules
- Identifiers begin with a letter or underscore.
- Subsequent characters may be letters, digits, or underscores.
- Identifiers are case-sensitive.

## Numeric Literal Rules
- Numeric literals are sequences of decimal digits.
- The lexer currently tokenizes integers only.

## Reserved Keywords
The following reserved words are tokenized as keyword tokens:
- `let`
- `fn`
- `if`
- `else`
- `return`

## Whitespace Handling
- Whitespace includes spaces, tabs, and newlines.
- Whitespace is ignored between tokens.

## Comment Rules
- `//` begins a single-line comment that continues until the next newline or end of input.
- Multi-line comments are not supported.

## Source Location Rules
- Every token must expose its starting line, starting column, start offset, and end offset.
- EOF tokens expose the final position after the last consumed character.

## Error Policy
- Unexpected characters, unterminated strings, and invalid escape sequences are reported as lexer diagnostics.
- The lexer does not yet implement recovery for invalid input.

## Unicode Policy
- The current implementation is ASCII-oriented for identifiers, numbers, and punctuation.
- Full Unicode support is not part of the current language specification.

## Determinism
The lexer must produce deterministic token streams for the same input text.
