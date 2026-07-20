"""Tests for permissions system."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

import storage
from user import create, has_permission, has_permission_on_ticket, set_role


class TestPermissions(unittest.TestCase):
    def setUp(self):
        storage.DATA_DIR = storage.Path("data")
        storage.clear("users")
        storage.clear("tickets")

    def tearDown(self):
        storage.clear("users")
        storage.clear("tickets")

    def _setup_roles(self):
        admin = create("admin", "admin@perm.com", "pass")
        manager = create("manager", "mgr@perm.com", "pass")
        agent = create("agent", "ag@perm.com", "pass")
        viewer = create("viewer", "vw@perm.com", "pass")
        set_role(manager["id"], "manager")
        set_role(viewer["id"], "viewer")
        return admin, manager, agent, viewer

    def test_admin_full_permissions(self):
        admin, _, _, _ = self._setup_roles()
        for action in [
            "create_ticket",
            "update_own_ticket",
            "update_any_ticket",
            "assign_ticket",
            "resolve_ticket",
            "close_ticket",
            "reopen_ticket",
            "add_comment",
            "view_ticket",
            "search_tickets",
            "view_reports",
            "export_csv",
            "import_csv",
            "delete_ticket",
            "manage_users",
        ]:
            self.assertTrue(
                has_permission(admin["id"], action), f"Admin lacks {action}"
            )

    def test_manager_can_manage_tickets(self):
        _, manager, _, _ = self._setup_roles()
        self.assertTrue(has_permission(manager["id"], "create_ticket"))
        self.assertTrue(has_permission(manager["id"], "assign_ticket"))
        self.assertTrue(has_permission(manager["id"], "view_reports"))
        self.assertFalse(has_permission(manager["id"], "manage_users"))

    def test_agent_limited_permissions(self):
        _, _, agent, _ = self._setup_roles()
        self.assertTrue(has_permission(agent["id"], "create_ticket"))
        self.assertTrue(has_permission(agent["id"], "add_comment"))
        self.assertFalse(has_permission(agent["id"], "assign_ticket"))
        self.assertFalse(has_permission(agent["id"], "manage_users"))
        self.assertFalse(has_permission(agent["id"], "delete_ticket"))

    def test_viewer_read_only(self):
        _, _, _, viewer = self._setup_roles()
        self.assertTrue(has_permission(viewer["id"], "view_ticket"))
        self.assertTrue(has_permission(viewer["id"], "search_tickets"))
        self.assertFalse(has_permission(viewer["id"], "create_ticket"))
        self.assertFalse(has_permission(viewer["id"], "add_comment"))

    def test_manager_can_update_any_ticket(self):
        _, manager, agent, _ = self._setup_roles()
        ticket = {"id": 1, "creator_id": agent["id"]}
        self.assertTrue(
            has_permission_on_ticket(manager["id"], "update_own_ticket", ticket)
        )

    def test_agent_cannot_update_other_ticket(self):
        _, _, agent, viewer = self._setup_roles()
        ticket = {"id": 1, "creator_id": viewer["id"]}
        self.assertFalse(
            has_permission_on_ticket(agent["id"], "update_own_ticket", ticket)
        )


if __name__ == "__main__":
    unittest.main()
