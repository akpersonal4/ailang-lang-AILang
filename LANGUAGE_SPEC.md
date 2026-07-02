# Language Specification

## Language Decisions

### Strings Only
AILang supports string literals only. Character literals are not part of the language.

### String Semantics
- String literals are delimited by double quotes.
- Escape sequences are supported for common control characters and the quote and backslash characters.
- The lexer must report unterminated strings and invalid escape sequences.
