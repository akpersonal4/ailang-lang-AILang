from inventory.stock_transfer import transfer_create, transfer_get, transfer_complete, transfer_cancel
from inventory import stock_movement
from core.helpers import helpers_get_map_value_safe
from core.storage import storage_add


def test_st_get_nonexistent():
    stnResult = transfer_get("NONEXISTENT-TRF")
    if stnResult is not False:
        print("FAIL: expected false for nonexistent transfer")
        return False
    print("PASS: transfer_get_nonexistent")
    return True


def test_st_transfer_create_and_get():
    stpProd = {"id": "ST-PROD-1", "name": "Transfer Test Prod"}
    storage_add("products", stpProd)
    stpTrf = transfer_create("ST-PROD-1", "WH-A", "WH-B", 50)
    if stpTrf is False:
        print("FAIL: transfer_create returned false")
        return False
    stpId = helpers_get_map_value_safe(stpTrf, "id", "")
    stpGot = transfer_get(stpId)
    if stpGot is False:
        print("FAIL: transfer_get_by_id returned false")
        return False
    stpStatus = helpers_get_map_value_safe(stpGot, "status", "")
    if stpStatus != "pending":
        print("FAIL: expected status pending, got " + stpStatus)
        return False
    stpSource = helpers_get_map_value_safe(stpGot, "source_location", "")
    if stpSource != "WH-A":
        print("FAIL: expected source WH-A, got " + stpSource)
        return False
    stpDest = helpers_get_map_value_safe(stpGot, "destination_location", "")
    if stpDest != "WH-B":
        print("FAIL: expected destination WH-B, got " + stpDest)
        return False
    print("PASS: transfer_create and transfer_get")
    return True


def test_st_transfer_complete():
    stcProd = {"id": "ST-PROD-2", "name": "Complete Test Prod"}
    storage_add("products", stcProd)
    stcTrf = transfer_create("ST-PROD-2", "WH-A", "WH-C", 25)
    stcId = helpers_get_map_value_safe(stcTrf, "id", "")
    stcCompleted = transfer_complete(stcId)
    if stcCompleted is False:
        print("FAIL: transfer_complete returned false")
        return False
    stcStatus = helpers_get_map_value_safe(stcCompleted, "status", "")
    if stcStatus != "completed":
        print("FAIL: expected status completed, got " + stcStatus)
        return False
    stcCompletedAt = helpers_get_map_value_safe(stcCompleted, "completed_at", "")
    if stcCompletedAt == "":
        print("FAIL: completed_at should not be empty")
        return False
    print("PASS: transfer_complete")
    return True


def test_st_transfer_cancel():
    stxProd = {"id": "ST-PROD-3", "name": "Cancel Test Prod"}
    storage_add("products", stxProd)
    stxTrf = transfer_create("ST-PROD-3", "WH-B", "WH-C", 10)
    stxId = helpers_get_map_value_safe(stxTrf, "id", "")
    transfer_cancel(stxId)
    stxGot = transfer_get(stxId)
    stxStatus = helpers_get_map_value_safe(stxGot, "status", "")
    if stxStatus != "cancelled":
        print("FAIL: expected status cancelled, got " + stxStatus)
        return False
    print("PASS: transfer_cancel")
    return True


def main():
    st1 = test_st_get_nonexistent()
    if st1 is False:
        return 1
    st2 = test_st_transfer_create_and_get()
    if st2 is False:
        return 1
    st3 = test_st_transfer_complete()
    if st3 is False:
        return 1
    st4 = test_st_transfer_cancel()
    if st4 is False:
        return 1
    print("ALL STOCK TRANSFER TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
