from core.helpers import (
    helpers_current_timestamp,
    helpers_generate_id,
    helpers_get_map_value_safe,
)
from core.storage import storage_add, storage_get_by_id, storage_list, storage_update


def supplier_create(
    spName,
    spContactPerson,
    spEmail,
    spPhone,
    spAddress,
    spPaymentTerms,
    spLeadTimeDays,
    spRating,
):
    spId = helpers_generate_id("SUP-")
    spNow = helpers_current_timestamp()
    spSupplier = {
        "id": spId,
        "name": spName,
        "contact_person": spContactPerson,
        "email": spEmail,
        "phone": spPhone,
        "address": spAddress,
        "payment_terms": spPaymentTerms,
        "lead_time_days": spLeadTimeDays,
        "rating": spRating,
        "active": True,
        "created_at": spNow,
        "updated_at": spNow,
    }
    storage_add("suppliers", spSupplier)
    return spSupplier


def supplier_get_by_id(spSupId):
    return storage_get_by_id("suppliers", spSupId)


def supplier_list():
    return storage_list("suppliers")


def supplier_update(spSupId, spChanges):
    spNow = helpers_current_timestamp()
    spChanges["updated_at"] = spNow
    return storage_update("suppliers", spSupId, spChanges)


def supplier_search(spSearchTerm):
    spAll = storage_list("suppliers")
    spResults = []
    spTermLower = spSearchTerm.lower()
    for spItem in spAll:
        spName = helpers_get_map_value_safe(spItem, "name", "")
        spContact = helpers_get_map_value_safe(spItem, "contact_person", "")
        spEmail = helpers_get_map_value_safe(spItem, "email", "")
        if (
            spTermLower in spName.lower()
            or spTermLower in spContact.lower()
            or spTermLower in spEmail.lower()
        ):
            spResults.append(spItem)
    return spResults


def supplier_top_rated(spMinRating):
    spAll = storage_list("suppliers")
    spResults = []
    for spItem in spAll:
        spRating = helpers_get_map_value_safe(spItem, "rating", 0)
        if spRating >= spMinRating:
            spResults.append(spItem)
    return spResults


def supplier_get_by_payment_terms(spTerms):
    spAll = storage_list("suppliers")
    spResults = []
    for spItem in spAll:
        spPayment = helpers_get_map_value_safe(spItem, "payment_terms", "")
        if spPayment == spTerms:
            spResults.append(spItem)
    return spResults
