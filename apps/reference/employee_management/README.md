# Employee Management System

An employee management system demonstrating AILang's department filtering, salary aggregation, and CSV export patterns.

## Features

- **Employee Records**: Create and store employee data as maps
- **Department Filtering**: Recursively filter employees by department
- **Salary Reports**: Calculate total and average salaries
- **CSV Export**: Generate CSV output from employee data

## Running

```bash
ail run main.ail
```

## Key Patterns

- **List filtering with recursion**: Build a new list by appending matches during recursive traversal
- **Salary aggregation**: Sum salaries via recursive accumulation
- **CSV generation**: Recursive string building with newline separators
- **Two display modes**: Full detail vs. brief format for filtered views

## Data Model

```json
{
  "id": 1,
  "name": "Alice",
  "dept": "Engineering",
  "salary": 95000
}
```
