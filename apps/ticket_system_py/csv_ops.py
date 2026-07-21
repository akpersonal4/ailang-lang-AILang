"""CSV import/export for tickets."""

import csv
from pathlib import Path

import ticket as ticket_mod
from storage import append, next_id


def export_tickets(filename: str) -> bool:
    tickets = ticket_mod.list_all()
    if not tickets:
        return False
    fields = [
        "id",
        "title",
        "description",
        "status",
        "priority",
        "creator_id",
        "assignee_id",
        "category",
        "created_at",
        "updated_at",
        "resolved_at",
    ]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(tickets)
    return True


def import_tickets(filename: str) -> int:
    path = Path(filename)
    if not path.exists():
        return 0
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        imported = 0
        for row in reader:
            ticket = {
                "id": next_id("tickets"),
                "title": row.get("title", ""),
                "description": row.get("description", ""),
                "status": row.get("status", "open"),
                "priority": row.get("priority", "low"),
                "creator_id": int(row.get("creator_id", 0)),
                "assignee_id": int(row.get("assignee_id", 0)),
                "category": row.get("category", ""),
                "created_at": int(row.get("created_at", 0)),
                "updated_at": int(row.get("updated_at", 0)),
                "resolved_at": int(row.get("resolved_at", 0)),
            }
            append("tickets", ticket)
            imported += 1
        return imported
