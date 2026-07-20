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


def warehouse_create(whName, whCode, whAddress, whCity, whCountry):
    whId = helpers_generate_id("WH-")
    whNow = helpers_current_timestamp()
    whItem = {
        "id": whId,
        "name": whName,
        "code": whCode,
        "address": whAddress,
        "city": whCity,
        "country": whCountry,
        "active": True,
        "created_at": whNow,
        "updated_at": whNow,
    }
    storage_add("warehouses", whItem)
    return whItem


def warehouse_get_by_id(whgId):
    return storage_get_by_id("warehouses", whgId)


def warehouse_update(whuId, whuChanges):
    whuNow = helpers_current_timestamp()
    whuChanges["updated_at"] = whuNow
    return storage_update("warehouses", whuId, whuChanges)


def warehouse_delete(whdId):
    return storage_delete("warehouses", whdId)


def warehouse_list():
    return storage_list("warehouses")


def warehouse_search(whsQuery):
    whsAll = storage_list("warehouses")
    whsResults = []
    whsQueryLower = whsQuery.lower()
    for whsrItem in whsAll:
        whsrName = helpers_get_map_value_safe(whsrItem, "name", "")
        whsrCode = helpers_get_map_value_safe(whsrItem, "code", "")
        whsrNameLower = whsrName.lower()
        whsrCodeLower = whsrCode.lower()
        if whsQueryLower in whsrNameLower or whsQueryLower in whsrCodeLower:
            whsResults.append(whsrItem)
    return whsResults
