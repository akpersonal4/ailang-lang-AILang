from business.reorder import reorder_set_level, reorder_get_level, reorder_check, reorder_list_needed, reorder_calculate_lead_time_demand
from core.helpers import helpers_get_map_value_safe


def test_reorder_set_and_get_level():
    trsResult = reorder_set_level("ROR-PROD-001", 10, 100, 20)
    if trsResult == False:
        print("FAIL: reorder_set_level returned false")
        return False
    trsLevel = reorder_get_level("ROR-PROD-001")
    if trsLevel == False:
        print("FAIL: reorder_get_level returned false for existing level")
        return False
    trsMin = helpers_get_map_value_safe(trsLevel, "min_level", 0)
    if trsMin != 10:
        print("FAIL: reorder_get_level - min_level mismatch")
        return False
    trsMax = helpers_get_map_value_safe(trsLevel, "max_level", 0)
    if trsMax != 100:
        print("FAIL: reorder_get_level - max_level mismatch")
        return False
    trsQty = helpers_get_map_value_safe(trsLevel, "reorder_qty", 0)
    if trsQty != 20:
        print("FAIL: reorder_get_level - reorder_qty mismatch")
        return False
    print("PASS: reorder_set_and_get_level")
    return True


def test_reorder_check():
    trcLevel = reorder_get_level("ROR-PROD-001")
    if trcLevel == False:
        print("FAIL: reorder_check - no level config found")
        return False
    trcNeeded = reorder_check("ROR-PROD-001")
    if trcNeeded == False:
        print("FAIL: reorder_check - expected true (current_stock 0 < min_level 10)")
        return False
    print("PASS: reorder_check")
    return True


def test_reorder_check_missing():
    trcmNeeded = reorder_check("NONEXISTENT-PROD")
    if trcmNeeded != False:
        print("FAIL: reorder_check_missing - expected false")
        return False
    print("PASS: reorder_check_missing")
    return True


def test_reorder_list_needed():
    reorder_set_level("ROR-PROD-002", 5, 50, 10)
    trnNeeded = reorder_list_needed()
    if trnNeeded == False:
        print("FAIL: reorder_list_needed returned false")
        return False
    trnLen = len(trnNeeded)
    if trnLen == 0:
        print("FAIL: reorder_list_needed - expected at least 1 product needing reorder")
        return False
    print("PASS: reorder_list_needed (" + str(trnLen) + " items)")
    return True


def test_reorder_calculate_lead_time_demand():
    trcResult = reorder_calculate_lead_time_demand(10, 5)
    if trcResult != 50:
        print("FAIL: reorder_calculate_lead_time_demand - expected 50, got " + str(trcResult))
        return False
    print("PASS: reorder_calculate_lead_time_demand")
    return True


def main():
    tr1 = test_reorder_set_and_get_level()
    if tr1 == False:
        return 1
    tr2 = test_reorder_check()
    if tr2 == False:
        return 1
    tr3 = test_reorder_check_missing()
    if tr3 == False:
        return 1
    tr4 = test_reorder_list_needed()
    if tr4 == False:
        return 1
    tr5 = test_reorder_calculate_lead_time_demand()
    if tr5 == False:
        return 1
    print("ALL REORDER TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
