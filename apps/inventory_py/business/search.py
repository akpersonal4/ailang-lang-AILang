from core.helpers import helpers_get_map_value_safe
from core.storage import storage_list


def search_all_rec(sa_items, sa_term, sa_type, sa_idx, sa_result):
    sa_term_lower = sa_term.lower()
    for sa_item in sa_items:
        sa_name = helpers_get_map_value_safe(sa_item, "name", "")
        sa_name_lower = sa_name.lower()
        if sa_term_lower in sa_name_lower:
            sa_entry = {
                "type": sa_type,
                "id": helpers_get_map_value_safe(sa_item, "id", "")
            }
            sa_result.append(sa_entry)
    return sa_result


def search_all(sa_term):
    sa_products = storage_list("products")
    sa_customers = storage_list("customers")
    sa_vendors = storage_list("vendors")
    sa_result = []
    sa_result = search_all_rec(sa_products, sa_term, "product", 0, sa_result)
    sa_result = search_all_rec(sa_customers, sa_term, "customer", 0, sa_result)
    sa_result = search_all_rec(sa_vendors, sa_term, "vendor", 0, sa_result)
    return sa_result
