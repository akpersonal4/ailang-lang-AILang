from core.helpers import helpers_get_map_value_safe
from core.storage import storage_list


def dashboard_count_low_stock_rec(dcl_items, dcl_threshold, dcl_idx, dcl_count):
    for dcl_item in dcl_items:
        dcl_qty = helpers_get_map_value_safe(dcl_item, "quantity_on_hand", 0)
        if dcl_qty < dcl_threshold:
            dcl_count += 1
    return dcl_count


def dashboard_collect_from_rec(dcf_items, dcf_start_idx, dcf_result):
    for i in range(dcf_start_idx, len(dcf_items)):
        dcf_result.append(dcf_items[i])
    return dcf_result


def dashboard_find_max_idx_rec(dfm_items, dfm_key, dfm_idx, dfm_max_idx):
    for i in range(1, len(dfm_items)):
        dfm_val = helpers_get_map_value_safe(dfm_items[i], dfm_key, 0)
        dfm_max_val = helpers_get_map_value_safe(dfm_items[dfm_max_idx], dfm_key, 0)
        if dfm_val > dfm_max_val:
            dfm_max_idx = i
    return dfm_max_idx


def dashboard_skip_index_rec(dsi_items, dsi_skip, dsi_idx, dsi_result):
    for i in range(len(dsi_items)):
        if i != dsi_skip:
            dsi_result.append(dsi_items[i])
    return dsi_result


def dashboard_build_val_map_rec(dbv_items, dbv_idx, dbv_map):
    for dbv_item in dbv_items:
        dbv_prod_id = helpers_get_map_value_safe(dbv_item, "product_id", "")
        dbv_map[dbv_prod_id] = dbv_item
    return dbv_map


def dashboard_compute_values_rec(dcv_products, dcv_val_map, dcv_idx, dcv_result):
    for dcv_product in dcv_products:
        dcv_prod_id = helpers_get_map_value_safe(dcv_product, "id", "")
        dcv_price = helpers_get_map_value_safe(dcv_product, "unit_price", 0)
        dcv_name = helpers_get_map_value_safe(dcv_product, "name", "")
        dcv_valuation = dcv_val_map.get(dcv_prod_id, False)
        dcv_qty = 0
        if dcv_valuation is not False:
            dcv_qty = helpers_get_map_value_safe(dcv_valuation, "quantity_on_hand", 0)
        dcv_value = dcv_price * dcv_qty
        dcv_entry = {
            "product_id": dcv_prod_id,
            "product_name": dcv_name,
            "value": dcv_value,
        }
        dcv_result.append(dcv_entry)
    return dcv_result


def dashboard_take_rec(dt_items, dt_count, dt_idx, dt_result):
    for i in range(min(dt_count, len(dt_items))):
        dt_result.append(dt_items[i])
    return dt_result


def dashboard_sort_build(dsb_items, dsb_key, dsb_result):
    remaining = list(dsb_items)
    while remaining:
        if len(remaining) == 0:
            break
        dsb_max_idx = dashboard_find_max_idx_rec(remaining, dsb_key, 1, 0)
        dsb_max_item = remaining[dsb_max_idx]
        dsb_result.append(dsb_max_item)
        remaining = dashboard_skip_index_rec(remaining, dsb_max_idx, 0, [])
    return dsb_result


def dashboard_sort_by_value(dsv_items, dsv_key):
    return dashboard_sort_build(dsv_items, dsv_key, [])


def dashboard_summary():
    ds_products = storage_list("products")
    ds_categories = storage_list("categories")
    ds_customers = storage_list("customers")
    ds_vendors = storage_list("vendors")
    ds_movements = storage_list("movements")
    ds_sales_orders = storage_list("sales_orders")
    ds_purchase_orders = storage_list("purchase_orders")
    ds_warehouses = storage_list("warehouses")
    ds_result = {
        "total_products": len(ds_products),
        "total_categories": len(ds_categories),
        "total_customers": len(ds_customers),
        "total_vendors": len(ds_vendors),
        "total_movements": len(ds_movements),
        "total_sales_orders": len(ds_sales_orders),
        "total_purchase_orders": len(ds_purchase_orders),
        "total_warehouses": len(ds_warehouses),
    }
    return ds_result


def dashboard_low_stock_count(dls_threshold):
    dls_items = storage_list("valuations")
    return dashboard_count_low_stock_rec(dls_items, dls_threshold, 0, 0)


def dashboard_recent_movements(drm_count):
    drm_items = storage_list("movements")
    drm_total = len(drm_items)
    if drm_total == 0:
        return []
    drm_start = drm_total - drm_count
    if drm_start < 0:
        drm_start = 0
    return dashboard_collect_from_rec(drm_items, drm_start, [])


def dashboard_top_products(dtp_limit):
    dtp_products = storage_list("products")
    dtp_valuations = storage_list("valuations")
    dtp_val_map = dashboard_build_val_map_rec(dtp_valuations, 0, {})
    dtp_values = dashboard_compute_values_rec(dtp_products, dtp_val_map, 0, [])
    dtp_sorted = dashboard_sort_by_value(dtp_values, "value")
    return dashboard_take_rec(dtp_sorted, dtp_limit, 0, [])
