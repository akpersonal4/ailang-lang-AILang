"""Tests for comment model."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

import storage
from comment import count_by_ticket, create, list_by_ticket


class TestComment(unittest.TestCase):
    def setUp(self):
        storage.DATA_DIR = storage.Path("data")
        storage.clear("comments")

    def tearDown(self):
        storage.clear("comments")

    def test_create_comment(self):
        c = create(1, 10, "This is a comment")
        self.assertIsNotNone(c)
        self.assertEqual(c["ticket_id"], 1)
        self.assertEqual(c["author_id"], 10)
        self.assertEqual(c["content"], "This is a comment")

    def test_list_by_ticket(self):
        create(1, 10, "Comment A")
        create(1, 20, "Comment B")
        create(2, 10, "Comment C")
        results = list_by_ticket(1)
        self.assertEqual(len(results), 2)

    def test_list_by_ticket_empty(self):
        results = list_by_ticket(999)
        self.assertEqual(results, [])

    def test_count_by_ticket(self):
        create(5, 10, "A")
        create(5, 20, "B")
        create(5, 30, "C")
        count = count_by_ticket(5)
        self.assertEqual(count, 3)

    def test_count_by_ticket_empty(self):
        count = count_by_ticket(999)
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
