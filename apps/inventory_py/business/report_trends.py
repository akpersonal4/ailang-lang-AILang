from core.helpers import helpers_get_map_value_safe
from core.storage import storage_list


def trend_find_max_idx_rec(tfmr_items, tfmr_value_key, tfmr_idx, tfmr_best_idx, tfmr_best_val):
    for i in range(len(tfmr_items)):
        tfmr_item = tfmr_items[i]
        tfmr_val = helpers_get_map_value_safe(tfmr_item, tfmr_value_key, 0)
        if tfmr_val > tfmr_best_val:
            tfmr_best_idx = i
            tfmr_best_val = tfmr_val
    return tfmr_best_idx


def trend_remove_idx_rec(tri_items, tri_skip_idx, tri_result, tri_idx):
    for i in range(len(tri_items)):
        if i != tri_skip_idx:
            tri_result.append(tri_items[i])
    return tri_result


def trend_sort_descending_rec(tsdr_items, tsdr_value_key, tsdr_result):
    remaining = list(tsdr_items)
    while remaining:
        first_val = helpers_get_map_value_safe(remaining[0], tsdr_value_key, 0)
        max_idx = trend_find_max_idx_rec(remaining, tsdr_value_key, 0, 0, first_val)
        max_item = remaining[max_idx]
        tsdr_result.append(max_item)
        new_remaining = []
        for i in range(len(remaining)):
            if i != max_idx:
                new_remaining.append(remaining[i])
        remaining = new_remaining
    return tsdr_result


def trend_take_first_rec(tffr_items, tffr_limit, tffr_result, tffr_idx):
    for i in range(min(tffr_limit, len(tffr_items))):
        tffr_result.append(tffr_items[i])
    return tffr_result


def trend_group_sales_rec(tgs_items, tgs_idx, tgs_acc):
    for tgs_item in tgs_items:
        tgs_prod_id = helpers_get_map_value_safe(tgs_item, "product_id", "")
        tgs_qty = helpers_get_map_value_safe(tgs_item, "quantity", 0)
        if tgs_prod_id in tgs_acc:
            tgs_existing = tgs_acc[tgs_prod_id]
            tgs_existing["total_qty"] += tgs_qty
        else:
            tgs_new_entry = {
                "product_id": tgs_prod_id,
                "total_qty": tgs_qty
            }
            tgs_acc[tgs_prod_id] = tgs_new_entry
    return tgs_acc


def trend_monthly_group_rec(tmgr_items, tmgr_idx, tmgr_acc):
    for tmgr_item in tmgr_items:
        tmgr_created = helpers_get_map_value_safe(tmgr_item, "created_at", "")
        if len(tmgr_created) >= 7:
            tmgr_month = tmgr_created[:7]
            tmgr_total = helpers_get_map_value_safe(tmgr_item, "total", 0)
            if tmgr_month in tmgr_acc:
                tmgr_existing = tmgr_acc[tmgr_month]
                tmgr_existing["count"] += 1
                tmgr_existing["total"] += tmgr_total
            else:
                tmgr_acc[tmgr_month] = {"count": 1, "total": tmgr_total}
    return tmgr_acc


def trend_map_to_list_rec(tmtl_keys, tmtl_acc, tmtl_result, tmtl_idx):
    for tmtl_key in tmtl_keys:
        if tmtl_key in tmtl_acc:
            tmtl_result.append(tmtl_acc[tmtl_key])
    return tmtl_result


def trend_monthly_to_list_rec(tmtlr_keys, tmtlr_acc, tmtlr_result, tmtlr_idx):
    for tmtlr_key in tmtlr_keys:
        if tmtlr_key in tmtlr_acc:
            tmtlr_entry = tmtlr_acc[tmtlr_key]
            tmtlr_result.append({
                "month": tmtlr_key,
                "count": helpers_get_map_value_safe(tmtlr_entry, "count", 0),
                "total": helpers_get_map_value_safe(tmtlr_entry, "total", 0)
            })
    return tmtlr_result


def trend_category_group_rec(tcgr_items, tcgr_idx, tcgr_acc):
    for tcgr_item in tcgr_items:
        tcgr_cat_id = helpers_get_map_value_safe(tcgr_item, "category_id", "uncategorized")
        if tcgr_cat_id in tcgr_acc:
            tcgr_acc[tcgr_cat_id] += 1
        else:
            tcgr_acc[tcgr_cat_id] = 1
    return tcgr_acc


def trend_category_to_list_rec(tctl_keys, tctl_acc, tctl_result, tctl_idx):
    for tctl_key in tctl_keys:
        tctl_result.append({
            "category_id": tctl_key,
            "count": helpers_get_map_value_safe(tctl_acc, tctl_key, 0)
        })
    return tctl_result


def trend_sort_descending(trend_items, trend_value_key):
    trend_result = []
    return trend_sort_descending_rec(trend_items, trend_value_key, trend_result)


def trend_monthly_sales():
    tms_orders = storage_list("sales_orders")
    tms_grouped = trend_monthly_group_rec(tms_orders, 0, {})
    tms_keys = list(tms_grouped.keys())
    tms_result = []
    return trend_monthly_to_list_rec(tms_keys, tms_grouped, tms_result, 0)


def trend_monthly_purchases():
    tmp_orders = storage_list("purchase_orders")
    tmp_grouped = trend_monthly_group_rec(tmp_orders, 0, {})
    tmp_keys = list(tmp_grouped.keys())
    tmp_result = []
    return trend_monthly_to_list_rec(tmp_keys, tmp_grouped, tmp_result, 0)


def trend_top_products(tp_limit):
    tp_items = storage_list("sales_items")
    tp_grouped = trend_group_sales_rec(tp_items, 0, {})
    tp_keys = list(tp_grouped.keys())
    tp_list = []
    tp_all = trend_map_to_list_rec(tp_keys, tp_grouped, tp_list, 0)
    tp_sorted = trend_sort_descending(tp_all, "total_qty")
    tp_result = []
    return trend_take_first_rec(tp_sorted, tp_limit, tp_result, 0)


def trend_category_breakdown():
    cb_products = storage_list("products")
    cb_acc = {}
    cb_grouped = trend_category_group_rec(cb_products, 0, cb_acc)
    cb_keys = list(cb_grouped.keys())
    cb_result = []
    return trend_category_to_list_rec(cb_keys, cb_grouped, cb_result, 0)
