from core.helpers import (
    helpers_current_timestamp,
    helpers_generate_id,
    helpers_get_map_value_safe,
    helpers_unix_timestamp,
)
from core.storage import storage_add, storage_delete, storage_list

STOCK_AGING_DAY_30 = 2592000
STOCK_AGING_DAY_60 = 5184000
STOCK_AGING_DAY_90 = 7776000


def stock_aging_record(product_id, warehouse_id, quantity, received_at):
    batch = {
        "id": helpers_generate_id("SAB-"),
        "product_id": product_id,
        "warehouse_id": warehouse_id,
        "quantity": quantity,
        "received_at": received_at,
        "created_at": helpers_current_timestamp(),
    }
    storage_add("stock_aging", batch)
    return batch


def stock_aging_get_batches(product_id, warehouse_id):
    all_items = storage_list("stock_aging")
    results = []
    for item in all_items:
        match_prod = helpers_get_map_value_safe(item, "product_id", "") == product_id
        match_ware = (
            helpers_get_map_value_safe(item, "warehouse_id", "") == warehouse_id
        )
        if match_prod and match_ware:
            results.append(item)
    return results


def stock_aging_summary(product_id):
    all_items = storage_list("stock_aging")
    now = helpers_unix_timestamp()
    count_0_30 = 0
    count_31_60 = 0
    count_61_90 = 0
    count_90_plus = 0
    for item in all_items:
        if helpers_get_map_value_safe(item, "product_id", "") == product_id:
            received = helpers_get_map_value_safe(item, "received_at", 0)
            quantity = helpers_get_map_value_safe(item, "quantity", 0)
            age = now - received
            if age <= STOCK_AGING_DAY_30:
                count_0_30 += quantity
            elif age <= STOCK_AGING_DAY_60:
                count_31_60 += quantity
            elif age <= STOCK_AGING_DAY_90:
                count_61_90 += quantity
            else:
                count_90_plus += quantity
    return {
        "0_30_days": count_0_30,
        "31_60_days": count_31_60,
        "61_90_days": count_61_90,
        "90_plus_days": count_90_plus,
    }


def stock_aging_remove_batch(product_id, warehouse_id, batch_id):
    return storage_delete("stock_aging", batch_id)
