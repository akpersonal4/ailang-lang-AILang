from datetime import datetime

from core.helpers import helpers_generate_id, helpers_current_timestamp, helpers_get_map_value_safe, helpers_pad_number
from core.storage import storage_list, storage_add, storage_get_by_id, storage_update


def invoice_list_by_customer(ivlcCustomerId):
    ivlcAll = storage_list("invoices")
    ivlcResults = []
    for ivlcItem in ivlcAll:
        if helpers_get_map_value_safe(ivlcItem, "customer_id", "") == ivlcCustomerId:
            ivlcResults.append(ivlcItem)
    return ivlcResults


def invoice_create(ivcrOrderId, ivcrCustomerId, ivcrItems, ivcrTotalAmount):
    ivcrId = helpers_generate_id("INV-")
    ivcrNow = helpers_current_timestamp()
    ivcrInvoice = {
        "id": ivcrId,
        "order_id": ivcrOrderId,
        "customer_id": ivcrCustomerId,
        "items": ivcrItems,
        "total_amount": ivcrTotalAmount,
        "status": "draft",
        "created_at": ivcrNow,
        "updated_at": ivcrNow,
    }
    storage_add("invoices", ivcrInvoice)
    return ivcrInvoice


def invoice_get_by_id(ivgInvId):
    return storage_get_by_id("invoices", ivgInvId)


def invoice_list():
    return storage_list("invoices")


def invoice_update_status(ivupInvId, ivupNewStatus):
    ivupChanges = {"status": ivupNewStatus, "updated_at": helpers_current_timestamp()}
    return storage_update("invoices", ivupInvId, ivupChanges)


def invoice_calculate_total(ivctItems):
    ivctSum = 0
    for ivctItem in ivctItems:
        ivctSum += helpers_get_map_value_safe(ivctItem, "line_total", 0)
    return ivctSum


def invoice_generate_number(ivgnSequence):
    ivgnYear = datetime.now().strftime("%Y")
    ivgnSeqStr = helpers_pad_number(ivgnSequence, 4)
    return "INV-" + ivgnYear + "-" + ivgnSeqStr
