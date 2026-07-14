"""Tests for conditions module."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from apps.workflow_engine_py import conditions


class TestConditions(unittest.TestCase):
    def test_data_has_key(self):
        instance = {"data": {"amount": "500"}}
        self.assertTrue(conditions.evaluate("data_has_key:amount", instance))

    def test_data_has_key_missing(self):
        instance = {"data": {"amount": "500"}}
        self.assertFalse(conditions.evaluate("data_has_key:description", instance))

    def test_data_equals(self):
        instance = {"data": {"status": "active"}}
        self.assertTrue(conditions.evaluate("data_equals:status:active", instance))

    def test_data_equals_wrong(self):
        instance = {"data": {"status": "active"}}
        self.assertFalse(conditions.evaluate("data_equals:status:inactive", instance))

    def test_data_not_empty(self):
        instance = {"data": {"name": "John"}}
        self.assertTrue(conditions.evaluate("data_not_empty:name", instance))

    def test_data_not_empty_empty(self):
        instance = {"data": {"name": ""}}
        self.assertFalse(conditions.evaluate("data_not_empty:name", instance))

    def test_created_by(self):
        instance = {"data": {}, "created_by": 1}
        self.assertTrue(conditions.evaluate("created_by:admin", instance))

    def test_check_all_pass(self):
        instance = {"data": {"amount": "500", "name": "John"}}
        result = conditions.check(["data_has_key:amount", "data_not_empty:name"], instance)
        self.assertTrue(result)

    def test_check_one_fails(self):
        instance = {"data": {"amount": "500"}}
        result = conditions.check(["data_has_key:amount", "data_has_key:name"], instance)
        self.assertFalse(result)

    def test_check_empty_conditions(self):
        instance = {"data": {}}
        result = conditions.check([], instance)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
