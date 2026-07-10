from core.helpers import helpers_generate_id, helpers_current_timestamp, helpers_get_map_value_safe
from core.storage import storage_list, storage_add, storage_get_by_id


def payment_create(pyInvoiceId, pyAmount, pyMethod, pyPaidBy):
    pyId = helpers_generate_id("PAY-")
    pyNow = helpers_current_timestamp()
    pyPayment = {
        "id": pyId,
        "invoice_id": pyInvoiceId,
        "amount": pyAmount,
        "method": pyMethod,
        "paid_by": pyPaidBy,
        "status": "completed",
        "created_at": pyNow,
    }
    storage_add("payments", pyPayment)
    return pyPayment


def payment_get_by_id(pyPaymentId):
    return storage_get_by_id("payments", pyPaymentId)


def payment_list():
    return storage_list("payments")


def payment_list_by_invoice(pyInvoiceId):
    pyAll = storage_list("payments")
    pyResults = []
    for pyItem in pyAll:
        if helpers_get_map_value_safe(pyItem, "invoice_id", "") == pyInvoiceId:
            pyResults.append(pyItem)
    return pyResults


def payment_list_by_method(pyMethod):
    pyAll = storage_list("payments")
    pyResults = []
    for pyItem in pyAll:
        if helpers_get_map_value_safe(pyItem, "method", "") == pyMethod:
            pyResults.append(pyItem)
    return pyResults


def payment_total_by_invoice(pyInvoiceId):
    pyAll = storage_list("payments")
    pySum = 0
    for pyItem in pyAll:
        if helpers_get_map_value_safe(pyItem, "invoice_id", "") == pyInvoiceId:
            pySum += helpers_get_map_value_safe(pyItem, "amount", 0)
    return pySum


def payment_refund(prPaymentId, prReason):
    prOriginal = storage_get_by_id("payments", prPaymentId)
    if prOriginal is False or prOriginal is None:
        return False
    prOriginalInvoiceId = helpers_get_map_value_safe(prOriginal, "invoice_id", "")
    prOriginalAmount = helpers_get_map_value_safe(prOriginal, "amount", 0)
    prOriginalMethod = helpers_get_map_value_safe(prOriginal, "method", "")
    prOriginalPaidBy = helpers_get_map_value_safe(prOriginal, "paid_by", "")
    prRefundId = helpers_generate_id("PAY-")
    prNow = helpers_current_timestamp()
    prRefundEntry = {
        "id": prRefundId,
        "invoice_id": prOriginalInvoiceId,
        "amount": 0 - prOriginalAmount,
        "method": prOriginalMethod,
        "paid_by": prOriginalPaidBy,
        "status": "refund",
        "reason": prReason,
        "original_payment_id": prPaymentId,
        "created_at": prNow,
    }
    storage_add("payments", prRefundEntry)
    return prRefundEntry
