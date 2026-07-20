from core.helpers import helpers_get_map_value_safe
from financial.tax import (
    tax_calculate,
    tax_create,
    tax_get_by_id,
    tax_list_by_country,
    tax_update_rate,
)


def test_tax_create():
    ttcResult = tax_create("VAT Standard", 20, "GB", "England")
    if ttcResult == False:
        print("FAIL: tax_create returned false")
        return False
    ttcId = helpers_get_map_value_safe(ttcResult, "id", "")
    if ttcId == "":
        print("FAIL: tax_create - tax id missing")
        return False
    ttcName = helpers_get_map_value_safe(ttcResult, "name", "")
    if ttcName != "VAT Standard":
        print("FAIL: tax_create - expected VAT Standard, got " + ttcName)
        return False
    ttcRate = helpers_get_map_value_safe(ttcResult, "rate", 0)
    if ttcRate != 20:
        print("FAIL: tax_create - expected rate 20, got " + str(ttcRate))
        return False
    print("PASS: tax_create")
    return True


def test_tax_get_by_id_missing():
    ttgmResult = tax_get_by_id("NONEXISTENT-TAX-ID")
    if ttgmResult != False:
        print("FAIL: tax_get_by_id_missing - expected false")
        return False
    print("PASS: tax_get_by_id_missing")
    return True


def test_tax_calculate():
    ttcalcTax = tax_create("Sales Tax", 10, "US", "California")
    ttcalcId = helpers_get_map_value_safe(ttcalcTax, "id", "")
    ttcalcResult = tax_calculate(1000, ttcalcId)
    if ttcalcResult != 100:
        print("FAIL: tax_calculate - expected 100, got " + str(ttcalcResult))
        return False
    print("PASS: tax_calculate (" + str(ttcalcResult) + ")")
    return True


def test_tax_list_by_country():
    tlbc1 = tax_create("VAT France", 20, "FR", "Ile-de-France")
    tlbc2 = tax_create("VAT France Reduced", 10, "FR", "Ile-de-France")
    tlbcResult = tax_list_by_country("FR")
    tlbcLen = len(tlbcResult)
    if tlbcLen < 2:
        print("FAIL: tax_list_by_country - expected at least 2, got " + str(tlbcLen))
        return False
    print("PASS: tax_list_by_country (" + str(tlbcLen) + " items)")
    return True


def test_tax_update_rate():
    turTax = tax_create("GST", 18, "IN", "Maharashtra")
    turId = helpers_get_map_value_safe(turTax, "id", "")
    turResult = tax_update_rate(turId, 15)
    if turResult == False:
        print("FAIL: tax_update_rate returned false")
        return False
    turCalcResult = tax_calculate(200, turId)
    if turCalcResult != 30:
        print(
            "FAIL: tax_update_rate - expected 30 after update, got "
            + str(turCalcResult)
        )
        return False
    print("PASS: tax_update_rate")
    return True


def main():
    tt1 = test_tax_create()
    if tt1 == False:
        return 1
    tt2 = test_tax_get_by_id_missing()
    if tt2 == False:
        return 1
    tt3 = test_tax_calculate()
    if tt3 == False:
        return 1
    tt4 = test_tax_list_by_country()
    if tt4 == False:
        return 1
    tt5 = test_tax_update_rate()
    if tt5 == False:
        return 1
    print("ALL TAX TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
