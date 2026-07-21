from core.helpers import helpers_get_map_value_safe
from financial.invoice import invoice_create, invoice_get_by_id, invoice_update_status
from financial.payment import payment_create
from financial.payment_integration import (
    pi_get_invoice_balance,
    pi_list_overdue_invoices,
    pi_process_invoice_payment,
)


def test_pi_process_payment():
    tppp_items = []
    tppp_item = {}
    tppp_item["product_id"] = "PI-PROD-1"
    tppp_item["quantity"] = 1
    tppp_item["unit_price"] = 500
    tppp_item["line_total"] = 500
    tppp_items.append(tppp_item)
    tppp_inv = invoice_create("ORDER-PI-1", "CUST-PI-1", tppp_items, 500)
    tppp_inv_id = helpers_get_map_value_safe(tppp_inv, "id", "")
    tppp_result = pi_process_invoice_payment(tppp_inv_id, 500, "card", "Test User")
    if tppp_result != True:
        print("FAIL: pi_process_invoice_payment returned " + str(tppp_result))
        return False
    tppp_updated = invoice_get_by_id(tppp_inv_id)
    tppp_status = helpers_get_map_value_safe(tppp_updated, "status", "")
    if tppp_status != "paid":
        print("FAIL: expected invoice status paid, got " + tppp_status)
        return False
    print("PASS: pi_process_invoice_payment")
    return True


def test_pi_get_balance():
    tpib_items = []
    tpib_item = {}
    tpib_item["product_id"] = "PI-PROD-2"
    tpib_item["quantity"] = 2
    tpib_item["unit_price"] = 300
    tpib_item["line_total"] = 600
    tpib_items.append(tpib_item)
    tpib_inv = invoice_create("ORDER-PI-2", "CUST-PI-2", tpib_items, 600)
    tpib_inv_id = helpers_get_map_value_safe(tpib_inv, "id", "")
    payment_create(tpib_inv_id, 200, "cash", "Test User")
    tpib_balance = pi_get_invoice_balance(tpib_inv_id)
    if tpib_balance != 400:
        print("FAIL: expected balance 400, got " + str(tpib_balance))
        return False
    print("PASS: pi_get_invoice_balance (" + str(tpib_balance) + ")")
    return True


def test_pi_list_overdue():
    tplo_items = []
    tplo_item = {}
    tplo_item["product_id"] = "PI-PROD-3"
    tplo_item["quantity"] = 1
    tplo_item["unit_price"] = 100
    tplo_item["line_total"] = 100
    tplo_items.append(tplo_item)
    tplo_inv1 = invoice_create("ORDER-PI-3A", "CUST-PI-3", tplo_items, 100)
    tplo_inv1_id = helpers_get_map_value_safe(tplo_inv1, "id", "")
    invoice_update_status(tplo_inv1_id, "sent")
    tplo_inv2 = invoice_create("ORDER-PI-3B", "CUST-PI-3", tplo_items, 100)
    tplo_inv3 = invoice_create("ORDER-PI-3C", "CUST-PI-3", tplo_items, 100)
    tplo_inv3_id = helpers_get_map_value_safe(tplo_inv3, "id", "")
    invoice_update_status(tplo_inv3_id, "paid")
    tplo_results = pi_list_overdue_invoices()
    if tplo_results == False:
        print("FAIL: pi_list_overdue returned false")
        return False
    tplo_len = len(tplo_results)
    if tplo_len < 1:
        print("FAIL: expected at least 1 overdue invoice, got " + str(tplo_len))
        return False
    print("PASS: pi_list_overdue (" + str(tplo_len) + " items)")
    return True


def test_pi_invoice_not_found():
    tpin_result = pi_process_invoice_payment("DOES-NOT-EXIST", 100, "card", "Test")
    if tpin_result != False:
        print("FAIL: expected false for nonexistent invoice")
        return False
    tpin_balance = pi_get_invoice_balance("DOES-NOT-EXIST")
    if tpin_balance != 0:
        print(
            "FAIL: expected 0 balance for nonexistent invoice, got " + str(tpin_balance)
        )
        return False
    print("PASS: pi_invoice_not_found")
    return True


def main():
    tp1 = test_pi_process_payment()
    if tp1 == False:
        return 1
    tp2 = test_pi_get_balance()
    if tp2 == False:
        return 1
    tp3 = test_pi_list_overdue()
    if tp3 == False:
        return 1
    tp4 = test_pi_invoice_not_found()
    if tp4 == False:
        return 1
    print("ALL PAYMENT INTEGRATION TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
