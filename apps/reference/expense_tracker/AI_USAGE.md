# AI Usage Guide — Expense Tracker

## Language Features Demonstrated
- Recursion with helper functions (index accumulator pattern)
- Map creation and field access
- List append, get, len operations
- Set for unique category collection
- JSON stringify/parse for persistence
- CSV export via recursive string building
- File read/write operations
- Conditional branching (if/else)
- String concatenation with + operator for multi-part strings

## stdlib Modules Used
- `list` — dynamic arrays
- `map` — key-value pairs per expense
- `set` — unique category collection
- `json` — serialization
- `csv` — CSV parsing (available for import)
- `file` — persistence
- `io` — output
- `convert` — type conversion
- `time` — available for timestamps

## Common Mistakes
- Forgetting `return` in recursive helpers
- Reusing variable names like `i` or `idx` across helper functions
- Not guarding `list.get` with `list.len` check
- Using `=` instead of `==` in conditions
- Mixing up `string.concat` (2 args) vs `+` (3+ strings)

## Recommended AI Prompts
- "Add a monthly budget limit per category"
- "Add sorting by amount (highest to lowest)"
- "Add a function to find expenses above a threshold"

## Related Diagnostics
- SEM002: Forward reference (callee must be defined before caller)
- TYP003: Type mismatch in comparison
- PAR001: Unexpected token
