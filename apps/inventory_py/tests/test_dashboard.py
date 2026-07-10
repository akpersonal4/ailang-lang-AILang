from core.helpers import helpers_get_map_value_safe
from business.dashboard import dashboard_summary, dashboard_low_stock_count, dashboard_top_products, dashboard_recent_movements


def test_dashboard_summary():
    tdResult = dashboard_summary()
    tdProducts = helpers_get_map_value_safe(tdResult, "total_products", -1)
    if tdProducts < 0:
        print("FAIL: summary missing total_products")
        return False
    tdCategories = helpers_get_map_value_safe(tdResult, "total_categories", -1)
    if tdCategories < 0:
        print("FAIL: summary missing total_categories")
        return False
    print("PASS: dashboard_summary")
    return True


def test_dashboard_low_stock_count():
    tdCount = dashboard_low_stock_count(10)
    if tdCount < 0:
        print("FAIL: low_stock_count returned negative")
        return False
    print("PASS: dashboard_low_stock_count (" + str(tdCount) + " items)")
    return True


def test_dashboard_top_products():
    tdTop = dashboard_top_products(3)
    tdLen = len(tdTop)
    if tdLen < 0:
        print("FAIL: top_products returned negative length")
        return False
    if tdLen > 1:
        tdFirst = tdTop[0]
        tdFirstVal = helpers_get_map_value_safe(tdFirst, "value", 0)
        tdLast = tdTop[tdLen - 1]
        tdLastVal = helpers_get_map_value_safe(tdLast, "value", 0)
        if tdFirstVal < tdLastVal:
            print("FAIL: top_products not sorted descending")
            return False
    print("PASS: dashboard_top_products (" + str(tdLen) + " items)")
    return True


def test_dashboard_recent_movements():
    tdRecent = dashboard_recent_movements(5)
    tdLen = len(tdRecent)
    if tdLen < 0:
        print("FAIL: recent_movements returned negative length")
        return False
    print("PASS: dashboard_recent_movements (" + str(tdLen) + " items)")
    return True


def main():
    td1 = test_dashboard_summary()
    if td1 == False:
        return 1
    td2 = test_dashboard_low_stock_count()
    if td2 == False:
        return 1
    td3 = test_dashboard_top_products()
    if td3 == False:
        return 1
    td4 = test_dashboard_recent_movements()
    if td4 == False:
        return 1
    print("ALL DASHBOARD TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
