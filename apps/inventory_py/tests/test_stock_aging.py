from core.helpers import helpers_get_map_value_safe, helpers_unix_timestamp
from inventory.stock_aging import (
    stock_aging_get_batches,
    stock_aging_record,
    stock_aging_remove_batch,
    stock_aging_summary,
)


def test_stock_aging_record_and_get_batches():
    tsagNow = helpers_unix_timestamp()
    tsagRecord = stock_aging_record("SAG-PROD-001", "SAG-WH-001", 50, tsagNow)
    if tsagRecord is False:
        print("FAIL: stock_aging_record returned false")
        return False
    tsagBatches = stock_aging_get_batches("SAG-PROD-001", "SAG-WH-001")
    if tsagBatches is False:
        print("FAIL: stock_aging_get_batches returned false")
        return False
    tsagLen = len(tsagBatches)
    if tsagLen == 0:
        print("FAIL: stock_aging_get_batches - no batches found")
        return False
    tsagFirst = tsagBatches[0]
    tsagProdId = helpers_get_map_value_safe(tsagFirst, "product_id", "")
    if tsagProdId != "SAG-PROD-001":
        print("FAIL: stock_aging_get_batches - wrong product_id")
        return False
    print("PASS: stock_aging_record and get_batches")
    return True


def test_stock_aging_summary():
    tsasNow = helpers_unix_timestamp()
    stock_aging_record("SAG-PROD-002", "SAG-WH-001", 100, tsasNow)
    tsasOld = tsasNow - 7000000
    stock_aging_record("SAG-PROD-002", "SAG-WH-001", 50, tsasOld)
    tsasSummary = stock_aging_summary("SAG-PROD-002")
    if tsasSummary is False:
        print("FAIL: stock_aging_summary returned false")
        return False
    tsas0_30 = helpers_get_map_value_safe(tsasSummary, "0_30_days", -1)
    if tsas0_30 <= 0:
        print("FAIL: stock_aging_summary - expected positive 0_30_days")
        return False
    tsas61_90 = helpers_get_map_value_safe(tsasSummary, "61_90_days", -1)
    if tsas61_90 <= 0:
        print(
            "FAIL: stock_aging_summary - expected positive 61_90_days for old batch (7000000s = ~81 days)"
        )
        return False
    print("PASS: stock_aging_summary")
    return True


def test_stock_aging_remove_batch():
    tsarNow = helpers_unix_timestamp()
    tsarRecord = stock_aging_record("SAG-PROD-003", "SAG-WH-001", 25, tsarNow)
    tsarBatchId = helpers_get_map_value_safe(tsarRecord, "id", "")
    tsarBefore = stock_aging_get_batches("SAG-PROD-003", "SAG-WH-001")
    tsarBeforeLen = len(tsarBefore)
    tsarRemove = stock_aging_remove_batch("SAG-PROD-003", "SAG-WH-001", tsarBatchId)
    if tsarRemove is False:
        print("FAIL: stock_aging_remove_batch returned false")
        return False
    tsarAfter = stock_aging_get_batches("SAG-PROD-003", "SAG-WH-001")
    tsarAfterLen = len(tsarAfter)
    if tsarAfterLen >= tsarBeforeLen:
        print("FAIL: stock_aging_remove_batch - count did not decrease")
        return False
    print("PASS: stock_aging_remove_batch")
    return True


def main():
    tsa1 = test_stock_aging_record_and_get_batches()
    if tsa1 is False:
        return 1
    tsa2 = test_stock_aging_summary()
    if tsa2 is False:
        return 1
    tsa3 = test_stock_aging_remove_batch()
    if tsa3 is False:
        return 1
    print("ALL STOCK AGING TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
