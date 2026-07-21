from core.helpers import helpers_get_map_value_safe
from models.vendor import vendor_create, vendor_get, vendor_list


def test_vendor_create():
    tvc_result = vendor_create(
        "Test Vendor Inc", "vendor@test.com", "555-4000", "Contact Person"
    )
    if tvc_result == False:
        print("FAIL: vendor_create returned false")
        return False
    tvc_id = helpers_get_map_value_safe(tvc_result, "id", "")
    if tvc_id == "":
        print("FAIL: vendor_create - no id")
        return False
    tvc_name = helpers_get_map_value_safe(tvc_result, "name", "")
    if tvc_name != "Test Vendor Inc":
        print("FAIL: vendor_create - name mismatch")
        return False
    tvc_email = helpers_get_map_value_safe(tvc_result, "email", "")
    if tvc_email != "vendor@test.com":
        print("FAIL: vendor_create - email mismatch")
        return False
    tvc_contact = helpers_get_map_value_safe(tvc_result, "contact_person", "")
    if tvc_contact != "Contact Person":
        print("FAIL: vendor_create - contact_person mismatch")
        return False
    print("PASS: vendor_create")
    return True


def test_vendor_get_by_id_missing():
    tvgm_result = vendor_get("NONEXISTENT-VENDOR-ID")
    if tvgm_result != False:
        print("FAIL: vendor_get_by_id_missing - expected false")
        return False
    print("PASS: vendor_get_by_id_missing")
    return True


def test_vendor_get_by_id():
    tvg_created = vendor_create(
        "GetTest Vendor", "get@vendor.com", "555-5000", "Get Contact"
    )
    tvg_id = helpers_get_map_value_safe(tvg_created, "id", "")
    tvg_found = vendor_get(tvg_id)
    if tvg_found == False:
        print("FAIL: vendor_get_by_id returned false for existing vendor")
        return False
    tvg_name = helpers_get_map_value_safe(tvg_found, "name", "")
    if tvg_name != "GetTest Vendor":
        print("FAIL: vendor_get_by_id - name mismatch")
        return False
    print("PASS: vendor_get_by_id")
    return True


def test_vendor_list():
    vendor_create("ListTest V1", "v1@test.com", "555-6001", "Contact1")
    vendor_create("ListTest V2", "v2@test.com", "555-6002", "Contact2")
    tvl_all = vendor_list()
    if len(tvl_all) == 0:
        print("FAIL: vendor_list returned empty list")
        return False
    print("PASS: vendor_list (" + str(len(tvl_all)) + " items)")
    return True


def main():
    tvr1 = test_vendor_create()
    if tvr1 == False:
        return 1
    tvr2 = test_vendor_get_by_id_missing()
    if tvr2 == False:
        return 1
    tvr3 = test_vendor_get_by_id()
    if tvr3 == False:
        return 1
    tvr4 = test_vendor_list()
    if tvr4 == False:
        return 1
    print("ALL VENDOR TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
