from core.helpers import helpers_generate_id, helpers_current_timestamp, helpers_get_map_value_safe
from core.storage import storage_add, storage_get_by_id, storage_update, storage_delete, storage_list

def product_create(pcName, pcDescription, pcSku, pcCategoryId, pcUnitPrice, pcCostPrice, pcUnit):
    pcId = helpers_generate_id("PRD-")
    pcNow = helpers_current_timestamp()
    pcProduct = {
        "id": pcId,
        "name": pcName,
        "description": pcDescription,
        "sku": pcSku,
        "category_id": pcCategoryId,
        "unit_price": pcUnitPrice,
        "cost_price": pcCostPrice,
        "unit": pcUnit,
        "active": True,
        "created_at": pcNow,
        "updated_at": "",
    }
    storage_add("products", pcProduct)
    return pcProduct

def product_get(pgId):
    return storage_get_by_id("products", pgId)

def product_update(puId, puChanges):
    puNow = helpers_current_timestamp()
    puChanges["updated_at"] = puNow
    return storage_update("products", puId, puChanges)


def product_update_status(pusId, pusStatus):
    pusChanges = {
        "active": pusStatus == "active",
        "updated_at": helpers_current_timestamp(),
    }
    return storage_update("products", pusId, pusChanges)


def product_deactivate_cascade(pdcId):
    from orders.purchase_order import purchase_list_by_product, purchase_cancel
    from inventory.stock_reservation import reservation_list_by_product, reservation_cancel
    from inventory.stock_movement import movement_list_by_product, movement_update_status
    
    pos = purchase_list_by_product(pdcId)
    for order in pos:
        purchase_cancel(helpers_get_map_value_safe(order, "id", ""))
    
    reservations = reservation_list_by_product(pdcId)
    for res in reservations:
        reservation_cancel(helpers_get_map_value_safe(res, "id", ""))
    
    movements = movement_list_by_product(pdcId)
    for mov in movements:
        movement_update_status(helpers_get_map_value_safe(mov, "id", ""), "cancelled")
    
    return True


def product_delete(pdId):
    return storage_delete("products", pdId)

def product_list():
    return storage_list("products")

def product_search(psQuery):
    psAll = storage_list("products")
    psResults = []
    psQueryLower = psQuery.lower()
    for pcsrItem in psAll:
        pcsrName = helpers_get_map_value_safe(pcsrItem, "name", "")
        pcsrNameLower = pcsrName.lower()
        if psQueryLower in pcsrNameLower:
            psResults.append(pcsrItem)
    return psResults
