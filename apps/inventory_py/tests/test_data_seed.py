from core.storage import storage_add
from business.data_seed import seed_all


def test_seed_all():
    tsProd = {
        "id": "SEED-PROD-1",
        "name": "Seed Test Product 1",
        "unit_price": 100
    }
    storage_add("products", tsProd)
    tsProd2 = {
        "id": "SEED-PROD-2",
        "name": "Seed Test Product 2",
        "unit_price": 50
    }
    storage_add("products", tsProd2)
    tsCust = {
        "id": "SEED-CUST-1",
        "name": "Seed Customer"
    }
    storage_add("customers", tsCust)
    tsSalesOrder = {
        "id": "SEED-SO-1",
        "customer_id": "SEED-CUST-1",
        "total": 500
    }
    storage_add("sales_orders", tsSalesOrder)
    tsSalesOrder2 = {
        "id": "SEED-SO-2",
        "customer_id": "SEED-CUST-1",
        "total": 1000
    }
    storage_add("sales_orders", tsSalesOrder2)
    tsInv = {
        "id": "SEED-INV-1",
        "customer_id": "SEED-CUST-1",
        "total_amount": 500,
        "status": "draft"
    }
    storage_add("invoices", tsInv)
    seed_all()
    print("PASS: seed_all completed without error")
    return True


def main():
    tsResult = test_seed_all()
    if tsResult == False:
        return 1
    print("ALL DATA SEED TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
