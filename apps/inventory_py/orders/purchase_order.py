from core.helpers import helpers_generate_id, helpers_current_timestamp, helpers_get_map_value_safe
from core.storage import storage_list, storage_add, storage_get_by_id, storage_update
from inventory.stock_movement import movement_create


def purchase_calc_line_total(pcQty, pcPrice):
    return pcQty * pcPrice


def purchase_recalc_total(prtOrderId):
    prtItems = storage_list("purchase_items")
    prtSum = 0
    for prtItem in prtItems:
        if helpers_get_map_value_safe(prtItem, "order_id", "") == prtOrderId:
            prtSum += helpers_get_map_value_safe(prtItem, "line_total", 0)
    prtChanges = {"total": prtSum, "updated_at": helpers_current_timestamp()}
    return storage_update("purchase_orders", prtOrderId, prtChanges)


def purchase_get_items(piOrderId):
    piItems = storage_list("purchase_items")
    piResults = []
    for piItem in piItems:
        if helpers_get_map_value_safe(piItem, "order_id", "") == piOrderId:
            piResults.append(piItem)
    return piResults


def purchase_list_by_vendor(plvVendorId):
    plvItems = storage_list("purchase_orders")
    plvResults = []
    for plvItem in plvItems:
        if helpers_get_map_value_safe(plvItem, "vendor_id", "") == plvVendorId:
            plvResults.append(plvItem)
    return plvResults


def purchase_receive_items(preItems, preOrderId):
    for priItem in preItems:
        priProdId = helpers_get_map_value_safe(priItem, "product_id", "")
        priQty = int(helpers_get_map_value_safe(priItem, "quantity", 0))
        movement_create(priProdId, "inbound", priQty, "purchase_order", preOrderId, "Purchase order received")
    return True


def purchase_create(pcrVendorId, pcrNotes):
    pcrId = helpers_generate_id("PO-")
    pcrNow = helpers_current_timestamp()
    pcrOrder = {
        "id": pcrId,
        "vendor_id": pcrVendorId,
        "status": "draft",
        "total": 0,
        "notes": pcrNotes,
        "created_at": pcrNow,
        "updated_at": pcrNow,
    }
    storage_add("purchase_orders", pcrOrder)
    return pcrOrder


def purchase_get(pgId):
    return storage_get_by_id("purchase_orders", pgId)


def purchase_list():
    return storage_list("purchase_orders")


def purchase_update_status(pusOrderId, pusNewStatus):
    pusChanges = {"status": pusNewStatus, "updated_at": helpers_current_timestamp()}
    return storage_update("purchase_orders", pusOrderId, pusChanges)


def purchase_order(poOrderId):
    return purchase_update_status(poOrderId, "ordered")


def purchase_add_item(paiOrderId, paiProductId, paiQty, paiPrice):
    paiLineTotal = purchase_calc_line_total(paiQty, paiPrice)
    paiId = helpers_generate_id("POI-")
    paiItem = {
        "id": paiId,
        "order_id": paiOrderId,
        "product_id": paiProductId,
        "quantity": paiQty,
        "unit_price": paiPrice,
        "line_total": paiLineTotal,
    }
    storage_add("purchase_items", paiItem)
    purchase_recalc_total(paiOrderId)
    return True


def purchase_receive(preOrderId):
    purchase_update_status(preOrderId, "received")
    preItems = purchase_get_items(preOrderId)
    return purchase_receive_items(preItems, preOrderId)


def purchase_cancel(pccOrderId):
    return purchase_update_status(pccOrderId, "cancelled")


def purchase_list_by_product(plpProductId):
    plpItems = storage_list("purchase_items")
    plpResults = []
    for plpItem in plpItems:
        if helpers_get_map_value_safe(plpItem, "product_id", "") == plpProductId:
            plpOrderId = helpers_get_map_value_safe(plpItem, "order_id", "")
            plpOrder = purchase_get(plpOrderId)
            if plpOrder:
                plpResults.append(plpOrder)
    return plpResults
