from core.helpers import (
    helpers_current_timestamp,
    helpers_generate_id,
)
from core.storage import storage_add, storage_list


def purchase_create(vendor_id, notes):
    po = {
        "id": helpers_generate_id("PO-"),
        "vendorId": vendor_id,
        "notes": notes,
        "status": "draft",
        "total": 0,
        "created_at": helpers_current_timestamp(),
        "updated_at": helpers_current_timestamp(),
    }
    storage_add("purchase_orders", po)
    return po


def purchase_get(po_id):
    for po in storage_list("purchase_orders"):
        if po.get("id") == po_id:
            return po
    return False


def purchase_get_items(order_id):
    return [i for i in storage_list("purchase_items") if i.get("order_id") == order_id]


def purchase_list_by_vendor(vendor_id):
    return [
        po for po in storage_list("purchase_orders") if po.get("vendor_id") == vendor_id
    ]
