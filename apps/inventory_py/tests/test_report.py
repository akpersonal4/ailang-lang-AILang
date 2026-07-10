from core.helpers import helpers_get_map_value_safe, helpers_current_timestamp, helpers_find_in_list
from core.storage import storage_add, storage_list
from business.report import stock_report_all_products, sales_report_all, profit_report_summary


def tr_create_customer():
    trcCustomer = {
        "id": "TREP-CUS-001",
        "name": "Report Customer",
        "email": "report@test.com",
        "phone": "555-REP",
        "active": True,
        "created_at": helpers_current_timestamp(),
        "updated_at": helpers_current_timestamp()
    }
    storage_add("customers", trcCustomer)
    trcLoaded = helpers_find_in_list(storage_list("customers"), "id", "TREP-CUS-001")
    if trcLoaded == False:
        return False
    return True


def tr_create_product():
    trpProduct = {
        "id": "TREP-PRD-001",
        "name": "Report Test Product",
        "sku": "RPT-001",
        "category_id": "",
        "unit_price": 50,
        "cost_price": 25,
        "unit": "pcs",
        "active": True,
        "created_at": helpers_current_timestamp(),
        "updated_at": ""
    }
    storage_add("products", trpProduct)
    trpLoaded = helpers_find_in_list(storage_list("products"), "id", "TREP-PRD-001")
    if trpLoaded == False:
        return False
    return True


def tr_create_movement():
    trmMovement = {
        "id": "TREP-MOV-001",
        "product_id": "TREP-PRD-001",
        "type": "inbound",
        "quantity": 100,
        "reference_type": "manual",
        "reference_id": "",
        "notes": "Test movement",
        "created_at": helpers_current_timestamp()
    }
    storage_add("movements", trmMovement)
    trmLoaded = helpers_find_in_list(storage_list("movements"), "id", "TREP-MOV-001")
    if trmLoaded == False:
        return False
    return True


def tr_create_sales_order():
    trsoOrder = {
        "id": "TREP-SO-001",
        "customer_id": "TREP-CUS-001",
        "status": "confirmed",
        "total": 500,
        "notes": "Test sales order",
        "created_at": helpers_current_timestamp(),
        "updated_at": helpers_current_timestamp()
    }
    storage_add("sales_orders", trsoOrder)
    return True


def tr_create_purchase_order():
    trpoOrder = {
        "id": "TREP-PO-001",
        "vendor_id": "TREP-VEN-001",
        "status": "received",
        "total": 300,
        "notes": "Test purchase order",
        "created_at": helpers_current_timestamp(),
        "updated_at": helpers_current_timestamp()
    }
    storage_add("purchase_orders", trpoOrder)
    return True


def tr_test_stock_report():
    trsrProducts = stock_report_all_products()
    trsrCount = len(trsrProducts)
    if trsrCount == 0:
        print("FAIL: stock_report_all_products returned empty list")
        return False
    print("PASS: stock_report_all_products (" + str(trsrCount) + " products)")
    return True


def tr_test_sales_report():
    trsrOrders = sales_report_all()
    trsrCount = len(trsrOrders)
    if trsrCount == 0:
        print("FAIL: sales_report_all returned empty list")
        return False
    print("PASS: sales_report_all (" + str(trsrCount) + " orders)")
    return True


def tr_test_profit_report():
    trprSummary = profit_report_summary()
    trprSalesTotal = helpers_get_map_value_safe(trprSummary, "sales_total", 0)
    trprPurchaseTotal = helpers_get_map_value_safe(trprSummary, "purchase_total", 0)
    trprSalesCount = helpers_get_map_value_safe(trprSummary, "sales_count", 0)
    trprPurchaseCount = helpers_get_map_value_safe(trprSummary, "purchase_count", 0)
    if trprSalesTotal == 0 and trprPurchaseTotal == 0:
        print("FAIL: profit_report_summary returned empty data")
        return False
    print("PASS: profit_report_summary (sales: " + str(trprSalesTotal) + ", purchases: " + str(trprPurchaseTotal) + ")")
    return True


def main():
    tm1 = tr_create_customer()
    if tm1 == False:
        return 1
    tm2 = tr_create_product()
    if tm2 == False:
        return 1
    tm3 = tr_create_movement()
    if tm3 == False:
        return 1
    tm4 = tr_create_sales_order()
    if tm4 == False:
        return 1
    tm5 = tr_create_purchase_order()
    if tm5 == False:
        return 1
    tm6 = tr_test_stock_report()
    if tm6 == False:
        return 1
    tm7 = tr_test_sales_report()
    if tm7 == False:
        return 1
    tm8 = tr_test_profit_report()
    if tm8 == False:
        return 1
    print("ALL REPORT TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
