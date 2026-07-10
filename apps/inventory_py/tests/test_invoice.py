from financial.invoice import invoice_create, invoice_get_by_id, invoice_calculate_total, invoice_generate_number, invoice_list_by_customer
from core.helpers import helpers_get_map_value_safe


def test_invoice_create():
    ticItems = []
    ticItem1 = {}
    ticItem1["product_id"] = "PRD-001"
    ticItem1["quantity"] = 2
    ticItem1["unit_price"] = 50
    ticItem1["line_total"] = 100
    ticItems.append(ticItem1)
    ticItem2 = {}
    ticItem2["product_id"] = "PRD-002"
    ticItem2["quantity"] = 1
    ticItem2["unit_price"] = 200
    ticItem2["line_total"] = 200
    ticItems.append(ticItem2)
    ticResult = invoice_create("SO-INV-001", "CUS-001", ticItems, 300)
    if ticResult == False:
        print("FAIL: invoice_create returned false")
        return False
    ticId = helpers_get_map_value_safe(ticResult, "id", "")
    if ticId == "":
        print("FAIL: invoice_create - no id generated")
        return False
    ticStatus = helpers_get_map_value_safe(ticResult, "status", "")
    if ticStatus != "draft":
        print("FAIL: invoice_create - expected status draft, got " + ticStatus)
        return False
    print("PASS: invoice_create")
    return True


def test_invoice_get_by_id_missing():
    tigmResult = invoice_get_by_id("NONEXISTENT-INVOICE-ID")
    if tigmResult != False:
        print("FAIL: invoice_get_by_id_missing - expected false")
        return False
    print("PASS: invoice_get_by_id_missing")
    return True


def test_invoice_calculate_total():
    tictItems = []
    tictItem1 = {}
    tictItem1["product_id"] = "PRD-A"
    tictItem1["line_total"] = 150
    tictItems.append(tictItem1)
    tictItem2 = {}
    tictItem2["product_id"] = "PRD-B"
    tictItem2["line_total"] = 75
    tictItems.append(tictItem2)
    tictItem3 = {}
    tictItem3["product_id"] = "PRD-C"
    tictItems.append(tictItem3)
    tictTotal = invoice_calculate_total(tictItems)
    if tictTotal != 225:
        print("FAIL: invoice_calculate_total - expected 225, got " + str(tictTotal))
        return False
    print("PASS: invoice_calculate_total (" + str(tictTotal) + ")")
    return True


def test_invoice_generate_number():
    tignResult = invoice_generate_number(5)
    if tignResult == False:
        print("FAIL: invoice_generate_number returned false")
        return False
    tignPrefix = tignResult[0:4]
    if tignPrefix != "INV-":
        print("FAIL: invoice_generate_number - expected INV- prefix, got " + tignPrefix)
        return False
    tignLen = len(tignResult)
    if tignLen < 12:
        print("FAIL: invoice_generate_number - result too short: " + tignResult)
        return False
    print("PASS: invoice_generate_number (" + tignResult + ")")
    return True


def test_invoice_list_by_customer():
    tilcItems = []
    tilcItemData = {}
    tilcItemData["product_id"] = "PRD-X"
    tilcItemData["line_total"] = 50
    tilcItems.append(tilcItemData)
    invoice_create("SO-CUS-1", "CUS-100", tilcItems, 50)
    invoice_create("SO-CUS-2", "CUS-100", tilcItems, 50)
    tilcResults = invoice_list_by_customer("CUS-100")
    tilcLen = len(tilcResults)
    if tilcLen < 2:
        print("FAIL: invoice_list_by_customer - expected at least 2, got " + str(tilcLen))
        return False
    print("PASS: invoice_list_by_customer (" + str(tilcLen) + " items)")
    return True


def main():
    ti1 = test_invoice_create()
    if ti1 == False:
        return 1
    ti2 = test_invoice_get_by_id_missing()
    if ti2 == False:
        return 1
    ti3 = test_invoice_calculate_total()
    if ti3 == False:
        return 1
    ti4 = test_invoice_generate_number()
    if ti4 == False:
        return 1
    ti5 = test_invoice_list_by_customer()
    if ti5 == False:
        return 1
    print("ALL INVOICE TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
