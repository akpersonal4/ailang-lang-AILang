import json

from core.storage import storage_list


def json_export_products():
    return json.dumps(storage_list("products"), indent=2)


def json_export_customers():
    return json.dumps(storage_list("customers"), indent=2)


def json_export_vendors():
    return json.dumps(storage_list("vendors"), indent=2)


def json_export_movements():
    return json.dumps(storage_list("movements"), indent=2)


def json_export_sales():
    return json.dumps(storage_list("sales_orders"), indent=2)


def json_export_purchases():
    return json.dumps(storage_list("purchase_orders"), indent=2)
