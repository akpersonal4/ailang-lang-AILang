from core.helpers import (
    helpers_generate_id,
    helpers_current_timestamp,
    helpers_get_map_value_safe,
)
from core.storage import storage_list, storage_save


def valuation_get(product_id):
    all_items = storage_list("valuations")
    for item in all_items:
        if helpers_get_map_value_safe(item, "product_id", "") == product_id:
            return item
    return None


def valuation_set(product_id, method, cost, qty):
    all_items = storage_list("valuations")
    existing = None
    for item in all_items:
        if helpers_get_map_value_safe(item, "product_id", "") == product_id:
            existing = item
            break
    now = helpers_current_timestamp()
    if existing is None:
        new_item = {
            "id": helpers_generate_id("VAL-"),
            "product_id": product_id,
            "method": method,
            "current_cost": cost,
            "quantity_on_hand": qty,
            "last_updated": now,
        }
        all_items.append(new_item)
        return storage_save("valuations", all_items)
    changes = {
        "method": method,
        "current_cost": cost,
        "quantity_on_hand": qty,
        "last_updated": now,
    }
    for key in changes:
        existing[key] = changes[key]
    return storage_save("valuations", all_items)


def valuation_calculate_average(product_id):
    return 0


def valuation_list():
    return storage_list("valuations")
