from core.helpers import (
    helpers_get_map_value_safe, helpers_generate_id,
    helpers_current_timestamp, helpers_find_in_list
)
from core.storage import storage_list, storage_add, storage_update


def reorder_list_needed_rec(rlnr_items, rlnr_results, rlnr_idx):
    for rlnr_item in rlnr_items:
        rlnr_current_stock = helpers_get_map_value_safe(rlnr_item, "current_stock", 0)
        rlnr_min_level = helpers_get_map_value_safe(rlnr_item, "min_level", 0)
        if rlnr_current_stock < rlnr_min_level:
            rlnr_results.append(rlnr_item)
    return rlnr_results


def reorder_get_level(rgl_product_id):
    rgl_all = storage_list("reorder_levels")
    return helpers_find_in_list(rgl_all, "product_id", rgl_product_id)


def reorder_set_level(rsl_product_id, rsl_min_level, rsl_max_level, rsl_reorder_qty):
    rsl_existing = reorder_get_level(rsl_product_id)
    if rsl_existing is False:
        rsl_new = {}
        rsl_id = helpers_generate_id("ROL-")
        rsl_new["id"] = rsl_id
        rsl_new["product_id"] = rsl_product_id
        rsl_new["min_level"] = rsl_min_level
        rsl_new["max_level"] = rsl_max_level
        rsl_new["reorder_qty"] = rsl_reorder_qty
        rsl_new["current_stock"] = 0
        rsl_new["created_at"] = helpers_current_timestamp()
        rsl_new["updated_at"] = helpers_current_timestamp()
        return storage_add("reorder_levels", rsl_new)
    rsl_existing_id = helpers_get_map_value_safe(rsl_existing, "id", "")
    rsl_changes = {
        "min_level": rsl_min_level,
        "max_level": rsl_max_level,
        "reorder_qty": rsl_reorder_qty,
        "updated_at": helpers_current_timestamp()
    }
    return storage_update("reorder_levels", rsl_existing_id, rsl_changes)


def reorder_check(rc_product_id):
    rc_level = reorder_get_level(rc_product_id)
    if rc_level is False:
        return False
    rc_current_stock = helpers_get_map_value_safe(rc_level, "current_stock", 0)
    rc_min_level = helpers_get_map_value_safe(rc_level, "min_level", 0)
    return rc_current_stock < rc_min_level


def reorder_list_all():
    return storage_list("reorder_levels")


def reorder_list_needed():
    rln_all = storage_list("reorder_levels")
    rln_results = []
    return reorder_list_needed_rec(rln_all, rln_results, 0)


def reorder_calculate_lead_time_demand(rld_daily_usage, rld_lead_time_days):
    return rld_daily_usage * rld_lead_time_days
