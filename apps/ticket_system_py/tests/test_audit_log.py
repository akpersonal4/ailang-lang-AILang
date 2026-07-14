"""Tests for audit log."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import storage
from audit_log import add, list_by_ticket, list_all


class TestAuditLog(unittest.TestCase):
    def setUp(self):
        storage.DATA_DIR = storage.Path("data")
        storage.clear("audit_log")

    def tearDown(self):
        storage.clear("audit_log")

    def test_add_entry(self):
        entry = add(1, 10, "created", "", "Test ticket")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["ticket_id"], 1)
        self.assertEqual(entry["action"], "created")
        self.assertEqual(entry["old_value"], "")
        self.assertEqual(entry["new_value"], "Test ticket")

    def test_list_by_ticket(self):
        add(1, 10, "created", "", "Ticket 1")
        add(1, 20, "commented", "", "Comment on 1")
        add(2, 10, "created", "", "Ticket 2")
        results = list_by_ticket(1)
        self.assertEqual(len(results), 2)

    def test_list_by_ticket_empty(self):
        results = list_by_ticket(999)
        self.assertEqual(results, [])

    def test_list_all(self):
        add(1, 10, "created", "", "A")
        add(2, 20, "created", "", "B")
        entries = list_all()
        self.assertEqual(len(entries), 2)


if __name__ == "__main__":
    unittest.main()
