from core.storage import storage_list
from core.helpers import helpers_get_map_value_safe, helpers_generate_id, helpers_current_timestamp


def movement_create(product_id, typ, quantity, ref_type, ref_id, notes):
    mov = {
        "id": helpers_generate_id("MOV-"),
        "product_id": product_id,
        "type": typ,
        "quantity": quantity,
        "reference_type": ref_type,
        "reference_id": ref_id,
        "notes": notes,
        "created_at": helpers_current_timestamp(),
    }
    storage_list("movements").append(mov)
    return mov


def movement_list():
    return storage_list("movements")


def movement_list_by_product(product_id):
    result = [m for m in storage_list("movements") if m.get("product_id") == product_id]
    return result


def movement_get_quantity_on_hand(product_id):
    return sum(
        m.get("quantity", 0) for m in storage_list("movements")
        if m.get("product_id") == product_id
    )


def movement_list_by_type(typ):
    return [m for m in storage_list("movements") if m.get("type") == typ]
