"""Audit log for tracking all mutations."""

import time

from storage import append, load, next_id


def add(
    ticket_id: int, user_id: int, action: str, old_value: str, new_value: str
) -> dict:
    entry = {
        "id": next_id("audit_log"),
        "ticket_id": ticket_id,
        "user_id": user_id,
        "action": action,
        "old_value": old_value,
        "new_value": new_value,
        "timestamp": int(time.time()),
    }
    append("audit_log", entry)
    return entry


def list_by_ticket(ticket_id: int) -> list[dict]:
    logs = load("audit_log")
    return [e for e in logs if e.get("ticket_id") == ticket_id]


def list_all() -> list[dict]:
    return load("audit_log")
