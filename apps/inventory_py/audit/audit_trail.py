from core.helpers import helpers_get_map_value_safe
from core.storage import storage_list


def at_range_rec(ar_items, ar_start, ar_end, ar_idx, ar_acc):
    for ar_item in ar_items:
        ar_created = helpers_get_map_value_safe(ar_item, "created_at", "")
        if ar_start <= ar_created <= ar_end:
            ar_acc.append(ar_item)
    return ar_acc


def at_user_rec(ar_items, ar_user_name, ar_idx, ar_acc):
    for ar_item in ar_items:
        ar_creator = helpers_get_map_value_safe(ar_item, "created_by", "")
        if ar_creator == ar_user_name:
            ar_acc.append(ar_item)
    return ar_acc


def at_summary_rec(ar_items, ar_idx, ar_acc):
    for ar_item in ar_items:
        ar_action = helpers_get_map_value_safe(ar_item, "action", "")
        ar_current_count = helpers_get_map_value_safe(ar_acc, ar_action, 0)
        ar_acc[ar_action] = ar_current_count + 1
    return ar_acc


def at_recent_rec(ar_items, ar_idx, ar_end, ar_acc):
    for i in range(ar_idx, ar_end):
        ar_acc.append(ar_items[i])
    return ar_acc


def audit_trail_list_by_date_range(ar_start_date, ar_end_date):
    ar_all = storage_list("audit_log")
    ar_results = []
    return at_range_rec(ar_all, ar_start_date, ar_end_date, 0, ar_results)


def audit_trail_list_by_user(ar_user_name):
    ar_all = storage_list("audit_log")
    ar_results = []
    return at_user_rec(ar_all, ar_user_name, 0, ar_results)


def audit_trail_summary_by_action():
    ar_all = storage_list("audit_log")
    ar_acc = {}
    return at_summary_rec(ar_all, 0, ar_acc)


def audit_trail_recent(ar_count):
    ar_all = storage_list("audit_log")
    ar_len = len(ar_all)
    ar_result = []
    if ar_len == 0:
        return ar_result
    ar_start = 0
    if ar_len > ar_count:
        ar_start = ar_len - ar_count
    return at_recent_rec(ar_all, ar_start, ar_len, ar_result)
