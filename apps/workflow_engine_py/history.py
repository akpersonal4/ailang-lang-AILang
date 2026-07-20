"""Instance history tracking."""

import time

from . import storage


def add(instance_id, from_state, to_state, performed_by, notes):
    entry = {
        "id": storage.next_id("history"),
        "instance_id": instance_id,
        "from_state": from_state,
        "to_state": to_state,
        "performed_by": performed_by,
        "notes": notes,
        "timestamp": int(time.time()),
    }
    storage.append("history", entry)
    return entry


def list_by_instance(instance_id):
    all_entries = storage.load("history")
    return [e for e in all_entries if e["instance_id"] == instance_id]


def list_all():
    return storage.load("history")
