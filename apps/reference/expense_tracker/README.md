# Expense Tracker

An expense tracking application demonstrating AILang's list, map, set, json, csv, and file modules with category-based aggregation.

## Features
- Add expenses with description, amount, and category
- Calculate totals by category
- Calculate grand total
- Collect unique categories via set
- Export to CSV file
- Save/load JSON persistence

## Architecture
- Data: List of maps, each map has "desc" (string), "amount" (number), "category" (string)
- Aggregation: Recursive helpers with category filter and running total
- Category collection: Set-based unique category tracking
- CSV export: Recursive string building with newline separators
- Persistence: JSON via `json.stringify`/`json.parse` + `file.write`/`file.read`

## LOC
~105

## stdlib Modules Used
- `list` — dynamic array operations
- `map` — key-value storage per expense
- `set` — unique category collection
- `json` — serialization/deserialization
- `csv` — available for CSV parsing
- `file` — file I/O
- `io` — output
- `convert` — type conversion
- `time` — available for timestamps

## Run
```bash
ail run apps/reference/expense_tracker/main.ail
```
