from business.reorder import reorder_set_level
from core.helpers import helpers_get_map_value_safe
from core.storage import storage_list


def seed_warehouses():
    from models.warehouse import warehouse_create

    warehouse_create("Main Warehouse", "WH-MAIN", "123 Main St", "New York", "US")
    warehouse_create(
        "Secondary Warehouse", "WH-SEC", "456 Oak Ave", "Los Angeles", "US"
    )
    print("Seeded 2 warehouses")
    return True


def seed_reorder_levels():
    srl_all_products = storage_list("products")
    srl_len = len(srl_all_products)
    if srl_len > 0:
        srl_first = srl_all_products[0]
        srl_first_id = helpers_get_map_value_safe(srl_first, "id", "")
        reorder_set_level(srl_first_id, 10, 100, 25)
    if srl_len > 1:
        srl_second = srl_all_products[1]
        srl_second_id = helpers_get_map_value_safe(srl_second, "id", "")
        reorder_set_level(srl_second_id, 10, 100, 25)
    print("Seeded reorder levels")
    return True


def seed_currencies():
    from financial.currency import currency_set_rate

    currency_set_rate("USD", "EUR", 0.92)
    currency_set_rate("USD", "GBP", 0.79)
    print("Seeded 2 currency rates")
    return True


def seed_taxes():
    from financial.tax import tax_create

    tax_create("VAT 20%", 20, "GB", "")
    tax_create("Sales Tax 8%", 8, "US", "")
    print("Seeded 2 tax rates")
    return True


def seed_suppliers():
    from models.supplier import supplier_create

    supplier_create(
        "Acme Supplies",
        "John Acme",
        "acme@example.com",
        "555-1001",
        "123 Supply Lane",
        "net_30",
        14,
        5,
    )
    supplier_create(
        "Global Parts",
        "Jane Global",
        "global@example.com",
        "555-1002",
        "456 Parts Blvd",
        "net_60",
        21,
        4,
    )
    print("Seeded 2 suppliers")
    return True


def seed_batches():
    from logistics.batch import batch_create

    sb_all_products = storage_list("products")
    sb_len = len(sb_all_products)
    if sb_len > 0:
        sb_first = sb_all_products[0]
        sb_first_id = helpers_get_map_value_safe(sb_first, "id", "")
        batch_create(sb_first_id, "BAT-2024-001", 100, "2025-12-31", "2024-01-15")
    if sb_len > 1:
        sb_second = sb_all_products[1]
        sb_second_id = helpers_get_map_value_safe(sb_second, "id", "")
        batch_create(sb_second_id, "BAT-2024-002", 200, "2025-06-30", "2024-02-01")
    print("Seeded batches")
    return True


def seed_serials():
    from logistics.serial_number import serial_register

    ss_all_products = storage_list("products")
    ss_len = len(ss_all_products)
    if ss_len > 0:
        ss_first = ss_all_products[0]
        ss_first_id = helpers_get_map_value_safe(ss_first, "id", "")
        ss_all_batches = storage_list("batches")
        ss_batch_id = ""
        if len(ss_all_batches) > 0:
            ss_first_batch = ss_all_batches[0]
            ss_batch_id = helpers_get_map_value_safe(ss_first_batch, "id", "")
        serial_register(ss_first_id, "SN-2024-00001", ss_batch_id)
        serial_register(ss_first_id, "SN-2024-00002", ss_batch_id)
    print("Seeded serial numbers")
    return True


def seed_payments():
    from financial.payment import payment_create

    sp_all_invoices = storage_list("invoices")
    sp_len = len(sp_all_invoices)
    if sp_len > 0:
        sp_first = sp_all_invoices[0]
        sp_first_id = helpers_get_map_value_safe(sp_first, "id", "")
        sp_total = helpers_get_map_value_safe(sp_first, "total_amount", 0)
        payment_create(sp_first_id, sp_total, "card", "Demo User")
    print("Seeded payments")
    return True


def seed_returns():
    from orders.returns import returns_create

    sr_all_sales = storage_list("sales_orders")
    sr_len = len(sr_all_sales)
    sr_all_products = storage_list("products")
    sr_prod_id = ""
    if len(sr_all_products) > 0:
        sr_first_prod = sr_all_products[0]
        sr_prod_id = helpers_get_map_value_safe(sr_first_prod, "id", "")
    if sr_len > 0:
        sr_first_order = sr_all_sales[0]
        sr_order_id = helpers_get_map_value_safe(sr_first_order, "id", "")
        returns_create(sr_order_id, sr_prod_id, 1, "Damaged item", "Demo User")
    print("Seeded returns")
    return True


def seed_shippings():
    from orders.shipping import shipping_create

    ssh_all_sales = storage_list("sales_orders")
    ssh_len = len(ssh_all_sales)
    if ssh_len > 0:
        ssh_first = ssh_all_sales[0]
        ssh_order_id = helpers_get_map_value_safe(ssh_first, "id", "")
        shipping_create(
            ssh_order_id, "FedEx", "TRACK-001", "123 Main St, New York", "Demo User"
        )
    print("Seeded shippings")
    return True


def seed_workflows():
    from business.workflow import workflow_create

    sw_all_sales = storage_list("sales_orders")
    sw_len = len(sw_all_sales)
    if sw_len > 0:
        sw_first = sw_all_sales[0]
        sw_order_id = helpers_get_map_value_safe(sw_first, "id", "")
        workflow_create(sw_order_id, "sales_order", 2500, "Demo User")
    if sw_len > 1:
        sw_second = sw_all_sales[1]
        sw_order_id = helpers_get_map_value_safe(sw_second, "id", "")
        workflow_create(sw_order_id, "sales_order", 7500, "Demo User")
    print("Seeded workflows")
    return True


def seed_all():
    seed_warehouses()
    seed_reorder_levels()
    seed_currencies()
    seed_taxes()
    seed_suppliers()
    seed_batches()
    seed_serials()
    seed_payments()
    seed_returns()
    seed_shippings()
    seed_workflows()
    print("All seed data created")
    return True
