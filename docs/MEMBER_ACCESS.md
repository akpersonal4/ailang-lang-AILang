# Member Access v1

Support for qualified member access expressions: `a.b` and `a.b()`.

## Grammar

```ebnf
postfix_expression
    → primary
    → postfix "." identifier
    → postfix "(" argument_list ")"
```

## AST Node

```python
@dataclass(frozen=True)
class MemberAccessNode:
    receiver: ASTNode
    member: IdentifierNode
    start_span: int | None = None
    end_span: int | None = None
```

## Examples

```ail
a.b
a.b()
a.b.c
a.b.c()
user.name
config.port
math.max
```

## Runtime Behavior

- Member access on dict values returns the value at the key `member`
- Nested member access chains left-to-right: `a.b.c` = `(a.b).c`
- Member call evaluates the callee as a member access, then invokes