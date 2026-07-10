from core.helpers import helpers_get_map_value_safe, helpers_unix_timestamp
from models.product import product_create, product_get, product_search, product_list


def test_product_create():
    tpc_result = product_create("ProdCreateTest", "A product for create test", "PCR-001", "test-cat-id", 150, 90, "pcs")
    if tpc_result == False:
        print("FAIL: product_create returned false")
        return False
    tpc_id = helpers_get_map_value_safe(tpc_result, "id", "")
    if tpc_id == "":
        print("FAIL: product_create - product id missing")
        return False
    tpc_name = helpers_get_map_value_safe(tpc_result, "name", "")
    if tpc_name != "ProdCreateTest":
        print("FAIL: product_create - expected ProdCreateTest, got " + tpc_name)
        return False
    print("PASS: product_create")
    return True


def test_product_get_by_id_missing():
    tpgm_result = product_get("NONEXISTENT-PRODUCT-ID")
    if tpgm_result != False:
        print("FAIL: product_get_by_id_missing - expected false")
        return False
    print("PASS: product_get_by_id_missing")
    return True


def test_product_get_by_id():
    tpg_created = product_create("ProdGetTest", "A product for get test", "PGT-001", "test-cat-id", 200, 120, "pcs")
    tpg_id = helpers_get_map_value_safe(tpg_created, "id", "")
    tpg_found = product_get(tpg_id)
    if tpg_found == False:
        print("FAIL: product_get_by_id returned false for existing product")
        return False
    tpg_name = helpers_get_map_value_safe(tpg_found, "name", "")
    if tpg_name != "ProdGetTest":
        print("FAIL: product_get_by_id - expected ProdGetTest, got " + tpg_name)
        return False
    print("PASS: product_get_by_id")
    return True


def test_product_search():
    tps_unique_name = "ZUniqueSearchItem_" + str(helpers_unix_timestamp())
    product_create(tps_unique_name, "For search test", "PSR-001", "test-cat-id", 50, 30, "pcs")
    tps_results = product_search("ZUniqueSearchItem")
    if len(tps_results) == 0:
        print("FAIL: product_search - expected at least 1 result")
        return False
    tps_first = tps_results[0]
    tps_first_name = helpers_get_map_value_safe(tps_first, "name", "")
    if tps_first_name != tps_unique_name:
        print("FAIL: product_search - expected " + tps_unique_name + ", got " + tps_first_name)
        return False
    print("PASS: product_search")
    return True


def test_product_list():
    product_create("ProdListItem1", "First list item", "PLI-001", "test-cat-id", 10, 5, "pcs")
    product_create("ProdListItem2", "Second list item", "PLI-002", "test-cat-id", 20, 10, "pcs")
    tpl_all = product_list()
    if len(tpl_all) == 0:
        print("FAIL: product_list returned empty list")
        return False
    print("PASS: product_list (" + str(len(tpl_all)) + " items)")
    return True


def main():
    tpr1 = test_product_create()
    if tpr1 == False:
        return 1
    tpr2 = test_product_get_by_id_missing()
    if tpr2 == False:
        return 1
    tpr3 = test_product_get_by_id()
    if tpr3 == False:
        return 1
    tpr4 = test_product_search()
    if tpr4 == False:
        return 1
    tpr5 = test_product_list()
    if tpr5 == False:
        return 1
    print("ALL PRODUCT TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
