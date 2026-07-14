"""Tests for search and filter operations."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import storage
from ticket import create, search, filter_by, set_status, assign


class TestSearch(unittest.TestCase):
    def setUp(self):
        storage.DATA_DIR = storage.Path("data")
        storage.clear("tickets")

    def tearDown(self):
        storage.clear("tickets")

    def test_search_by_title(self):
        create("Login fails", "high", "bug", "Cannot login", 1)
        create("Export CSV", "low", "feature", "Export data", 1)
        results = search("Login")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Login fails")

    def test_search_by_description(self):
        create("Task 1", "low", "task", "Implement dark mode", 1)
        create("Task 2", "medium", "task", "Fix light mode", 1)
        results = search("dark mode")
        self.assertEqual(len(results), 1)

    def test_search_case_sensitive(self):
        create("BUG", "high", "bug", "critical issue", 1)
        results = search("bug")
        self.assertEqual(len(results), 0)

    def test_search_no_match(self):
        create("Task", "low", "a", "desc", 1)
        results = search("nonexistent")
        self.assertEqual(results, [])

    def test_filter_by_category(self):
        create("T1", "low", "bug", "d", 1)
        create("T2", "low", "feature", "d", 1)
        create("T3", "low", "bug", "d", 1)
        results = filter_by("category", "bug")
        self.assertEqual(len(results), 2)

    def test_filter_by_assignee(self):
        create("T1", "low", "a", "d", 1)
        t2 = create("T2", "low", "a", "d", 1)
        assign(t2["id"], 99)
        results = filter_by("assignee_id", "99")
        self.assertEqual(len(results), 1)

    def test_filter_by_status_open(self):
        create("T1", "low", "a", "d", 1)
        t2 = create("T2", "low", "a", "d", 1)
        set_status(t2["id"], "resolved")
        results = filter_by("status", "open")
        self.assertEqual(len(results), 1)

    def test_filter_no_match(self):
        create("T1", "low", "a", "d", 1)
        results = filter_by("category", "nonexistent")
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
