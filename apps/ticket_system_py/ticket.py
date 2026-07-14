"""Ticket model with CRUD, status transitions, search, and escalation."""

import time
from typing import Optional

import storage
from storage import load, append, update_field, delete_by_id, next_id


def create(title: str, priority: str, category: str, description: str, creator_id: int) -> dict:
    ticket = {
        "id": next_id("tickets"),
        "title": title,
        "description": description,
        "status": "open",
        "priority": priority,
        "creator_id": creator_id,
        "assignee_id": 0,
        "category": category,
        "created_at": int(time.time()),
        "updated_at": int(time.time()),
        "resolved_at": 0,
    }
    append("tickets", ticket)
    return ticket


def find_by_id(ticket_id: int) -> Optional[dict]:
    return storage.find_by_id("tickets", ticket_id)


def update(ticket_id: int, field: str, value) -> bool:
    return update_field("tickets", ticket_id, field, value)


def assign(ticket_id: int, assignee_id: int) -> bool:
    return update_field("tickets", ticket_id, "assignee_id", assignee_id)


def set_status(ticket_id: int, status: str) -> bool:
    updated = update_field("tickets", ticket_id, "status", status)
    if updated and status == "resolved":
        update_field("tickets", ticket_id, "resolved_at", int(time.time()))
    return updated


def list_all() -> list[dict]:
    return load("tickets")


def list_by_user(user_id: int) -> list[dict]:
    tickets = load("tickets")
    return [t for t in tickets if t.get("assignee_id") == user_id]


def search(query: str) -> list[dict]:
    tickets = load("tickets")
    return [
        t for t in tickets
        if query in t.get("title", "") or query in t.get("description", "")
    ]


def filter_by(field: str, value: str) -> list[dict]:
    tickets = load("tickets")
    return [t for t in tickets if str(t.get(field, "")) == value]


def delete(ticket_id: int) -> bool:
    return delete_by_id("tickets", ticket_id)


def count_by_status() -> dict:
    tickets = load("tickets")
    counts = {"open": 0, "in_progress": 0, "resolved": 0, "closed": 0}
    for t in tickets:
        status = t.get("status", "open")
        if status in counts:
            counts[status] += 1
    return counts


def count_by_priority() -> dict:
    tickets = load("tickets")
    counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for t in tickets:
        priority = t.get("priority", "low")
        if priority in counts:
            counts[priority] += 1
    return counts


def count_by_agent() -> dict:
    tickets = load("tickets")
    counts: dict[str, int] = {}
    for t in tickets:
        aid = str(t.get("assignee_id", 0))
        counts[aid] = counts.get(aid, 0) + 1
    return counts


def escalate_sla() -> int:
    from audit_log import add as audit_add
    tickets = load("tickets")
    now = int(time.time())
    escalated = 0
    for t in tickets:
        status = t["status"]
        priority = t["priority"]
        age = now - t["created_at"]
        if status not in ("resolved", "closed"):
            should_escalate = False
            if priority == "critical" and age > 14400:
                should_escalate = True
            if priority == "high" and age > 86400:
                should_escalate = True
            if should_escalate:
                update_field("tickets", t["id"], "priority", "critical")
                audit_add(t["id"], 0, "sla_escalated", priority, "critical")
                escalated += 1
    return escalated


def escalate_unassigned() -> int:
    from audit_log import add as audit_add
    tickets = load("tickets")
    now = int(time.time())
    escalated = 0
    for t in tickets:
        if (t["priority"] == "critical"
                and t["assignee_id"] == 0
                and (now - t["created_at"]) > 1800):
            audit_add(t["id"], 0, "unassigned_critical", "", "needs_assignment")
            escalated += 1
    return escalated
