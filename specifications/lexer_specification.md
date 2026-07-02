# Lexer Specification

## Scope
This document defines the lexical rules for the initial AILang lexer increments.

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
| Strings | `"..."` | ⬜ |
| Characters | `'a'` | Decision pending |
| Comments | `//`, `/* */` | ⬜ |
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
- Whitespace is ignored between tokens.

## Error Policy
- Unexpected characters raise a deterministic error.
- The lexer does not yet implement recovery for invalid input.

## Unicode Policy
- The current implementation is ASCII-oriented and does not yet define full Unicode support.

## Determinism
The lexer must produce deterministic token streams for the same input text.
