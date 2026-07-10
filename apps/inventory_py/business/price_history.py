from core.helpers import (
    helpers_get_map_value_safe, helpers_generate_id,
    helpers_current_timestamp
)
from core.storage import storage_list, storage_add, storage_save


def ph_filter_by_product_rec(pm_items, pm_product_id, pm_idx, pm_acc):
    for pm_item in pm_items:
        pm_prod_id = helpers_get_map_value_safe(pm_item, "product_id", "")
        if pm_prod_id == pm_product_id:
            pm_acc.append(pm_item)
    return pm_acc


def ph_clear_product_rec(pm_items, pm_product_id, pm_idx, pm_acc):
    for pm_item in pm_items:
        pm_prod_id = helpers_get_map_value_safe(pm_item, "product_id", "")
        if pm_prod_id != pm_product_id:
            pm_acc.append(pm_item)
    return pm_acc


def price_history_record(pm_product_id, pm_old_price, pm_new_price, pm_changed_by):
    pm_record = {}
    pm_id = helpers_generate_id("PH-")
    pm_now = helpers_current_timestamp()
    pm_record["id"] = pm_id
    pm_record["product_id"] = pm_product_id
    pm_record["old_price"] = pm_old_price
    pm_record["new_price"] = pm_new_price
    pm_record["changed_by"] = pm_changed_by
    pm_record["created_at"] = pm_now
    storage_add("price_history", pm_record)
    return pm_record


def price_history_get_by_product(pm_product_id):
    pm_all = storage_list("price_history")
    pm_results = []
    return ph_filter_by_product_rec(pm_all, pm_product_id, 0, pm_results)


def price_history_latest(pm_product_id):
    pm_filtered = price_history_get_by_product(pm_product_id)
    pm_len = len(pm_filtered)
    if pm_len == 0:
        return False
    return pm_filtered[pm_len - 1]


def price_history_list():
    return storage_list("price_history")


def price_history_clear_product(pm_product_id):
    pm_all = storage_list("price_history")
    pm_filtered = []
    pm_result = ph_clear_product_rec(pm_all, pm_product_id, 0, pm_filtered)
    return storage_save("price_history", pm_result)
