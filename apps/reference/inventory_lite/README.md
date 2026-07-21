# Inventory Management Lite

A lightweight inventory management system demonstrating AILang's map-based records, recursive search patterns, and JSON persistence.

## Features

- **Product CRUD**: Create, find, and manage products
- **Stock Operations**: Stock in/out with automatic updates
- **Value Reports**: Calculate total inventory value
- **JSON Persistence**: Save and load inventory from files

## Running

```bash
ail run main.ail
```

## Key Patterns

- **Map-based records**: Products stored as maps with typed fields
- **Recursive search**: Linear scan with early return on match
- **Recursive aggregation**: Count and sum via tail recursion
- **JSON serialization**: Full inventory round-trip through `json.stringify`/`json.parse`

## Data Model

```json
{
  "id": 1,
  "name": "Widget",
  "price": 9.99,
  "stock": 100
}
```
