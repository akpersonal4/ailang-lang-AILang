from core.helpers import helpers_get_map_value_safe
from core.storage import storage_add
from inventory.stock_adjustment import (
    adjustment_create,
    adjustment_get_by_id,
    adjustment_get_discrepancies,
    adjustment_list_by_product,
    adjustment_summary,
)


def test_adj_create_and_get():
    tagProd = {"id": "ADJ-TEST-PROD-1", "name": "Adjustment Test Product"}
    storage_add("products", tagProd)
    tagAdj = adjustment_create("ADJ-TEST-PROD-1", 50, 60, "Test adjustment", "tester")
    if tagAdj is False:
        print("FAIL: adjustment_create returned false")
        return False
    tagId = helpers_get_map_value_safe(tagAdj, "id", "")
    if tagId == "":
        print("FAIL: adjustment has no id")
        return False
    tagFetched = adjustment_get_by_id(tagId)
    if tagFetched is False:
        print("FAIL: could not fetch adjustment by id")
        return False
    tagDiff = helpers_get_map_value_safe(tagFetched, "difference", 0)
    if tagDiff != 10:
        print("FAIL: expected difference 10, got " + str(tagDiff))
        return False
    print("PASS: adjustment_create and get_by_id")
    return True


def test_adj_list_by_product():
    talProd = {"id": "ADJ-TEST-PROD-2", "name": "Adj List Product"}
    storage_add("products", talProd)
    adjustment_create("ADJ-TEST-PROD-2", 100, 120, "First adj", "tester")
    adjustment_create("ADJ-TEST-PROD-2", 120, 110, "Second adj", "tester")
    talList = adjustment_list_by_product("ADJ-TEST-PROD-2")
    talLen = len(talList)
    if talLen != 2:
        print("FAIL: expected 2 adjustments, got " + str(talLen))
        return False
    print("PASS: adjustment_list_by_product")
    return True


def test_adj_discrepancies():
    tadProd = {"id": "ADJ-TEST-PROD-3", "name": "Discrepancy Product"}
    storage_add("products", tadProd)
    adjustment_create("ADJ-TEST-PROD-3", 100, 105, "Small diff", "tester")
    adjustment_create("ADJ-TEST-PROD-3", 50, 100, "Large diff", "tester")
    tadDisc = adjustment_get_discrepancies(10)
    tadLen = len(tadDisc)
    if tadLen == 0:
        print("FAIL: expected at least 1 discrepancy")
        return False
    print("PASS: adjustment_get_discrepancies")
    return True


def test_adj_summary():
    tasProd = {"id": "ADJ-TEST-PROD-4", "name": "Summary Product"}
    storage_add("products", tasProd)
    adjustment_create("ADJ-TEST-PROD-4", 50, 60, "Pos adj", "tester")
    adjustment_create("ADJ-TEST-PROD-4", 100, 80, "Neg adj", "tester")
    tasSummary = adjustment_summary()
    tasTotal = helpers_get_map_value_safe(tasSummary, "total_adjustments", 0)
    if tasTotal == 0:
        print("FAIL: expected non-zero total_adjustments")
        return False
    print("PASS: adjustment_summary")
    return True


def main():
    ta1 = test_adj_create_and_get()
    if ta1 is False:
        return 1
    ta2 = test_adj_list_by_product()
    if ta2 is False:
        return 1
    ta3 = test_adj_discrepancies()
    if ta3 is False:
        return 1
    ta4 = test_adj_summary()
    if ta4 is False:
        return 1
    print("ALL STOCK ADJUSTMENT TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
