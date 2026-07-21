"""Tests for instance module."""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from apps.workflow_engine_py import instance, storage, workflow_def


class TestInstance(unittest.TestCase):
    def setUp(self):
        storage.clear("instances")
        storage.clear("workflow_defs")
        storage.clear("history")
        transitions = [
            {
                "from_state": "draft",
                "to_state": "submitted",
                "action": "submit",
                "conditions": [],
                "required_role": "operator",
            },
            {
                "from_state": "submitted",
                "to_state": "approved",
                "action": "approve",
                "conditions": [],
                "required_role": "operator",
            },
        ]
        self.defn = workflow_def.create_with_data(
            "Test", "desc", ["draft", "submitted", "approved"], "draft", transitions
        )

    def test_create(self):
        inst = instance.create(self.defn["id"], 1, "{}")
        self.assertIsNotNone(inst)
        self.assertEqual(inst["current_state"], "draft")
        self.assertEqual(inst["workflow_id"], self.defn["id"])

    def test_create_bad_workflow(self):
        result = instance.create(999, 1, "{}")
        self.assertFalse(result)

    def test_find_by_id(self):
        inst = instance.create(self.defn["id"], 1, "{}")
        found = instance.find_by_id(inst["id"])
        self.assertIsNotNone(found)
        self.assertEqual(found["current_state"], "draft")

    def test_transition(self):
        inst = instance.create(self.defn["id"], 1, "{}")
        result = instance.transition(inst["id"], "submit", 1, "")
        self.assertNotIn("error", result)
        self.assertEqual(result["current_state"], "submitted")

    def test_transition_invalid(self):
        inst = instance.create(self.defn["id"], 1, "{}")
        result = instance.transition(inst["id"], "approve", 1, "")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "invalid_transition")

    def test_list_by_workflow(self):
        instance.create(self.defn["id"], 1, "{}")
        instance.create(self.defn["id"], 1, "{}")
        result = instance.list_by_workflow(self.defn["id"])
        self.assertEqual(len(result), 2)

    def test_list_by_user(self):
        instance.create(self.defn["id"], 1, "{}")
        instance.create(self.defn["id"], 2, "{}")
        result = instance.list_by_user(1)
        self.assertEqual(len(result), 1)

    def test_set_data(self):
        inst = instance.create(self.defn["id"], 1, "{}")
        result = instance.set_data(inst["id"], "amount", "500")
        self.assertTrue(result)
        found = instance.find_by_id(inst["id"])
        self.assertEqual(found["data"]["amount"], "500")

    def test_cancel(self):
        inst = instance.create(self.defn["id"], 1, "{}")
        result = instance.cancel(inst["id"], 1, "no longer needed")
        self.assertTrue(result)
        found = instance.find_by_id(inst["id"])
        self.assertEqual(found["current_state"], "cancelled")

    def test_report_workflow(self):
        instance.create(self.defn["id"], 1, "{}")
        inst2 = instance.create(self.defn["id"], 1, "{}")
        instance.transition(inst2["id"], "submit", 1, "")
        counts = instance.report_workflow(self.defn["id"])
        self.assertEqual(counts["draft"], 1)
        self.assertEqual(counts["submitted"], 1)

    def test_report_activity(self):
        instance.create(self.defn["id"], 1, "{}")
        entries = instance.report_activity()
        self.assertGreater(len(entries), 0)


if __name__ == "__main__":
    unittest.main()
