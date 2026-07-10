from core.helpers import helpers_get_map_value_safe
from core.storage import storage_list


def pi_list_overdue_invoices_rec(pilor_items, pilor_idx, pilor_acc):
    for pilor_item in pilor_items:
        pilor_status = helpers_get_map_value_safe(pilor_item, "status", "")
        if pilor_status == "sent":
            pilor_acc.append(pilor_item)
    return pilor_acc


def pi_process_invoice_payment(pip_invoice_id, pip_amount, pip_method, pip_paid_by):
    from financial.invoice import invoice_get_by_id, invoice_update_status
    from financial.payment import payment_create
    pip_inv = invoice_get_by_id(pip_invoice_id)
    if pip_inv is False:
        return False
    pip_total = helpers_get_map_value_safe(pip_inv, "total_amount", 0)
    payment_create(pip_invoice_id, pip_amount, pip_method, pip_paid_by)
    if pip_amount >= pip_total:
        invoice_update_status(pip_invoice_id, "paid")
    return True


def pi_get_invoice_balance(pig_invoice_id):
    from financial.invoice import invoice_get_by_id
    from financial.payment import payment_total_by_invoice
    pig_inv = invoice_get_by_id(pig_invoice_id)
    if pig_inv is False:
        return 0
    pig_total = helpers_get_map_value_safe(pig_inv, "total_amount", 0)
    pig_paid = payment_total_by_invoice(pig_invoice_id)
    return pig_total - pig_paid


def pi_list_overdue_invoices():
    from financial.invoice import invoice_list
    pio_all = invoice_list()
    pio_results = []
    return pi_list_overdue_invoices_rec(pio_all, 0, pio_results)
