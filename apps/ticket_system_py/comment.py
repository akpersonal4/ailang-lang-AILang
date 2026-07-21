"""Comment model for ticket discussions."""

import time

from storage import append, load, next_id


def create(ticket_id: int, author_id: int, content: str) -> dict:
    comment = {
        "id": next_id("comments"),
        "ticket_id": ticket_id,
        "author_id": author_id,
        "content": content,
        "created_at": int(time.time()),
    }
    append("comments", comment)
    return comment


def list_by_ticket(ticket_id: int) -> list[dict]:
    comments = load("comments")
    return [c for c in comments if c.get("ticket_id") == ticket_id]


def count_by_ticket(ticket_id: int) -> int:
    return len(list_by_ticket(ticket_id))
