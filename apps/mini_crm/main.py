#!/usr/bin/env python3
"""Mini CRM Platform - Python Implementation
Target: 800-1500 LOC, Production-style structure
Modules: Customer, Product, Invoice, User, Search, Reporting, Export, Audit
"""

import json
import os
import sys
from typing import Any, Dict, List

# ============================================================
# Level 1: Storage Layer
# ============================================================

DATA_DIR = "apps/mini_crm/data"
CUSTOMERS_PATH = os.path.join(DATA_DIR, "customers.json")
PRODUCTS_PATH = os.path.join(DATA_DIR, "products.json")
INVOICES_PATH = os.path.join(DATA_DIR, "invoices.json")
USERS_PATH = os.path.join(DATA_DIR, "users.json")
AUDIT_PATH = os.path.join(DATA_DIR, "audit.json")


def load_json_list(filepath: str) -> List[Dict]:
    if not os.path.exists(filepath):
        return []
    with open(filepath) as f:
        content = f.read()
    if not content:
        return []
    return json.loads(content)


def save_json_list(filepath: str, items: List[Dict]) -> int:
    with open(filepath, "w") as f:
        json.dump(items, f)
    return 0


# ============================================================
# Level 2: Customer Module
# ============================================================


def make_customer(
    id: str,
    name: str,
    email: str,
    phone: str,
    company: str,
    status: str = "ACTIVE",
    notes: str = "",
) -> Dict:
    return {
        "id": id,
        "name": name,
        "email": email,
        "phone": phone,
        "company": company,
        "status": status,
        "notes": notes,
        "created": __import__("time").time(),
        "loyalty_points": 0,
    }


def customer_create(id: str, name: str, email: str, phone: str, company: str) -> str:
    customers = load_json_list(CUSTOMERS_PATH)
    if any(c.get("id") == id for c in customers):
        return "Error: Customer already exists"
    customer = make_customer(id, name, email, phone, company)
    customers.append(customer)
    save_json_list(CUSTOMERS_PATH, customers)
    return f"Customer {id} created"


def customer_list_all() -> List[Dict]:
    return load_json_list(CUSTOMERS_PATH)


def customer_find_by_id(customer_id: str) -> Dict | None:
    customers = load_json_list(CUSTOMERS_PATH)
    for c in customers:
        if c.get("id") == customer_id:
            return c
    return None


def customer_update(
    customer_id: str,
    name: str,
    email: str,
    phone: str,
    company: str,
    status: str,
    notes: str,
) -> str:
    customers = load_json_list(CUSTOMERS_PATH)
    for c in customers:
        if c.get("id") == customer_id:
            if name:
                c["name"] = name
            if email:
                c["email"] = email
            if phone:
                c["phone"] = phone
            if company:
                c["company"] = company
            if status:
                c["status"] = status
            if notes:
                c["notes"] = notes
            save_json_list(CUSTOMERS_PATH, customers)
            return f"Customer {customer_id} updated"
    return "Error: Customer not found"


def customer_delete(customer_id: str) -> str:
    customers = load_json_list(CUSTOMERS_PATH)
    for c in customers[:]:
        if c.get("id") == customer_id:
            customers.remove(c)
            save_json_list(CUSTOMERS_PATH, customers)
            return f"Customer {customer_id} deleted"
    return "Error: Customer not found"


def customer_search_by_name(name_substr: str) -> List[Dict]:
    customers = load_json_list(CUSTOMERS_PATH)
    lower = name_substr.lower()
    return [c for c in customers if "name" in c and lower in c["name"].lower()]


def customer_set_status(customer_id: str, status: str) -> str:
    customers = load_json_list(CUSTOMERS_PATH)
    for c in customers:
        if c.get("id") == customer_id:
            c["status"] = status
            save_json_list(CUSTOMERS_PATH, customers)
            return f"Customer {customer_id} status set to {status}"
    return "Error: Customer not found"


def customer_add_note(customer_id: str, note: str) -> str:
    customers = load_json_list(CUSTOMERS_PATH)
    for c in customers:
        if c.get("id") == customer_id:
            existing = c.get("notes", "")
            c["notes"] = f"{existing}; {note}" if existing else note
            save_json_list(CUSTOMERS_PATH, customers)
            return "Note added"
    return "Error: Customer not found"


# Loyalty points - earn on purchases
def customer_add_loyalty_points(customer_id: str, points: int) -> str:
    customers = load_json_list(CUSTOMERS_PATH)
    for c in customers:
        if c.get("id") == customer_id:
            current = c.get("loyalty_points", 0)
            c["loyalty_points"] = current + points
            save_json_list(CUSTOMERS_PATH, customers)
            return "Loyalty points added"
    return "Error: Customer not found"


def customer_get_loyalty_points(customer_id: str) -> int:
    c = customer_find_by_id(customer_id)
    if c is None:
        return 0
    return c.get("loyalty_points", 0)


# Customer tags - add/remove tags
def customer_add_tag(customer_id: str, tag: str) -> str:
    customers = load_json_list(CUSTOMERS_PATH)
    for c in customers:
        if c.get("id") == customer_id:
            tags = c.get("tags", [])
            tags.append(tag)
            c["tags"] = tags
            save_json_list(CUSTOMERS_PATH, customers)
            return "Tag added"
    return "Error: Customer not found"


def customer_remove_tag(customer_id: str, tag: str) -> str:
    customers = load_json_list(CUSTOMERS_PATH)
    for c in customers:
        if c.get("id") == customer_id:
            if "tags" in c:
                c["tags"] = [t for t in c["tags"] if t != tag]
            save_json_list(CUSTOMERS_PATH, customers)
            return "Tag removed"
    return "Error: Customer not found"


def customer_tags(customer_id: str) -> List[str]:
    c = customer_find_by_id(customer_id)
    if c is None:
        return []
    return c.get("tags", [])


def customer_count_by_status(status_val: str) -> int:
    customers = load_json_list(CUSTOMERS_PATH)
    return sum(1 for c in customers if c.get("status") == status_val)


# ============================================================
# Level 3: Product Module
# ============================================================


def make_product(id: str, name: str, category: str, price: int, inventory: int) -> Dict:
    return {
        "id": id,
        "name": name,
        "category": category,
        "price": price,
        "inventory": inventory,
        "created": __import__("time").time(),
    }


def product_create(
    id: str, name: str, category: str, price: int, inventory: int
) -> str:
    products = load_json_list(PRODUCTS_PATH)
    if any(p.get("id") == id for p in products):
        return "Error: Product already exists"
    product = make_product(id, name, category, price, inventory)
    products.append(product)
    save_json_list(PRODUCTS_PATH, products)
    return f"Product {id} created"


def product_list_all() -> List[Dict]:
    return load_json_list(PRODUCTS_PATH)


def product_find_by_id(product_id: str) -> Dict | None:
    products = load_json_list(PRODUCTS_PATH)
    for p in products:
        if p.get("id") == product_id:
            return p
    return None


def product_update(
    id: str, name: str, category: str, price: int, inventory: int
) -> str:
    products = load_json_list(PRODUCTS_PATH)
    for p in products:
        if p.get("id") == id:
            if name:
                p["name"] = name
            if category:
                p["category"] = category
            if price > 0:
                p["price"] = price
            if inventory >= 0:
                p["inventory"] = inventory
            save_json_list(PRODUCTS_PATH, products)
            return f"Product {id} updated"
    return "Error: Product not found"


def product_delete(product_id: str) -> str:
    products = load_json_list(PRODUCTS_PATH)
    for p in products[:]:
        if p.get("id") == product_id:
            products.remove(p)
            save_json_list(PRODUCTS_PATH, products)
            return f"Product {product_id} deleted"
    return "Error: Product not found"


def product_search_by_name(name_substr: str) -> List[Dict]:
    products = load_json_list(PRODUCTS_PATH)
    lower = name_substr.lower()
    return [p for p in products if "name" in p and lower in p["name"].lower()]


def product_get_price(product_id: str) -> int:
    p = product_find_by_id(product_id)
    if p is None:
        return 0
    return p.get("price", 0)


def product_get_inventory(product_id: str) -> int:
    p = product_find_by_id(product_id)
    if p is None:
        return 0
    return p.get("inventory", 0)


def product_decrement_inventory(product_id: str, amount: int) -> str:
    products = load_json_list(PRODUCTS_PATH)
    for p in products:
        if p.get("id") == product_id:
            p["inventory"] = p.get("inventory", 0) - amount
            save_json_list(PRODUCTS_PATH, products)
            return "OK"
    return "Error: Product not found"


# Product bundles - products that contain other products
def make_product_bundle(id: str, component_ids: List[str], bundle_price: int) -> Dict:
    return {
        "id": id,
        "type": "bundle",
        "components": component_ids,
        "bundle_price": bundle_price,
    }


def product_create_bundle(id: str, component_ids: List[str], bundle_price: int) -> str:
    products = load_json_list(PRODUCTS_PATH)
    if any(p.get("id") == id for p in products):
        return "Error: Product already exists"
    bundle = make_product_bundle(id, component_ids, bundle_price)
    products.append(bundle)
    save_json_list(PRODUCTS_PATH, products)
    return f"Bundle {id} created"


def product_is_bundle(product_id: str) -> bool:
    p = product_find_by_id(product_id)
    if p is None:
        return False
    return p.get("type") == "bundle"


def product_count_by_category(category: str) -> int:
    products = load_json_list(PRODUCTS_PATH)
    return sum(1 for p in products if p.get("category") == category)


# ============================================================
# Level 4: Invoice Module - Invoice Items
# ============================================================


def make_invoice_item(product_id: str, quantity: int, unit_price: int) -> Dict:
    return {
        "product_id": product_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "total": quantity * unit_price,
    }


# ============================================================
# Level 5: Invoice Module - Core Invoice Operations
# ============================================================


def make_invoice(
    id: str, customer_id: str, items: List[Dict], subtotal: int, tax: int, total: int
) -> Dict:
    return {
        "id": id,
        "customer_id": customer_id,
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "created": __import__("time").time(),
        "status": "DRAFT",
    }


def invoice_calculate_subtotal(items: List[Dict]) -> int:
    return sum(item.get("total", 0) for item in items)


# GST calculation (18% default for this system)
def invoice_calculate_gst(subtotal: int, gst_rate: float) -> int:
    return int(subtotal * gst_rate / 100)


# Discount engine - two types: percentage or fixed amount
def invoice_apply_discount(
    subtotal: int, discount_type: str, discount_value: int
) -> int:
    if discount_type == "percent":
        return int(subtotal * (100 - discount_value) / 100)
    if discount_type == "fixed":
        return subtotal - discount_value
    return subtotal


def invoice_calculate_tax(subtotal: int, tax_rate: float) -> int:
    return int(subtotal * tax_rate / 100)


def invoice_create(id: str, customer_id: str) -> str:
    invoices = load_json_list(INVOICES_PATH)
    if any(inv.get("id") == id for inv in invoices):
        return "Error: Invoice already exists"
    inv = make_invoice(id, customer_id, [], 0, 0, 0)
    invoices.append(inv)
    save_json_list(INVOICES_PATH, invoices)
    return f"Invoice {id} created"


def invoice_list_all() -> List[Dict]:
    return load_json_list(INVOICES_PATH)


def invoice_find_by_id(invoice_id: str) -> Dict | None:
    invoices = load_json_list(INVOICES_PATH)
    for inv in invoices:
        if inv.get("id") == invoice_id:
            return inv
    return None


def invoice_add_item(invoice_id: str, product_id: str, quantity: int) -> str:
    invoices = load_json_list(INVOICES_PATH)
    for inv in invoices:
        if inv.get("id") == invoice_id:
            price = product_get_price(product_id)
            item = make_invoice_item(product_id, quantity, price)
            items = inv.get("items", [])
            items.append(item)
            inv["items"] = items
            sub = invoice_calculate_subtotal(items)
            tax = invoice_calculate_tax(sub, 0)
            inv["subtotal"] = sub
            inv["tax"] = tax
            inv["total"] = sub + tax
            save_json_list(INVOICES_PATH, invoices)
            return "Item added"
    return "Error: Invoice not found"


def invoice_get_total(invoice_id: str) -> int:
    inv = invoice_find_by_id(invoice_id)
    if inv is None:
        return 0
    return inv.get("total", 0)


def invoice_get_subtotal(invoice_id: str) -> int:
    inv = invoice_find_by_id(invoice_id)
    if inv is None:
        return 0
    return inv.get("subtotal", 0)


def invoice_set_status(invoice_id: str, status: str) -> str:
    invoices = load_json_list(INVOICES_PATH)
    for inv in invoices:
        if inv.get("id") == invoice_id:
            inv["status"] = status
            save_json_list(INVOICES_PATH, invoices)
            return f"Invoice {invoice_id} status set to {status}"
    return "Error: Invoice not found"


def invoice_get_history(customer_id: str) -> List[Dict]:
    invoices = load_json_list(INVOICES_PATH)
    return [inv for inv in invoices if inv.get("customer_id") == customer_id]


# ============================================================
# Level 6: User Module
# ============================================================


def make_user(id: str, username: str, role: str, permissions: List[str]) -> Dict:
    return {
        "id": id,
        "username": username,
        "role": role.lower(),
        "permissions": permissions,
        "created": __import__("time").time(),
        "activity": [],
    }


def user_create(id: str, username: str, role: str) -> str:
    users = load_json_list(USERS_PATH)
    if any(u.get("id") == id for u in users):
        return "Error: User already exists"
    perms = ["read"]
    if role.lower() == "admin":
        perms.extend(["write", "delete", "admin"])
    elif role.lower() == "manager":
        perms.append("write")
    user = make_user(id, username, role, perms)
    users.append(user)
    save_json_list(USERS_PATH, users)
    return f"User {id} created"


def user_list_all() -> List[Dict]:
    return load_json_list(USERS_PATH)


def user_find_by_id(user_id: str) -> Dict | None:
    users = load_json_list(USERS_PATH)
    for u in users:
        if u.get("id") == user_id:
            return u
    return None


def user_has_permission(user_id: str, permission: str) -> bool:
    u = user_find_by_id(user_id)
    if u is None:
        return False
    return permission in u.get("permissions", [])


def user_add_activity(user_id: str, action: str) -> str:
    users = load_json_list(USERS_PATH)
    for u in users:
        if u.get("id") == user_id:
            activity = u.get("activity", [])
            activity.append({"action": action, "timestamp": __import__("time").time()})
            u["activity"] = activity
            save_json_list(USERS_PATH, users)
            return "Activity logged"
    return "Error: User not found"


# ============================================================
# Level 7: Audit Module
# ============================================================


def audit_log(action: str, user_id: str, details: str) -> int:
    logs = load_json_list(AUDIT_PATH)
    entry = {
        "action": action,
        "user_id": user_id,
        "details": details,
        "timestamp": __import__("time").time(),
    }
    logs.append(entry)
    save_json_list(AUDIT_PATH, logs)
    return 0


def audit_list_all() -> List[Dict]:
    return load_json_list(AUDIT_PATH)


def audit_list_by_user(user_id: str) -> List[Dict]:
    logs = load_json_list(AUDIT_PATH)
    return [log for log in logs if log.get("user_id") == user_id]


# ============================================================
# Level 8: Search Module (cross-module)
# ============================================================


def search_all_entities(query: str) -> Dict:
    return {
        "customers": customer_search_by_name(query),
        "products": product_search_by_name(query),
    }


# ============================================================
# Level 9: Report Module
# ============================================================


def report_sales_summary() -> Dict:
    invoices = load_json_list(INVOICES_PATH)
    total_revenue = sum(inv.get("total", 0) for inv in invoices)
    invoice_count = len(invoices)
    avg_invoice = int(total_revenue / invoice_count) if invoice_count > 0 else 0
    return {
        "total_revenue": total_revenue,
        "invoice_count": invoice_count,
        "avg_invoice": avg_invoice,
    }


def report_customer_summary() -> Dict:
    customers = load_json_list(CUSTOMERS_PATH)
    return {
        "total_customers": len(customers),
        "active": customer_count_by_status("ACTIVE"),
        "inactive": customer_count_by_status("INACTIVE"),
    }


def report_product_summary() -> Dict:
    products = load_json_list(PRODUCTS_PATH)
    return {
        "total_products": len(products),
        "total_inventory": sum(p.get("inventory", 0) for p in products),
    }


# ============================================================
# Level 10: Export Module
# ============================================================


def export_to_json(data: Any, filepath: str) -> int:
    with open(filepath, "w") as f:
        json.dump(data, f)
    return 0


def export_to_csv(data_list: List[Dict], columns: List[str]) -> List[str]:
    lines = []
    lines.append(",".join(columns))  # header
    for item in data_list:
        row = [str(item.get(col, "")) for col in columns]
        lines.append(",".join(row))
    return lines


def export_customers_csv(filepath: str) -> str:
    customers = customer_list_all()
    columns = ["id", "name", "email", "company", "status"]
    lines = export_to_csv(customers, columns)
    with open(filepath, "w") as f:
        f.write("\n".join(lines))
    return f"Exported {len(customers)} customers"


def export_products_csv(filepath: str) -> str:
    products = product_list_all()
    columns = ["id", "name", "category", "price", "inventory"]
    lines = export_to_csv(products, columns)
    with open(filepath, "w") as f:
        f.write("\n".join(lines))
    return f"Exported {len(products)} products"


def export_invoices_csv(filepath: str) -> str:
    invoices = invoice_list_all()
    columns = ["id", "customer_id", "subtotal", "tax", "total"]
    lines = export_to_csv(invoices, columns)
    with open(filepath, "w") as f:
        f.write("\n".join(lines))
    return f"Exported {len(invoices)} invoices"


# ============================================================
# Level 11: Display Utilities
# ============================================================


def display_customer(c: Dict | None) -> None:
    if c is None:
        print("Customer not found")
        return
    print(f"  ID: {c.get('id')}")
    print(f"  Name: {c.get('name')}")
    print(f"  Company: {c.get('company')}")
    print(f"  Status: {c.get('status')}")


def display_customer_list(customers: List[Dict]) -> None:
    for c in customers:
        display_customer(c)
        print("  ---")


# ============================================================
# Level 12: CLI Dispatch
# ============================================================


def cmd_customer_add(args: List[str], start: int) -> str:
    if len(args) < start + 4:
        return "Usage: customer add <id> <name> <email> <phone> [company]"
    customer_id = args[start]
    name = args[start + 1]
    email = args[start + 2]
    phone = args[start + 3]
    company = args[start + 4] if len(args) > start + 4 else ""
    return customer_create(customer_id, name, email, phone, company)


def cmd_customer_list() -> str:
    customers = customer_list_all()
    if not customers:
        return "No customers found"
    display_customer_list(customers)
    return f"{len(customers)} customer(s)"


def cmd_customer_search(args: List[str], start: int) -> str:
    if len(args) <= start:
        return "Usage: customer search <query>"
    query = args[start]
    results = customer_search_by_name(query)
    if not results:
        return f"No customers found matching {query}"
    display_customer_list(results)
    return f"{len(results)} match(es)"


def cmd_customer_dispatch(args: List[str], start: int) -> str:
    if start >= len(args):
        return "Error: Missing customer subcommand"
    subcmd = args[start].lower()
    if subcmd == "add":
        return cmd_customer_add(args, start + 1)
    if subcmd == "list":
        return cmd_customer_list()
    if subcmd == "search":
        return cmd_customer_search(args, start + 1)
    return f"Error: Unknown customer subcommand: {subcmd}"


def cmd_product_add(args: List[str], start: int) -> str:
    if len(args) < start + 4:
        return "Usage: product add <id> <name> <category> <price> [inventory]"
    product_id = args[start]
    name = args[start + 1]
    category = args[start + 2]
    price = int(args[start + 3])
    inv = int(args[start + 4]) if len(args) > start + 4 else 0
    return product_create(product_id, name, category, price, inv)


def cmd_product_list() -> str:
    products = product_list_all()
    if not products:
        return "No products found"
    return f"{len(products)} product(s)"


def cmd_product_dispatch(args: List[str], start: int) -> str:
    if start >= len(args):
        return "Error: Missing product subcommand"
    subcmd = args[start].lower()
    if subcmd == "add":
        return cmd_product_add(args, start + 1)
    if subcmd == "list":
        return cmd_product_list()
    return f"Error: Unknown product subcommand: {subcmd}"


def cmd_invoice_create(args: List[str], start: int) -> str:
    if len(args) < start + 2:
        return "Usage: invoice create <id> <customer_id>"
    invoice_id = args[start]
    customer_id = args[start + 1]
    return invoice_create(invoice_id, customer_id)


def cmd_invoice_dispatch(args: List[str], start: int) -> str:
    if start >= len(args):
        return "Error: Missing invoice subcommand"
    subcmd = args[start].lower()
    if subcmd == "create":
        return cmd_invoice_create(args, start + 1)
    return f"Error: Unknown invoice subcommand: {subcmd}"


def cmd_report_sales() -> str:
    r = report_sales_summary()
    print("=== Sales Summary ===")
    print(f"Total Revenue: {r.get('total_revenue')}")
    print(f"Invoice Count: {r.get('invoice_count')}")
    return ""


def cmd_report_customers() -> str:
    r = report_customer_summary()
    print("=== Customer Summary ===")
    print(f"Total: {r.get('total_customers')}")
    print(f"Active: {r.get('active')}")
    return ""


def cmd_report_dispatch(args: List[str], start: int) -> str:
    if start >= len(args):
        return "Error: Missing report subcommand"
    subcmd = args[start].lower()
    if subcmd == "sales":
        return cmd_report_sales()
    if subcmd == "customers":
        return cmd_report_customers()
    return f"Error: Unknown report subcommand: {subcmd}"


def cmd_export_customers() -> str:
    return export_customers_csv("apps/mini_crm/data/customers_export.csv")


def cmd_export_dispatch(args: List[str], start: int) -> str:
    if start >= len(args):
        return "Error: Missing export subcommand"
    subcmd = args[start].lower()
    if subcmd == "customers":
        return cmd_export_customers()
    return f"Error: Unknown export subcommand: {subcmd}"


def show_usage() -> int:
    print("Mini CRM Platform - Python Implementation")
    print("")
    print("Customer Commands:")
    print("  customer add <id> <name> <email> <phone> [company]")
    print("  customer list")
    print("  customer search <query>")
    print("")
    print("Product Commands:")
    print("  product add <id> <name> <category> <price> [inventory]")
    print("  product list")
    print("")
    print("Invoice Commands:")
    print("  invoice create <id> <customer_id>")
    print("")
    print("Report Commands:")
    print("  report sales")
    print("  report customers")
    print("")
    print("Export Commands:")
    print("  export customers")
    return 0


# ============================================================
# Level 13: Main Entry Point
# ============================================================


def main() -> int:
    args = sys.argv[1:]
    if len(args) < 1:
        show_usage()
        return 0
    cmd = args[0].lower()
    result = ""
    if cmd == "customer":
        result = cmd_customer_dispatch(args, 1)
    elif cmd == "product":
        result = cmd_product_dispatch(args, 1)
    elif cmd == "invoice":
        result = cmd_invoice_dispatch(args, 1)
    elif cmd == "report":
        result = cmd_report_dispatch(args, 1)
    elif cmd == "export":
        result = cmd_export_dispatch(args, 1)
    elif cmd in ["help", "--help", "-h"]:
        show_usage()
        return 0
    else:
        show_usage()
        return 0
    if result:
        print(result)
    return 0


if __name__ == "__main__":
    main()
