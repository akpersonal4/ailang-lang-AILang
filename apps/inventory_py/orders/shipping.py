from core.helpers import (
    helpers_current_timestamp,
    helpers_generate_id,
    helpers_get_map_value_safe,
)
from core.storage import storage_add, storage_get_by_id, storage_list, storage_update


def shipping_create(
    shcrOrderId, shcrCarrier, shcrTrackingNumber, shcrShipAddress, shcrShippedBy
):
    shcrId = helpers_generate_id("SHP-")
    shcrNow = helpers_current_timestamp()
    shcrShipment = {
        "id": shcrId,
        "order_id": shcrOrderId,
        "carrier": shcrCarrier,
        "tracking_number": shcrTrackingNumber,
        "ship_address": shcrShipAddress,
        "shipped_by": shcrShippedBy,
        "status": "pending",
        "created_at": shcrNow,
        "updated_at": shcrNow,
    }
    storage_add("shipments", shcrShipment)
    return shcrShipment


def shipping_get_by_id(shgShipId):
    return storage_get_by_id("shipments", shgShipId)


def shipping_list():
    return storage_list("shipments")


def shipping_list_by_order(shloOrderId):
    shloAll = storage_list("shipments")
    shloResults = []
    for shloItem in shloAll:
        if helpers_get_map_value_safe(shloItem, "order_id", "") == shloOrderId:
            shloResults.append(shloItem)
    return shloResults


def shipping_update_status(shupShipId, shupNewStatus):
    shupChanges = {"status": shupNewStatus, "updated_at": helpers_current_timestamp()}
    return storage_update("shipments", shupShipId, shupChanges)


def shipping_list_by_status(shlsFilterStatus):
    shlsAll = storage_list("shipments")
    shlsResults = []
    for shlsItem in shlsAll:
        if helpers_get_map_value_safe(shlsItem, "status", "") == shlsFilterStatus:
            shlsResults.append(shlsItem)
    return shlsResults
