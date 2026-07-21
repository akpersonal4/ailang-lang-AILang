# JSON Transformer — AI Usage Guide

## Key AILang Patterns

### JSON Parse/Stringify
- `json.parse(json_string)` — converts JSON string to AILang maps/lists
- `json.stringify(value, pretty)` — converts AILang data to JSON string

### Map Field Transformation
- Use `map.get(record, field)` to read fields
- Use `map.set(record, field, value)` to write transformed fields
- Create new maps with `map.new()` for normalized records

### Record Normalization Pattern
- Recursive helper iterates over list by index
- Base case: `if (idx >= list.len(records)) { return records }`
- Transform each record, set it back with `list.set`, recurse with `idx + 1`

### File I/O Pipeline
1. `file.read(path)` — read input file as string
2. `json.parse` — convert to AILang data structure
3. Transform with recursion over list indices
4. `json.stringify` — convert back to JSON string
5. `file.write(path, content)` — write output file

## Common Pitfalls
- `string.concat` takes exactly 2 args — use `+` for 3+ strings
- Always check `list.len` before `list.get` to avoid index-out-of-bounds
- `map.get` requires the key to exist — use `map.has` to guard unknown keys
- Bottom-up ordering: `uppercase_field` before `normalize_record` before `normalize_records_helper`
