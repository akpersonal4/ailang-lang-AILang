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
