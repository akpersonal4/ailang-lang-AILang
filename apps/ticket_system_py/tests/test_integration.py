"""Integration tests for ticket system."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from pathlib import Path

import comment
import csv_ops
import storage
import ticket
from audit_log import add as audit_add
from audit_log import list_all as audit_list_all
from audit_log import list_by_ticket
from comment import count_by_ticket
from comment import create as create_comment
from ticket import (
    assign,
    count_by_priority,
    count_by_status,
    set_status,
)
from ticket import (
    create as create_ticket,
)
from user import create, set_role


class TestIntegration(unittest.TestCase):
    def setUp(self):
        storage.DATA_DIR = storage.Path("data")
        for name in ["users", "tickets", "comments", "audit_log"]:
            storage.clear(name)
        Path("data").mkdir(exist_ok=True)

    def tearDown(self):
        for name in ["users", "tickets", "comments", "audit_log"]:
            storage.clear(name)

    def test_full_ticket_lifecycle(self):
        admin = create("admin1", "a@test.com", "pass")
        agent = create("agent1", "b@test.com", "pass")
        set_role(agent["id"], "agent")

        t = create_ticket("Bug fix", "high", "bug", "Fix the crash", admin["id"])
        self.assertEqual(t["status"], "open")
        audit_add(t["id"], admin["id"], "created", "", "Bug fix")

        assign(t["id"], agent["id"])
        audit_add(t["id"], admin["id"], "assigned", "0", str(agent["id"]))
        set_status(t["id"], "in_progress")
        audit_add(t["id"], admin["id"], "status_changed", "open", "in_progress")

        create_comment(t["id"], agent["id"], "Working on this")
        create_comment(t["id"], admin["id"], "Thanks for the update")

        set_status(t["id"], "resolved")
        audit_add(t["id"], agent["id"], "status_changed", "in_progress", "resolved")
        set_status(t["id"], "closed")
        audit_add(t["id"], agent["id"], "status_changed", "resolved", "closed")

        final = ticket.find_by_id(t["id"])
        self.assertEqual(final["status"], "closed")
        self.assertEqual(final["assignee_id"], agent["id"])

        comments = comment.list_by_ticket(t["id"])
        self.assertEqual(len(comments), 2)

        audit_entries = list_by_ticket(t["id"])
        self.assertGreater(len(audit_entries), 0)

    def test_multiple_tickets_different_statuses(self):
        u = create("u1", "u@test.com", "pass")
        t1 = create_ticket("T1", "low", "a", "d", u["id"])
        t2 = create_ticket("T2", "high", "b", "d", u["id"])
        t3 = create_ticket("T3", "critical", "c", "d", u["id"])
        set_status(t2["id"], "resolved")
        set_status(t3["id"], "closed")

        counts = count_by_status()
        self.assertEqual(counts["open"], 1)
        self.assertEqual(counts["resolved"], 1)
        self.assertEqual(counts["closed"], 1)

    def test_ticket_counts_by_priority(self):
        u = create("u1", "u@test.com", "pass")
        create_ticket("T1", "low", "a", "d", u["id"])
        create_ticket("T2", "low", "a", "d", u["id"])
        create_ticket("T3", "high", "a", "d", u["id"])
        create_ticket("T4", "critical", "a", "d", u["id"])

        counts = count_by_priority()
        self.assertEqual(counts["low"], 2)
        self.assertEqual(counts["high"], 1)
        self.assertEqual(counts["critical"], 1)

    def test_comment_count_across_tickets(self):
        u = create("u1", "u@test.com", "pass")
        t1 = create_ticket("T1", "low", "a", "d", u["id"])
        t2 = create_ticket("T2", "low", "a", "d", u["id"])
        create_comment(t1["id"], u["id"], "Comment 1")
        create_comment(t1["id"], u["id"], "Comment 2")
        create_comment(t2["id"], u["id"], "Comment 3")

        self.assertEqual(count_by_ticket(t1["id"]), 2)
        self.assertEqual(count_by_ticket(t2["id"]), 1)

    def test_user_roles_affect_ticket_access(self):
        admin = create("admin", "a@test.com", "pass")
        viewer = create("viewer", "v@test.com", "pass")
        set_role(viewer["id"], "viewer")

        from user import has_permission

        self.assertTrue(has_permission(admin["id"], "create_ticket"))
        self.assertFalse(has_permission(viewer["id"], "create_ticket"))
        self.assertTrue(has_permission(viewer["id"], "view_ticket"))

    def test_csv_export_import(self):
        u = create("u1", "u@test.com", "pass")
        create_ticket("Export T1", "high", "bug", "desc1", u["id"])
        create_ticket("Export T2", "low", "feature", "desc2", u["id"])

        result = csv_ops.export_tickets("data/test_export.csv")
        self.assertTrue(result)
        self.assertTrue(Path("data/test_export.csv").exists())

        storage.clear("tickets")
        imported = csv_ops.import_tickets("data/test_export.csv")
        self.assertEqual(imported, 2)
        tickets = ticket.list_all()
        self.assertEqual(len(tickets), 2)

        Path("data/test_export.csv").unlink(missing_ok=True)

    def test_audit_log_records_all_mutations(self):
        u = create("u1", "u@test.com", "pass")
        t = create_ticket("Audit T1", "low", "a", "d", u["id"])
        audit_add(t["id"], u["id"], "created", "", "Audit T1")
        assign(t["id"], u["id"])
        audit_add(t["id"], u["id"], "assigned", "0", str(u["id"]))
        set_status(t["id"], "resolved")
        audit_add(t["id"], u["id"], "status_changed", "open", "resolved")
        create_comment(t["id"], u["id"], "Comment")
        audit_add(t["id"], u["id"], "commented", "", "Comment")

        entries = audit_list_all()
        self.assertGreater(len(entries), 0)
        actions = [e["action"] for e in entries]
        self.assertIn("created", actions)


if __name__ == "__main__":
    unittest.main()
