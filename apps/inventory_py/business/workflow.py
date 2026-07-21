from core.helpers import (
    helpers_current_timestamp,
    helpers_generate_id,
    helpers_get_map_value_safe,
)
from core.storage import storage_add, storage_get_by_id, storage_list, storage_update


def wfgor_find_by_order_rec(wfgor_items, wfgor_order_id, wfgor_idx):
    for wfgor_item in wfgor_items:
        wfgor_item_order_id = helpers_get_map_value_safe(wfgor_item, "order_id", "")
        if wfgor_item_order_id == wfgor_order_id:
            return wfgor_item
    return False


def wfpar_filter_pending_rec(wfpar_items, wfpar_results, wfpar_idx):
    for wfpar_item in wfpar_items:
        wfpar_stage = helpers_get_map_value_safe(wfpar_item, "stage", "")
        if wfpar_stage == "pending" or wfpar_stage == "approved_by_manager":
            wfpar_results.append(wfpar_item)
    return wfpar_results


def workflow_create(wfcr_order_id, wfcr_order_type, wfcr_amount, wfcr_created_by):
    wfcr_workflow = {}
    wfcr_id = helpers_generate_id("WF-")
    wfcr_now = helpers_current_timestamp()
    wfcr_workflow["id"] = wfcr_id
    wfcr_workflow["order_id"] = wfcr_order_id
    wfcr_workflow["order_type"] = wfcr_order_type
    wfcr_workflow["amount"] = wfcr_amount
    wfcr_workflow["stage"] = "pending"
    wfcr_workflow["approver"] = ""
    wfcr_workflow["reject_reason"] = ""
    wfcr_workflow["created_by"] = wfcr_created_by
    wfcr_workflow["created_at"] = wfcr_now
    wfcr_workflow["updated_at"] = wfcr_now
    storage_add("workflows", wfcr_workflow)
    return wfcr_workflow


def workflow_get_by_id(wfgi_id):
    return storage_get_by_id("workflows", wfgi_id)


def workflow_get_by_order(wfgo_order_id):
    wfgo_all = storage_list("workflows")
    return wfgor_find_by_order_rec(wfgo_all, wfgo_order_id, 0)


def workflow_approve_manager(wfam_id, wfam_approver):
    wfam_workflow = storage_get_by_id("workflows", wfam_id)
    if wfam_workflow is False:
        return False
    wfam_now = helpers_current_timestamp()
    wfam_changes = {}
    wfam_changes["approver"] = wfam_approver
    wfam_changes["updated_at"] = wfam_now
    wfam_amount = helpers_get_map_value_safe(wfam_workflow, "amount", 0)
    if wfam_amount <= 5000:
        wfam_changes["stage"] = "approved"
    else:
        wfam_changes["stage"] = "approved_by_manager"
    return storage_update("workflows", wfam_id, wfam_changes)


def workflow_approve_director(wfad_id, wfad_approver):
    wfad_workflow = storage_get_by_id("workflows", wfad_id)
    if wfad_workflow is False:
        return False
    wfad_stage = helpers_get_map_value_safe(wfad_workflow, "stage", "")
    if wfad_stage != "approved_by_manager":
        return False
    wfad_now = helpers_current_timestamp()
    wfad_changes = {
        "stage": "approved_by_director",
        "approver": wfad_approver,
        "updated_at": wfad_now,
    }
    return storage_update("workflows", wfad_id, wfad_changes)


def workflow_fulfill(wff_id):
    wff_workflow = storage_get_by_id("workflows", wff_id)
    if wff_workflow is False:
        return False
    wff_now = helpers_current_timestamp()
    wff_changes = {"stage": "fulfilled", "updated_at": wff_now}
    return storage_update("workflows", wff_id, wff_changes)


def workflow_close(wfcl_id):
    wfcl_workflow = storage_get_by_id("workflows", wfcl_id)
    if wfcl_workflow is False:
        return False
    wfcl_now = helpers_current_timestamp()
    wfcl_changes = {"stage": "closed", "updated_at": wfcl_now}
    return storage_update("workflows", wfcl_id, wfcl_changes)


def workflow_reject(wfr_id, wfr_reason):
    wfr_workflow = storage_get_by_id("workflows", wfr_id)
    if wfr_workflow is False:
        return False
    wfr_now = helpers_current_timestamp()
    wfr_changes = {
        "stage": "rejected",
        "reject_reason": wfr_reason,
        "updated_at": wfr_now,
    }
    return storage_update("workflows", wfr_id, wfr_changes)


def workflow_get_stage(wfgs_id):
    wfgs_workflow = storage_get_by_id("workflows", wfgs_id)
    if wfgs_workflow is False:
        return ""
    return helpers_get_map_value_safe(wfgs_workflow, "stage", "")


def workflow_pending_approvals():
    wfpa_all = storage_list("workflows")
    wfpa_results = []
    return wfpar_filter_pending_rec(wfpa_all, wfpa_results, 0)
