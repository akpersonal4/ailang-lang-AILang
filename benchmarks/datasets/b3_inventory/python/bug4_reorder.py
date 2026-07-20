from core.helpers import (
    helpers_current_timestamp,
    helpers_find_in_list,
    helpers_generate_id,
)
from core.storage import storage_add, storage_list, storage_update


def reorder_get_level(product_id):
    return helpers_find_in_list(
        storage_list("reorder_levels"), "product_id", product_id
    )


def reorder_set_level(product_id, min_level, max_level, reorder_qty):
    existing = reorder_get_level(product_id)
    now = helpers_current_timestamp()
    if existing is False:
        new_level = {
            "id": helpers_generate_id("ROL-"),
            "product_id": product_id,
            "min_level": min_level,
            "max_level": max_level,
            "reorder_qty": reorder_qty,
            "current_stock": 0,
            "created_at": now,
            "updated_at": now,
        }
        return storage_add("reorder_levels", new_level)
    return storage_update(
        "reorder_levels",
        existing["id"],
        {
            "min_level": min_level,
            "max_level": max_level,
            "reorder_qty": reorder_qty,
            "updated_at": now,
        },
    )


def reorder_check(product_id):
    level = reorder_get_level(product_id)
    if level is False:
        return False
    return level.get("current_stock", 0) > level.get("min_level", 0)


def reorder_list_all():
    return storage_list("reorder_levels")


def reorder_list_needed():
    return [
        r
        for r in storage_list("reorder_levels")
        if r.get("current_stock", 0) > r.get("min_level", 0)
    ]


def reorder_calculate_lead_time_demand(daily_usage, lead_days):
    return daily_usage * lead_days
