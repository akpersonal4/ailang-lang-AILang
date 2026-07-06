# AI Benchmark Matrix

**Version:** 0.1.1  
**Date:** 2026-07-05  
**Applications:** 21  

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Compiles and runs successfully |
| ⚠️ | Compiles but runtime issues |
| ❌ | Compilation or runtime errors |
| - | Not applicable / No external API calls |
| L | Low difficulty |
| M | Medium difficulty |
| H | High difficulty |

---

## Benchmark Matrix

| Application | Category | LOC | Features | Difficulty | Expected Output | GPT | Gemini | Claude | Kimi | DeepSeek | Llama | First-pass Compile | First-pass Run | Compile Iterations | Runtime Iterations | Final Rating |
|-------------|----------|-----|----------|------------|-----------------|-----|--------|--------|------|----------|-------|-------------------|---------------|------------------|------------------|--------------|
| banking_ledger | Data Management | 56 | list, map, time, recursion | M | Account balances, transactions | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| bmi_calculator | Utilities | 20 | arithmetic, conditionals | L | BMI values and categories | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| calculator | Utilities | 14 | arithmetic | L | Arithmetic results | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| config_reader | File Processing | 23 | file, string | M | Config validation, file contents | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| contact_book | Data Management | 50 | list, map, recursion, search | M | Contact list, search | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| csv_analyzer | Data Processing | 28 | csv, list, map, convert | M | CSV stats, averages | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| employee_management | Business Logic | 43 | list, map, arithmetic | M | Payroll, bonuses | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| expense_tracker | Data Management | 47 | list, map, time, aggregation | M | Expense totals | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| file_copy | File Processing | 27 | file, path, comparison | M | File copy verification | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| file_search | File Processing | 28 | file, string | M | Search results | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| grade_calculator | Utilities | 18 | conditionals | L | Grade letters | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| inventory | Data Management | 44 | list, map, multiplication | M | Inventory value | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| invoice_generator | Business Logic | 48 | list, map, time, arithmetic | M | Invoice with totals | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| json_formatter | Data Processing | 20 | json, file, path | M | JSON roundtrip | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| log_analyzer | File Processing | 10 | file, string | L | File stats | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| markdown_stats | Text Processing | 21 | string | M | Markdown analysis | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| number_base | Utilities | 59 | convert, recursion, arithmetic | H | Binary/hex conversion | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| password_generator | Security | 45 | random, list, string | M | Random passwords | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| random_data_generator | Utilities | 40 | random, list | M | Random numbers | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| scientific_calculator | Utilities | 39 | recursion, math | H | Factorial, GCD, prime check | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| simple_quiz | Education | 27 | random, conditionals | M | Quiz with score | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| student_management | Education | 53 | list, map, arithmetic | M | Class stats | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| temperature_converter | Utilities | 15 | arithmetic | L | Temperature conversions | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| text_search | Text Processing | 20 | string | M | Case-insensitive search | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| todo_manager | Productivity | 45 | list, map, booleans | M | Todo list with completion | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| unit_converter | Utilities | 14 | arithmetic | L | Unit conversions | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |
| word_counter | Text Processing | 12 | string | L | String stats | - | - | - | - | - | - | ✅ | ✅ | 1 | 1 | - |

---

## Category Distribution

| Category | Applications | Avg LOC |
|----------|--------------|---------|
| Utilities | 9 | 28 |
| Data Management | 4 | 48 |
| File Processing | 4 | 22 |
| Business Logic | 2 | 46 |
| Education | 2 | 40 |
| Text Processing | 3 | 18 |
| Data Processing | 2 | 24 |
| Security | 1 | 45 |
| Productivity | 1 | 45 |

---

## Difficulty Analysis

| Difficulty | Applications | Avg LOC | Characteristics |
|------------|--------------|---------|-----------------|
| Low (L) | 7 | 15 | Simple conditionals, arithmetic |
| Medium (M) | 13 | 35 | Collections, multiple modules |
| High (H) | 2 | 49 | Complex recursion, algorithms |

---

## Stdlib Module Usage

| Module | Applications Using |
|--------|-------------------|
| list | 12 |
| map | 10 |
| string | 7 |
| time | 3 |
| file | 4 |
| csv | 1 |
| json | 1 |
| path | 2 |
| random | 3 |
| math | 1 |
| convert | 1 |
| io | 2 |
| environment | 0 |
| set | 0 |
| system | 0 |

---

## Feature Usage Patterns

| Feature | Count | Applications |
|---------|-------|--------------|
| Recursion | 7 | number_base, password_generator, random_data_generator, scientific_calculator, simple_quiz, todo_manager, banking_ledger |
| Map operations | 12 | All data management apps |
| List operations | 15 | Most applications |
| Multi-module import | 10 | Complex applications |

---

## Complexity Correlation

Applications with higher complexity tend to:
- Use more stdlib modules (3-4 modules)
- Have longer line counts (45-59 LOC)
- Require deeper understanding of recursion patterns
- Use map structures for data modeling

---

## Recommendations for AI Benchmarking

1. **Start with Low difficulty** - calculator, grade_calculator, log_analyzer, word_counter, temperature_converter
2. **Progress to Medium** - Most applications fall here
3. **High difficulty** - number_base, scientific_calculator require careful recursion handling
4. **Key challenges for AI:**
   - Recursion instead of loops
   - Map-as-record pattern
   - Module-qualified function calls
   - Helper function patterns for iteration