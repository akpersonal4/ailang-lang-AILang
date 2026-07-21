# Reference Applications

Eight canonical AILang applications demonstrating real-world patterns.
Each app is self-contained, compiles cleanly, and runs end-to-end.

## Applications

### 1. Todo Manager (`apps/reference/todo_manager/`)

**Patterns:** list CRUD, map operations, JSON persistence, recursive counting

~97 LOC. Manages a todo list with add, complete, delete, save, and load operations.
Demonstrates list + map data modeling and JSON file I/O.

### 2. Expense Tracker (`apps/reference/expense_tracker/`)

**Patterns:** aggregation, category filtering, CSV export, JSON persistence

~145 LOC. Tracks expenses with category-based totals, CSV export, and JSON save/load.
Demonstrates recursive aggregation and data transformation pipelines.

### 3. Inventory Lite (`apps/reference/inventory_lite/`)

**Patterns:** map CRUD, stock operations, JSON persistence, inventory valuation

~120 LOC. Manages product inventory with stock in/out, value calculations, and file persistence.
Demonstrates map-centric data modeling.

### 4. Employee Management (`apps/reference/employee_management/`)

**Patterns:** filtering, salary reports, CSV export, recursive processing

~142 LOC. Manages employees with department filtering, salary aggregation, and CSV output.
Demonstrates recursive list processing with accumulation.

### 5. Log Analyzer (`apps/reference/log_analyzer/`)

**Patterns:** file parsing, string splitting, level counting, report generation

~137 LOC. Parses log files, counts errors/warnings, generates level-based reports.
Demonstrates string parsing and map-based aggregation.

### 6. CSV ETL (`apps/reference/csv_etl/`)

**Patterns:** CSV parsing, validation, transformation, pipeline processing

~104 LOC. End-to-end CSV pipeline: parse, validate, transform, display.
Demonstrates data validation and multi-stage transformation.

### 7. JSON Transformer (`apps/reference/json_transformer/`)

**Patterns:** JSON parsing, map normalization, string operations, JSON export

~81 LOC. Reads JSON, normalizes fields (uppercase, formatting), writes output.
Demonstrates JSON round-trip and map transformation.

### 8. Invoice Generator (`apps/reference/invoice_generator/`)

**Patterns:** business logic, tax calculation, math operations, JSON export

~110 LOC. Generates invoices with line items, subtotals, tax, and total.
Demonstrates math operations and structured data output.

## Running Reference Apps

Each app requires running from its own directory (for relative path access to sample data):

```bash
cd apps/reference/todo_manager
ail run main.ail
```

## AI Training Corpus

Each app includes `AI_USAGE.md` documenting:
- Which AI tools were used (if any)
- What patterns the AI generated
- What required human correction
- Lessons learned for AI-assisted AILang development

## Adding New Reference Apps

1. Create directory under `apps/reference/`
2. Include: `main.ail`, `README.md`, `AI_USAGE.md`, `sample_input/`, `sample_output/`, `tests/`
3. Ensure `ail fmt`, `ail check`, `ail build`, `ail test`, `ail run` all pass
4. Document AI usage in `AI_USAGE.md`
