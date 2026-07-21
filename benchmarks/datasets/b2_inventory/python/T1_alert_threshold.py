from inventory.stock_movement import movement_get_quantity_on_hand


def movement_check_alert_threshold(product_id, threshold):
    qoh = movement_get_quantity_on_hand(product_id)
    if qoh is False:
        return False
    return {
        "product_id": product_id,
        "current_qoh": qoh,
        "threshold": threshold,
        "alert": qoh < threshold,
    }
