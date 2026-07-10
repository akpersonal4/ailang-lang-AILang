from core.helpers import helpers_current_timestamp, helpers_find_in_list
from core.storage import storage_add, storage_list
from export.csv_export import csv_products, csv_customers
from export.json_export import json_export_products, json_export_customers


def te_create_product():
    tepProduct = {
        "id": "TEXP-PRD-001",
        "name": "Export Test Product",
        "sku": "EXP-001",
        "category_id": "",
        "unit_price": 75,
        "cost_price": 40,
        "unit": "pcs",
        "active": True,
        "created_at": helpers_current_timestamp(),
        "updated_at": ""
    }
    storage_add("products", tepProduct)
    tepLoaded = helpers_find_in_list(storage_list("products"), "id", "TEXP-PRD-001")
    if tepLoaded == False:
        return False
    return True


def te_create_customer():
    tecCustomer = {
        "id": "TEXP-CUS-001",
        "name": "Export Test Customer",
        "email": "export@test.com",
        "phone": "555-EXP",
        "active": True,
        "created_at": helpers_current_timestamp(),
        "updated_at": helpers_current_timestamp()
    }
    storage_add("customers", tecCustomer)
    tecLoaded = helpers_find_in_list(storage_list("customers"), "id", "TEXP-CUS-001")
    if tecLoaded == False:
        return False
    return True


def te_test_csv_products():
    tecpCsv = csv_products()
    tecpLen = len(tecpCsv)
    if tecpLen == 0:
        print("FAIL: csv_products returned empty string")
        return False
    if tecpCsv.startswith("id,name,sku,unit_price,unit") == False:
        print("FAIL: csv_products missing header")
        return False
    print("PASS: csv_products")
    return True


def te_test_csv_customers():
    teccCsv = csv_customers()
    teccLen = len(teccCsv)
    if teccLen == 0:
        print("FAIL: csv_customers returned empty string")
        return False
    if teccCsv.startswith("id,name,email,phone") == False:
        print("FAIL: csv_customers missing header")
        return False
    print("PASS: csv_customers")
    return True


def te_test_json_products():
    tejpJson = json_export_products()
    tejpLen = len(tejpJson)
    if tejpLen == 0:
        print("FAIL: json_export_products returned empty string")
        return False
    if tejpJson.startswith("[") == False:
        print("FAIL: json_export_products not valid JSON array")
        return False
    print("PASS: json_export_products")
    return True


def te_test_json_customers():
    tejcJson = json_export_customers()
    tejcLen = len(tejcJson)
    if tejcLen == 0:
        print("FAIL: json_export_customers returned empty string")
        return False
    if tejcJson.startswith("[") == False:
        print("FAIL: json_export_customers not valid JSON array")
        return False
    print("PASS: json_export_customers")
    return True


def main():
    tm1 = te_create_product()
    if tm1 == False:
        return 1
    tm2 = te_create_customer()
    if tm2 == False:
        return 1
    tm3 = te_test_csv_products()
    if tm3 == False:
        return 1
    tm4 = te_test_csv_customers()
    if tm4 == False:
        return 1
    tm5 = te_test_json_products()
    if tm5 == False:
        return 1
    tm6 = te_test_json_customers()
    if tm6 == False:
        return 1
    print("ALL EXPORT TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
