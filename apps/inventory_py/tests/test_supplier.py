from core.helpers import helpers_get_map_value_safe
from models.supplier import supplier_create, supplier_get_by_id, supplier_update, supplier_search, supplier_top_rated, supplier_get_by_payment_terms


def test_supplier_create():
    ts_result = supplier_create("TestSupply Co", "John Contact", "john@test.com", "555-0100", "123 Supply St", "net30", 14, 4)
    if ts_result == False:
        print("FAIL: supplier_create returned false")
        return False
    ts_id = helpers_get_map_value_safe(ts_result, "id", "")
    if ts_id == "":
        print("FAIL: supplier_create - no id")
        return False
    ts_name = helpers_get_map_value_safe(ts_result, "name", "")
    if ts_name != "TestSupply Co":
        print("FAIL: supplier_create - name mismatch")
        return False
    ts_contact = helpers_get_map_value_safe(ts_result, "contact_person", "")
    if ts_contact != "John Contact":
        print("FAIL: supplier_create - contact_person mismatch")
        return False
    ts_payment = helpers_get_map_value_safe(ts_result, "payment_terms", "")
    if ts_payment != "net30":
        print("FAIL: supplier_create - payment_terms mismatch")
        return False
    ts_rating = helpers_get_map_value_safe(ts_result, "rating", 0)
    if ts_rating != 4:
        print("FAIL: supplier_create - rating mismatch")
        return False
    print("PASS: supplier_create")
    return True


def test_supplier_get_by_id_missing():
    ts_result = supplier_get_by_id("NONEXISTENT-SUPPLIER")
    if ts_result != False:
        print("FAIL: supplier_get_by_id_missing - expected false")
        return False
    print("PASS: supplier_get_by_id_missing")
    return True


def test_supplier_get_by_id():
    ts_created = supplier_create("GetTest Supply", "Alice Get", "alice@get.com", "555-0200", "456 Get Ave", "net60", 30, 5)
    ts_id = helpers_get_map_value_safe(ts_created, "id", "")
    ts_found = supplier_get_by_id(ts_id)
    if ts_found == False:
        print("FAIL: supplier_get_by_id returned false")
        return False
    ts_name = helpers_get_map_value_safe(ts_found, "name", "")
    if ts_name != "GetTest Supply":
        print("FAIL: supplier_get_by_id - name mismatch")
        return False
    print("PASS: supplier_get_by_id")
    return True


def test_supplier_update():
    ts_created = supplier_create("UpdateTest Supply", "Bob Update", "bob@update.com", "555-0300", "789 Update Blvd", "net30", 7, 3)
    ts_id = helpers_get_map_value_safe(ts_created, "id", "")
    ts_changes = {"rating": 5, "payment_terms": "net15"}
    ts_update_result = supplier_update(ts_id, ts_changes)
    if ts_update_result == False:
        print("FAIL: supplier_update returned false")
        return False
    ts_updated = supplier_get_by_id(ts_id)
    ts_rating = helpers_get_map_value_safe(ts_updated, "rating", 0)
    if ts_rating != 5:
        print("FAIL: supplier_update - expected rating 5, got " + str(ts_rating))
        return False
    ts_payment = helpers_get_map_value_safe(ts_updated, "payment_terms", "")
    if ts_payment != "net15":
        print("FAIL: supplier_update - expected net15, got " + ts_payment)
        return False
    print("PASS: supplier_update")
    return True


def test_supplier_search():
    supplier_create("SearchTest Alpha", "Sam Search", "sam@search.com", "555-0400", "101 Search Ln", "net30", 14, 4)
    ts_results = supplier_search("SearchTest")
    if ts_results == False:
        print("FAIL: supplier_search returned false")
        return False
    ts_len = len(ts_results)
    if ts_len == 0:
        print("FAIL: supplier_search - no results")
        return False
    ts_first = ts_results[0]
    ts_first_name = helpers_get_map_value_safe(ts_first, "name", "")
    if "SearchTest" not in ts_first_name:
        print("FAIL: supplier_search - name does not contain SearchTest")
        return False
    print("PASS: supplier_search (" + str(ts_len) + " items)")
    return True


def test_supplier_top_rated():
    supplier_create("TopRated Low", "Low", "low@test.com", "555-0500", "1 Low Rd", "net30", 7, 2)
    supplier_create("TopRated High", "High", "high@test.com", "555-0600", "2 High St", "net60", 14, 5)
    ts_results = supplier_top_rated(4)
    if ts_results == False:
        print("FAIL: supplier_top_rated returned false")
        return False
    ts_len = len(ts_results)
    if ts_len == 0:
        print("FAIL: supplier_top_rated - no results")
        return False
    ts_found = False
    for ts_item in ts_results:
        ts_name = helpers_get_map_value_safe(ts_item, "name", "")
        if ts_name == "TopRated High":
            ts_found = True
            break
    if ts_found == False:
        print("FAIL: supplier_top_rated - expected TopRated High in results")
        return False
    print("PASS: supplier_top_rated (" + str(ts_len) + " items)")
    return True


def test_supplier_get_by_payment_terms():
    supplier_create("PaymentTest Net60 A", "Pay A", "paya@test.com", "555-0700", "10 Pay Rd", "net60", 30, 3)
    supplier_create("PaymentTest Net60 B", "Pay B", "payb@test.com", "555-0800", "20 Pay Ln", "net60", 45, 4)
    ts_results = supplier_get_by_payment_terms("net60")
    if ts_results == False:
        print("FAIL: supplier_get_by_payment_terms returned false")
        return False
    ts_len = len(ts_results)
    if ts_len < 2:
        print("FAIL: supplier_get_by_payment_terms - expected at least 2, got " + str(ts_len))
        return False
    print("PASS: supplier_get_by_payment_terms (" + str(ts_len) + " items)")
    return True


def main():
    tsr1 = test_supplier_create()
    if tsr1 == False:
        return 1
    tsr2 = test_supplier_get_by_id_missing()
    if tsr2 == False:
        return 1
    tsr3 = test_supplier_get_by_id()
    if tsr3 == False:
        return 1
    tsr4 = test_supplier_update()
    if tsr4 == False:
        return 1
    tsr5 = test_supplier_search()
    if tsr5 == False:
        return 1
    tsr6 = test_supplier_top_rated()
    if tsr6 == False:
        return 1
    tsr7 = test_supplier_get_by_payment_terms()
    if tsr7 == False:
        return 1
    print("ALL SUPPLIER TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
