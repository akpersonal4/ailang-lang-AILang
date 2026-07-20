from core.helpers import helpers_get_map_value_safe
from core.storage import storage_add
from inventory.transfer_integration import (
    ti_create_transfer,
    ti_get_by_id,
    ti_list_by_warehouse,
    ti_summary,
)


def test_ti_create_and_get():
    ttcg_prod = {}
    ttcg_prod["id"] = "TI-PROD-1"
    ttcg_prod["name"] = "TI Test Product"
    storage_add("products", ttcg_prod)
    ttcg_result = ti_create_transfer("TI-PROD-1", "WH-1", "WH-2", 50, "test_user")
    if ttcg_result == False:
        print("FAIL: ti_create_transfer returned false")
        return False
    ttcg_id = helpers_get_map_value_safe(ttcg_result, "id", "")
    if ttcg_id == "":
        print("FAIL: ti_create_transfer - id missing")
        return False
    ttcg_got = ti_get_by_id(ttcg_id)
    if ttcg_got == False:
        print("FAIL: ti_get_by_id returned false")
        return False
    ttcg_status = helpers_get_map_value_safe(ttcg_got, "status", "")
    if ttcg_status != "pending":
        print("FAIL: expected status pending, got " + ttcg_status)
        return False
    ttcg_qty = helpers_get_map_value_safe(ttcg_got, "quantity", 0)
    if ttcg_qty != 50:
        print("FAIL: expected quantity 50, got " + str(ttcg_qty))
        return False
    print("PASS: ti_create_and_get")
    return True


def test_ti_get_nonexistent():
    ttgn_result = ti_get_by_id("NONEXISTENT-TI-ID")
    if ttgn_result != False:
        print("FAIL: expected false for nonexistent transfer integration")
        return False
    print("PASS: ti_get_nonexistent")
    return True


def test_ti_list_by_warehouse():
    ttlw_prod = {}
    ttlw_prod["id"] = "TI-PROD-2"
    ttlw_prod["name"] = "TI Test Product 2"
    storage_add("products", ttlw_prod)
    ti_create_transfer("TI-PROD-2", "WH-A", "WH-B", 10, "user1")
    ti_create_transfer("TI-PROD-2", "WH-A", "WH-C", 20, "user1")
    ti_create_transfer("TI-PROD-2", "WH-B", "WH-C", 30, "user1")
    ttlw_results = ti_list_by_warehouse("WH-A")
    if ttlw_results == False:
        print("FAIL: ti_list_by_warehouse returned false")
        return False
    ttlw_len = len(ttlw_results)
    if ttlw_len < 2:
        print("FAIL: expected at least 2 for WH-A, got " + str(ttlw_len))
        return False
    print("PASS: ti_list_by_warehouse (" + str(ttlw_len) + " items)")
    return True


def test_ti_summary():
    tts_prod = {}
    tts_prod["id"] = "TI-PROD-3"
    tts_prod["name"] = "TI Test Product 3"
    storage_add("products", tts_prod)
    ti_create_transfer("TI-PROD-3", "WH-X", "WH-Y", 5, "user2")
    ti_create_transfer("TI-PROD-3", "WH-X", "WH-Z", 15, "user2")
    tts_summary = ti_summary()
    if tts_summary == False:
        print("FAIL: ti_summary returned false")
        return False
    tts_pending = helpers_get_map_value_safe(tts_summary, "pending", 0)
    if tts_pending < 2:
        print("FAIL: expected pending >= 2, got " + str(tts_pending))
        return False
    print("PASS: ti_summary (pending=" + str(tts_pending) + ")")
    return True


def main():
    tt1 = test_ti_create_and_get()
    if tt1 == False:
        return 1
    tt2 = test_ti_get_nonexistent()
    if tt2 == False:
        return 1
    tt3 = test_ti_list_by_warehouse()
    if tt3 == False:
        return 1
    tt4 = test_ti_summary()
    if tt4 == False:
        return 1
    print("ALL TRANSFER INTEGRATION TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
