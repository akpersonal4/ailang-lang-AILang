from financial.payment import payment_create, payment_get_by_id, payment_list_by_invoice, payment_total_by_invoice, payment_refund
from core.helpers import helpers_get_map_value_safe


def test_payment_create():
    tpcResult = payment_create("INV-PC-001", 500, "card", "Alice")
    if tpcResult == False:
        print("FAIL: payment_create returned false")
        return False
    tpcId = helpers_get_map_value_safe(tpcResult, "id", "")
    if tpcId == "":
        print("FAIL: payment_create - payment id missing")
        return False
    tpcStatus = helpers_get_map_value_safe(tpcResult, "status", "")
    if tpcStatus != "completed":
        print("FAIL: payment_create - expected status completed, got " + tpcStatus)
        return False
    tpcAmount = helpers_get_map_value_safe(tpcResult, "amount", 0)
    if tpcAmount != 500:
        print("FAIL: payment_create - expected amount 500, got " + str(tpcAmount))
        return False
    print("PASS: payment_create")
    return True


def test_payment_get_by_id_missing():
    tpgmResult = payment_get_by_id("NONEXISTENT-PAYMENT-ID")
    if tpgmResult != False:
        print("FAIL: payment_get_by_id_missing - expected false")
        return False
    print("PASS: payment_get_by_id_missing")
    return True


def test_payment_list_by_invoice():
    tplbi1 = payment_create("INV-LIST-001", 200, "cash", "Bob")
    tplbi2 = payment_create("INV-LIST-001", 300, "card", "Bob")
    tplbiResults = payment_list_by_invoice("INV-LIST-001")
    tplbiLen = len(tplbiResults)
    if tplbiLen < 2:
        print("FAIL: payment_list_by_invoice - expected at least 2, got " + str(tplbiLen))
        return False
    print("PASS: payment_list_by_invoice (" + str(tplbiLen) + " items)")
    return True


def test_payment_total_by_invoice():
    tptbi1 = payment_create("INV-TOT-001", 150, "card", "Carol")
    tptbi2 = payment_create("INV-TOT-001", 250, "cash", "Carol")
    tptbiTotal = payment_total_by_invoice("INV-TOT-001")
    if tptbiTotal != 400:
        print("FAIL: payment_total_by_invoice - expected 400, got " + str(tptbiTotal))
        return False
    print("PASS: payment_total_by_invoice (" + str(tptbiTotal) + ")")
    return True


def test_payment_refund():
    tprOrig = payment_create("INV-REF-001", 1000, "bank_transfer", "Dave")
    tprOrigId = helpers_get_map_value_safe(tprOrig, "id", "")
    tprRefund = payment_refund(tprOrigId, "Customer requested refund")
    if tprRefund == False:
        print("FAIL: payment_refund returned false")
        return False
    tprRefundStatus = helpers_get_map_value_safe(tprRefund, "status", "")
    if tprRefundStatus != "refund":
        print("FAIL: payment_refund - expected status refund, got " + tprRefundStatus)
        return False
    tprRefundAmount = helpers_get_map_value_safe(tprRefund, "amount", 0)
    if tprRefundAmount >= 0:
        print("FAIL: payment_refund - expected negative amount, got " + str(tprRefundAmount))
        return False
    tprRefundReason = helpers_get_map_value_safe(tprRefund, "reason", "")
    if tprRefundReason != "Customer requested refund":
        print("FAIL: payment_refund - reason mismatch, got " + tprRefundReason)
        return False
    print("PASS: payment_refund")
    return True


def main():
    tp1 = test_payment_create()
    if tp1 == False:
        return 1
    tp2 = test_payment_get_by_id_missing()
    if tp2 == False:
        return 1
    tp3 = test_payment_list_by_invoice()
    if tp3 == False:
        return 1
    tp4 = test_payment_total_by_invoice()
    if tp4 == False:
        return 1
    tp5 = test_payment_refund()
    if tp5 == False:
        return 1
    print("ALL PAYMENT TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
