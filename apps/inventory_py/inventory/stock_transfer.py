from core.helpers import (
    helpers_generate_id,
    helpers_current_timestamp,
    helpers_get_map_value_safe,
)
from core.storage import storage_add, storage_list, storage_get_by_id, storage_save
from inventory.stock_movement import movement_create


def transfer_create(prod_id, source, dest, qty, status="pending"):
    transfer = {
        "id": helpers_generate_id("TRF-"),
        "product_id": prod_id,
        "source_location": source,
        "destination_location": dest,
        "quantity": qty,
        "status": status,
        "created_at": helpers_current_timestamp(),
        "completed_at": "",
    }
    storage_add("transfers", transfer)
    return transfer


def transfer_get(trf_id):
    return storage_get_by_id("transfers", trf_id)


def transfer_update_status(transfer_id, new_status):
    items = storage_list("transfers")
    for item in items:
        if helpers_get_map_value_safe(item, "id", "") == transfer_id:
            item["status"] = new_status
            break
    return storage_save("transfers", items)


def transfer_complete(tcmp_id):
    tcmp_transfer = transfer_get(tcmp_id)
    if tcmp_transfer is False:
        return False
    tcmp_status = helpers_get_map_value_safe(tcmp_transfer, "status", "")
    if tcmp_status != "pending":
        return False
    items = storage_list("transfers")
    for item in items:
        if helpers_get_map_value_safe(item, "id", "") == tcmp_id:
            now = helpers_current_timestamp()
            item["status"] = "completed"
            item["completed_at"] = now
            product_id = helpers_get_map_value_safe(item, "product_id", "")
            source = helpers_get_map_value_safe(item, "source_location", "")
            dest = helpers_get_map_value_safe(item, "destination_location", "")
            qty = helpers_get_map_value_safe(item, "quantity", 0)
            out_qty = 0 - qty
            movement_create(product_id, "transfer_out", out_qty, "transfer", tcmp_id, "Transfer out from " + source)
            movement_create(product_id, "transfer_in", qty, "transfer", tcmp_id, "Transfer in to " + dest)
            break
    storage_save("transfers", items)
    return storage_get_by_id("transfers", tcmp_id)


def transfer_cancel(tcnc_id):
    items = storage_list("transfers")
    for item in items:
        if helpers_get_map_value_safe(item, "id", "") == tcnc_id:
            item["status"] = "cancelled"
            break
    return storage_save("transfers", items)


def transfer_list():
    return storage_list("transfers")


def transfer_list_pending():
    items = storage_list("transfers")
    results = []
    for item in items:
        if helpers_get_map_value_safe(item, "status", "") == "pending":
            results.append(item)
    return results
