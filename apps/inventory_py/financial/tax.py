from core.helpers import helpers_generate_id, helpers_current_timestamp, helpers_get_map_value_safe
from core.storage import storage_list, storage_add, storage_get_by_id, storage_update


def tax_create(txName, txRate, txCountry, txRegion):
    txId = helpers_generate_id("TAX-")
    txNow = helpers_current_timestamp()
    txRule = {
        "id": txId,
        "name": txName,
        "rate": txRate,
        "country": txCountry,
        "region": txRegion,
        "created_at": txNow,
    }
    storage_add("tax_rates", txRule)
    return txRule


def tax_get_by_id(txTaxId):
    return storage_get_by_id("tax_rates", txTaxId)


def tax_list():
    return storage_list("tax_rates")


def tax_calculate(tcAmount, tcTaxId):
    tcTax = storage_get_by_id("tax_rates", tcTaxId)
    if tcTax is False or tcTax is None:
        return 0
    tcRate = helpers_get_map_value_safe(tcTax, "rate", 0)
    return tcAmount * tcRate / 100


def tax_list_by_country(txCountry):
    txAll = storage_list("tax_rates")
    txResults = []
    for txItem in txAll:
        if helpers_get_map_value_safe(txItem, "country", "") == txCountry:
            txResults.append(txItem)
    return txResults


def tax_update_rate(turTaxId, turNewRate):
    turChanges = {"rate": turNewRate}
    return storage_update("tax_rates", turTaxId, turChanges)
