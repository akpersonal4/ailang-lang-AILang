"""Tests for user module."""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from apps.workflow_engine_py import storage, user


class TestUser(unittest.TestCase):
    def setUp(self):
        storage.clear("users")

    def test_create_first_admin(self):
        result = user.create("admin", "admin@test.com", "pass123")
        self.assertIsNotNone(result)
        self.assertEqual(result["role"], "admin")
        self.assertEqual(result["username"], "admin")

    def test_create_subsequent_operator(self):
        user.create("admin", "admin@test.com", "pass123")
        result = user.create("operator1", "op@test.com", "pass456")
        self.assertIsNotNone(result)
        self.assertEqual(result["role"], "operator")

    def test_create_duplicate(self):
        user.create("admin", "admin@test.com", "pass123")
        result = user.create("admin", "other@test.com", "pass")
        self.assertFalse(result)

    def test_create_duplicate_email(self):
        user.create("admin", "admin@test.com", "pass123")
        result = user.create("other", "admin@test.com", "pass")
        self.assertFalse(result)

    def test_find_by_username(self):
        user.create("admin", "admin@test.com", "pass123")
        result = user.find_by_username("admin")
        self.assertIsNotNone(result)
        self.assertEqual(result["email"], "admin@test.com")

    def test_find_by_username_not_found(self):
        result = user.find_by_username("nobody")
        self.assertFalse(result)

    def test_authenticate(self):
        user.create("admin", "admin@test.com", "pass123")
        result = user.authenticate("admin", "pass123")
        self.assertIsNotNone(result)
        self.assertEqual(result["username"], "admin")

    def test_authenticate_wrong_password(self):
        user.create("admin", "admin@test.com", "pass123")
        result = user.authenticate("admin", "wrong")
        self.assertFalse(result)

    def test_has_permission(self):
        user.create("admin", "admin@test.com", "pass123")
        self.assertTrue(user.has_permission(1, "create_workflow"))
        self.assertTrue(user.has_permission(1, "delete_workflow"))

    def test_operator_permissions(self):
        user.create("admin", "a@a.com", "pass")
        op = user.create("op1", "b@b.com", "pass")
        self.assertFalse(user.has_permission(op["id"], "create_workflow"))
        self.assertTrue(user.has_permission(op["id"], "view_workflow"))

    def test_viewer_permissions(self):
        user.create("admin", "a@a.com", "pass")
        vw = user.create("viewer1", "c@c.com", "pass")
        user.set_role(vw["id"], "viewer")
        self.assertFalse(user.has_permission(vw["id"], "create_instance"))
        self.assertTrue(user.has_permission(vw["id"], "view_instance"))


if __name__ == "__main__":
    unittest.main()
