from business.report_trends import (
    trend_category_breakdown,
    trend_monthly_sales,
    trend_top_products,
)
from core.helpers import helpers_get_map_value_safe
from core.storage import storage_add


def trend_find_month_rec(tfmrItems, tfmrTargetMonth, tfmrIdx):
    if tfmrIdx >= len(tfmrItems):
        return False
    tfmrEntry = tfmrItems[tfmrIdx]
    tfmrMonth = helpers_get_map_value_safe(tfmrEntry, "month", "")
    if tfmrMonth == tfmrTargetMonth:
        return True
    return trend_find_month_rec(tfmrItems, tfmrTargetMonth, tfmrIdx + 1)


def test_trend_monthly_sales():
    tmsCat = {"id": "TREND-TEST-CAT", "name": "Trend Test Category"}
    storage_add("categories", tmsCat)
    tmsOrder1 = {
        "id": "TREND-SO-1",
        "customer_id": "TREND-CUST-1",
        "status": "confirmed",
        "total": 100,
        "created_at": "2024-01-15T10:00:00",
        "updated_at": "2024-01-15T10:00:00",
        "notes": "",
    }
    storage_add("sales_orders", tmsOrder1)
    tmsOrder2 = {
        "id": "TREND-SO-2",
        "customer_id": "TREND-CUST-1",
        "status": "confirmed",
        "total": 200,
        "created_at": "2024-01-20T10:00:00",
        "updated_at": "2024-01-20T10:00:00",
        "notes": "",
    }
    storage_add("sales_orders", tmsOrder2)
    tmsMonthly = trend_monthly_sales()
    tmsLen = len(tmsMonthly)
    if tmsLen == 0:
        print("FAIL: expected at least 1 monthly entry")
        return False
    tmsFound = trend_find_month_rec(tmsMonthly, "2024-01", 0)
    if tmsFound == False:
        print("FAIL: expected month 2024-01 in results")
        return False
    print("PASS: trend_monthly_sales")
    return True


def test_trend_top_products():
    ttpProd1 = {
        "id": "TREND-TOP-PROD-1",
        "name": "Top Product 1",
        "category_id": "TREND-TOP-CAT",
        "active": True,
    }
    storage_add("products", ttpProd1)
    ttpProd2 = {
        "id": "TREND-TOP-PROD-2",
        "name": "Top Product 2",
        "category_id": "TREND-TOP-CAT",
        "active": True,
    }
    storage_add("products", ttpProd2)
    ttpItem1 = {
        "id": "TREND-SOI-1",
        "order_id": "TREND-SO-TOP",
        "product_id": "TREND-TOP-PROD-1",
        "quantity": 10,
        "unit_price": 50,
        "line_total": 500,
    }
    storage_add("sales_items", ttpItem1)
    ttpItem2 = {
        "id": "TREND-SOI-2",
        "order_id": "TREND-SO-TOP",
        "product_id": "TREND-TOP-PROD-2",
        "quantity": 5,
        "unit_price": 30,
        "line_total": 150,
    }
    storage_add("sales_items", ttpItem2)
    ttpTop = trend_top_products(1)
    ttpLen = len(ttpTop)
    if ttpLen != 1:
        print("FAIL: expected 1 top product, got " + str(ttpLen))
        return False
    print("PASS: trend_top_products")
    return True


def test_trend_category_breakdown():
    tcbCat = {"id": "TREND-BREAK-CAT", "name": "Breakdown Category"}
    storage_add("categories", tcbCat)
    tcbProd1 = {
        "id": "TREND-BREAK-PROD-1",
        "name": "Breakdown Product 1",
        "category_id": "TREND-BREAK-CAT",
        "active": True,
    }
    storage_add("products", tcbProd1)
    tcbProd2 = {
        "id": "TREND-BREAK-PROD-2",
        "name": "Breakdown Product 2",
        "category_id": "TREND-BREAK-CAT",
        "active": True,
    }
    storage_add("products", tcbProd2)
    tcbBreakdown = trend_category_breakdown()
    tcbLen = len(tcbBreakdown)
    if tcbLen == 0:
        print("FAIL: expected at least 1 category entry")
        return False
    tcbFirst = tcbBreakdown[0]
    tcbCount = helpers_get_map_value_safe(tcbFirst, "count", 0)
    if tcbCount < 2:
        print("FAIL: expected at least 2 products in category, got " + str(tcbCount))
        return False
    print("PASS: trend_category_breakdown")
    return True


def main():
    tt1 = test_trend_monthly_sales()
    if tt1 == False:
        return 1
    tt2 = test_trend_top_products()
    if tt2 == False:
        return 1
    tt3 = test_trend_category_breakdown()
    if tt3 == False:
        return 1
    print("ALL REPORT TRENDS TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
