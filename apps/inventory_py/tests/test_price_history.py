from business.price_history import (
    price_history_get_by_product,
    price_history_latest,
    price_history_list,
    price_history_record,
)
from core.helpers import helpers_get_map_value_safe


def test_price_history_record():
    tpResult = price_history_record("PROD-PH-001", 100, 120, "admin")
    if tpResult == False:
        print("FAIL: price_history_record returned false")
        return False
    tpId = helpers_get_map_value_safe(tpResult, "id", "")
    if tpId == "":
        print("FAIL: price_history_record - no id")
        return False
    tpProductId = helpers_get_map_value_safe(tpResult, "product_id", "")
    if tpProductId != "PROD-PH-001":
        print("FAIL: price_history_record - product_id mismatch")
        return False
    tpOldPrice = helpers_get_map_value_safe(tpResult, "old_price", 0)
    if tpOldPrice != 100:
        print("FAIL: price_history_record - old_price mismatch")
        return False
    tpNewPrice = helpers_get_map_value_safe(tpResult, "new_price", 0)
    if tpNewPrice != 120:
        print("FAIL: price_history_record - new_price mismatch")
        return False
    print("PASS: price_history_record")
    return True


def test_price_history_get_by_product():
    price_history_record("PROD-PH-002", 200, 220, "editor")
    price_history_record("PROD-PH-002", 220, 250, "editor")
    price_history_record("PROD-PH-003", 50, 60, "viewer")
    tpResults = price_history_get_by_product("PROD-PH-002")
    if tpResults == False:
        print("FAIL: price_history_get_by_product returned false")
        return False
    tpLen = len(tpResults)
    if tpLen != 2:
        print("FAIL: price_history_get_by_product - expected 2, got " + str(tpLen))
        return False
    print("PASS: price_history_get_by_product (" + str(tpLen) + " items)")
    return True


def test_price_history_latest():
    price_history_record("PROD-PH-004", 300, 350, "manager")
    price_history_record("PROD-PH-004", 350, 400, "manager")
    tpLatest = price_history_latest("PROD-PH-004")
    if tpLatest == False:
        print("FAIL: price_history_latest returned false")
        return False
    tpNewPrice = helpers_get_map_value_safe(tpLatest, "new_price", 0)
    if tpNewPrice != 400:
        print(
            "FAIL: price_history_latest - expected new_price 400, got "
            + str(tpNewPrice)
        )
        return False
    print("PASS: price_history_latest")
    return True


def test_price_history_latest_empty():
    tpLatest = price_history_latest("PROD-PH-NONEXISTENT")
    if tpLatest != False:
        print("FAIL: price_history_latest_empty - expected false")
        return False
    print("PASS: price_history_latest_empty")
    return True


def test_price_history_list():
    tpResults = price_history_list()
    if tpResults == False:
        print("FAIL: price_history_list returned false")
        return False
    tpLen = len(tpResults)
    if tpLen == 0:
        print("FAIL: price_history_list - empty list")
        return False
    print("PASS: price_history_list (" + str(tpLen) + " items)")
    return True


def main():
    tpr1 = test_price_history_record()
    if tpr1 == False:
        return 1
    tpr2 = test_price_history_get_by_product()
    if tpr2 == False:
        return 1
    tpr3 = test_price_history_latest()
    if tpr3 == False:
        return 1
    tpr4 = test_price_history_latest_empty()
    if tpr4 == False:
        return 1
    tpr5 = test_price_history_list()
    if tpr5 == False:
        return 1
    print("ALL PRICE HISTORY TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
