from core.helpers import (
    helpers_get_map_value_safe, helpers_generate_id,
    helpers_list_contains
)
from core.storage import storage_list, storage_add, storage_update


def permission_find_rec(pm_items, pm_role, pm_resource, pm_idx):
    for pm_item in pm_items:
        pm_role_val = helpers_get_map_value_safe(pm_item, "role", "")
        pm_resource_val = helpers_get_map_value_safe(pm_item, "resource", "")
        if pm_role_val == pm_role and pm_resource_val == pm_resource:
            return pm_item
    return False


def permission_check_rec(pm_items, pm_action, pm_idx):
    for pm_item in pm_items:
        if pm_item == pm_action:
            return True
    return False


def permission_remove_action_rec(pm_items, pm_remove_action, pm_idx, pm_acc):
    for pm_item in pm_items:
        if pm_item != pm_remove_action:
            pm_acc.append(pm_item)
    return pm_acc


def permission_get_role_permissions_rec(pm_items, pm_role_name, pm_idx, pm_acc):
    for pm_item in pm_items:
        pm_item_role = helpers_get_map_value_safe(pm_item, "role", "")
        if pm_item_role == pm_role_name:
            pm_acc.append(pm_item)
    return pm_acc


def permission_list_roles_rec(pm_items, pm_idx, pm_acc):
    for pm_item in pm_items:
        pm_role_name = helpers_get_map_value_safe(pm_item, "role", "")
        pm_exists = helpers_list_contains(pm_acc, pm_role_name)
        if pm_exists is False and pm_role_name != "":
            pm_acc.append(pm_role_name)
    return pm_acc


def permission_define(pm_role_name, pm_resource, pm_actions):
    pm_record = {}
    pm_id = helpers_generate_id("PERM-")
    pm_record["id"] = pm_id
    pm_record["role"] = pm_role_name
    pm_record["resource"] = pm_resource
    pm_record["actions"] = pm_actions
    storage_add("permissions", pm_record)
    return pm_record


def permission_get_role_permissions(pm_role_name):
    pm_all = storage_list("permissions")
    pm_results = []
    return permission_get_role_permissions_rec(pm_all, pm_role_name, 0, pm_results)


def permission_get_resource_permissions(pm_role_name, pm_resource):
    pm_all = storage_list("permissions")
    return permission_find_rec(pm_all, pm_role_name, pm_resource, 0)


def permission_check(pm_role_name, pm_resource, pm_action):
    pm_all = storage_list("permissions")
    pm_record = permission_find_rec(pm_all, pm_role_name, pm_resource, 0)
    if pm_record is False:
        return False
    pm_actions = helpers_get_map_value_safe(pm_record, "actions", [])
    return permission_check_rec(pm_actions, pm_action, 0)


def permission_add_action(pm_role_name, pm_resource, pm_action):
    pm_all = storage_list("permissions")
    pm_record = permission_find_rec(pm_all, pm_role_name, pm_resource, 0)
    if pm_record is False:
        return False
    pm_id = helpers_get_map_value_safe(pm_record, "id", "")
    pm_actions = helpers_get_map_value_safe(pm_record, "actions", [])
    pm_exists = helpers_list_contains(pm_actions, pm_action)
    if pm_exists is False:
        pm_actions.append(pm_action)
    pm_changes = {"actions": pm_actions}
    return storage_update("permissions", pm_id, pm_changes)


def permission_remove_action(pm_role_name, pm_resource, pm_action):
    pm_all = storage_list("permissions")
    pm_record = permission_find_rec(pm_all, pm_role_name, pm_resource, 0)
    if pm_record is False:
        return False
    pm_id = helpers_get_map_value_safe(pm_record, "id", "")
    pm_actions = helpers_get_map_value_safe(pm_record, "actions", [])
    pm_filtered = []
    pm_new_actions = permission_remove_action_rec(pm_actions, pm_action, 0, pm_filtered)
    pm_changes = {"actions": pm_new_actions}
    return storage_update("permissions", pm_id, pm_changes)


def permission_list_roles():
    pm_all = storage_list("permissions")
    pm_roles = []
    return permission_list_roles_rec(pm_all, 0, pm_roles)
