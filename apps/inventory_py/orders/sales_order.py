from core.helpers import (
    helpers_current_timestamp,
    helpers_generate_id,
    helpers_get_map_value_safe,
)
from core.storage import (
    storage_add,
    storage_delete,
    storage_get_by_id,
    storage_list,
    storage_update,
)
from inventory.stock_movement import movement_create


def sales_calculate_line_total(soiQty, soiPrice):
    return soiQty * soiPrice


def sales_recalculate_total(srtOrderId):
    srtItems = storage_list("sales_items")
    srtSum = 0
    for srtItem in srtItems:
        if helpers_get_map_value_safe(srtItem, "order_id", "") == srtOrderId:
            srtSum += helpers_get_map_value_safe(srtItem, "line_total", 0)
    srtChanges = {"total": srtSum, "updated_at": helpers_current_timestamp()}
    return storage_update("sales_orders", srtOrderId, srtChanges)


def sales_get_items(siOrderId):
    siItems = storage_list("sales_items")
    siResults = []
    for siItem in siItems:
        if helpers_get_map_value_safe(siItem, "order_id", "") == siOrderId:
            siResults.append(siItem)
    return siResults


def sales_list_by_customer(lccCustId):
    lccAll = storage_list("sales_orders")
    lccResults = []
    for lccItem in lccAll:
        if helpers_get_map_value_safe(lccItem, "customer_id", "") == lccCustId:
            lccResults.append(lccItem)
    return lccResults


def sales_ship_items(sshItems):
    for ssItem in sshItems:
        ssProdId = helpers_get_map_value_safe(ssItem, "product_id", "")
        ssQty = int(helpers_get_map_value_safe(ssItem, "quantity", 0))
        ssNegQty = 0 - ssQty
        movement_create(
            ssProdId,
            "outbound",
            ssNegQty,
            "sales_order",
            helpers_get_map_value_safe(ssItem, "order_id", ""),
            "Sales order shipment",
        )
    return True


def sales_create(sccCustomerId, sccNotes):
    sccId = helpers_generate_id("SO-")
    sccNow = helpers_current_timestamp()
    sccOrder = {
        "id": sccId,
        "customer_id": sccCustomerId,
        "status": "draft",
        "total": 0,
        "notes": sccNotes,
        "created_at": sccNow,
        "updated_at": sccNow,
    }
    storage_add("sales_orders", sccOrder)
    return sccOrder


def sales_get(sgId):
    return storage_get_by_id("sales_orders", sgId)


def sales_list():
    return storage_list("sales_orders")


def sales_update_status(usOrderId, usNewStatus):
    usChanges = {"status": usNewStatus, "updated_at": helpers_current_timestamp()}
    return storage_update("sales_orders", usOrderId, usChanges)


def sales_confirm(scfOrderId):
    return sales_update_status(scfOrderId, "confirmed")


def sales_add_item(saOrderId, saProductId, saQty, saPrice):
    saLineTotal = sales_calculate_line_total(saQty, saPrice)
    saId = helpers_generate_id("SOI-")
    saItem = {
        "id": saId,
        "order_id": saOrderId,
        "product_id": saProductId,
        "quantity": saQty,
        "unit_price": saPrice,
        "line_total": saLineTotal,
    }
    storage_add("sales_items", saItem)
    sales_recalculate_total(saOrderId)
    return True


def sales_ship(sshOrderId):
    sales_update_status(sshOrderId, "shipped")
    sshItems = sales_get_items(sshOrderId)
    return sales_ship_items(sshItems)


def sales_cancel(sclOrderId):
    return sales_update_status(sclOrderId, "cancelled")


def sales_delete_by_id(sdOrderId):
    return storage_delete("sales_orders", sdOrderId)
