from inventory.stock_reservation import reservation_create, reservation_get_by_id, reservation_list_by_order, reservation_fulfill, reservation_cancel, reservation_check_availability
from inventory import stock_movement
from core.helpers import helpers_get_map_value_safe
from core.storage import storage_add


def test_rsrv_create_and_get():
    trsProd = {"id": "RSRV-TEST-PROD-1", "name": "Reservation Test Product"}
    storage_add("products", trsProd)
    stock_movement.movement_create("RSRV-TEST-PROD-1", "inbound", 100, "manual", "INIT", "Initial stock")
    trsRes = reservation_create("RSRV-TEST-ORDER-1", "RSRV-TEST-PROD-1", 30)
    if trsRes is False:
        print("FAIL: reservation_create returned false")
        return False
    trsId = helpers_get_map_value_safe(trsRes, "id", "")
    if trsId == "":
        print("FAIL: reservation has no id")
        return False
    trsFetched = reservation_get_by_id(trsId)
    if trsFetched is False:
        print("FAIL: could not fetch reservation by id")
        return False
    print("PASS: reservation_create and get_by_id")
    return True


def test_rsrv_list_by_order():
    trsoProd = {"id": "RSRV-TEST-PROD-2", "name": "Reservation List Product"}
    storage_add("products", trsoProd)
    stock_movement.movement_create("RSRV-TEST-PROD-2", "inbound", 100, "manual", "INIT", "Initial stock")
    reservation_create("RSRV-TEST-ORDER-2", "RSRV-TEST-PROD-2", 20)
    reservation_create("RSRV-TEST-ORDER-2", "RSRV-TEST-PROD-2", 30)
    trsoList = reservation_list_by_order("RSRV-TEST-ORDER-2")
    trsoLen = len(trsoList)
    if trsoLen != 2:
        print("FAIL: expected 2 reservations, got " + str(trsoLen))
        return False
    print("PASS: reservation_list_by_order")
    return True


def test_rsrv_fulfill():
    trfProd = {"id": "RSRV-TEST-PROD-3", "name": "Fulfill Product"}
    storage_add("products", trfProd)
    stock_movement.movement_create("RSRV-TEST-PROD-3", "inbound", 100, "manual", "INIT", "Initial stock")
    trfRes = reservation_create("RSRV-TEST-ORDER-3", "RSRV-TEST-PROD-3", 10)
    trfId = helpers_get_map_value_safe(trfRes, "id", "")
    trfResult = reservation_fulfill(trfId)
    if trfResult is False:
        print("FAIL: fulfill returned false")
        return False
    trfFetched = reservation_get_by_id(trfId)
    trfStatus = helpers_get_map_value_safe(trfFetched, "status", "")
    if trfStatus != "fulfilled":
        print("FAIL: expected status fulfilled, got " + trfStatus)
        return False
    print("PASS: reservation_fulfill")
    return True


def test_rsrv_cancel():
    trcProd = {"id": "RSRV-TEST-PROD-4", "name": "Cancel Product"}
    storage_add("products", trcProd)
    stock_movement.movement_create("RSRV-TEST-PROD-4", "inbound", 100, "manual", "INIT", "Initial stock")
    trcRes = reservation_create("RSRV-TEST-ORDER-4", "RSRV-TEST-PROD-4", 10)
    trcId = helpers_get_map_value_safe(trcRes, "id", "")
    trcResult = reservation_cancel(trcId)
    if trcResult is False:
        print("FAIL: cancel returned false")
        return False
    trcFetched = reservation_get_by_id(trcId)
    trcStatus = helpers_get_map_value_safe(trcFetched, "status", "")
    if trcStatus != "cancelled":
        print("FAIL: expected status cancelled, got " + trcStatus)
        return False
    print("PASS: reservation_cancel")
    return True


def test_rsrv_check_availability():
    trcaProd = {"id": "RSRV-TEST-PROD-5", "name": "Availability Product"}
    storage_add("products", trcaProd)
    stock_movement.movement_create("RSRV-TEST-PROD-5", "inbound", 50, "manual", "INIT", "Initial stock")
    trcaAvailable = reservation_check_availability("RSRV-TEST-PROD-5", 30)
    if trcaAvailable is not True:
        print("FAIL: expected true for available stock")
        return False
    trcaNotAvailable = reservation_check_availability("RSRV-TEST-PROD-5", 100)
    if trcaNotAvailable is not False:
        print("FAIL: expected false for insufficient stock")
        return False
    print("PASS: reservation_check_availability")
    return True


def main():
    tr1 = test_rsrv_create_and_get()
    if tr1 is False:
        return 1
    tr2 = test_rsrv_list_by_order()
    if tr2 is False:
        return 1
    tr3 = test_rsrv_fulfill()
    if tr3 is False:
        return 1
    tr4 = test_rsrv_cancel()
    if tr4 is False:
        return 1
    tr5 = test_rsrv_check_availability()
    if tr5 is False:
        return 1
    print("ALL STOCK RESERVATION TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
