from core.helpers import helpers_generate_id, helpers_current_timestamp, helpers_get_map_value_safe
from core.storage import storage_add, storage_get_by_id, storage_update, storage_delete, storage_list

def vendor_create(vcName, vcEmail, vcPhone, vcContact):
    vcId = helpers_generate_id("VEN-")
    vcNow = helpers_current_timestamp()
    vcVendor = {
        "id": vcId,
        "name": vcName,
        "email": vcEmail,
        "phone": vcPhone,
        "contact_person": vcContact,
        "active": True,
        "created_at": vcNow,
        "updated_at": vcNow,
    }
    storage_add("vendors", vcVendor)
    return vcVendor

def vendor_get(vgId):
    return storage_get_by_id("vendors", vgId)

def vendor_update(vuId, vuChanges):
    vuNow = helpers_current_timestamp()
    vuChanges["updated_at"] = vuNow
    return storage_update("vendors", vuId, vuChanges)

def vendor_delete(vdId):
    return storage_delete("vendors", vdId)

def vendor_list():
    return storage_list("vendors")

def vendor_search(vsQuery):
    vsAll = storage_list("vendors")
    vsResults = []
    vrQueryLower = vsQuery.lower()
    for vrItem in vsAll:
        vrName = helpers_get_map_value_safe(vrItem, "name", "")
        vrNameLower = vrName.lower()
        if vrQueryLower in vrNameLower:
            vsResults.append(vrItem)
    return vsResults
