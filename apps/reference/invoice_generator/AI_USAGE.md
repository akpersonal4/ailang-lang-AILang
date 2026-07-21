# Invoice Generator — AI Usage Guide

## Key AILang Patterns

### Business Logic Calculations
- Use `math.mul(a, b)` for multiplication
- Use `math.div(a, b)` for division
- Use `+` for addition (supported natively in AILang)
- No loops — recursive helpers iterate over line items by index

### Tax Computation
- Store tax rate as whole number (e.g., 8 for 8%)
- Calculate: `math.div(math.mul(subtotal, rate), 100)`
- Display: concatenate rate with `"%"` string directly

### Currency Formatting
- `format_currency(amount)` pattern: `"$" + convert.to_string(amount)`
- Returns strings like `$300`, `$24`, `$324`

### JSON Export
- Build invoice as nested map structure with `map.new()` / `map.set`
- `json.stringify(invoice, true)` for pretty-printed output
- `file.write(path, json_string)` to save to disk

### Invoice Data Model
```json
{
  "customer": { "name": "...", "address": "...", "email": "..." },
  "items": [ { "desc": "...", "qty": N, "price": N, "total": N } ],
  "date": "YYYY-MM-DD",
  "subtotal": N,
  "tax_rate": N,
  "tax": N,
  "total": N
}
```

## Common Pitfalls
- `calc_subtotal_helper` calls `line_total` (callee defined before caller)
- `display_line_items_helper` uses `format_currency` (defined earlier in file)
- All recursive helpers use `_helper` suffix and unique variable names
- `add_line_item` mutates the list via `list.append` then returns it
