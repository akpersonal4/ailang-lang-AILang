from core.helpers import (
    helpers_current_timestamp,
    helpers_find_in_list,
    helpers_get_map_value_safe,
)
from core.storage import storage_add, storage_list
from inventory.stock_movement import movement_list
from orders.purchase_order import (
    purchase_add_item,
    purchase_create,
    purchase_get,
    purchase_get_items,
    purchase_receive,
)


def test_po_nonexistent():
    tpnResult = purchase_get("NON-EXISTENT-ORDER")
    if tpnResult != False:
        print("FAIL: purchase_get returned non-false for non-existent order")
        return False
    print("PASS: purchase_get_nonexistent")
    return True


def test_po_create_vendor():
    tpvenVendor = {}
    tpvenVendor["id"] = "TEST-VEN-001"
    tpvenVendor["name"] = "Test Vendor"
    tpvenVendor["email"] = "test@vendor.com"
    tpvenVendor["phone"] = "555-TEST"
    tpvenVendor["contact_person"] = "TestContact"
    tpvenVendor["active"] = True
    tpvenNow = helpers_current_timestamp()
    tpvenVendor["created_at"] = tpvenNow
    tpvenVendor["updated_at"] = tpvenNow
    storage_add("vendors", tpvenVendor)
    tpvenLoaded = helpers_find_in_list(storage_list("vendors"), "id", "TEST-VEN-001")
    if tpvenLoaded == False:
        print("FAIL: vendor not found after storage_add")
        return False
    print("PASS: created test vendor")
    return True


def test_po_create_product():
    tpcpProduct = {}
    tpcpProduct["id"] = "TEST-PRD-001"
    tpcpProduct["name"] = "Test Product"
    tpcpProduct["sku"] = "TST-001"
    tpcpProduct["category_id"] = ""
    tpcpProduct["unit_price"] = 100
    tpcpProduct["cost_price"] = 50
    tpcpProduct["unit"] = "pcs"
    tpcpProduct["active"] = True
    tpcpNow = helpers_current_timestamp()
    tpcpProduct["created_at"] = tpcpNow
    tpcpProduct["updated_at"] = ""
    storage_add("products", tpcpProduct)
    tpcpLoaded = helpers_find_in_list(storage_list("products"), "id", "TEST-PRD-001")
    if tpcpLoaded == False:
        print("FAIL: product not found after storage_add")
        return False
    print("PASS: created test product")
    return True


def test_po_create_valuation():
    tpcvVal = {}
    tpcvVal["id"] = "TEST-VAL-001"
    tpcvVal["product_id"] = "TEST-PRD-001"
    tpcvVal["method"] = "fifo"
    tpcvVal["current_cost"] = 0
    tpcvVal["quantity_on_hand"] = 0
    tpcvNow = helpers_current_timestamp()
    tpcvVal["last_updated"] = tpcvNow
    storage_add("valuations", tpcvVal)
    tpcvLoaded = helpers_find_in_list(storage_list("valuations"), "id", "TEST-VAL-001")
    if tpcvLoaded == False:
        print("FAIL: valuation not found after storage_add")
        return False
    print("PASS: created test valuation")
    return True


def test_po_verify_items(tpviOrderId):
    tpviItems = purchase_get_items(tpviOrderId)
    tpviCount = len(tpviItems)
    if tpviCount != 1:
        print("FAIL: expected 1 item, got " + str(tpviCount))
        return False
    tpviFirst = tpviItems[0]
    tpviQty = helpers_get_map_value_safe(tpviFirst, "quantity", 0)
    if tpviQty != 5:
        print("FAIL: expected quantity 5, got " + str(tpviQty))
        return False
    tpviPrice = helpers_get_map_value_safe(tpviFirst, "unit_price", 0)
    if tpviPrice != 100:
        print("FAIL: expected unit_price 100, got " + str(tpviPrice))
        return False
    tpviProdId = helpers_get_map_value_safe(tpviFirst, "product_id", "")
    if tpviProdId != "TEST-PRD-001":
        print("FAIL: expected product_id TEST-PRD-001, got " + tpviProdId)
        return False
    print("PASS: purchase_verify_items")
    return True


def test_po_receive_order(tproOrderId):
    tproResult = purchase_receive(tproOrderId)
    if tproResult == False:
        print("FAIL: purchase_receive returned false")
        return False
    tproMovements = movement_list()
    tproCount = len(tproMovements)
    if tproCount == 0:
        print("FAIL: no stock movements created after receive")
        return False
    print("PASS: purchase_receive")
    return True


def main():
    tm1 = test_po_nonexistent()
    if tm1 == False:
        return 1
    tm2 = test_po_create_vendor()
    if tm2 == False:
        return 1
    tm3 = test_po_create_product()
    if tm3 == False:
        return 1
    tm4 = test_po_create_valuation()
    if tm4 == False:
        return 1
    tmPO = purchase_create("TEST-VEN-001", "Test purchase order")
    tmPOId = helpers_get_map_value_safe(tmPO, "id", "")
    print("Created PO with id: " + tmPOId)
    tmAddItem = purchase_add_item(tmPOId, "TEST-PRD-001", 5, 100)
    if tmAddItem == False:
        print("FAIL: purchase_add_item returned false")
        return 1
    print("PASS: purchase_add_item")
    tm5 = test_po_verify_items(tmPOId)
    if tm5 == False:
        return 1
    tm6 = test_po_receive_order(tmPOId)
    if tm6 == False:
        return 1
    print("ALL PURCHASE ORDER TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
