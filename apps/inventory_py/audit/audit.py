from core.helpers import helpers_current_timestamp, helpers_generate_id
from core.storage import storage_add, storage_list


def audit_log_create(entity, entity_id, action, user, details):
    log_entry = {}
    log_entry["id"] = helpers_generate_id("AUD-")
    log_entry["action"] = action
    log_entry["entity_type"] = entity
    log_entry["entity_id"] = entity_id
    log_entry["old_values"] = details
    log_entry["new_values"] = details
    log_entry["created_by"] = user
    log_entry["created_at"] = helpers_current_timestamp()
    return storage_add("audit_log", log_entry)


def audit_log(action, entity_type, entity_id, old_values, new_values, created_by):
    log_entry = {}
    log_entry["id"] = helpers_generate_id("AUD-")
    log_entry["action"] = action
    log_entry["entity_type"] = entity_type
    log_entry["entity_id"] = entity_id
    log_entry["old_values"] = old_values
    log_entry["new_values"] = new_values
    log_entry["created_by"] = created_by
    log_entry["created_at"] = helpers_current_timestamp()
    return storage_add("audit_log", log_entry)


def audit_list():
    return storage_list("audit_log")


def audit_filter_rec(al_items, al_entity_type, al_entity_id, al_idx, al_acc):
    for al_item in al_items:
        if (
            al_item.get("entity_type") == al_entity_type
            and al_item.get("entity_id") == al_entity_id
        ):
            al_acc.append(al_item)
    return al_acc


def audit_list_by_entity(entity_type, entity_id):
    al_all_logs = storage_list("audit_log")
    al_filtered = []
    return audit_filter_rec(al_all_logs, entity_type, entity_id, 0, al_filtered)
