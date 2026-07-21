from core.helpers import helpers_get_map_value_safe
from inventory.stock_valuation import valuation_get, valuation_list, valuation_set


def test_sv_get_nonexistent():
    svmResult = valuation_get("NONEXISTENT-PROD")
    if svmResult is not None:
        print("FAIL: expected false for nonexistent valuation")
        return False
    print("PASS: valuation_get_nonexistent")
    return True


def test_sv_set_and_get():
    svgResult = valuation_set("SV-PROD-1", "fifo", 100, 50)
    if svgResult is False:
        print("FAIL: valuation_set returned false")
        return False
    svgGot = valuation_get("SV-PROD-1")
    if svgGot is False:
        print("FAIL: valuation_get returned false")
        return False
    svgCost = helpers_get_map_value_safe(svgGot, "current_cost", 0)
    if svgCost != 100:
        print("FAIL: expected current_cost 100, got " + str(svgCost))
        return False
    svgMethod = helpers_get_map_value_safe(svgGot, "method", "")
    if svgMethod != "fifo":
        print("FAIL: expected method fifo, got " + svgMethod)
        return False
    svgQty = helpers_get_map_value_safe(svgGot, "quantity_on_hand", 0)
    if svgQty != 50:
        print("FAIL: expected quantity_on_hand 50, got " + str(svgQty))
        return False
    print("PASS: valuation_set and valuation_get")
    return True


def test_sv_list():
    valuation_set("SV-PROD-L1", "fifo", 50, 10)
    valuation_set("SV-PROD-L2", "average", 75, 20)
    svlList = valuation_list()
    svlLen = len(svlList)
    if svlLen < 2:
        print("FAIL: expected at least 2 valuations, got " + str(svlLen))
        return False
    print("PASS: valuation_list")
    return True


def main():
    sv1 = test_sv_get_nonexistent()
    if sv1 is False:
        return 1
    sv2 = test_sv_set_and_get()
    if sv2 is False:
        return 1
    sv3 = test_sv_list()
    if sv3 is False:
        return 1
    print("ALL STOCK VALUATION TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
