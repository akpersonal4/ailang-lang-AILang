import sys

from core.storage import storage_clear_all
from business.report import (
    stock_report_all_products, stock_report_valuation, stock_report_get_qty,
    stock_report_aging, sales_report_all, sales_report_total_revenue,
    sales_report_count_by_status, sales_report_items,
    profit_report_summary
)
from export.csv_export import csv_products
from export.json_export import json_export_products
from business.search import search_all
from business.dashboard import dashboard_summary
from business.permission import permission_define, permission_add_action, permission_check
from logistics.batch import batch_list
from business.workflow import workflow_pending_approvals
from audit.audit_integration import audit_integration_full_report


def main_demo_create_products():
    from models.category import category_create
    from models.product import product_create

    cat1 = category_create("Electronics", "Electronic devices and accessories", "")
    cat2 = category_create("Office Supplies", "Paper, pens, and office equipment", "")
    cat1_id = cat1.get("id", "")
    cat2_id = cat2.get("id", "")
    product_create("Laptop", "High-performance laptop", "LAP-001", cat1_id, 1200, 900, "pcs")
    product_create("Mouse", "Wireless mouse", "MOU-001", cat1_id, 25, 15, "pcs")
    product_create("Notebook", "A5 ruled notebook", "NTB-001", cat2_id, 5, 3, "pcs")
    product_create("Desk Lamp", "LED desk lamp", "LMP-001", cat2_id, 45, 30, "pcs")
    print("Created 2 categories and 4 products")
    return True


def main_demo_create_customers():
    from models.customer import customer_create
    customer_create("Alice Corp", "alice@example.com", "555-0101")
    customer_create("Bob Industries", "bob@example.com", "555-0102")
    customer_create("Charlie Ltd", "charlie@example.com", "555-0103")
    print("Created 3 customers")
    return True


def main_demo_create_vendors():
    from models.vendor import vendor_create
    vendor_create("TechSupply Inc", "info@techsupply.com", "555-0201", "John Vendor")
    vendor_create("OfficeMart", "sales@officemart.com", "555-0202", "Jane Vendor")
    print("Created 2 vendors")
    return True


def main_demo_stock_and_orders():
    from models.product import product_list
    from models.customer import customer_list
    from models.vendor import vendor_list
    from inventory.stock_movement import movement_create
    from orders.sales_order import sales_create, sales_add_item
    from orders.purchase_order import purchase_create, purchase_add_item

    all_products = product_list()
    prod_count = len(all_products)
    if prod_count == 0:
        print("No products found. Run init first.")
        return False
    first_prod = all_products[0]
    first_prod_id = first_prod.get("id", "")
    movement_create(first_prod_id, "inbound", 50, "manual", "", "Initial stock")
    print("Created inbound movement for first product")
    all_customers = customer_list()
    if len(all_customers) > 0:
        first_cust = all_customers[0]
        first_cust_id = first_cust.get("id", "")
        new_order = sales_create(first_cust_id, "First test order")
        order_id = new_order.get("id", "")
        sales_add_item(order_id, first_prod_id, 2, first_prod.get("unit_price", 0))
        print("Created sales order with 1 item")
    all_vendors = vendor_list()
    if len(all_vendors) > 0:
        first_ven = all_vendors[0]
        first_ven_id = first_ven.get("id", "")
        new_po = purchase_create(first_ven_id, "First purchase order")
        po_id = new_po.get("id", "")
        purchase_add_item(po_id, first_prod_id, 10, 850)
        print("Created purchase order with 1 item")
    return True


def main_report():
    from models.category import category_list
    from models.customer import customer_list
    from models.vendor import vendor_list
    from inventory.stock_movement import movement_list
    from orders.sales_order import sales_list
    from orders.purchase_order import purchase_list

    all_products = stock_report_all_products()
    prod_count = len(all_products)
    all_customers = customer_list()
    cust_count = len(all_customers)
    all_vendors = vendor_list()
    ven_count = len(all_vendors)
    all_movements = movement_list()
    mov_count = len(all_movements)
    all_sales = sales_list()
    sales_count = len(all_sales)
    all_purchases = purchase_list()
    purchase_count = len(all_purchases)
    print("=== INVENTORY REPORT ===")
    print("Products: " + str(prod_count))
    print("Categories: " + str(len(category_list())))
    print("Customers: " + str(cust_count))
    print("Vendors: " + str(ven_count))
    print("Stock Movements: " + str(mov_count))
    print("Sales Orders: " + str(sales_count))
    print("Purchase Orders: " + str(purchase_count))
    print("=== END REPORT ===")
    return True


def main_export_csv():
    csv_products_str = csv_products()
    print("=== PRODUCTS CSV ===")
    print(csv_products_str)
    print("=== END ===")
    return True


def main_export_json():
    json_products = json_export_products()
    print("=== PRODUCTS JSON ===")
    print(json_products)
    print("=== END ===")
    return True


def main_help():
    print("Usage: python main.py <command>")
    print("")
    print("Commands:")
    print("  init       - Initialize demo data (products, customers, vendors)")
    print("  stock      - Create demo stock movements and orders")
    print("  report     - Show inventory summary report")
    print("  csv        - Export products as CSV")
    print("  json       - Export products as JSON")
    print("  search <q> - Search across all entities")
    print("  seed       - Seed demo data for all modules")
    print("  reserve    - Create demo stock reservation")
    print("  adjust     - Create demo stock adjustment")
    print("  warehouse  - List warehouses")
    print("  dashboard  - Show dashboard summary")
    print("  permission - Demo permission operations")
    print("  batch      - Demo batch operations")
    print("  workflow   - Demo workflow operations")
    print("  audit_full - Show full audit report")
    print("  help       - Show this help")
    return True


def main_seed():
    from business.data_seed import seed_all
    seed_all()
    return 0


def main_reserve():
    from models.product import product_list
    from inventory.stock_reservation import reservation_create

    mr_all_products = product_list()
    mr_prod_count = len(mr_all_products)
    if mr_prod_count == 0:
        print("No products found. Run init first.")
        return False
    mr_first = mr_all_products[0]
    mr_first_id = mr_first.get("id", "")
    mr_reservation = reservation_create("DEMO-ORDER", mr_first_id, 5)
    if mr_reservation is False:
        print("Failed to create reservation (insufficient stock)")
    else:
        print("Created demo reservation")
    return True


def main_adjust():
    from models.product import product_list
    from inventory.stock_adjustment import adjustment_create

    ma_all_products = product_list()
    ma_prod_count = len(ma_all_products)
    if ma_prod_count == 0:
        print("No products found. Run init first.")
        return False
    ma_first = ma_all_products[0]
    ma_first_id = ma_first.get("id", "")
    adjustment_create(ma_first_id, 100, 95, "Cycle count adjustment", "Demo User")
    print("Created demo stock adjustment")
    return True


def main_warehouse():
    from models.warehouse import warehouse_list
    mw_all = warehouse_list()
    mw_count = len(mw_all)
    print("Total warehouses: " + str(mw_count))
    return True


def main_dashboard():
    md_summary = dashboard_summary()
    md_products = md_summary.get("total_products", 0)
    md_cat = md_summary.get("total_categories", 0)
    md_cust = md_summary.get("total_customers", 0)
    md_vend = md_summary.get("total_vendors", 0)
    md_mov = md_summary.get("total_movements", 0)
    md_sales = md_summary.get("total_sales_orders", 0)
    md_purch = md_summary.get("total_purchase_orders", 0)
    md_wh = md_summary.get("total_warehouses", 0)
    print("=== DASHBOARD SUMMARY ===")
    print("Products: " + str(md_products))
    print("Categories: " + str(md_cat))
    print("Customers: " + str(md_cust))
    print("Vendors: " + str(md_vend))
    print("Stock Movements: " + str(md_mov))
    print("Sales Orders: " + str(md_sales))
    print("Purchase Orders: " + str(md_purch))
    print("Warehouses: " + str(md_wh))
    print("=== END ===")
    return True


def main_permission():
    mp_defined = permission_define("admin", "products", [])
    permission_add_action("admin", "products", "create")
    permission_add_action("admin", "products", "read")
    permission_add_action("admin", "products", "update")
    permission_add_action("admin", "products", "delete")
    mp_check = permission_check("admin", "products", "create")
    if mp_check:
        print("Permission check passed: admin can create products")
    else:
        print("Permission check failed")
    return True


def main_batch():
    mb_all = batch_list()
    mb_count = len(mb_all)
    print("Total batches: " + str(mb_count))
    return True


def main_workflow():
    mw_all = workflow_pending_approvals()
    mw_count = len(mw_all)
    print("Pending workflow approvals: " + str(mw_count))
    return True


def main_audit_full():
    maf_report = audit_integration_full_report()
    print(maf_report)
    return True


def main():
    main_args = sys.argv
    main_arg_count = len(main_args)
    if main_arg_count < 2:
        return main_help()
    main_command = main_args[1]
    if main_command == "init":
        main_demo_create_products()
        main_demo_create_customers()
        main_demo_create_vendors()
        return 0
    if main_command == "stock":
        main_demo_stock_and_orders()
        return 0
    if main_command == "report":
        main_report()
        return 0
    if main_command == "csv":
        main_export_csv()
        return 0
    if main_command == "json":
        main_export_json()
        return 0
    if main_command == "seed":
        main_seed()
        return 0
    if main_command == "reserve":
        main_reserve()
        return 0
    if main_command == "adjust":
        main_adjust()
        return 0
    if main_command == "warehouse":
        main_warehouse()
        return 0
    if main_command == "dashboard":
        main_dashboard()
        return 0
    if main_command == "permission":
        main_permission()
        return 0
    if main_command == "batch":
        main_batch()
        return 0
    if main_command == "workflow":
        main_workflow()
        return 0
    if main_command == "audit_full":
        main_audit_full()
        return 0
    if main_command == "help":
        main_help()
        return 0
    print("Unknown command: " + main_command)
    main_help()
    return 1


if __name__ == "__main__":
    exit(main())
