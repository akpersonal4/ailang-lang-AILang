from core.helpers import helpers_get_map_value_safe
from models.warehouse import warehouse_create, warehouse_get_by_id, warehouse_search, warehouse_list


def test_warehouse_create():
    twc_result = warehouse_create("Main Warehouse", "WH-001", "123 Main St", "New York", "USA")
    if twc_result == False:
        print("FAIL: warehouse_create returned false")
        return False
    twc_id = helpers_get_map_value_safe(twc_result, "id", "")
    if twc_id == "":
        print("FAIL: warehouse_create - no id")
        return False
    twc_name = helpers_get_map_value_safe(twc_result, "name", "")
    if twc_name != "Main Warehouse":
        print("FAIL: warehouse_create - name mismatch")
        return False
    twc_code = helpers_get_map_value_safe(twc_result, "code", "")
    if twc_code != "WH-001":
        print("FAIL: warehouse_create - code mismatch")
        return False
    twc_city = helpers_get_map_value_safe(twc_result, "city", "")
    if twc_city != "New York":
        print("FAIL: warehouse_create - city mismatch")
        return False
    print("PASS: warehouse_create")
    return True


def test_warehouse_get_by_id_missing():
    twgm_result = warehouse_get_by_id("NONEXISTENT-WH-ID")
    if twgm_result != False:
        print("FAIL: warehouse_get_by_id_missing - expected false")
        return False
    print("PASS: warehouse_get_by_id_missing")
    return True


def test_warehouse_get_by_id():
    twg_created = warehouse_create("GetTest WH", "WH-GET", "456 Oak Ave", "Chicago", "USA")
    twg_id = helpers_get_map_value_safe(twg_created, "id", "")
    twg_found = warehouse_get_by_id(twg_id)
    if twg_found == False:
        print("FAIL: warehouse_get_by_id returned false for existing warehouse")
        return False
    twg_name = helpers_get_map_value_safe(twg_found, "name", "")
    if twg_name != "GetTest WH":
        print("FAIL: warehouse_get_by_id - name mismatch")
        return False
    print("PASS: warehouse_get_by_id")
    return True


def test_warehouse_search_by_name():
    tws_created = warehouse_create("SearchTest Warehouse", "SRC-001", "789 Pine Rd", "Houston", "USA")
    tws_results = warehouse_search("SearchTest")
    if tws_results == False:
        print("FAIL: warehouse_search_by_name returned false")
        return False
    tws_len = len(tws_results)
    if tws_len == 0:
        print("FAIL: warehouse_search_by_name - no results")
        return False
    tws_first = tws_results[0]
    tws_first_name = helpers_get_map_value_safe(tws_first, "name", "")
    if tws_first_name != "SearchTest Warehouse":
        print("FAIL: warehouse_search_by_name - wrong name")
        return False
    print("PASS: warehouse_search_by_name (" + str(tws_len) + " items)")
    return True


def test_warehouse_search_by_code():
    twsc_results = warehouse_search("SRC-001")
    twsc_len = len(twsc_results)
    if twsc_len == 0:
        print("FAIL: warehouse_search_by_code - no results")
        return False
    print("PASS: warehouse_search_by_code (" + str(twsc_len) + " items)")
    return True


def main():
    twr1 = test_warehouse_create()
    if twr1 == False:
        return 1
    twr2 = test_warehouse_get_by_id_missing()
    if twr2 == False:
        return 1
    twr3 = test_warehouse_get_by_id()
    if twr3 == False:
        return 1
    twr4 = test_warehouse_search_by_name()
    if twr4 == False:
        return 1
    twr5 = test_warehouse_search_by_code()
    if twr5 == False:
        return 1
    print("ALL WAREHOUSE TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
