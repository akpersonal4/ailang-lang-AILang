# Intermediate Representation Specification (IR v1)

This document defines the Intermediate Representation (IR) for AILang. It acts as the immutable contract between the type-checked Abstract Syntax Tree (AST) and downstream modules such as the execution engine/runtime.

---

## 1. Design Principles

- **Immutability**: All IR nodes are implemented as frozen dataclasses (`frozen=True`).
- **Purity**: Syntax-only artifacts (braces, parentheses, colons, semicolons) are completely eliminated.
- **Span Preservation**: Every IR node carries `start_span` and `end_span` offsets derived from the source AST nodes to preserve diagnostic mapping.
- **No Side-Effects**: Lowering is a pure tree-to-tree transformation without semantic validation or type checks (which are done in the front-end).

---

## 2. IR Node Inventory

The IR contains exactly 13 node types.

### Structural Nodes

1. **`ProgramIR`**
   - **Fields**:
     - `body: tuple[IRNode, ...]`
     - `start_span: int | None`
     - `end_span: int | None`
   - **Description**: The top-level module containing declarations and statements.

2. **`FunctionIR`**
   - **Fields**:
     - `name: str`
     - `parameters: tuple[str, ...]`
     - `body: BlockIR`
     - `start_span: int | None`
     - `end_span: int | None`
   - **Description**: A declared function.

3. **`BlockIR`**
   - **Fields**:
     - `statements: tuple[IRNode, ...]`
     - `start_span: int | None`
     - `end_span: int | None`
   - **Description**: A scoped list of statements.

### Statement Nodes

4. **`VariableDeclarationIR`**
   - **Fields**:
     - `name: str`
     - `initializer: IRExpression`
     - `start_span: int | None`
     - `end_span: int | None`
   - **Description**: A new local or global variable declaration.

5. **`AssignmentIR`**
   - **Fields**:
     - `target: str`
     - `value: IRExpression`
     - `start_span: int | None`
     - `end_span: int | None`
   - **Description**: Modifying a variable in scope.

6. **`IfIR`**
   - **Fields**:
     - `condition: IRExpression`
     - `then_block: BlockIR`
     - `else_block: BlockIR | None`
     - `start_span: int | None`
     - `end_span: int | None`
   - **Description**: Conditional execution block.

7. **`ReturnIR`**
   - **Fields**:
     - `value: IRExpression`
     - `start_span: int | None`
     - `end_span: int | None`
   - **Description**: Returns a value from a function.

8. **`ExpressionStatementIR`**
   - **Fields**:
     - `expression: IRExpression`
     - `start_span: int | None`
     - `end_span: int | None`
   - **Description**: Evaluates an expression for side effects.

### Expression Nodes

9. **`BinaryOperationIR`**
   - **Fields**:
     - `left: IRExpression`
     - `operator: str`
     - `right: IRExpression`
     - `start_span: int | None`
     - `end_span: int | None`
   - **Description**: Performs binary operations (`+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `<=`, `>`, `>=`, `&&`, `||`).

10. **`UnaryOperationIR`**
    - **Fields**:
      - `operator: str`
      - `operand: IRExpression`
      - `start_span: int | None`
      - `end_span: int | None`
    - **Description**: Performs unary operations (`-`, `!`).

11. **`CallIR`**
    - **Fields**:
      - `callee: str`
      - `arguments: tuple[IRExpression, ...]`
      - `start_span: int | None`
      - `end_span: int | None`
    - **Description**: A function invocation.

12. **`LiteralIR`**
    - **Fields**:
      - `value: object` (Python `int`, `float`, or `str`)
      - `start_span: int | None`
      - `end_span: int | None`
    - **Description**: Represents raw constants.

13. **`VariableReferenceIR`**
    - **Fields**:
      - `name: str`
      - `start_span: int | None`
      - `end_span: int | None`
    - **Description**: Referencing a variable or parameter by name.

---

## 3. AST to IR Lowering Rules

- A binary expression with operator `=` is lowered to `AssignmentIR` if the target is a variable reference; otherwise, it is treated as a `BinaryOperationIR`.
- Numeric literals are parsed into Python `int` or `float` types based on the presence of a decimal point.
- String literals preserve the raw string content.
- Parameters of functions are simplified from `ParameterNode` lists to simple tuples of strings (`tuple[str, ...]`).

---

## 4. Printer Format (Deterministic)

The pretty-printer outputs a structured, indented tree format. Every indent consists of two spaces. Example output:

```text
Program
  VariableDeclaration x
    Literal 10
  Function foo
    Block
      Return
        VariableReference x
```

---

## 5. Validation Assertions

- Every node must have `start_span` and `end_span` attributes present (even if their values are `None` due to unavailable source info).
- `ProgramIR` must not be empty.
- `FunctionIR` parameters must be a tuple.
- `AssignmentIR` must have a non-empty target name.
- `CallIR` must have a non-empty callee name.
