from core.storage import storage_list, storage_update


def product_cancel_purchase_orders(product_id):
    for po in storage_list("purchase_orders"):
        status = po.get("status", "")
        if status in ("draft", "pending"):
            storage_update("purchase_orders", po["id"], {"status": "cancelled"})


def product_cancel_reservations(product_id):
    for res in storage_list("reservations"):
        if res.get("product_id") == product_id and res.get("status") in (
            "active",
            "pending",
        ):
            storage_update("reservations", res["id"], {"status": "cancelled"})


def product_flag_movements(product_id):
    for mov in storage_list("movements"):
        if mov.get("product_id") == product_id:
            storage_update("movements", mov["id"], {"status": "cancelled"})


def product_deactivate_cascade(prod_id):
    product_cancel_purchase_orders(prod_id)
    product_cancel_reservations(prod_id)
    product_flag_movements(prod_id)
    return True
