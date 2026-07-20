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


def category_create(ccName, ccDescription, ccParentId):
    ccId = helpers_generate_id("CAT-")
    ccNow = helpers_current_timestamp()
    ccCategory = {
        "id": ccId,
        "name": ccName,
        "description": ccDescription,
        "parent_id": ccParentId,
        "created_at": ccNow,
    }
    storage_add("categories", ccCategory)
    return ccCategory


def category_get(cgId):
    return storage_get_by_id("categories", cgId)


def category_update(cuId, cuChanges):
    return storage_update("categories", cuId, cuChanges)


def category_delete(cdId):
    return storage_delete("categories", cdId)


def category_list():
    return storage_list("categories")


def category_list_by_parent(clpParentId):
    clpAll = storage_list("categories")
    clpResults = []
    for clpItem in clpAll:
        clpParent = helpers_get_map_value_safe(clpItem, "parent_id", "")
        if clpParent == clpParentId:
            clpResults.append(clpItem)
    return clpResults
