"""Tests for storage module."""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from apps.workflow_engine_py import storage


class TestStorage(unittest.TestCase):
    def setUp(self):
        storage.clear("test_items")

    def test_load_empty(self):
        result = storage.load("nonexistent")
        self.assertEqual(result, [])

    def test_append_and_load(self):
        item = {"id": 1, "name": "test"}
        storage.append("test_items", item)
        items = storage.load("test_items")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "test")

    def test_next_id(self):
        self.assertEqual(storage.next_id("test_items"), 1)
        storage.append("test_items", {"id": 1, "name": "a"})
        self.assertEqual(storage.next_id("test_items"), 2)
        storage.append("test_items", {"id": 5, "name": "b"})
        self.assertEqual(storage.next_id("test_items"), 6)

    def test_find_by_id(self):
        storage.append("test_items", {"id": 1, "name": "a"})
        storage.append("test_items", {"id": 2, "name": "b"})
        result = storage.find_by_id("test_items", 2)
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "b")

    def test_find_by_id_not_found(self):
        result = storage.find_by_id("test_items", 999)
        self.assertFalse(result)

    def test_update_field(self):
        storage.append("test_items", {"id": 1, "name": "a"})
        result = storage.update_field("test_items", 1, "name", "updated")
        self.assertTrue(result)
        item = storage.find_by_id("test_items", 1)
        self.assertEqual(item["name"], "updated")

    def test_delete_by_id(self):
        storage.append("test_items", {"id": 1, "name": "a"})
        storage.append("test_items", {"id": 2, "name": "b"})
        storage.delete_by_id("test_items", 1)
        items = storage.load("test_items")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], 2)

    def test_clear(self):
        storage.append("test_items", {"id": 1, "name": "a"})
        storage.clear("test_items")
        items = storage.load("test_items")
        self.assertEqual(items, [])


if __name__ == "__main__":
    unittest.main()
