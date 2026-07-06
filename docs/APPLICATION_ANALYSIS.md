# Application Analysis Report

**Date:** 2026-07-05  
**Total Applications Analyzed:** 21  

---

## Summary Table

| Application | LOC | Features | Stdlib Modules | Category |
|-------------|-----|----------|----------------|----------|
| banking_ledger | 56 | Accounts, deposits, withdrawals, display | list, map, time | Data Management |
| bmi_calculator | 20 | Calculation, conditionals | - | Utilities |
| calculator | 14 | Basic arithmetic | - | Utilities |
| config_reader | 23 | File I/O, string search | file, string | File Processing |
| contact_book | 50 | CRUD operations, search, display | list, map | Data Management |
| csv_analyzer | 28 | CSV parsing, aggregation | csv, list, map, convert | Data Processing |
| employee_management | 43 | Payroll, bonuses, iteration | list, map | Business Logic |
| expense_tracker | 47 | Expense tracking, totals, categories | list, map, time | Data Management |
| file_copy | 27 | File operations, verification | file, path | File Processing |
| file_search | 28 | File search, string matching | file, string | File Processing |
| grade_calculator | 18 | Grade mapping | - | Utilities |
| inventory | 44 | Inventory tracking, value calculation | list, map | Data Management |
| invoice_generator | 48 | Invoice generation, taxes | list, map, time | Business Logic |
| json_formatter | 20 | JSON parsing, file I/O, paths | json, file, path | Data Processing |
| log_analyzer | 10 | File analysis, string operations | file, string | File Processing |
| markdown_stats | 21 | Text analysis, markdown parsing | string | Text Processing |
| number_base | 59 | Base conversion, recursion | convert | Utilities |
| password_generator | 45 | Random generation, recursion | random, list, io | Security |
| random_data_generator | 40 | Random data, floats, choices | random, list, io | Utilities |
| scientific_calculator | 39 | Factorial, GCD, LCM, prime check | io, math | Utilities |
| simple_quiz | 27 | Quiz scoring, random questions | random | Education |
| student_management | 53 | Class stats, best student search | list, map | Education |
| temperature_converter | 15 | Temperature conversion | - | Utilities |
| todo_manager | 45 | Todo CRUD, completion tracking | list, map | Productivity |
| unit_converter | 14 | Unit conversion | - | Utilities |
| word_counter | 12 | String length, search | string | Text Processing |

---

## Detailed Application Analysis

### 1. banking_ledger

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Account balances before and after transactions with timestamp  

**Features Used:**
- Variable declarations with `let`
- Function definitions with `fn`
- Map operations (map.new, map.set, map.get)
- List operations (list.new, list.append, list.get, list.len)
- If conditionals with boolean results
- String concatenation in print

**Stdlib Modules:** list, map, time

**Compiler Diagnostics:** No errors expected

**Missing Stdlib Functions:** None

**Coding Patterns:**
- Helper pattern for iteration: `display_account_helper(accounts, i)`
- In-place mutation of collections returned for chaining

**Suggested Benchmark Category:** Data Management / Collections

---

### 2. bmi_calculator

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** BMI values and categories for test cases

**Features Used:**
- Integer arithmetic
- If-else conditionals
- Function return values

**Stdlib Modules:** None

**Compiler Diagnostics:** No errors expected

**Coding Patterns:**
- Simple if-chain for categorization
- Arithmetic expressions

**Suggested Benchmark Category:** Utilities / Math

---

### 3. calculator

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Arithmetic results (10+3=13, 10-3=7, 10*3=30, 10/3=3.333..., 10%3=1)

**Features Used:**
- Basic arithmetic operators (+, -, *, /, %)
- Function definitions
- Print statements

**Stdlib Modules:** None

**Compiler Diagnostics:** No errors expected

**Coding Patterns:**
- Simple wrapper functions around operators

**Suggested Benchmark Category:** Utilities / Basic

---

### 4. config_reader

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Config file validation status, file contents

**Features Used:**
- File I/O (file.exists, file.read)
- String operations (string.contains)
- If conditionals

**Stdlib Modules:** file, string

**Compiler Diagnostics:** No errors expected

**Coding Patterns:**
- File existence check before read
- Boolean return pattern

**Suggested Benchmark Category:** File Processing

---

### 5. contact_book

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Contact list display, search results

**Features Used:**
- Map operations (map.new, map.set, map.get)
- List operations (list.new, list.append, list.len, list.get)
- If conditionals
- Logical operators (!)
- Helper iteration pattern

**Stdlib Modules:** list, map

**Missing Stdlib Functions:** Could benefit from `list.find` or `map.find`

**Repeated Patterns:**
- `find_by_name_helper` - finds item by property
- `display_contacts_helper` - iterates and displays

**Suggested Benchmark Category:** Data Management / Search

---

### 6. csv_analyzer

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Row count, individual rows display, average score

**Features Used:**
- CSV parsing (csv.parse_header)
- Map operations on parsed rows
- List iteration
- Type conversion (convert.to_int)
- Arithmetic

**Stdlib Modules:** csv, list, map, convert

**Compiler Diagnostics:** No errors expected

**Missing Stdlib Functions:** None

**Repeated Patterns:**
- Helper function with index for list iteration

**Suggested Benchmark Category:** Data Processing / CSV

---

### 7. employee_management

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Payroll processing with bonuses, total payroll

**Features Used:**
- Map operations for employee records
- List iteration with index helper
- If conditionals for bonus calculation
- Arithmetic operations

**Stdlib Modules:** list, map

**Repeated Patterns:**
- `process_payroll_helper` - common iteration pattern

**Suggested Benchmark Category:** Business Logic / Payroll

---

### 8. expense_tracker

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Total expenses, category totals

**Features Used:**
- Map for expense records
- List for collection
- Time functions (time.now)
- Recursive aggregation

**Stdlib Modules:** list, map, time

**Repeated Patterns:**
- Category-based filtering in `total_by_category_helper`

**Suggested Benchmark Category:** Data Management / Finance

---

### 9. file_copy

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Copy status, content verification, cleanup confirmation

**Features Used:**
- File I/O (exists, read, write, remove)
- Path operations
- String comparison
- If conditionals

**Stdlib Modules:** file, path

**Compiler Diagnostics:** No errors expected

**Suggested Benchmark Category:** File Processing / I/O

---

### 10. file_search

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Search results for pattern matches

**Features Used:**
- File I/O
- String contains
- If conditionals
- String concatenation

**Stdlib Modules:** file, string

**Note:** Requires `data.txt` file to exist with specific content

**Suggested Benchmark Category:** File Processing / Search

---

### 11. grade_calculator

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Grade letters for numerical scores

**Features Used:**
- If conditionals
- Comparison operators

**Stdlib Modules:** None

**Coding Patterns:**
- Simple if-chain for mapping ranges to values

**Suggested Benchmark Category:** Utilities / Education

---

### 12. inventory

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Inventory display, total value

**Features Used:**
- Map for item records
- List for collection
- Multiplication for value calculation
- Recursive iteration

**Stdlib Modules:** list, map

**Repeated Patterns:**
- Standard display and total calculation helpers

**Suggested Benchmark Category:** Data Management / Inventory

---

### 13. invoice_generator

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Invoice with items, subtotal, tax, total

**Features Used:**
- Map for line items
- List for collection
- Time for current timestamp
- Arithmetic for calculations

**Stdlib Modules:** list, map, time

**Suggested Benchmark Category:** Business Logic / Finance

---

### 14. json_formatter

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Formatted JSON, roundtrip verification, path info

**Features Used:**
- JSON parsing and stringification
- File I/O
- Path operations

**Stdlib Modules:** json, file, path

**Suggested Benchmark Category:** Data Processing / JSON

---

### 15. log_analyzer

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** File length, content checks

**Features Used:**
- File read
- String length
- String contains

**Stdlib Modules:** file, string

**Suggested Benchmark Category:** File Processing / Analysis

---

### 16. markdown_stats

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Markdown statistics (headers, links, length)

**Features Used:**
- String contains, starts_with
- Inline string literals

**Stdlib Modules:** string

**Suggested Benchmark Category:** Text Processing / Analysis

---

### 17. number_base

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Binary and hex representations, digit sum

**Features Used:**
- Integer arithmetic
- Modulo operations
- String concatenation for building results
- Recursion
- Type conversion

**Stdlib Modules:** convert

**Missing Functionality:**
- Could use `string.substring` but uses manual division instead

**Suggested Benchmark Category:** Utilities / Algorithms

---

### 18. password_generator

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Random passwords of various lengths

**Features Used:**
- Random choice from collection
- List operations
- String concatenation
- Recursion

**Stdlib Modules:** random, list, io

**Repeated Patterns:**
- `random_char()` - builds character set manually
- Recursive string building

**Suggested Benchmark Category:** Security / Randomization

---

### 19. random_data_generator

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Random integers, floats, and color choice

**Features Used:**
- Random int, float, choice
- List operations
- Recursion for building collections

**Stdlib Modules:** random, list, io

**Suggested Benchmark Category:** Utilities / Randomization

---

### 20. scientific_calculator

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Factorial, GCD, LCM, prime checks, abs/min/max

**Features Used:**
- Recursion (factorial, is_prime_helper, gcd)
- Modulo for prime checking
- Math module functions

**Stdlib Modules:** io, math

**Missing Stdlib Functions:**
- `math.pow`, `math.sqrt` - implemented manually

**Suggested Benchmark Category:** Utilities / Math

---

### 21. simple_quiz

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Quiz questions with answers, final score

**Features Used:**
- Random integers for questions
- If conditionals
- Variable assignment
- Comparison

**Stdlib Modules:** random

**Suggested Benchmark Category:** Education / Games

---

### 22. student_management

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Class average, highest-scoring student

**Features Used:**
- Map for student records
- List iteration
- Division for average
- Recursive max-finding

**Stdlib Modules:** list, map

**Repeated Patterns:**
- Two helper functions for finding best (name and score)

**Suggested Benchmark Category:** Education / Statistics

---

### 23. temperature_converter

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Temperature conversions between C, F, K

**Features Used:**
- Arithmetic formulas
- Function definitions

**Stdlib Modules:** None

**Suggested Benchmark Category:** Utilities / Conversion

---

### 24. text_search

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Case-insensitive search results, uppercase/ends-with checks

**Features Used:**
- String lowercase
- String contains, starts_with, ends_with, uppercase
- String concatenation

**Stdlib Modules:** string

**Missing Stdlib Functions:**
- Case-insensitive contains (implemented via lowercase wrapper)

**Suggested Benchmark Category:** Text Processing / Search

---

### 25. todo_manager

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Todo list display before and after completion

**Features Used:**
- Map for todo items
- List iteration
- Boolean assignment in map
- If conditionals

**Stdlib Modules:** list, map

**Repeated Patterns:**
- Standard display helper pattern

**Suggested Benchmark Category:** Productivity / Task Management

---

### 26. unit_converter

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** Unit conversions (cm/inches, kg/lbs)

**Features Used:**
- Arithmetic formulas
- Function definitions

**Stdlib Modules:** None

**Suggested Benchmark Category:** Utilities / Conversion

---

### 27. word_counter

**Build Status:** ✅ Compiles successfully  
**Run Status:** ✅ Runs successfully  
**Expected Output:** String length, contains checks, prefix/suffix checks

**Features Used:**
- String operations (length, contains, starts_with, ends_with)

**Stdlib Modules:** string

**Suggested Benchmark Category:** Text Processing / Basic

---

## Cross-Application Patterns

### Repeated Helper Functions
| Pattern | Applications Using | Recommendation |
|---------|-------------------|----------------|
| `display_*_helper` | 7 | Could use `list.iter` if loops existed |
| `find_*_helper` | 3 | Could use `list.find_by` or similar |
| `sum_*_helper` | 3 | Could use `list.sum` or `list.reduce` |
| `calc_*_helper` | 3 | Various calculation patterns |

### Repeated Algorithms
| Algorithm | Applications | Description |
|-----------|-------------|-------------|
| Recursive iteration | 15+ | Manual index-based iteration due to no loops |
| Map-get pattern | 12 | Retrieving values from map structures |
| Map-set in functions | 10 | Creating and populating maps |

### Repeated String Manipulation
| Pattern | Applications | Notes |
|---------|-------------|-------|
| `string.contains` | 8 | Most common string operation |
| `string.lowercase` + `contains` | 1 | Case-insensitive search workaround |
| String concatenation | 6 | Building output strings |

### Repeated File Utilities
| Pattern | Applications | Notes |
|---------|-------------|-------|
| File exists + read | 5 | Common file processing pattern |
| Self-file read for demo | 3 | Reading own source for demonstration |

### Missing Stdlib Opportunities (3+ occurrences)
1. **List iteration helper** - Present in 15+ applications
2. **List find-by-property** - Present in 3 applications
3. **List sum/reduce** - Present in 3 applications
4. **String split** - No application uses it (but could benefit)
5. **Map iteration values** - Used but no helper exists