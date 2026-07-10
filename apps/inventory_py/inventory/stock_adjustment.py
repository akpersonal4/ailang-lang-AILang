from core.helpers import helpers_generate_id, helpers_current_timestamp, helpers_get_map_value_safe
from core.storage import storage_add, storage_list, storage_get_by_id
from inventory.stock_movement import movement_create


def adjustment_create(product_id, expected_qty, actual_qty, reason, adjusted_by):
    difference = actual_qty - expected_qty
    adjustment = {
        "id": helpers_generate_id("ADJ-"),
        "product_id": product_id,
        "expected_qty": expected_qty,
        "actual_qty": actual_qty,
        "difference": difference,
        "reason": reason,
        "adjusted_by": adjusted_by,
        "created_at": helpers_current_timestamp(),
    }
    if difference != 0:
        movement_create(product_id, "adjustment", difference, "adjustment", adjustment["id"], reason)
    storage_add("adjustments", adjustment)
    return adjustment


def adjustment_get_by_id(adj_id):
    return storage_get_by_id("adjustments", adj_id)


def adjustment_list():
    return storage_list("adjustments")


def adjustment_list_by_product(product_id):
    all_items = storage_list("adjustments")
    results = []
    for item in all_items:
        if helpers_get_map_value_safe(item, "product_id", "") == product_id:
            results.append(item)
    return results


def adjustment_get_discrepancies(threshold):
    all_items = storage_list("adjustments")
    results = []
    for item in all_items:
        diff = helpers_get_map_value_safe(item, "difference", 0)
        if diff < 0:
            abs_diff = 0 - diff
            if abs_diff > threshold:
                results.append(item)
        elif diff > threshold:
            results.append(item)
    return results


def adjustment_summary():
    all_items = storage_list("adjustments")
    acc = {"total_adjustments": 0, "total_positive": 0, "total_negative": 0, "net_change": 0}
    for item in all_items:
        diff = helpers_get_map_value_safe(item, "difference", 0)
        acc["total_adjustments"] += 1
        if diff > 0:
            acc["total_positive"] += diff
        else:
            acc["total_negative"] += diff
        acc["net_change"] += diff
    return acc
