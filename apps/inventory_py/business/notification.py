from core.storage import storage_list


def notification_check_low_stock_rec(nl_items, nl_threshold, nl_idx, nl_result):
    for nl_item in nl_items:
        if "quantity_on_hand" in nl_item:
            nl_qty = nl_item["quantity_on_hand"]
            if nl_qty < nl_threshold:
                nl_result.append(nl_item)
    return nl_result


def notification_check_low_stock(nl_threshold):
    nl_items = storage_list("valuations")
    nl_result = []
    return notification_check_low_stock_rec(nl_items, nl_threshold, 0, nl_result)


def notification_check_out_of_stock_rec(ns_items, ns_idx, ns_result):
    for ns_item in ns_items:
        if "quantity_on_hand" in ns_item:
            ns_qty = int(ns_item["quantity_on_hand"])
            if ns_qty == 0:
                ns_result.append(ns_item)
    return ns_result


def notification_check_out_of_stock():
    ns_items = storage_list("valuations")
    ns_result = []
    return notification_check_out_of_stock_rec(ns_items, 0, ns_result)
