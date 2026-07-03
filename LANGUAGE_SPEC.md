# Language Specification

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

## Member Access
AILang supports qualified member access expressions: `a.b` and `a.b()`.

### Grammar
```
postfix_expression
    → primary
    → postfix "." identifier
    → postfix "(" argument_list ")"
```

### AST
- `MemberAccessNode(receiver, member)` - represents `receiver.member`

### Semantics
- Member access on dict values returns the value at the key `member`
- Nested member access chains left-to-right: `a.b.c` = `(a.b).c`
- Member call evaluates callee as member access, then invokes

## Modules

### Grammar
```
import_declaration
    → "import" identifier ( "." identifier )* [ "as" identifier ] ";"
    → "import" "*" [ "as" identifier ] "from" string_literal ";"
```

### Syntax Rules
- Import declarations are top-level only
- Module path maps to file path: `math.max` → `math/max.ail`
- All top-level declarations are exported by default
- No circular imports allowed

### Examples
```ail
import math.max;
import io.print as p;
import math.*;
math.max(10, 20)
```

## Syntax Goals
- The language grammar should remain explicit and deterministic.
- The grammar is the source of truth for parser design and implementation.
- The parser must follow the grammar rather than inventing syntax.