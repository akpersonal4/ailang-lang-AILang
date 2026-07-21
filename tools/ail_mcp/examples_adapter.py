# AILang MCP Server - Examples Adapter
# Provides canonical AILang code examples

"""Examples adapter for MCP server - provides canonical AILang code examples."""

from __future__ import annotations

from typing import Any

EXAMPLES = {
    "hello": {
        "title": "Hello World",
        "description": "Basic AILang program with functions and variables",
        "code": """fn greet(name) {
    let message = "Hello, " + name + "!";
    io.writeln(message);
    return 0;
}

fn main() {
    let result = greet("AILang");
    return 0;
}""",
    },
    "inventory": {
        "title": "Inventory Management",
        "description": "CRUD operations with maps and lists",
        "code": """fn create_item(id, name, quantity) {
    let item = map.new();
    map.set(item, "id", id);
    map.set(item, "name", name);
    map.set(item, "quantity", quantity);
    return item;
}

fn add_item(inventory, item) {
    list.append(inventory, item);
    return inventory;
}

fn find_item(inventory, id) {
    let len = list.len(inventory);
    let found = find_item_recursive(inventory, id, 0, len);
    return found;
}

fn find_item_recursive(inventory, id, index, len) {
    if index >= len {
        return none;
    }
    let item = list.get(inventory, index);
    let item_id = map.get(item, "id");
    if item_id == id {
        return item;
    }
    return find_item_recursive(inventory, id, index + 1, len);
}

fn main() {
    let inventory = list.new();
    let item1 = create_item(1, "Widget", 100);
    let item2 = create_item(2, "Gadget", 50);
    let inventory = add_item(inventory, item1);
    let inventory = add_item(inventory, item2);
    let found = find_item(inventory, 1);
    io.writeln("Found item: " + map.get(found, "name"));
    return 0;
}""",
    },
    "csv": {
        "title": "CSV Import",
        "description": "Reading and parsing CSV files",
        "code": """fn process_row(row) {
    let name = list.get(row, 0);
    let value = list.get(row, 1);
    io.writeln("Name: " + name + ", Value: " + value);
    return row;
}

fn process_csv(content) {
    let rows = csv.parse(content);
    let len = list.len(rows);
    let processed = process_rows(rows, 0, len);
    return processed;
}

fn process_rows(rows, index, len) {
    if index >= len {
        return rows;
    }
    let row = list.get(rows, index);
    let processed = process_row(row);
    return process_rows(rows, index + 1, len);
}

fn main() {
    let content = "name,value\\nfoo,42\\nbar,7";
    let result = process_csv(content);
    return 0;
}""",
    },
    "json": {
        "title": "JSON Processing",
        "description": "Parsing and manipulating JSON data",
        "code": """fn process_user(user_json) {
    let user = json.parse(user_json);
    let name = map.get(user, "name");
    let age = map.get(user, "age");
    io.writeln("User: " + name + ", Age: " + convert.to_string(age));
    return user;
}

fn create_user(name, age) {
    let user = map.new();
    map.set(user, "name", name);
    map.set(user, "age", age);
    return user;
}

fn main() {
    let user = create_user("Alice", 30);
    let user_json = json.stringify(user);
    let processed = process_user(user_json);
    return 0;
}""",
    },
    "recursion": {
        "title": "Recursion Patterns",
        "description": "Common recursion patterns for iteration",
        "code": """fn factorial(n) {
    if n <= 1 {
        return 1;
    }
    return n * factorial(n - 1);
}

fn sum_list(list, index) {
    if index >= list.len(list) {
        return 0;
    }
    return list.get(list, index) + sum_list(list, index + 1);
}

fn map_list(list, index) {
    if index >= list.len(list) {
        return list;
    }
    let item = list.get(list, index);
    let mapped = item * 2;
    list.set(list, index, mapped);
    return map_list(list, index + 1);
}

fn main() {
    let fact = factorial(5);
    io.writeln("Factorial: " + convert.to_string(fact));
    let numbers = list.new();
    list.append(numbers, 1);
    list.append(numbers, 2);
    list.append(numbers, 3);
    let total = sum_list(numbers, 0);
    io.writeln("Sum: " + convert.to_string(total));
    return 0;
}""",
    },
    "file_io": {
        "title": "File I/O",
        "description": "Reading and writing files",
        "code": """fn read_and_process(filename) {
    let exists = file.exists(filename);
    if exists == false {
        io.writeln("File not found: " + filename);
        return none;
    }
    let content = file.read(filename);
    io.writeln("Content length: " + convert.to_string(string.length(content)));
    return content;
}

fn write_report(filename, content) {
    file.write(filename, content);
    io.writeln("Report written to: " + filename);
    return filename;
}

fn main() {
    let content = "Hello, World!\\nThis is a test file.";
    let filename = "test.txt";
    let written = write_report(filename, content);
    let read_content = read_and_process(filename);
    return 0;
}""",
    },
    "todo_manager": {
        "title": "Todo Manager",
        "description": "List CRUD with JSON persistence and recursive counting",
        "code": """import list;
import map;
import json;
import file;
import io;
import convert;

fn create_todo(title) {
    let entry = map.new();
    map.set(entry, "title", title);
    map.set(entry, "done", 0);
    return entry;
}

fn add_todo(todos, title) {
    let entry = create_todo(title);
    list.append(todos, entry);
    return todos;
}

fn complete_todo(todos, index) {
    let entry = list.get(todos, index);
    map.set(entry, "done", 1);
    return todos;
}

fn display_todos_helper(todos, pos) {
    if (pos >= list.len(todos)) { return 0 }
    let entry = list.get(todos, pos);
    let done = map.get(entry, "done");
    if (done) {
        io.writeln("[x]" + map.get(entry, "title"));
    } else {
        io.writeln("[ ]" + map.get(entry, "title"));
    }
    return display_todos_helper(todos, pos + 1);
}

fn main() {
    let todos = list.new();
    todos = add_todo(todos, "Learn AILang");
    todos = add_todo(todos, "Build an app");
    display_todos_helper(todos, 0);
    todos = complete_todo(todos, 0);
    io.writeln("After completing task 1:");
    display_todos_helper(todos, 0);
    file.write("data/todos.json", json.stringify(todos));
    return 0;
}""",
    },
    "expense_tracker": {
        "title": "Expense Tracker",
        "description": "Category-based aggregation with CSV export",
        "code": """import list;
import map;
import io;
import convert;

fn create_expense(desc, amount, category) {
    let entry = map.new();
    map.set(entry, "desc", desc);
    map.set(entry, "amount", amount);
    map.set(entry, "category", category);
    return entry;
}

fn total_by_category_helper(expenses, idx, category) {
    if (idx >= list.len(expenses)) { return 0 }
    let entry = list.get(expenses, idx);
    let cat = map.get(entry, "category");
    let amt = map.get(entry, "amount");
    if (cat == category) {
        return total_by_category_helper(expenses, idx + 1, category) + amt
    }
    return total_by_category_helper(expenses, idx + 1, category)
}

fn main() {
    let expenses = list.new();
    list.append(expenses, create_expense("Groceries", 150, "Food"));
    list.append(expenses, create_expense("Gas", 45, "Transport"));
    list.append(expenses, create_expense("Dinner", 80, "Food"));
    io.writeln("Food total: $" + convert.to_string(total_by_category_helper(expenses, 0, "Food")));
    io.writeln("Transport total: $" + convert.to_string(total_by_category_helper(expenses, 0, "Transport")));
    return 0;
}""",
    },
    "log_analyzer": {
        "title": "Log Analyzer",
        "description": "File parsing with string splitting and level-based reporting",
        "code": """import list;
import map;
import string;
import io;
import convert;

fn count_level_helper(entries, idx, target) {
    if (idx >= list.len(entries)) { return 0 }
    let entry = list.get(entries, idx);
    let level = map.get(entry, "level");
    if (level == target) {
        return 1 + count_level_helper(entries, idx + 1, target)
    }
    return count_level_helper(entries, idx + 1, target)
}

fn main() {
    let content = "2024-01-01 10:00 INFO Server started\\n2024-01-01 10:01 ERROR Connection failed\\n2024-01-01 10:02 WARN Retry";
    let lines = string.split(content, "\\n");
    io.writeln("Loaded " + convert.to_string(list.len(lines)) + " log entries");
    io.writeln("Errors: " + convert.to_string(count_level_helper(lines, 0, "ERROR")));
    io.writeln("Warnings: " + convert.to_string(count_level_helper(lines, 0, "WARN")));
    return 0;
}""",
    },
    "csv_etl": {
        "title": "CSV ETL Pipeline",
        "description": "Parse, validate, transform pipeline with CSV I/O",
        "code": """import list;
import map;
import csv;
import string;
import io;
import convert;

fn validate_row(row) {
    let name = map.get(row, "name");
    let email = map.get(row, "email");
    if (string.length(string.trim(name)) == 0) { return 0 }
    if (string.length(string.trim(email)) == 0) { return 0 }
    return 1
}

fn validate_helper(rows, idx, acc) {
    if (idx >= list.len(rows)) { return acc }
    let row = list.get(rows, idx);
    if (validate_row(row) == 1) { list.append(acc, row) }
    return validate_helper(rows, idx + 1, acc)
}

fn main() {
    let content = "name,email,age\\nalice,alice@example.com,30\\nbob,bob@example.com,25\\n,,";
    let rows = csv.parse_header(content);
    io.writeln("Input: " + convert.to_string(list.len(rows)) + " rows");
    let valid = validate_helper(rows, 0, list.new());
    io.writeln("Valid: " + convert.to_string(list.len(valid)) + " rows");
    return 0;
}""",
    },
    "json_transformer": {
        "title": "JSON Transformer",
        "description": "JSON normalization with string operations and map transformation",
        "code": """import list;
import map;
import json;
import io;
import string;

fn normalize_record(original) {
    let name_val = string.uppercase(map.get(original, "name"));
    let city_val = string.uppercase(map.get(original, "city"));
    let normalized = map.new();
    map.set(normalized, "name", name_val);
    map.set(normalized, "city", city_val);
    map.set(normalized, "score", map.get(original, "score"));
    return normalized;
}

fn normalize_helper(recs, idx, result) {
    if (idx >= list.len(recs)) { return result }
    let updated = normalize_record(list.get(recs, idx));
    list.append(result, updated);
    return normalize_helper(recs, idx + 1, result);
}

fn main() {
    let json_str = "[{\\"name\\": \\"alice\\", \\"city\\": \\"new york\\", \\"score\\": 85}, {\\"name\\": \\"bob\\", \\"city\\": \\"los angeles\\", \\"score\\": 92}]";
    let records = json.parse(json_str);
    let result = normalize_helper(records, 0, list.new());
    io.writeln("Normalized " + convert.to_string(list.len(result)) + " records");
    io.writeln(json.stringify(result));
    return 0;
}""",
    },
    "invoice_generator": {
        "title": "Invoice Generator",
        "description": "Business logic with math operations and structured JSON output",
        "code": """import list;
import map;
import json;
import io;
import convert;
import math;

fn create_line_item(desc, qty, price) {
    let li = map.new();
    map.set(li, "desc", desc);
    map.set(li, "qty", qty);
    map.set(li, "price", price);
    map.set(li, "total", math.mul(qty, price));
    return li;
}

fn calc_subtotal_helper(items, idx) {
    if (idx >= list.len(items)) { return 0 }
    let item = list.get(items, idx);
    let item_total = map.get(item, "total");
    return item_total + calc_subtotal_helper(items, idx + 1)
}

fn main() {
    let items = list.new();
    list.append(items, create_line_item("Keyboard", 1, 50));
    list.append(items, create_line_item("Mouse", 2, 25));
    list.append(items, create_line_item("Monitor", 1, 200));
    let subtotal = calc_subtotal_helper(items, 0);
    let tax = math.div(math.mul(subtotal, 8), 100);
    io.writeln("Subtotal: $" + convert.to_string(subtotal));
    io.writeln("Tax (8%): $" + convert.to_string(tax));
    io.writeln("Total: $" + convert.to_string(subtotal + tax));
    return 0;
}""",
    },
}


def get_examples(category: str | None = None) -> dict[str, Any]:
    """Get canonical AILang code examples.

    Args:
        category: Optional category (hello, inventory, csv, json, recursion, file_io)

    Returns:
        Dictionary with example code
    """
    if category:
        if category in EXAMPLES:
            return {
                "category": category,
                **EXAMPLES[category],
            }
        else:
            return {
                "error": f"Category not found: {category}",
                "available_categories": list(EXAMPLES.keys()),
            }

    return {
        "categories": list(EXAMPLES.keys()),
        "examples": EXAMPLES,
    }
