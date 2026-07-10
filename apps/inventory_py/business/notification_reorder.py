from core.helpers import (
    helpers_get_map_value_safe, helpers_generate_id,
    helpers_current_timestamp
)
from core.storage import storage_list, storage_add, storage_save
from business.reorder import reorder_check, reorder_list_all


def rn_check_rec(rncr_levels, rncr_idx, rncr_count):
    for rncr_level in rncr_levels:
        rncr_product_id = helpers_get_map_value_safe(rncr_level, "product_id", "")
        rncr_needs_reorder = reorder_check(rncr_product_id)
        if rncr_needs_reorder:
            rncr_min_level = helpers_get_map_value_safe(rncr_level, "min_level", 0)
            rncr_notif = {}
            rncr_notif_id = helpers_generate_id("RN-")
            rncr_now = helpers_current_timestamp()
            rncr_notif["id"] = rncr_notif_id
            rncr_notif["product_id"] = rncr_product_id
            rncr_notif["min_level"] = rncr_min_level
            rncr_notif["created_at"] = rncr_now
            storage_add("reorder_notifications", rncr_notif)
            rncr_count += 1
    return rncr_count


def rn_clear_rec(rncl_items, rncl_product_id, rncl_results, rncl_idx):
    for rncl_item in rncl_items:
        rncl_item_prod_id = helpers_get_map_value_safe(rncl_item, "product_id", "")
        if rncl_item_prod_id != rncl_product_id:
            rncl_results.append(rncl_item)
    return rncl_results


def reorder_notify_check_all():
    rnca_levels = reorder_list_all()
    rnca_count = rn_check_rec(rnca_levels, 0, 0)
    return rnca_count


def reorder_notify_get_pending():
    return storage_list("reorder_notifications")


def reorder_notify_clear(rnc_product_id):
    rnc_items = storage_list("reorder_notifications")
    rnc_results = []
    rnc_filtered = rn_clear_rec(rnc_items, rnc_product_id, rnc_results, 0)
    return storage_save("reorder_notifications", rnc_filtered)


def reorder_notify_summary():
    rns_items = storage_list("reorder_notifications")
    return len(rns_items)
