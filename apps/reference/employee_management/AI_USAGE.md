# AI Usage Guide: Employee Management System

## Key Patterns Demonstrated

### 1. Department Filtering with Recursion

The filter pattern builds a new list by appending matches during recursive traversal. The `result` list is passed as an accumulator parameter.

```ailang
fn filter_by_dept_helper(employees, idx, dept, result) {
    if (idx >= list.len(employees)) { return result }
    let emp = list.get(employees, idx);
    if (map.get(emp, "dept") == dept) {
        list.append(result, emp)
    };
    return filter_by_dept_helper(employees, idx + 1, dept, result)
}

fn filter_by_dept(employees, dept) {
    let result = list.new();
    return filter_by_dept_helper(employees, 0, dept, result)
}
```

**Pattern**: Initialize accumulator in wrapper, pass through recursive calls, return at base case.

**Rule**: Always use `map.has` before `map.get` when key existence is uncertain. Here, keys are guaranteed by `create_employee`.

### 2. Salary Aggregation

Total and average salary use recursive accumulation. The `avg_salary` function composes `total_salary` and `count_employees`.

```ailang
fn total_salary_helper(employees, idx) {
    if (idx >= list.len(employees)) { return 0 }
    let emp = list.get(employees, idx);
    let sal = map.get(emp, "salary");
    return sal + total_salary_helper(employees, idx + 1)
}
```

**Pattern**: Base case returns zero identity element, recursive case adds current value to tail result.

### 3. CSV Export

Recursive string building with newline separators. The `export_csv_helper` builds rows bottom-up, prepending each row to the rest.

```ailang
fn export_csv_helper(employees, idx) {
    if (idx >= list.len(employees)) { return "" }
    let emp = list.get(employees, idx);
    let row = export_csv_row(emp);
    let rest = export_csv_helper(employees, idx + 1);
    if (rest == "") { return row }
    return row + "\n" + rest
}
```

**Pattern**: Base case returns empty string, recursive case concatenates current row with newline separator.

**Rule**: `string.concat` takes exactly 2 arguments. Use `+` operator for 3+ string concatenations.

### 4. Two Display Modes

The system provides two display functions:
- `display_employees`: Full detail (id, name, dept, salary)
- `display_dept`: Brief format (id, name, salary) for filtered views

This avoids conditional logic in a single display function.

## Common Mistakes

1. **Variable collision**: Using `i` in both `filter_by_dept_helper` and `total_salary_helper` violates unique naming rules
2. **Missing accumulator init**: Forgetting `let result = list.new();` in wrapper function causes undefined behavior
3. **Wrong order**: Defining `filter_by_dept` before `filter_by_dept_helper` causes forward reference error
4. **Missing semicolon after if block**: The `list.append` inside `if` needs a semicolon before the closing brace
5. **Division by zero**: `avg_salary` assumes non-empty list; add guard if empty list is possible
