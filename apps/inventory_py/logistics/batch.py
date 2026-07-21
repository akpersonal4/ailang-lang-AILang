from core.helpers import (
    helpers_current_timestamp,
    helpers_generate_id,
    helpers_get_map_value_safe,
)
from core.storage import storage_add, storage_get_by_id, storage_list, storage_update


def batch_date_to_int(bdt_date_str):
    bdt_parts = bdt_date_str.split("-")
    bdt_len = len(bdt_parts)
    if bdt_len < 3:
        return 0
    bdt_numeric = bdt_parts[0] + bdt_parts[1] + bdt_parts[2]
    return int(bdt_numeric)


def batch_list_by_product_rec(blpr_items, blpr_product_id, blpr_idx, blpr_acc):
    for blpr_item in blpr_items:
        blpr_item_product_id = helpers_get_map_value_safe(blpr_item, "product_id", "")
        if blpr_item_product_id == blpr_product_id:
            blpr_acc.append(blpr_item)
    return blpr_acc


def batch_get_expiring_before_rec(gebr_items, gebr_expiry_int, gebr_idx, gebr_acc):
    for gebr_item in gebr_items:
        gebr_item_expiry = helpers_get_map_value_safe(gebr_item, "expiry_date", "")
        gebr_item_expiry_int = batch_date_to_int(gebr_item_expiry)
        if gebr_item_expiry_int < gebr_expiry_int:
            gebr_acc.append(gebr_item)
    return gebr_acc


def batch_get_active_by_product_rec(
    gabpr_items, gabpr_product_id, gabpr_idx, gabpr_acc
):
    for gabpr_item in gabpr_items:
        gabpr_item_product_id = helpers_get_map_value_safe(gabpr_item, "product_id", "")
        gabpr_item_qty = helpers_get_map_value_safe(gabpr_item, "quantity", 0)
        if gabpr_item_product_id == gabpr_product_id and gabpr_item_qty > 0:
            gabpr_acc.append(gabpr_item)
    return gabpr_acc


def batch_create(
    bt_product_id, bt_batch_number, bt_quantity, bt_expiry_date, bt_received_date
):
    bt_batch = {}
    bt_id = helpers_generate_id("BAT-")
    bt_now = helpers_current_timestamp()
    bt_batch["id"] = bt_id
    bt_batch["product_id"] = bt_product_id
    bt_batch["batch_number"] = bt_batch_number
    bt_batch["quantity"] = bt_quantity
    bt_batch["expiry_date"] = bt_expiry_date
    bt_batch["received_date"] = bt_received_date
    bt_batch["created_at"] = bt_now
    storage_add("batches", bt_batch)
    return bt_batch


def batch_get_by_id(bt_batch_id):
    return storage_get_by_id("batches", bt_batch_id)


def batch_list():
    return storage_list("batches")


def batch_list_by_product(bt_product_id):
    bt_all = storage_list("batches")
    bt_results = []
    return batch_list_by_product_rec(bt_all, bt_product_id, 0, bt_results)


def batch_update_quantity(bt_batch_id, bt_new_qty):
    bt_changes = {"quantity": bt_new_qty}
    return storage_update("batches", bt_batch_id, bt_changes)


def batch_get_expiring_before(bt_expiry_date):
    bt_all = storage_list("batches")
    bt_results = []
    bt_expiry_int = batch_date_to_int(bt_expiry_date)
    return batch_get_expiring_before_rec(bt_all, bt_expiry_int, 0, bt_results)


def batch_get_active_by_product(bt_product_id):
    bt_all = storage_list("batches")
    bt_results = []
    return batch_get_active_by_product_rec(bt_all, bt_product_id, 0, bt_results)
