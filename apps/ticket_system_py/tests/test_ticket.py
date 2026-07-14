"""Tests for ticket model."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import storage
import ticket
from ticket import (
    create, find_by_id, update, assign, set_status,
    list_all, list_by_user, search, filter_by, delete,
    count_by_status, count_by_priority, count_by_agent,
)
import audit_log


class TestTicket(unittest.TestCase):
    def setUp(self):
        storage.DATA_DIR = storage.Path("data")
        storage.clear("tickets")
        storage.clear("audit_log")

    def tearDown(self):
        storage.clear("tickets")
        storage.clear("audit_log")

    def test_create_ticket(self):
        t = create("Bug", "high", "bug", "Fix this", 1)
        self.assertIsNotNone(t)
        self.assertEqual(t["title"], "Bug")
        self.assertEqual(t["status"], "open")
        self.assertEqual(t["priority"], "high")
        self.assertEqual(t["creator_id"], 1)

    def test_find_by_id(self):
        t = create("Task", "low", "task", "Do it", 1)
        found = find_by_id(t["id"])
        self.assertIsNotNone(found)
        self.assertEqual(found["title"], "Task")

    def test_find_by_id_not_found(self):
        result = find_by_id(999999)
        self.assertIsNone(result)

    def test_update_ticket(self):
        t = create("UpdateMe", "medium", "feature", "desc", 1)
        result = update(t["id"], "title", "Updated")
        self.assertTrue(result)
        found = find_by_id(t["id"])
        self.assertEqual(found["title"], "Updated")

    def test_assign_ticket(self):
        t = create("Assign", "high", "bug", "desc", 1)
        result = assign(t["id"], 42)
        self.assertTrue(result)
        found = find_by_id(t["id"])
        self.assertEqual(found["assignee_id"], 42)

    def test_set_status_resolved(self):
        t = create("Resolve", "medium", "task", "desc", 1)
        result = set_status(t["id"], "resolved")
        self.assertTrue(result)
        found = find_by_id(t["id"])
        self.assertEqual(found["status"], "resolved")
        self.assertGreater(found["resolved_at"], 0)

    def test_set_status_closed(self):
        t = create("Close", "low", "task", "desc", 1)
        set_status(t["id"], "closed")
        found = find_by_id(t["id"])
        self.assertEqual(found["status"], "closed")

    def test_list_all(self):
        create("T1", "low", "a", "d", 1)
        create("T2", "high", "b", "d", 1)
        tickets = list_all()
        self.assertEqual(len(tickets), 2)

    def test_list_by_user(self):
        t1 = create("T1", "low", "a", "d", 1)
        t2 = create("T2", "low", "a", "d", 2)
        t3 = create("T3", "low", "a", "d", 1)
        assign(t1["id"], 1)
        assign(t3["id"], 1)
        results = list_by_user(1)
        self.assertEqual(len(results), 2)

    def test_search_tickets(self):
        create("Login bug", "high", "bug", "Login fails", 1)
        create("Logout bug", "medium", "bug", "Logout broken", 1)
        create("Feature", "low", "task", "Add dark mode", 1)
        results = search("bug")
        self.assertEqual(len(results), 2)

    def test_search_no_results(self):
        create("Task", "low", "a", "desc", 1)
        results = search("nonexistent")
        self.assertEqual(len(results), 0)

    def test_filter_by_status(self):
        create("T1", "low", "a", "d", 1)
        t2 = create("T2", "low", "a", "d", 1)
        set_status(t2["id"], "resolved")
        results = filter_by("status", "resolved")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "T2")

    def test_filter_by_priority(self):
        create("T1", "high", "a", "d", 1)
        create("T2", "low", "a", "d", 1)
        results = filter_by("priority", "high")
        self.assertEqual(len(results), 1)

    def test_delete_ticket(self):
        t = create("Delete", "low", "a", "d", 1)
        result = delete(t["id"])
        self.assertTrue(result)
        found = find_by_id(t["id"])
        self.assertIsNone(found)

    def test_count_by_status(self):
        create("T1", "low", "a", "d", 1)
        t2 = create("T2", "low", "a", "d", 1)
        t3 = create("T3", "low", "a", "d", 1)
        set_status(t2["id"], "resolved")
        set_status(t3["id"], "closed")
        counts = count_by_status()
        self.assertEqual(counts["open"], 1)
        self.assertEqual(counts["resolved"], 1)
        self.assertEqual(counts["closed"], 1)

    def test_count_by_priority(self):
        create("T1", "high", "a", "d", 1)
        create("T2", "critical", "a", "d", 1)
        create("T3", "low", "a", "d", 1)
        counts = count_by_priority()
        self.assertEqual(counts["high"], 1)
        self.assertEqual(counts["critical"], 1)
        self.assertEqual(counts["low"], 1)

    def test_count_by_agent(self):
        create("T1", "low", "a", "d", 1)
        t2 = create("T2", "low", "a", "d", 1)
        t3 = create("T3", "low", "a", "d", 1)
        assign(t2["id"], 10)
        assign(t3["id"], 10)
        counts = count_by_agent()
        self.assertEqual(counts.get("0", 0), 1)
        self.assertEqual(counts.get("10", 0), 2)


if __name__ == "__main__":
    unittest.main()
