"""Integration tests for workflow engine."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from apps.workflow_engine_py import storage
from apps.workflow_engine_py import user
from apps.workflow_engine_py import workflow_def
from apps.workflow_engine_py import instance
from apps.workflow_engine_py import history
from apps.workflow_engine_py import conditions


class TestIntegration(unittest.TestCase):
    def setUp(self):
        storage.clear("users")
        storage.clear("workflow_defs")
        storage.clear("instances")
        storage.clear("history")
        self.admin = user.create("admin", "admin@test.com", "pass")

    def test_full_lifecycle(self):
        defn = workflow_def.create_with_data(
            "Expense", "Approval workflow",
            ["draft", "submitted", "approved"],
            "draft",
            [
                {"from_state": "draft", "to_state": "submitted", "action": "submit", "conditions": [], "required_role": "operator"},
                {"from_state": "submitted", "to_state": "approved", "action": "approve", "conditions": ["data_has_key:amount"], "required_role": "operator"},
            ]
        )
        inst = instance.create(defn["id"], self.admin["id"], '{"amount": "500"}')
        self.assertEqual(inst["current_state"], "draft")
        result = instance.transition(inst["id"], "submit", self.admin["id"], "")
        self.assertEqual(result["current_state"], "submitted")
        result2 = instance.transition(inst["id"], "approve", self.admin["id"], "Looks good")
        self.assertEqual(result2["current_state"], "approved")
        h = history.list_by_instance(inst["id"])
        self.assertGreaterEqual(len(h), 2)

    def test_condition_blocks_transition(self):
        defn = workflow_def.create_with_data(
            "Test", "Test",
            ["a", "b"],
            "a",
            [{"from_state": "a", "to_state": "b", "action": "go", "conditions": ["data_has_key:required"], "required_role": "operator"}]
        )
        inst = instance.create(defn["id"], self.admin["id"], '{}')
        result = instance.transition(inst["id"], "go", self.admin["id"], "")
        self.assertEqual(result["error"], "conditions_not_met")
        instance.set_data(inst["id"], "required", "yes")
        result2 = instance.transition(inst["id"], "go", self.admin["id"], "")
        self.assertNotIn("error", result2)
        self.assertEqual(result2["current_state"], "b")

    def test_workflow_delete_no_instances(self):
        defn = workflow_def.create_with_data("Test", "desc", ["a"], "a", [])
        result = workflow_def.delete(defn["id"])
        self.assertTrue(result)

    def test_workflow_delete_with_instances(self):
        defn = workflow_def.create_with_data("Test", "desc", ["a", "b"], "a", [])
        instance.create(defn["id"], self.admin["id"], '{}')
        result = workflow_def.delete(defn["id"])
        self.assertFalse(result)

    def test_report_workflow(self):
        defn = workflow_def.create_with_data("Test", "desc", ["a", "b", "c"], "a", [
            {"from_state": "a", "to_state": "b", "action": "go", "conditions": [], "required_role": "operator"},
        ])
        instance.create(defn["id"], self.admin["id"], '{}')
        inst2 = instance.create(defn["id"], self.admin["id"], '{}')
        instance.transition(inst2["id"], "go", self.admin["id"], "")
        counts = instance.report_workflow(defn["id"])
        self.assertEqual(counts["a"], 1)
        self.assertEqual(counts["b"], 1)

    def test_export_import_roundtrip(self):
        workflow_def.create_with_data("A", "desc1", ["x", "y"], "x", [])
        workflow_def.create_with_data("B", "desc2", ["p", "q"], "p", [])
        data = workflow_def.export()
        storage.clear("workflow_defs")
        count = workflow_def.import_workflows(data)
        self.assertEqual(count, 2)
        all_defs = workflow_def.list_all()
        self.assertEqual(len(all_defs), 2)

    def test_cancel_instance(self):
        defn = workflow_def.create_with_data("Test", "desc", ["a", "b"], "a", [
            {"from_state": "a", "to_state": "b", "action": "go", "conditions": [], "required_role": "operator"},
        ])
        inst = instance.create(defn["id"], self.admin["id"], '{}')
        result = instance.cancel(inst["id"], self.admin["id"], "cancelled")
        self.assertTrue(result)
        found = instance.find_by_id(inst["id"])
        self.assertEqual(found["current_state"], "cancelled")


if __name__ == "__main__":
    unittest.main()
