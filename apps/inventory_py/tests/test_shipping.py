from orders.shipping import shipping_create, shipping_get_by_id, shipping_update_status, shipping_list_by_order, shipping_list_by_status
from core.helpers import helpers_get_map_value_safe


def test_shipping_create():
    tscResult = shipping_create("SO-SHP-001", "FedEx", "FX-123456789", "123 Main St, City", "Warehouse A")
    if tscResult == False:
        print("FAIL: shipping_create returned false")
        return False
    tscId = helpers_get_map_value_safe(tscResult, "id", "")
    if tscId == "":
        print("FAIL: shipping_create - no id generated")
        return False
    tscStatus = helpers_get_map_value_safe(tscResult, "status", "")
    if tscStatus != "pending":
        print("FAIL: shipping_create - expected status pending, got " + tscStatus)
        return False
    tscCarrier = helpers_get_map_value_safe(tscResult, "carrier", "")
    if tscCarrier != "FedEx":
        print("FAIL: shipping_create - carrier mismatch")
        return False
    print("PASS: shipping_create")
    return True


def test_shipping_get_by_id_missing():
    tsgmResult = shipping_get_by_id("NONEXISTENT-SHIPMENT-ID")
    if tsgmResult != False:
        print("FAIL: shipping_get_by_id_missing - expected false")
        return False
    print("PASS: shipping_get_by_id_missing")
    return True


def test_shipping_update_status():
    tsusCreated = shipping_create("SO-SHP-002", "UPS", "UP-987654321", "456 Oak Ave, Town", "Warehouse B")
    tsusId = helpers_get_map_value_safe(tsusCreated, "id", "")
    tsusUpdated = shipping_update_status(tsusId, "in_transit")
    if tsusUpdated == False:
        print("FAIL: shipping_update_status returned false")
        return False
    tsusFetched = shipping_get_by_id(tsusId)
    tsusStatus = helpers_get_map_value_safe(tsusFetched, "status", "")
    if tsusStatus != "in_transit":
        print("FAIL: shipping_update_status - expected in_transit, got " + tsusStatus)
        return False
    print("PASS: shipping_update_status")
    return True


def test_shipping_list_by_order():
    tslo1 = shipping_create("SO-LIST-SHP", "USPS", "TRK-111", "Addr 1", "User X")
    tslo2 = shipping_create("SO-LIST-SHP", "DHL", "TRK-222", "Addr 2", "User Y")
    tsloResults = shipping_list_by_order("SO-LIST-SHP")
    tsloLen = len(tsloResults)
    if tsloLen < 2:
        print("FAIL: shipping_list_by_order - expected at least 2, got " + str(tsloLen))
        return False
    print("PASS: shipping_list_by_order (" + str(tsloLen) + " items)")
    return True


def test_shipping_list_by_status():
    tsls1 = shipping_create("SO-STATUS-1", "FedEx", "FX-AAA", "Addr S1", "Ops 1")
    tsls1Id = helpers_get_map_value_safe(tsls1, "id", "")
    shipping_update_status(tsls1Id, "delivered")
    tsls2 = shipping_create("SO-STATUS-2", "UPS", "UP-BBB", "Addr S2", "Ops 2")
    tsls2Id = helpers_get_map_value_safe(tsls2, "id", "")
    shipping_update_status(tsls2Id, "delivered")
    tslsResults = shipping_list_by_status("delivered")
    tslsLen = len(tslsResults)
    if tslsLen < 2:
        print("FAIL: shipping_list_by_status - expected at least 2, got " + str(tslsLen))
        return False
    print("PASS: shipping_list_by_status (" + str(tslsLen) + " items)")
    return True


def main():
    ts1 = test_shipping_create()
    if ts1 == False:
        return 1
    ts2 = test_shipping_get_by_id_missing()
    if ts2 == False:
        return 1
    ts3 = test_shipping_update_status()
    if ts3 == False:
        return 1
    ts4 = test_shipping_list_by_order()
    if ts4 == False:
        return 1
    ts5 = test_shipping_list_by_status()
    if ts5 == False:
        return 1
    print("ALL SHIPPING TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
