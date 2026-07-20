from core.helpers import helpers_current_timestamp
from core.storage import storage_get_by_id, storage_update


def ti_approve_transfer(transfer_id):
    found = storage_get_by_id("transfers", transfer_id)
    if found is False:
        return False
    if found.get("status") != "pending_approval":
        return False
    return storage_update(
        "transfers",
        transfer_id,
        {
            "status": "pending",
            "approved_at": helpers_current_timestamp(),
        },
    )


def ti_reject_transfer(transfer_id):
    found = storage_get_by_id("transfers", transfer_id)
    if found is False:
        return False
    if found.get("status") != "pending_approval":
        return False
    return storage_update(
        "transfers",
        transfer_id,
        {
            "status": "rejected",
            "rejected_at": helpers_current_timestamp(),
        },
    )
