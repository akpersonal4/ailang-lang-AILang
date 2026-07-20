from core.helpers import (
    helpers_current_timestamp,
    helpers_generate_id,
    helpers_get_map_value_safe,
)
from core.storage import storage_add, storage_get_by_id, storage_list, storage_update


def returns_create(
    rtrnSoOrderId, rtrnProductId, rtrnQuantity, rtrnReason, rtrnReturnBy
):
    rtrnId = helpers_generate_id("RET-")
    rtrnNow = helpers_current_timestamp()
    rtrnReturn = {
        "id": rtrnId,
        "order_id": rtrnSoOrderId,
        "product_id": rtrnProductId,
        "quantity": rtrnQuantity,
        "reason": rtrnReason,
        "return_by": rtrnReturnBy,
        "status": "pending",
        "created_at": rtrnNow,
        "updated_at": rtrnNow,
    }
    storage_add("returns", rtrnReturn)
    return rtrnReturn


def returns_get_by_id(rtgReturnId):
    return storage_get_by_id("returns", rtgReturnId)


def returns_list():
    return storage_list("returns")


def returns_list_by_order(rtloOrderId):
    rtloAll = storage_list("returns")
    rtloResults = []
    for rtloItem in rtloAll:
        if helpers_get_map_value_safe(rtloItem, "order_id", "") == rtloOrderId:
            rtloResults.append(rtloItem)
    return rtloResults


def returns_approve(rtapReturnId):
    rtapChanges = {"status": "approved", "updated_at": helpers_current_timestamp()}
    return storage_update("returns", rtapReturnId, rtapChanges)


def returns_reject(rtrejReturnId, rtrejReason):
    rtrejChanges = {
        "status": "rejected",
        "rejection_reason": rtrejReason,
        "updated_at": helpers_current_timestamp(),
    }
    return storage_update("returns", rtrejReturnId, rtrejChanges)


def returns_complete(rtcmpReturnId):
    rtcmpChanges = {"status": "completed", "updated_at": helpers_current_timestamp()}
    return storage_update("returns", rtcmpReturnId, rtcmpChanges)
