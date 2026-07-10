from core.helpers import helpers_get_map_value_safe, helpers_current_timestamp, helpers_find_in_list
from core.storage import storage_add, storage_list
from business.notification import notification_check_low_stock, notification_check_out_of_stock
from business.search import search_all


def tn_create_product():
    tnpProduct = {
        "id": "TNOT-PRD-001",
        "name": "Test Notification Product",
        "sku": "NOT-001",
        "category_id": "",
        "unit_price": 30,
        "cost_price": 15,
        "unit": "pcs",
        "active": True,
        "created_at": helpers_current_timestamp(),
        "updated_at": ""
    }
    storage_add("products", tnpProduct)
    tnpLoaded = helpers_find_in_list(storage_list("products"), "id", "TNOT-PRD-001")
    if tnpLoaded == False:
        return False
    return True


def tn_create_valuation_low():
    tnvlVal = {
        "id": "TNOT-VAL-001",
        "product_id": "TNOT-PRD-001",
        "method": "fifo",
        "current_cost": 15,
        "quantity_on_hand": 2,
        "last_updated": helpers_current_timestamp()
    }
    storage_add("valuations", tnvlVal)
    tnvlLoaded = helpers_find_in_list(storage_list("valuations"), "id", "TNOT-VAL-001")
    if tnvlLoaded == False:
        return False
    return True


def tn_create_valuation_out():
    tnvoVal = {
        "id": "TNOT-VAL-002",
        "product_id": "TNOT-PRD-002",
        "method": "fifo",
        "current_cost": 0,
        "quantity_on_hand": 0,
        "last_updated": helpers_current_timestamp()
    }
    storage_add("valuations", tnvoVal)
    tnvoLoaded = helpers_find_in_list(storage_list("valuations"), "id", "TNOT-VAL-002")
    if tnvoLoaded == False:
        return False
    return True


def tn_create_search_customer():
    tnscCustomer = {
        "id": "TNOT-CUS-001",
        "name": "Test Search Customer",
        "email": "search@test.com",
        "phone": "555-SRC",
        "active": True,
        "created_at": helpers_current_timestamp(),
        "updated_at": helpers_current_timestamp()
    }
    storage_add("customers", tnscCustomer)
    tnscLoaded = helpers_find_in_list(storage_list("customers"), "id", "TNOT-CUS-001")
    if tnscLoaded == False:
        return False
    return True


def tn_create_search_vendor():
    tnsvVendor = {
        "id": "TNOT-VEN-001",
        "name": "Test Search Vendor",
        "email": "vendor@test.com",
        "phone": "555-VEN",
        "contact_person": "SearchContact",
        "active": True,
        "created_at": helpers_current_timestamp(),
        "updated_at": helpers_current_timestamp()
    }
    storage_add("vendors", tnsvVendor)
    tnsvLoaded = helpers_find_in_list(storage_list("vendors"), "id", "TNOT-VEN-001")
    if tnsvLoaded == False:
        return False
    return True


def tn_find_result_rec(tnfrItems, tnfrTarget, tnfrIdx):
    if tnfrIdx >= len(tnfrItems):
        return False
    tnfrItem = tnfrItems[tnfrIdx]
    tnfrProdId = helpers_get_map_value_safe(tnfrItem, "product_id", "")
    if tnfrProdId == tnfrTarget:
        return tnfrItem
    return tn_find_result_rec(tnfrItems, tnfrTarget, tnfrIdx + 1)


def tn_find_result(tnfrItems, tnfrTarget):
    return tn_find_result_rec(tnfrItems, tnfrTarget, 0)


def tn_test_low_stock():
    tnlsItems = notification_check_low_stock(5)
    tnlsCount = len(tnlsItems)
    if tnlsCount == 0:
        print("FAIL: notification_check_low_stock returned empty")
        return False
    tnlsFound = tn_find_result(tnlsItems, "TNOT-PRD-001")
    if tnlsFound == False:
        print("FAIL: low stock did not find TNOT-PRD-001 in results")
        return False
    print("PASS: notification_check_low_stock (found " + str(tnlsCount) + " low)")
    return True


def tn_test_out_of_stock():
    tnosItems = notification_check_out_of_stock()
    tnosFound = tn_find_result(tnosItems, "TNOT-PRD-002")
    if tnosFound == False:
        print("FAIL: notification_check_out_of_stock did not find TNOT-PRD-002")
        return False
    print("PASS: notification_check_out_of_stock")
    return True


def tn_test_search():
    tnsrResults = search_all("Test")
    tnsrCount = len(tnsrResults)
    if tnsrCount == 0:
        print("FAIL: search_all returned empty results")
        return False
    print("PASS: search_all (" + str(tnsrCount) + " results)")
    return True


def main():
    tm1 = tn_create_product()
    if tm1 == False:
        return 1
    tm2 = tn_create_valuation_low()
    if tm2 == False:
        return 1
    tm3 = tn_create_valuation_out()
    if tm3 == False:
        return 1
    tm4 = tn_test_low_stock()
    if tm4 == False:
        return 1
    tm5 = tn_test_out_of_stock()
    if tm5 == False:
        return 1
    tm6 = tn_create_search_customer()
    if tm6 == False:
        return 1
    tm7 = tn_create_search_vendor()
    if tm7 == False:
        return 1
    tm8 = tn_test_search()
    if tm8 == False:
        return 1
    print("ALL NOTIFICATION AND SEARCH TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
