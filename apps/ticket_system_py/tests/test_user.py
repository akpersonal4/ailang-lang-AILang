"""Tests for user model."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import storage
import user
from user import create, find_by_username, authenticate, set_role, list_all, has_permission, has_permission_on_ticket


class TestUser(unittest.TestCase):
    def setUp(self):
        storage.DATA_DIR = storage.Path("data")
        storage.clear("users")
        storage.clear("tickets")

    def tearDown(self):
        storage.clear("users")
        storage.clear("tickets")

    def test_create_first_user_is_admin(self):
        u = create("admin1", "admin@test.com", "pass123")
        self.assertIsNotNone(u)
        self.assertEqual(u["role"], "admin")

    def test_create_subsequent_user_is_agent(self):
        create("admin1", "a@test.com", "pass")
        u2 = create("agent1", "b@test.com", "pass")
        self.assertIsNotNone(u2)
        self.assertEqual(u2["role"], "agent")

    def test_create_duplicate_username_returns_none(self):
        create("u1", "a@test.com", "pass")
        result = create("u1", "b@test.com", "pass")
        self.assertIsNone(result)

    def test_create_duplicate_email_returns_none(self):
        create("u1", "shared@test.com", "pass")
        result = create("u2", "shared@test.com", "pass")
        self.assertIsNone(result)

    def test_find_by_username(self):
        create("lookup", "l@test.com", "pass")
        found = find_by_username("lookup")
        self.assertIsNotNone(found)
        self.assertEqual(found["username"], "lookup")

    def test_find_by_username_not_found(self):
        result = find_by_username("nonexistent")
        self.assertIsNone(result)

    def test_authenticate_success(self):
        create("authuser", "auth@test.com", "correctpass")
        u = authenticate("authuser", "correctpass")
        self.assertIsNotNone(u)
        self.assertEqual(u["username"], "authuser")

    def test_authenticate_wrong_password(self):
        create("authuser2", "auth2@test.com", "wrongpass")
        result = authenticate("authuser2", "badpassword")
        self.assertIsNone(result)

    def test_authenticate_nonexistent_user(self):
        result = authenticate("ghost", "pass")
        self.assertIsNone(result)

    def test_set_role(self):
        u = create("roleuser", "role@test.com", "pass")
        result = set_role(u["id"], "manager")
        self.assertTrue(result)
        found = find_by_username("roleuser")
        self.assertEqual(found["role"], "manager")

    def test_list_all(self):
        create("u1", "a@test.com", "pass")
        create("u2", "b@test.com", "pass")
        users = list_all()
        self.assertEqual(len(users), 2)

    def test_has_permission_admin(self):
        u = create("adminp", "adm@test.com", "pass")
        self.assertTrue(has_permission(u["id"], "manage_users"))
        self.assertTrue(has_permission(u["id"], "delete_ticket"))

    def test_has_permission_agent_cannot_manage_users(self):
        create("adminx", "ax@test.com", "pass")
        u2 = create("agentx", "ag@test.com", "pass")
        self.assertFalse(has_permission(u2["id"], "manage_users"))
        self.assertFalse(has_permission(u2["id"], "delete_ticket"))

    def test_has_permission_agent_can_create_ticket(self):
        create("adminy", "ay@test.com", "pass")
        u2 = create("agenta", "aa@test.com", "pass")
        self.assertTrue(has_permission(u2["id"], "create_ticket"))

    def test_has_permission_viewer_read_only(self):
        create("adminz", "az@test.com", "pass")
        u2 = create("viewr", "vr@test.com", "pass")
        set_role(u2["id"], "viewer")
        self.assertTrue(has_permission(u2["id"], "view_ticket"))
        self.assertFalse(has_permission(u2["id"], "create_ticket"))

    def test_has_permission_on_ticket_creator_can_update_own(self):
        u = create("creator", "cr@test.com", "pass")
        t = {"id": 1, "creator_id": u["id"], "status": "open"}
        self.assertTrue(has_permission_on_ticket(u["id"], "update_own_ticket", t))

    def test_has_permission_on_ticket_other_cannot_update_own(self):
        u1 = create("c1", "c1@test.com", "pass")
        create("c2", "c2@test.com", "pass")
        u2 = find_by_username("c2")
        t = {"id": 1, "creator_id": u1["id"], "status": "open"}
        self.assertFalse(has_permission_on_ticket(u2["id"], "update_own_ticket", t))


if __name__ == "__main__":
    unittest.main()
