"""JSON file persistence layer for ticket system."""

import json
from pathlib import Path

DATA_DIR = Path("data")


def _collection_path(name: str) -> Path:
    return DATA_DIR / f"{name}.json"


def load(name: str) -> list[dict]:
    path = _collection_path(name)
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def save(name: str, items: list[dict]) -> list[dict]:
    path = _collection_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    return items


def next_id(name: str) -> int:
    items = load(name)
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def append(name: str, item: dict) -> dict:
    items = load(name)
    items.append(item)
    save(name, items)
    return item


def find_by_id(name: str, item_id: int) -> dict | None:
    items = load(name)
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def update_field(name: str, item_id: int, field: str, value) -> bool:
    items = load(name)
    for item in items:
        if item["id"] == item_id:
            item[field] = value
            save(name, items)
            return True
    return False


def delete_by_id(name: str, item_id: int) -> bool:
    items = load(name)
    items = [item for item in items if item["id"] != item_id]
    save(name, items)
    return True


def clear(name: str) -> None:
    save(name, [])
