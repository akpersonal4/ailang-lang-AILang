from business.notification_reorder import (
    reorder_notify_check_all,
    reorder_notify_clear,
    reorder_notify_get_pending,
    reorder_notify_summary,
)
from business.reorder import reorder_set_level
from core.helpers import helpers_current_timestamp, helpers_get_map_value_safe
from core.storage import storage_add


def test_rn_check_all():
    trnProd = {"id": "RN-TEST-PROD-1", "name": "Reorder Notify Product"}
    storage_add("products", trnProd)
    reorder_set_level("RN-TEST-PROD-1", 10, 100, 50)
    trnValuation = {
        "id": "RN-VAL-1",
        "product_id": "RN-TEST-PROD-1",
        "quantity_on_hand": 5,
        "current_cost": 10,
        "method": "fifo",
        "last_updated": helpers_current_timestamp(),
    }
    storage_add("valuations", trnValuation)
    trnCount = reorder_notify_check_all()
    if trnCount == 0:
        print("FAIL: expected at least 1 notification")
        return False
    print("PASS: reorder_notify_check_all")
    return True


def test_rn_get_pending():
    trpProd = {"id": "RN-TEST-PROD-2", "name": "Pending Notify Product"}
    storage_add("products", trpProd)
    reorder_set_level("RN-TEST-PROD-2", 5, 50, 25)
    trpValuation = {
        "id": "RN-VAL-2",
        "product_id": "RN-TEST-PROD-2",
        "quantity_on_hand": 2,
        "current_cost": 10,
        "method": "fifo",
        "last_updated": helpers_current_timestamp(),
    }
    storage_add("valuations", trpValuation)
    reorder_notify_check_all()
    trpPending = reorder_notify_get_pending()
    trpLen = len(trpPending)
    if trpLen == 0:
        print("FAIL: expected at least 1 pending notification")
        return False
    print("PASS: reorder_notify_get_pending")
    return True


def test_rn_clear():
    trcProd = {"id": "RN-TEST-PROD-3", "name": "Clear Notify Product"}
    storage_add("products", trcProd)
    reorder_set_level("RN-TEST-PROD-3", 5, 50, 25)
    trcValuation = {
        "id": "RN-VAL-3",
        "product_id": "RN-TEST-PROD-3",
        "quantity_on_hand": 1,
        "current_cost": 10,
        "method": "fifo",
        "last_updated": helpers_current_timestamp(),
    }
    storage_add("valuations", trcValuation)
    reorder_notify_check_all()
    trcResult = reorder_notify_clear("RN-TEST-PROD-3")
    trcPending = reorder_notify_get_pending()
    trcLen = len(trcPending)
    trcFound = False
    trcCheckIdx = 0
    if trcLen > 0:
        trcCheckItem = trcPending[trcCheckIdx]
        trcCheckProd = helpers_get_map_value_safe(trcCheckItem, "product_id", "")
        if trcCheckProd == "RN-TEST-PROD-3":
            trcFound = True
    if trcFound:
        print("FAIL: notification still exists after clear")
        return False
    print("PASS: reorder_notify_clear")
    return True


def test_rn_summary():
    trsProd = {"id": "RN-TEST-PROD-4", "name": "Summary Notify Product"}
    storage_add("products", trsProd)
    reorder_set_level("RN-TEST-PROD-4", 10, 100, 50)
    trsValuation = {
        "id": "RN-VAL-4",
        "product_id": "RN-TEST-PROD-4",
        "quantity_on_hand": 3,
        "current_cost": 10,
        "method": "fifo",
        "last_updated": helpers_current_timestamp(),
    }
    storage_add("valuations", trsValuation)
    reorder_notify_check_all()
    trsCount = reorder_notify_summary()
    if trsCount == 0:
        print("FAIL: expected non-zero summary count")
        return False
    print("PASS: reorder_notify_summary")
    return True


def main():
    tr1 = test_rn_check_all()
    if tr1 == False:
        return 1
    tr2 = test_rn_get_pending()
    if tr2 == False:
        return 1
    tr3 = test_rn_clear()
    if tr3 == False:
        return 1
    tr4 = test_rn_summary()
    if tr4 == False:
        return 1
    print("ALL NOTIFICATION REORDER TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
