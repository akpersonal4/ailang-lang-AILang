# AI Usage Guide — Todo Manager

## Language Features Demonstrated
- Recursion with helper functions (index accumulator pattern)
- Map creation and field access
- List append, get, len operations
- JSON stringify/parse for persistence
- File read/write operations
- Conditional branching (if/else)

## stdlib Modules Used
- `list` — dynamic arrays
- `map` — key-value pairs
- `json` — serialization
- `file` — persistence
- `io` — output
- `convert` — type conversion

## Common Mistakes
- Forgetting `return` in recursive helpers
- Reusing variable names like `i` or `x` across functions
- Not guarding `list.get` with `list.len` check
- Using `=` instead of `==` in conditions

## Recommended AI Prompts
- "Add a priority field to each todo item"
- "Add a search function that finds todos by title substring"
- "Add a due date field and sort by date"

## Related Diagnostics
- SEM002: Forward reference (callee must be defined before caller)
- TYP003: Type mismatch in comparison
- PAR001: Unexpected token
