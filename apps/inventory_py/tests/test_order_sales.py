from core.helpers import helpers_get_map_value_safe
from core.storage import storage_add
from orders.sales_order import (
    sales_add_item,
    sales_confirm,
    sales_create,
    sales_get,
    sales_get_items,
)


def test_so_get_nonexistent():
    sonResult = sales_get("NONEXISTENT-SO")
    if sonResult != False:
        print("FAIL: expected false for nonexistent sales order")
        return False
    print("PASS: sales_get_nonexistent")
    return True


def test_so_create_and_get():
    socCust = {}
    socCust["id"] = "SO-CUST-1"
    socCust["name"] = "Test Customer"
    storage_add("customers", socCust)
    socOrder = sales_create("SO-CUST-1", "Test order")
    if socOrder == False:
        print("FAIL: sales_create returned false")
        return False
    socId = helpers_get_map_value_safe(socOrder, "id", "")
    socGot = sales_get(socId)
    if socGot == False:
        print("FAIL: sales_get returned false for created order")
        return False
    socStatus = helpers_get_map_value_safe(socGot, "status", "")
    if socStatus != "draft":
        print("FAIL: expected status draft, got " + socStatus)
        return False
    socCustId = helpers_get_map_value_safe(socGot, "customer_id", "")
    if socCustId != "SO-CUST-1":
        print("FAIL: expected customer_id SO-CUST-1, got " + socCustId)
        return False
    print("PASS: sales_create and sales_get")
    return True


def test_so_add_item_and_get_items():
    soiCust = {}
    soiCust["id"] = "SO-CUST-2"
    soiCust["name"] = "Item Test Customer"
    storage_add("customers", soiCust)
    soiOrder = sales_create("SO-CUST-2", "Item test")
    soiId = helpers_get_map_value_safe(soiOrder, "id", "")
    soiResult = sales_add_item(soiId, "PROD-A", 5, 100)
    if soiResult == False:
        print("FAIL: sales_add_item returned false")
        return False
    soiItems = sales_get_items(soiId)
    soiLen = len(soiItems)
    if soiLen != 1:
        print("FAIL: expected 1 item, got " + str(soiLen))
        return False
    soiFirst = soiItems[0]
    soiQty = helpers_get_map_value_safe(soiFirst, "quantity", 0)
    if soiQty != 5:
        print("FAIL: expected quantity 5, got " + str(soiQty))
        return False
    print("PASS: sales_add_item and sales_get_items")
    return True


def test_so_confirm():
    socfCust = {}
    socfCust["id"] = "SO-CUST-3"
    socfCust["name"] = "Confirm Test Customer"
    storage_add("customers", socfCust)
    socfOrder = sales_create("SO-CUST-3", "Confirm test")
    socfId = helpers_get_map_value_safe(socfOrder, "id", "")
    sales_confirm(socfId)
    socfGot = sales_get(socfId)
    socfStatus = helpers_get_map_value_safe(socfGot, "status", "")
    if socfStatus != "confirmed":
        print("FAIL: expected status confirmed, got " + socfStatus)
        return False
    print("PASS: sales_confirm")
    return True


def main():
    so1 = test_so_get_nonexistent()
    if so1 == False:
        return 1
    so2 = test_so_create_and_get()
    if so2 == False:
        return 1
    so3 = test_so_add_item_and_get_items()
    if so3 == False:
        return 1
    so4 = test_so_confirm()
    if so4 == False:
        return 1
    print("ALL SALES ORDER TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
