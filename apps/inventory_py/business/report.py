from core.helpers import helpers_get_map_value_safe
from core.storage import storage_list


# --- Stock Report ---

def stock_report_calc_rec(sr_movements, sr_product_id, sr_idx, sr_total):
    for sr_item in sr_movements:
        sr_item_prod_id = helpers_get_map_value_safe(sr_item, "product_id", "")
        if sr_item_prod_id == sr_product_id:
            sr_total += helpers_get_map_value_safe(sr_item, "quantity", 0)
    return sr_total


def stock_report_get_qty(sg_product_id):
    sg_movements = storage_list("movements")
    return stock_report_calc_rec(sg_movements, sg_product_id, 0, 0)


def stock_report_valuation():
    return storage_list("valuations")


def stock_report_aging_rec(sa_movements, sa_idx, sa_result):
    for sa_item in sa_movements:
        sa_type = helpers_get_map_value_safe(sa_item, "type", "")
        if sa_type == "inbound":
            sa_qty = int(helpers_get_map_value_safe(sa_item, "quantity", 0))
            if sa_qty > 0:
                sa_result.append(sa_item)
    return sa_result


def stock_report_aging():
    sa_all = storage_list("movements")
    sa_result = []
    return stock_report_aging_rec(sa_all, 0, sa_result)


def stock_report_all_products():
    return storage_list("products")


# --- Sales Report ---

def sales_report_all():
    return storage_list("sales_orders")


def sales_report_by_status_rec(rs_items, rs_status, rs_idx, rs_result):
    for rs_item in rs_items:
        rs_item_status = helpers_get_map_value_safe(rs_item, "status", "")
        if rs_item_status == rs_status:
            rs_result.append(rs_item)
    return rs_result


def sales_report_by_status(rs_status):
    rs_all = storage_list("sales_orders")
    rs_result = []
    return sales_report_by_status_rec(rs_all, rs_status, 0, rs_result)


def sales_report_total_revenue_rec(rt_items, rt_idx, rt_sum):
    for rt_item in rt_items:
        if "total" in rt_item:
            rt_sum += int(rt_item["total"])
    return rt_sum


def sales_report_total_revenue():
    rt_all = storage_list("sales_orders")
    return sales_report_total_revenue_rec(rt_all, 0, 0)


def sales_report_count_by_status_rec(rc_items, rc_status, rc_idx, rc_count):
    for rc_item in rc_items:
        rc_item_status = helpers_get_map_value_safe(rc_item, "status", "")
        if rc_item_status == rc_status:
            rc_count += 1
    return rc_count


def sales_report_count_by_status(rc_status):
    rc_all = storage_list("sales_orders")
    return sales_report_count_by_status_rec(rc_all, rc_status, 0, 0)


def sales_report_items():
    return storage_list("sales_items")


# --- Profit Report ---

def profit_report_sales_sum_rec(ps_items, ps_idx, ps_sum):
    for ps_item in ps_items:
        if "total" in ps_item:
            ps_sum += int(ps_item["total"])
    return ps_sum


def profit_report_purchase_sum_rec(pp_items, pp_idx, pp_sum):
    for pp_item in pp_items:
        if "total" in pp_item:
            pp_sum += int(pp_item["total"])
    return pp_sum


def profit_report_summary():
    pr_sales = storage_list("sales_orders")
    pr_purchases = storage_list("purchase_orders")
    pr_sales_total = profit_report_sales_sum_rec(pr_sales, 0, 0)
    pr_purchase_total = profit_report_purchase_sum_rec(pr_purchases, 0, 0)
    pr_result = {
        "sales_total": pr_sales_total,
        "sales_count": len(pr_sales),
        "purchase_total": pr_purchase_total,
        "purchase_count": len(pr_purchases)
    }
    return pr_result
