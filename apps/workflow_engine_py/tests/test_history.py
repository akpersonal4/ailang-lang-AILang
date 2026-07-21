"""Tests for history module."""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from apps.workflow_engine_py import history, storage


class TestHistory(unittest.TestCase):
    def setUp(self):
        storage.clear("history")

    def test_add(self):
        entry = history.add(1, "a", "b", 1, "moved")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["from_state"], "a")
        self.assertEqual(entry["to_state"], "b")
        self.assertEqual(entry["notes"], "moved")

    def test_list_by_instance(self):
        history.add(1, "a", "b", 1, "note1")
        history.add(1, "b", "c", 1, "note2")
        history.add(2, "x", "y", 2, "note3")
        entries = history.list_by_instance(1)
        self.assertEqual(len(entries), 2)

    def test_list_all(self):
        history.add(1, "a", "b", 1, "note1")
        history.add(2, "x", "y", 2, "note2")
        entries = history.list_all()
        self.assertEqual(len(entries), 2)


if __name__ == "__main__":
    unittest.main()
