from core.helpers import helpers_get_map_value_safe
from core.storage import storage_add
from inventory.stock_movement import (
    movement_check_alert_threshold,
    movement_create,
    movement_get_quantity_on_hand,
    movement_list_by_product,
    movement_list_by_type,
)


def test_sm_create_and_list_by_product():
    smCat = {"id": "SM-TEST-CAT", "name": "Test Cat"}
    storage_add("categories", smCat)
    smProd = {"id": "SM-TEST-PROD", "name": "Test Prod"}
    storage_add("products", smProd)
    smMov = movement_create(
        "SM-TEST-PROD", "inbound", 100, "manual", "REF-001", "Test inbound"
    )
    if smMov is False:
        print("FAIL: movement_create returned false")
        return False
    smList = movement_list_by_product("SM-TEST-PROD")
    smLen = len(smList)
    if smLen == 0:
        print("FAIL: expected at least 1 movement, got 0")
        return False
    smFirst = smList[0]
    smProdId = helpers_get_map_value_safe(smFirst, "product_id", "")
    if smProdId != "SM-TEST-PROD":
        print("FAIL: expected product_id SM-TEST-PROD, got " + smProdId)
        return False
    print("PASS: movement_create and list_by_product")
    return True


def test_sm_get_quantity_on_hand():
    smqProd = {"id": "SM-PROD-QOH", "name": "QOH Test Prod"}
    storage_add("products", smqProd)
    movement_create("SM-PROD-QOH", "inbound", 100, "manual", "REF-Q1", "Inbound")
    movement_create("SM-PROD-QOH", "outbound", -30, "manual", "REF-Q2", "Outbound")
    smqQoh = movement_get_quantity_on_hand("SM-PROD-QOH")
    if smqQoh != 70:
        print("FAIL: expected QOH 70, got " + str(smqQoh))
        return False
    print("PASS: movement_get_quantity_on_hand")
    return True


def test_sm_list_by_type():
    smtProd = {"id": "SM-PROD-TYPE", "name": "Type Test Prod"}
    storage_add("products", smtProd)
    movement_create(
        "SM-PROD-TYPE", "adjustment", 10, "manual", "REF-T1", "Adjustment 1"
    )
    movement_create(
        "SM-PROD-TYPE", "adjustment", 20, "manual", "REF-T2", "Adjustment 2"
    )
    smtList = movement_list_by_type("adjustment")
    smtLen = len(smtList)
    if smtLen < 2:
        print("FAIL: expected at least 2 adjustments, got " + str(smtLen))
        return False
    print("PASS: movement_list_by_type")
    return True


def test_sm_check_alert_threshold_below():
    prod = {"id": "SM-PROD-ALERT", "name": "Alert Test Prod"}
    storage_add("products", prod)
    movement_create("SM-PROD-ALERT", "inbound", 10, "manual", "REF-A1", "Small inbound")
    result = movement_check_alert_threshold("SM-PROD-ALERT", 50)
    if result is False:
        print("FAIL: expected alert map, got false")
        return False
    if helpers_get_map_value_safe(result, "alert", False) is not True:
        print("FAIL: expected alert=true")
        return False
    qoh = helpers_get_map_value_safe(result, "current_qoh", 0)
    if qoh != 10:
        print("FAIL: expected current_qoh 10, got " + str(qoh))
        return False
    print("PASS: movement_check_alert_threshold (below threshold)")
    return True


def test_sm_check_alert_threshold_above():
    prod = {"id": "SM-PROD-SAFE", "name": "Safe Test Prod"}
    storage_add("products", prod)
    movement_create("SM-PROD-SAFE", "inbound", 100, "manual", "REF-A2", "Large inbound")
    result = movement_check_alert_threshold("SM-PROD-SAFE", 50)
    if result is False:
        print("FAIL: expected non-alert map, got false")
        return False
    if helpers_get_map_value_safe(result, "alert", True) is not False:
        print("FAIL: expected alert=false")
        return False
    print("PASS: movement_check_alert_threshold (above threshold)")
    return True


def test_sm_check_alert_threshold_unknown():
    result = movement_check_alert_threshold("SM-PROD-UNKNOWN", 50)
    if result is not False:
        print("FAIL: expected false for unknown product")
        return False
    print("PASS: movement_check_alert_threshold (unknown product)")
    return True


def main():
    sm1 = test_sm_create_and_list_by_product()
    if sm1 is False:
        return 1
    sm2 = test_sm_get_quantity_on_hand()
    if sm2 is False:
        return 1
    sm3 = test_sm_list_by_type()
    if sm3 is False:
        return 1
    sm4 = test_sm_check_alert_threshold_below()
    if sm4 is False:
        return 1
    sm5 = test_sm_check_alert_threshold_above()
    if sm5 is False:
        return 1
    sm6 = test_sm_check_alert_threshold_unknown()
    if sm6 is False:
        return 1
    print("ALL STOCK MOVEMENT TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
