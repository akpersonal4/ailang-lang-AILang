# Benchmark Report — Mini SQL Engine

## Application Summary

| Attribute | Value |
|-----------|-------|
| Name | Mini SQL Engine |
| Purpose | Parse and execute SQL SELECT queries over CSV-backed in-memory tables — supports filtering, sorting, aggregation, and limiting |
| Lines of Code | 839 |
| Functions | 67 |
| Modules Used | 8 (`string`, `list`, `map`, `convert`, `csv`, `file`, `io`, `json`) |

## Development Metrics

| Metric | Result |
|--------|--------|
| First Compile | FAIL |
| Final Compile | PASS |
| First Runtime | FAIL |
| Final Runtime | PASS |
| Compiler Iterations | 3 |
| Runtime Iterations | 6 |
| Total Revisions | 9 |
| Development Time | ~48 min |

## Features Implemented

| Feature | Status | Details |
|---------|--------|---------|
| SELECT * | ✅ | Expands `*` to all table columns (uppercase normalized) |
| SELECT column list | ✅ | Specific column selection, case-insensitive |
| WHERE with =, !=, <, <=, >, >= | ✅ | Numeric comparison when both sides numeric; string comparison otherwise |
| WHERE with AND | ✅ | Left-to-right short-circuit evaluation |
| WHERE with OR | ✅ | Left-to-right short-circuit evaluation |
| ORDER BY (ASC/DESC) | ✅ | Recursive selection sort on projected rows |
| LIMIT | ✅ | Takes first N rows after sorting |
| DISTINCT | ✅ | Applied after projection, before ORDER BY |
| COUNT(\*) | ✅ | Counts rows after filtering/sorting/limiting |
| CSV table loading | ✅ | Uses `csv.parse_header`, normalizes column names to uppercase |
| String literal conditions | ✅ | Single-quoted strings in WHERE clauses |
| Combined queries | ✅ | All clauses composable (WHERE + ORDER BY + LIMIT, etc.) |

## SQL Feature Support

```sql
SELECT [DISTINCT] {* | column [, ...] | COUNT(*)}
FROM table_name
[WHERE condition [AND|OR condition ...]]
[ORDER BY column [ASC|DESC]]
[LIMIT n]
```

Conditions: `column|value OPERATOR column|value` where OPERATOR ∈ {`=`, `!=`, `<`, `<=`, `>`, `>=`}

## Benchmark

### Test Data: `apps/mini_sql/data.csv`

```
name,age,city,score
Alice,30,New York,95
Bob,25,Los Angeles,87
Charlie,35,Chicago,92
Diana,28,New York,88
Eve,32,Los Angeles,91
Frank,27,Chicago,85
Grace,31,New York,94
Henry,29,Los Angeles,89
```

### Query Results

| # | Query | Runtime | Rows |
|---|-------|---------|------|
| 1 | `SELECT * FROM data` | ✅ | 8 |
| 2 | `SELECT name, age FROM data` | ✅ | 8 |
| 3 | `SELECT * FROM data WHERE age > 30` | ✅ | 3 |
| 4 | `SELECT * FROM data ORDER BY age` | ✅ | 8 |
| 5 | `SELECT * FROM data ORDER BY age DESC` | ✅ | 8 |
| 6 | `SELECT * FROM data LIMIT 3` | ✅ | 3 |
| 7 | `SELECT DISTINCT city FROM data` | ✅ | 3 |
| 8 | `SELECT COUNT(*) FROM data` | ✅ | 1 |
| 9 | `SELECT COUNT(*) FROM data WHERE age >= 30` | ✅ | 1 |
| 10 | `SELECT * FROM data WHERE age > 25 AND city = 'New York'` | ✅ | 3 |
| 11 | `SELECT name, score FROM data WHERE city = 'Los Angeles' ORDER BY score DESC` | ✅ | 3 |
| 12 | `SELECT * FROM data ORDER BY score DESC LIMIT 3` | ✅ | 3 |

### Test Run

```sh
ail run apps/mini_sql/main.ail apps/mini_sql/data.csv "SELECT * FROM data WHERE age > 30"
```

Output:
```
NAME | AGE | CITY | SCORE
-------------------------
Charlie | 35 | Chicago | 92
Eve | 32 | Los Angeles | 91
Grace | 31 | New York | 94
(3 rows)
```

## Design Decisions

1. **Recursive tokenizer**: AILang has no `while`/`for`/`loop`, so the tokenizer uses a single `tokenize_step` recursive function with pure recursive collectors (`collect_digits`, `collect_alphanum`) that don't call back to the main loop, avoiding forward-reference problems.

2. **Uppercase normalization**: Column names, `ORDER BY` references, and `SELECT` column identifiers are normalized to uppercase for case-insensitive matching. Projected output columns use uppercase keys.

3. **DISTINCT before ORDER BY**: DISTINCT is applied after projection (to operate on selected columns only) and before ORDER BY, following standard SQL semantics.

4. **Nested if instead of &&**: AILang's `&&` does not short-circuit. All `cond_a && depends_on_a` patterns use nested `if` statements instead.

5. **No regex, no split**: String operations use the `find_substring` utility (defined in Level 0) and recursive character-by-character parsing. The `csv.parse_header` module handles CSV splitting.

## Challenges Encountered

| Challenge | Impact | Workaround |
|-----------|--------|------------|
| No forward references | All 67 functions must be in dependency order | Leveled file structure (L0→L8) |
| No while/for/loop | Every iteration is recursive | Recursion with accumulator parameters |
| No short-circuit && | `list.get([], 0)` throws even when guarded by `len == 1 &&` | Nested `if` statements |
| No try/catch | Cannot recover from missing map keys | Explicit `map.has` checks before every `map.get` |
| No regex | SQL parsing is character-by-character | Recursive char processing |
| No string.split | No built-in tokenization | Custom `find_substring` + `split_string` utility |
