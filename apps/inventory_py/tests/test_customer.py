from core.helpers import helpers_get_map_value_safe
from models.customer import customer_create, customer_get, customer_list


def test_customer_create():
    tcc_result = customer_create("Test Customer", "test@customer.com", "555-1000")
    if tcc_result == False:
        print("FAIL: customer_create returned false")
        return False
    tcc_id = helpers_get_map_value_safe(tcc_result, "id", "")
    if tcc_id == "":
        print("FAIL: customer_create - no id")
        return False
    tcc_name = helpers_get_map_value_safe(tcc_result, "name", "")
    if tcc_name != "Test Customer":
        print("FAIL: customer_create - name mismatch")
        return False
    tcc_email = helpers_get_map_value_safe(tcc_result, "email", "")
    if tcc_email != "test@customer.com":
        print("FAIL: customer_create - email mismatch")
        return False
    tcc_phone = helpers_get_map_value_safe(tcc_result, "phone", "")
    if tcc_phone != "555-1000":
        print("FAIL: customer_create - phone mismatch")
        return False
    print("PASS: customer_create")
    return True


def test_customer_get_by_id_missing():
    tcgm_result = customer_get("NONEXISTENT-CUSTOMER-ID")
    if tcgm_result != False:
        print("FAIL: customer_get_by_id_missing - expected false")
        return False
    print("PASS: customer_get_by_id_missing")
    return True


def test_customer_get_by_id():
    tcg_created = customer_create("GetTest Customer", "gettest@example.com", "555-2000")
    tcg_id = helpers_get_map_value_safe(tcg_created, "id", "")
    tcg_found = customer_get(tcg_id)
    if tcg_found == False:
        print("FAIL: customer_get_by_id returned false for existing customer")
        return False
    tcg_name = helpers_get_map_value_safe(tcg_found, "name", "")
    if tcg_name != "GetTest Customer":
        print("FAIL: customer_get_by_id - name mismatch")
        return False
    print("PASS: customer_get_by_id")
    return True


def test_customer_list():
    customer_create("ListTest C1", "c1@test.com", "555-3001")
    customer_create("ListTest C2", "c2@test.com", "555-3002")
    tcl_all = customer_list()
    if len(tcl_all) == 0:
        print("FAIL: customer_list returned empty list")
        return False
    print("PASS: customer_list (" + str(len(tcl_all)) + " items)")
    return True


def main():
    tcr1 = test_customer_create()
    if tcr1 == False:
        return 1
    tcr2 = test_customer_get_by_id_missing()
    if tcr2 == False:
        return 1
    tcr3 = test_customer_get_by_id()
    if tcr3 == False:
        return 1
    tcr4 = test_customer_list()
    if tcr4 == False:
        return 1
    print("ALL CUSTOMER TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
