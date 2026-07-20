"""Tests for workflow_def module."""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from apps.workflow_engine_py import storage, workflow_def


class TestWorkflowDef(unittest.TestCase):
    def setUp(self):
        storage.clear("workflow_defs")
        storage.clear("instances")

    def test_create(self):
        result = workflow_def.create(
            "Approval", "Simple approval", '["pending","approved","rejected"]', "[]"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Approval")
        self.assertEqual(result["initial_state"], "pending")

    def test_create_duplicate(self):
        workflow_def.create("Approval", "desc", '["a","b"]', "[]")
        result = workflow_def.create("Approval", "desc2", '["c","d"]', "[]")
        self.assertFalse(result)

    def test_find_by_name(self):
        workflow_def.create("Approval", "desc", '["a"]', "[]")
        result = workflow_def.find_by_name("Approval")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Approval")

    def test_find_by_id(self):
        defn = workflow_def.create("Approval", "desc", '["a"]', "[]")
        result = workflow_def.find_by_id(defn["id"])
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Approval")

    def test_list_all(self):
        workflow_def.create("A", "desc1", '["a"]', "[]")
        workflow_def.create("B", "desc2", '["b"]', "[]")
        all_defs = workflow_def.list_all()
        self.assertEqual(len(all_defs), 2)

    def test_delete_no_instances(self):
        defn = workflow_def.create("A", "desc", '["a"]', "[]")
        result = workflow_def.delete(defn["id"])
        self.assertTrue(result)
        self.assertFalse(workflow_def.find_by_id(defn["id"]))

    def test_delete_has_instances(self):
        from apps.workflow_engine_py import instance

        defn = workflow_def.create("A", "desc", '["a","b"]', "[]")
        instance.create(defn["id"], 1, "{}")
        result = workflow_def.delete(defn["id"])
        self.assertFalse(result)

    def test_validate_transition(self):
        transitions = [
            {
                "from_state": "a",
                "to_state": "b",
                "action": "go",
                "conditions": [],
                "required_role": "operator",
            }
        ]
        defn = workflow_def.create_with_data(
            "Test", "desc", ["a", "b"], "a", transitions
        )
        result = workflow_def.validate_transition(defn["id"], "a", "go")
        self.assertIsNotNone(result)
        self.assertEqual(result["to_state"], "b")

    def test_validate_transition_wrong_from(self):
        transitions = [
            {
                "from_state": "a",
                "to_state": "b",
                "action": "go",
                "conditions": [],
                "required_role": "operator",
            }
        ]
        defn = workflow_def.create_with_data(
            "Test", "desc", ["a", "b"], "a", transitions
        )
        result = workflow_def.validate_transition(defn["id"], "b", "go")
        self.assertFalse(result)

    def test_export_import(self):
        workflow_def.create("A", "desc", '["a","b"]', "[]")
        data = workflow_def.export()
        storage.clear("workflow_defs")
        count = workflow_def.import_workflows(data)
        self.assertEqual(count, 1)
        all_defs = workflow_def.list_all()
        self.assertEqual(len(all_defs), 1)
        self.assertEqual(all_defs[0]["name"], "A")


if __name__ == "__main__":
    unittest.main()
