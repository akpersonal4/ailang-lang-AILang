from core.helpers import helpers_get_map_value_safe
from core.storage import storage_list


def csv_escape_field(cf_value):
    return str(cf_value)


def csv_join_fields(jf_fields, jf_sep):
    return jf_sep.join(jf_fields)


def csv_product_row(fp_item):
    fp_fields = [
        helpers_get_map_value_safe(fp_item, "id", ""),
        helpers_get_map_value_safe(fp_item, "name", ""),
        helpers_get_map_value_safe(fp_item, "sku", ""),
        str(helpers_get_map_value_safe(fp_item, "unit_price", 0)),
        helpers_get_map_value_safe(fp_item, "unit", ""),
    ]
    return csv_join_fields(fp_fields, ",")


def csv_products():
    fp_all = storage_list("products")
    fp_header = "id,name,sku,unit_price,unit\n"
    fp_result = fp_header
    for fp_item in fp_all:
        fp_result += csv_product_row(fp_item) + "\n"
    return fp_result


def csv_customer_row(fc_item):
    fc_fields = [
        helpers_get_map_value_safe(fc_item, "id", ""),
        helpers_get_map_value_safe(fc_item, "name", ""),
        helpers_get_map_value_safe(fc_item, "email", ""),
        helpers_get_map_value_safe(fc_item, "phone", ""),
    ]
    return csv_join_fields(fc_fields, ",")


def csv_customers():
    fc_all = storage_list("customers")
    fc_header = "id,name,email,phone\n"
    fc_result = fc_header
    for fc_item in fc_all:
        fc_result += csv_customer_row(fc_item) + "\n"
    return fc_result


def csv_movements_row(fm_item):
    fm_fields = [
        helpers_get_map_value_safe(fm_item, "id", ""),
        helpers_get_map_value_safe(fm_item, "product_id", ""),
        helpers_get_map_value_safe(fm_item, "type", ""),
        str(helpers_get_map_value_safe(fm_item, "quantity", 0)),
        helpers_get_map_value_safe(fm_item, "created_at", ""),
    ]
    return csv_join_fields(fm_fields, ",")


def csv_movements():
    fm_all = storage_list("movements")
    fm_header = "id,product_id,type,quantity,created_at\n"
    fm_result = fm_header
    for fm_item in fm_all:
        fm_result += csv_movements_row(fm_item) + "\n"
    return fm_result
