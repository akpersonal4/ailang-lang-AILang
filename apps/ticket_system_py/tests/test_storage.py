"""Tests for storage layer."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from pathlib import Path

from storage import (
    append,
    clear,
    delete_by_id,
    find_by_id,
    load,
    next_id,
    save,
    update_field,
)


class TestStorage(unittest.TestCase):
    def setUp(self):
        Path("data").mkdir(exist_ok=True)
        clear("test_collection")

    def tearDown(self):
        clear("test_collection")

    def test_load_empty_returns_empty_list(self):
        result = load("test_empty")
        self.assertEqual(result, [])

    def test_save_and_load(self):
        items = [{"id": 1, "name": "test"}]
        save("test_collection", items)
        loaded = load("test_collection")
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["name"], "test")

    def test_next_id_empty(self):
        result = next_id("test_next_empty")
        self.assertEqual(result, 1)

    def test_next_id_after_append(self):
        append("test_collection", {"id": 10, "name": "x"})
        result = next_id("test_collection")
        self.assertEqual(result, 11)

    def test_find_by_id_exists(self):
        save("test_collection", [{"id": 5, "v": "found"}])
        result = find_by_id("test_collection", 5)
        self.assertIsNotNone(result)
        self.assertEqual(result["v"], "found")

    def test_find_by_id_not_exists(self):
        save("test_collection", [{"id": 1, "v": "nope"}])
        result = find_by_id("test_collection", 99)
        self.assertIsNone(result)

    def test_update_field(self):
        save("test_collection", [{"id": 1, "status": "old"}])
        result = update_field("test_collection", 1, "status", "new")
        self.assertTrue(result)
        loaded = find_by_id("test_collection", 1)
        self.assertEqual(loaded["status"], "new")

    def test_update_field_nonexistent(self):
        result = update_field("test_collection", 999, "x", "y")
        self.assertFalse(result)

    def test_delete_by_id(self):
        save("test_collection", [{"id": 1}, {"id": 2}])
        result = delete_by_id("test_collection", 1)
        self.assertTrue(result)
        loaded = load("test_collection")
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["id"], 2)

    def test_append(self):
        append("test_collection", {"id": 1, "a": "b"})
        append("test_collection", {"id": 2, "c": "d"})
        loaded = load("test_collection")
        self.assertEqual(len(loaded), 2)

    def test_clear(self):
        save("test_collection", [{"id": 1}, {"id": 2}])
        clear("test_collection")
        loaded = load("test_collection")
        self.assertEqual(loaded, [])

    def test_load_corrupt_json_returns_empty(self):
        Path("data").mkdir(exist_ok=True)
        with open("data/test_corrupt.json", "w") as f:
            f.write("{invalid json")
        result = load("test_corrupt")
        self.assertEqual(result, [])
        Path("data/test_corrupt.json").unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
