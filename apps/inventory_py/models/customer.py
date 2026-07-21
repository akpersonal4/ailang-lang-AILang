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


def customer_create(createName, createEmail, createPhone):
    createId = helpers_generate_id("CUS-")
    createNow = helpers_current_timestamp()
    createCustomer = {
        "id": createId,
        "name": createName,
        "email": createEmail,
        "phone": createPhone,
        "active": True,
        "created_at": createNow,
        "updated_at": createNow,
    }
    storage_add("customers", createCustomer)
    return createCustomer


def customer_get(getId):
    return storage_get_by_id("customers", getId)


def customer_update(updId, updChanges):
    updNow = helpers_current_timestamp()
    updChanges["updated_at"] = updNow
    return storage_update("customers", updId, updChanges)


def customer_delete(delId):
    return storage_delete("customers", delId)


def customer_list():
    return storage_list("customers")


def customer_search(srchQuery):
    srchAll = storage_list("customers")
    srchResults = []
    srQueryLower = srchQuery.lower()
    for srItem in srchAll:
        srName = helpers_get_map_value_safe(srItem, "name", "")
        srNameLower = srName.lower()
        if srQueryLower in srNameLower:
            srchResults.append(srItem)
    return srchResults
