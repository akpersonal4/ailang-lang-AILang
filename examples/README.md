# AILang Examples

A collection of example programs demonstrating AILang features and patterns.

## Quick Start

```bash
# Run any example
ail run examples/hello_world/main.ail

# Run with specific arguments
ail run examples/calculator/main.ail
```

## Examples by Difficulty

### Beginner

| Example | Description | Features |
|---------|-------------|----------|
| [hello_world](hello_world/) | Hello World program | `io.writeln`, basic structure |
| [variables](variables/) | Variable declaration and assignment | `let`, reassignment |
| [functions](functions/) | Function definition and calling | `fn`, `return`, parameters |
| [if_else](if_else/) | Conditional logic | `if`, `else`, boolean operators |
| [calculator](calculator/) | Basic calculator | Arithmetic, `io.writeln`, `convert.to_int` |
| [bmi_calc](bmi_calc/) | BMI calculator | Floating point, conditionals |
| [age_calc](age_calc/) | Age calculator | Arithmetic, strings |
| [salary_calc](salary_calc/) | Salary calculator | Arithmetic, conditionals |
| [loan_emi](loan_emi/) | Loan EMI calculator | Floating point, math operations |
| [electricity_bill](electricity_bill/) | Electricity bill calculator | Conditionals, arithmetic |
| [income_tax](income_tax/) | Income tax calculator | Nested conditionals |
| [voting_eligibility](voting_eligibility/) | Voting eligibility checker | Boolean logic |
| [password_validate](password_validate/) | Password validator | String operations, conditionals |
| [date_validate](date_validate/) | Date validator | String operations |
| [attendance](attendance/) | Attendance tracker | Lists, conditionals |
| [currency_converter](currency_converter/) | Currency converter | Arithmetic, I/O |
| [num_stats](num_stats/) | Number statistics | Math operations, conditionals |
| [prime_checker](prime_checker/) | Prime number checker | Recursion, conditionals |

### Intermediate

| Example | Description | Features |
|---------|-------------|----------|
| [fibonacci](fibonacci/) | Fibonacci sequence | Recursion, `list.append` |
| [recursion](recursion/) | Recursion patterns | Recursive functions |
| [collections](collections/) | List and map operations | `list.*`, `map.*` |
| [string_utils](string_utils.ail) | String utilities | `string.*` functions |
| [file_io](file_io.ail) | File I/O operations | `file.*` functions |
| [json_demo](json_demo.ail) | JSON operations | `json.parse`, `json.stringify` |
| [csv_demo](csv_demo.ail) | CSV operations | `csv.parse`, `csv.stringify` |
| [json_parser](json_parser/) | JSON file parser | File I/O, JSON, error handling |
| [csv_reader](csv_reader/) | CSV file reader | File I/O, CSV parsing |
| [config_loader](config_loader/) | Configuration file loader | File I/O, JSON |
| [word_counter](word_counter/) | Word frequency counter | Strings, maps, recursion |
| [text_search](text_search/) | Text search tool | String operations, lists |
| [student_records](student_records/) | Student record system | Maps, lists, persistence |
| [payroll](payroll/) | Payroll calculator | Arithmetic, lists, maps |
| [invoice_gen](invoice_gen/) | Invoice generator | String formatting, file I/O |
| [rule_engine](rule_engine/) | Simple rule engine | Maps, lists, conditionals |
| [expr_eval](expr_eval/) | Expression evaluator | Recursion, stacks |
| [ini_parser](ini_parser/) | INI file parser | File I/O, string operations |
| [markdown_parser](markdown_parser/) | Markdown to HTML | String operations, file I/O |
| [library_mgr](library_mgr/) | Library management | CRUD, persistence, reports |
| [banking](banking/) | Banking system | Maps, lists, file I/O |
| [shopping_cart](shopping_cart/) | Shopping cart | Maps, lists, arithmetic |
| [dir_tree](dir_tree/) | Directory tree viewer | File I/O, recursion |
| [file_copy](file_copy/) | File copy utility | File I/O |
| [modules](modules/) | Module system demo | Imports, modules |
| [integration](integration/) | Integration demo | Multiple features |

### Advanced

| Example | Description | Features |
|---------|-------------|----------|
| [http_client](http_client/) | HTTP client | External libraries |
| [rule_engine](rule_engine/) | Rule engine | Complex maps, lists |
| [expr_eval](expr_eval/) | Expression evaluator | Parsing, recursion |
| [static_analyzer](../apps/static_analyzer/) | Self-analyzing tool | Advanced recursion, analysis |

## Patterns

The `patterns/` directory contains reusable patterns for common operations:

| Pattern | Description | Usage |
|---------|-------------|-------|
| [recursive_filter](patterns/recursive_filter/) | Filter list by condition | Finding items matching criteria |
| [recursive_map](patterns/recursive_map/) | Transform list elements | Converting data formats |
| [recursive_reduce](patterns/recursive_reduce/) | Accumulate list to single value | Summing, counting, aggregating |
| [recursive_search](patterns/recursive_search/) | Search list for item | Finding specific items |
| [string_find](patterns/string_find/) | Find substring in string | Text search operations |
| [string_split](patterns/string_split/) | Split string by delimiter | CSV parsing, text processing |
| [json_store](patterns/json_store/) | JSON file persistence | Save/load data |
| [csv_reader](patterns/csv_reader/) | CSV file reading | Import data from CSV |
| [dependency_graph](patterns/dependency_graph/) | Dependency resolution | Topological sorting |
| [topological_sort](patterns/topological_sort/) | Topological sort | Task ordering |

## Running Examples

### Basic execution

```bash
ail run examples/hello_world/main.ail
```

### With arguments

```bash
ail run examples/calculator/main.ail
```

### Running tests

```bash
ail test examples/student_records/tests/
```

## Common Patterns

### List of Maps

Most real-world applications use lists of maps for data storage:

```ail
import list;
import map;

fn main() {
    let users = list.new();
    
    let user1 = map.new();
    map.set(user1, "id", 1);
    map.set(user1, "name", "Alice");
    list.append(users, user1);
    
    let user2 = map.new();
    map.set(user2, "id", 2);
    map.set(user2, "name", "Bob");
    list.append(users, user2);
    
    return 0;
}
```

### Filter Pattern

```ail
import list;
import map;

fn filter_by_status(items, status) {
    return filter_recursive(items, status, list.new(), 0)
}

fn filter_recursive(items, status, result, idx) {
    if (idx >= list.len(items)) {
        return result
    }
    let item = list.get(items, idx);
    if (map.get(item, "status") == status) {
        list.append(result, item);
    }
    return filter_recursive(items, status, result, idx + 1)
}
```

### Map Accumulation Pattern

```ail
import list;
import map;

fn count_by_status(items) {
    return count_recursive(items, map.new(), 0)
}

fn count_recursive(items, counts, idx) {
    if (idx >= list.len(items)) {
        return counts
    }
    let item = list.get(items, idx);
    let status = map.get(item, "status");
    let current = 0;
    if (map.has(counts, status)) {
        current = map.get(counts, status);
    }
    map.set(counts, status, current + 1);
    return count_recursive(items, counts, idx + 1)
}
```

## Getting Help

- [Getting Started](../docs/reference/GETTING_STARTED.md) — Step-by-step introduction
- [Language Tour](../docs/reference/LANGUAGE_TOUR.md) — Complete language feature tour
- [Standard Library Reference](../docs/reference/STDLIB_REFERENCE.md) — All modules documented

## Contributing Examples

To add a new example:

1. Create a directory with a descriptive name
2. Add `main.ail` as the entry point
3. Add a `README.md` explaining what the example does
4. Add comments in the code explaining key concepts
5. Ensure it runs with `ail run main.ail`
