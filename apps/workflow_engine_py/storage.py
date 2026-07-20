"""JSON persistence layer for workflow engine."""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load(name):
    _ensure_data_dir()
    path = os.path.join(DATA_DIR, f"{name}.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        content = f.read()
    if not content:
        return []
    return json.loads(content)


def save(name, items):
    _ensure_data_dir()
    path = os.path.join(DATA_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(items, f)
    return items


def next_id(name):
    items = load(name)
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def append(name, item):
    items = load(name)
    items.append(item)
    save(name, items)
    return item


def find_by_id(name, item_id):
    items = load(name)
    for item in items:
        if item["id"] == item_id:
            return item
    return False


def update_field(name, item_id, field, value):
    items = load(name)
    for item in items:
        if item["id"] == item_id:
            item[field] = value
            save(name, items)
            return True
    return False


def delete_by_id(name, item_id):
    items = load(name)
    items = [item for item in items if item["id"] != item_id]
    save(name, items)
    return True


def clear(name):
    save(name, [])
    return True
