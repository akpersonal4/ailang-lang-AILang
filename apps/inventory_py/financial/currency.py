from core.helpers import helpers_get_map_value_safe
from core.storage import storage_list, storage_save


def currency_default_rates():
    return {
        "USD_EUR": 0.92,
        "USD_GBP": 0.79,
        "USD_JPY": 149,
        "USD_INR": 83,
    }


def currency_get_direct_rate(gdrFrom, gdrTo):
    gdrRates = currency_default_rates()
    if gdrFrom == "USD":
        gdrKey = "USD_" + gdrTo
        if gdrKey in gdrRates:
            return gdrRates[gdrKey]
        return False
    if gdrTo == "USD":
        gdrKey = "USD_" + gdrFrom
        if gdrKey in gdrRates:
            return 1.0 / gdrRates[gdrKey]
        return False
    gdrFromKey = "USD_" + gdrFrom
    gdrToKey = "USD_" + gdrTo
    if gdrFromKey in gdrRates and gdrToKey in gdrRates:
        gdrInUsd = 1.0 / gdrRates[gdrFromKey]
        return gdrInUsd * gdrRates[gdrToKey]
    return False


def currency_get_rate(cgrFrom, cgrTo):
    cgrKey = cgrFrom + "_" + cgrTo
    cgrStored = storage_list("currency_rates")
    for cgrItem in cgrStored:
        if helpers_get_map_value_safe(cgrItem, "key", "") == cgrKey:
            return helpers_get_map_value_safe(cgrItem, "rate", False)
    return currency_get_direct_rate(cgrFrom, cgrTo)


def currency_convert(ccAmount, ccFrom, ccTo):
    if ccFrom == ccTo:
        return ccAmount
    ccRate = currency_get_rate(ccFrom, ccTo)
    if ccRate is not False:
        return ccAmount * ccRate
    ccRevRate = currency_get_rate(ccTo, ccFrom)
    if ccRevRate is not False:
        return ccAmount / ccRevRate
    return ccAmount


def currency_format(cfAmount, cfCode):
    cfStr = str(cfAmount)
    symbols = {
        "USD": "$",
        "EUR": "\u20ac",
        "GBP": "\u00a3",
        "JPY": "\u00a5",
        "INR": "\u20b9",
    }
    if cfCode in symbols:
        return symbols[cfCode] + cfStr
    return cfStr


def currency_list():
    return ["USD", "EUR", "GBP", "JPY", "INR"]


def currency_set_rate(csrFrom, csrTo, csrRate):
    csrKey = csrFrom + "_" + csrTo
    csrExisting = storage_list("currency_rates")
    csrFiltered = [
        csrItem
        for csrItem in csrExisting
        if helpers_get_map_value_safe(csrItem, "key", "") != csrKey
    ]
    csrEntry = {"key": csrKey, "rate": csrRate}
    csrFiltered.append(csrEntry)
    storage_save("currency_rates", csrFiltered)
    return True
