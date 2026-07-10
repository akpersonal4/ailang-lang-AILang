from core.helpers import helpers_get_map_value_safe, helpers_generate_id, helpers_current_timestamp
from core.storage import storage_list, storage_get_by_id, storage_add


def ti_list_by_warehouse_rec(tilwr_items, tilwr_warehouse_id, tilwr_idx, tilwr_acc):
    for tilwr_item in tilwr_items:
        tilwr_source = helpers_get_map_value_safe(tilwr_item, "source_warehouse_id", "")
        if tilwr_source == tilwr_warehouse_id:
            tilwr_acc.append(tilwr_item)
        else:
            tilwr_dest = helpers_get_map_value_safe(tilwr_item, "dest_warehouse_id", "")
            if tilwr_dest == tilwr_warehouse_id:
                tilwr_acc.append(tilwr_item)
    return tilwr_acc


def ti_summary_rec(tisr_items, tisr_idx, tisr_pending, tisr_completed, tisr_cancelled):
    for tisr_item in tisr_items:
        tisr_status = helpers_get_map_value_safe(tisr_item, "status", "")
        if tisr_status == "pending":
            tisr_pending += 1
        elif tisr_status == "completed":
            tisr_completed += 1
        elif tisr_status == "cancelled":
            tisr_cancelled += 1
    return {"pending": tisr_pending, "completed": tisr_completed, "cancelled": tisr_cancelled}


def ti_create_transfer(tic_product_id, tic_source_warehouse_id, tic_dest_warehouse_id, tic_quantity, tic_created_by):
    from inventory.stock_transfer import transfer_create
    from inventory.stock_movement import movement_create
    tic_status = "pending_approval" if tic_quantity > 100 else "pending"
    tic_transfer = transfer_create(tic_product_id, tic_source_warehouse_id, tic_dest_warehouse_id, tic_quantity, tic_status)
    tic_transfer_id = helpers_get_map_value_safe(tic_transfer, "id", "")
    tic_now = helpers_current_timestamp()
    tic_out_qty = 0 - tic_quantity
    tic_out_notes = "Transfer out to " + tic_dest_warehouse_id
    movement_create(tic_product_id, "transfer_out", tic_out_qty, "transfer", tic_transfer_id, tic_out_notes)
    tic_in_notes = "Transfer in from " + tic_source_warehouse_id
    movement_create(tic_product_id, "transfer_in", tic_quantity, "transfer", tic_transfer_id, tic_in_notes)
    tic_integration = {}
    tic_integration_id = helpers_generate_id("TI-")
    tic_integration["id"] = tic_integration_id
    tic_integration["transfer_id"] = tic_transfer_id
    tic_integration["product_id"] = tic_product_id
    tic_integration["source_warehouse_id"] = tic_source_warehouse_id
    tic_integration["dest_warehouse_id"] = tic_dest_warehouse_id
    tic_integration["quantity"] = tic_quantity
    tic_integration["status"] = tic_status
    tic_integration["created_by"] = tic_created_by
    tic_integration["created_at"] = tic_now
    storage_add("transfer_integrations", tic_integration)
    return tic_integration


def ti_get_by_id(tigi_id):
    return storage_get_by_id("transfer_integrations", tigi_id)


def ti_list():
    return storage_list("transfer_integrations")


def ti_list_by_warehouse(tilw_warehouse_id):
    tilw_all = storage_list("transfer_integrations")
    tilw_results = []
    return ti_list_by_warehouse_rec(tilw_all, tilw_warehouse_id, 0, tilw_results)


def ti_approve_transfer(tia_id):
    from core.storage import storage_update
    tia_changes = {"status": "pending", "updated_at": helpers_current_timestamp()}
    tia_integration = ti_get_by_id(tia_id)
    if tia_integration is False:
        return False
    tia_transfer_id = helpers_get_map_value_safe(tia_integration, "transfer_id", "")
    from inventory.stock_transfer import transfer_get, transfer_update_status
    transfer_update_status(tia_transfer_id, "pending")
    return storage_update("transfer_integrations", tia_id, tia_changes)


def ti_reject_transfer(tir_id):
    from core.storage import storage_update
    tir_changes = {"status": "rejected", "updated_at": helpers_current_timestamp()}
    tir_integration = ti_get_by_id(tir_id)
    if tir_integration is False:
        return False
    tir_transfer_id = helpers_get_map_value_safe(tir_integration, "transfer_id", "")
    from inventory.stock_transfer import transfer_update_status
    transfer_update_status(tir_transfer_id, "rejected")
    return storage_update("transfer_integrations", tir_id, tir_changes)


def ti_summary():
    tis_all = storage_list("transfer_integrations")
    return ti_summary_rec(tis_all, 0, 0, 0, 0)
