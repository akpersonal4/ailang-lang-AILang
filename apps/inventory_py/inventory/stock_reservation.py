from core.helpers import (
    helpers_current_timestamp,
    helpers_generate_id,
    helpers_get_map_value_safe,
)
from core.storage import storage_add, storage_get_by_id, storage_list, storage_update
from inventory.stock_movement import movement_get_quantity_on_hand


def reservation_list_by_order(order_id):
    all_items = storage_list("reservations")
    results = []
    for item in all_items:
        if helpers_get_map_value_safe(item, "order_id", "") == order_id:
            results.append(item)
    return results


def reservation_check_availability(product_id, requested_qty):
    qoh = movement_get_quantity_on_hand(product_id)
    return qoh >= requested_qty


def reservation_create(order_id, product_id, quantity):
    available = reservation_check_availability(product_id, quantity)
    if not available:
        return None
    reservation = {
        "id": helpers_generate_id("RES-"),
        "order_id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "status": "active",
        "created_at": helpers_current_timestamp(),
        "updated_at": helpers_current_timestamp(),
    }
    storage_add("reservations", reservation)
    return reservation


def reservation_get_by_id(res_id):
    return storage_get_by_id("reservations", res_id)


def reservation_list():
    return storage_list("reservations")


def reservation_fulfill(rsf_id):
    existing = storage_get_by_id("reservations", rsf_id)
    if existing is None:
        return None
    changes = {
        "status": "fulfilled",
        "updated_at": helpers_current_timestamp(),
    }
    return storage_update("reservations", rsf_id, changes)


def reservation_cancel(rcc_id):
    existing = storage_get_by_id("reservations", rcc_id)
    if existing is None:
        return None
    changes = {
        "status": "cancelled",
        "updated_at": helpers_current_timestamp(),
    }
    return storage_update("reservations", rcc_id, changes)


def reservation_list_by_product(product_id):
    all_items = storage_list("reservations")
    results = []
    for item in all_items:
        if helpers_get_map_value_safe(item, "product_id", "") == product_id:
            results.append(item)
    return results
