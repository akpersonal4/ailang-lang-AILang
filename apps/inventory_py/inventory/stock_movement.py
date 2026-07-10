from core.helpers import (
    helpers_generate_id,
    helpers_current_timestamp,
    helpers_get_map_value_safe,
)
from core.storage import storage_add, storage_list, storage_update


def movement_create(product_id, m_type, quantity, ref_type, ref_id, notes):
    movement = {
        "id": helpers_generate_id("MOV-"),
        "product_id": product_id,
        "type": m_type,
        "quantity": quantity,
        "reference_type": ref_type,
        "reference_id": ref_id,
        "notes": notes,
        "created_at": helpers_current_timestamp(),
        "status": "active",
    }
    storage_add("movements", movement)
    return movement


def movement_list():
    return storage_list("movements")


def movement_list_by_product(product_id):
    all_items = storage_list("movements")
    results = []
    for item in all_items:
        if helpers_get_map_value_safe(item, "product_id", "") == product_id:
            results.append(item)
    return results


def movement_get_quantity_on_hand(product_id):
    all_items = storage_list("movements")
    total = 0
    for item in all_items:
        if helpers_get_map_value_safe(item, "product_id", "") == product_id:
            total += helpers_get_map_value_safe(item, "quantity", 0)
    return total


def movement_check_alert_threshold(product_id, threshold):
    items = movement_list_by_product(product_id)
    if not items:
        return False
    qoh = movement_get_quantity_on_hand(product_id)
    if qoh < threshold:
        return {
            "product_id": product_id,
            "current_qoh": qoh,
            "threshold": threshold,
            "alert": True,
        }
    return {
        "product_id": product_id,
        "alert": False,
    }


def movement_list_by_type(m_type):
    all_items = storage_list("movements")
    results = []
    for item in all_items:
        if helpers_get_map_value_safe(item, "type", "") == m_type:
            results.append(item)
    return results


def movement_update_status(movement_id, new_status):
    changes = {"status": new_status}
    return storage_update("movements", movement_id, changes)
