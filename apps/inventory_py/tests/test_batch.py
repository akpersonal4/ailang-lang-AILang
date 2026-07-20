from core.helpers import helpers_get_map_value_safe
from logistics.batch import (
    batch_create,
    batch_get_active_by_product,
    batch_get_by_id,
    batch_get_expiring_before,
    batch_list_by_product,
    batch_update_quantity,
)


def test_batch_create():
    tbcResult = batch_create("PRD-001", "BAT-2026-001", 100, "2026-12-31", "2026-01-15")
    if tbcResult is False:
        print("FAIL: batch_create returned false")
        return False
    tbcId = helpers_get_map_value_safe(tbcResult, "id", "")
    if tbcId == "":
        print("FAIL: batch_create - batch id missing")
        return False
    tbcQty = helpers_get_map_value_safe(tbcResult, "quantity", 0)
    if tbcQty != 100:
        print("FAIL: batch_create - expected quantity 100, got " + str(tbcQty))
        return False
    tbcProductId = helpers_get_map_value_safe(tbcResult, "product_id", "")
    if tbcProductId != "PRD-001":
        print("FAIL: batch_create - expected PRD-001, got " + tbcProductId)
        return False
    print("PASS: batch_create")
    return True


def test_batch_get_by_id_missing():
    tbgmResult = batch_get_by_id("NONEXISTENT-BATCH-ID")
    if tbgmResult is not False:
        print("FAIL: batch_get_by_id_missing - expected false")
        return False
    print("PASS: batch_get_by_id_missing")
    return True


def test_batch_list_by_product():
    batch_create("PRD-LIST-001", "BLP-001", 50, "2026-06-30", "2026-01-01")
    batch_create("PRD-LIST-001", "BLP-002", 75, "2026-07-31", "2026-01-01")
    tblpResults = batch_list_by_product("PRD-LIST-001")
    tblpLen = len(tblpResults)
    if tblpLen < 2:
        print("FAIL: batch_list_by_product - expected at least 2, got " + str(tblpLen))
        return False
    print("PASS: batch_list_by_product (" + str(tblpLen) + " items)")
    return True


def test_batch_update_quantity():
    tbuqBatch = batch_create("PRD-UPD-001", "BUQ-001", 200, "2026-09-30", "2026-02-01")
    tbuqId = helpers_get_map_value_safe(tbuqBatch, "id", "")
    tbuqResult = batch_update_quantity(tbuqId, 150)
    if tbuqResult is False:
        print("FAIL: batch_update_quantity returned false")
        return False
    tbuqUpdated = batch_get_by_id(tbuqId)
    if tbuqUpdated is False:
        print("FAIL: batch_update_quantity - batch not found after update")
        return False
    tbuqNewQty = helpers_get_map_value_safe(tbuqUpdated, "quantity", 0)
    if tbuqNewQty != 150:
        print("FAIL: batch_update_quantity - expected 150, got " + str(tbuqNewQty))
        return False
    print("PASS: batch_update_quantity")
    return True


def test_batch_get_expiring_before():
    batch_create("PRD-EXP-001", "GEB-001", 100, "2026-03-15", "2026-01-01")
    batch_create("PRD-EXP-001", "GEB-002", 100, "2026-09-15", "2026-01-01")
    tgebResults = batch_get_expiring_before("2026-06-01")
    tgebLen = len(tgebResults)
    if tgebLen == 0:
        print("FAIL: batch_get_expiring_before - expected at least 1 expiring batch")
        return False
    print("PASS: batch_get_expiring_before")
    return True


def test_batch_get_active_by_product():
    batch_create("PRD-ACT-001", "GAB-001", 50, "2026-12-31", "2026-01-01")
    batch_create("PRD-ACT-001", "GAB-002", 0, "2026-12-31", "2026-01-01")
    tgabResults = batch_get_active_by_product("PRD-ACT-001")
    tgabLen = len(tgabResults)
    if tgabLen == 0:
        print("FAIL: batch_get_active_by_product - expected at least 1 active batch")
        return False
    tgabFirst = tgabResults[0]
    tgabFirstQty = helpers_get_map_value_safe(tgabFirst, "quantity", 0)
    if tgabFirstQty <= 0:
        print("FAIL: batch_get_active_by_product - found batch with zero quantity")
        return False
    print("PASS: batch_get_active_by_product (" + str(tgabLen) + " active)")
    return True


def main():
    tb1 = test_batch_create()
    if tb1 is False:
        return 1
    tb2 = test_batch_get_by_id_missing()
    if tb2 is False:
        return 1
    tb3 = test_batch_list_by_product()
    if tb3 is False:
        return 1
    tb4 = test_batch_update_quantity()
    if tb4 is False:
        return 1
    tb5 = test_batch_get_expiring_before()
    if tb5 is False:
        return 1
    tb6 = test_batch_get_active_by_product()
    if tb6 is False:
        return 1
    print("ALL BATCH TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
