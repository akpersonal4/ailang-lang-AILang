from core.helpers import helpers_get_map_value_safe
from core.storage import storage_list
from audit.audit_trail import audit_trail_summary_by_action, audit_trail_recent


def ai_format_entry(aife_item):
    aife_action = helpers_get_map_value_safe(aife_item, "action", "")
    aife_entity = helpers_get_map_value_safe(aife_item, "entity_type", "")
    aife_entity_id = helpers_get_map_value_safe(aife_item, "entity_id", "")
    aife_user = helpers_get_map_value_safe(aife_item, "created_by", "")
    aife_time = helpers_get_map_value_safe(aife_item, "created_at", "")
    return aife_time + " | " + aife_user + " | " + aife_action + " | " + aife_entity + " | " + aife_entity_id


def ai_summary_rec(aisr_items, aisr_idx, aisr_acc):
    for aisr_item in aisr_items:
        aisr_entity = helpers_get_map_value_safe(aisr_item, "entity_type", "")
        aisr_current = helpers_get_map_value_safe(aisr_acc, aisr_entity, 0)
        aisr_acc[aisr_entity] = aisr_current + 1
    return aisr_acc


def ai_build_summary_lines(aisl_keys, aisl_summary, aisl_result, aisl_idx):
    for aisl_key in aisl_keys:
        aisl_count = helpers_get_map_value_safe(aisl_summary, aisl_key, 0)
        aisl_result += aisl_key + ": " + str(aisl_count) + "\n"
    return aisl_result


def ai_recent_rec(airr_items, airr_idx, airr_end, airr_acc):
    for i in range(airr_idx, airr_end):
        airr_formatted = ai_format_entry(airr_items[i])
        airr_acc.append(airr_formatted)
    return airr_acc


def audit_integration_full_report():
    air_summary = audit_trail_summary_by_action()
    air_all = storage_list("audit_log")
    air_total = len(air_all)
    air_report = "=== AUDIT REPORT ===\n"
    air_report += "Total Entries: " + str(air_total) + "\n"
    air_report += "--- Summary by Action ---\n"
    air_keys = list(air_summary.keys())
    air_report = ai_build_summary_lines(air_keys, air_summary, air_report, 0)
    air_report += "=== END REPORT ==="
    return air_report


def audit_integration_summary_by_entity():
    aise_all = storage_list("audit_log")
    aise_acc = {}
    return ai_summary_rec(aise_all, 0, aise_acc)


def audit_integration_recent_activity(aic_count):
    aic_recent = audit_trail_recent(aic_count)
    aic_len = len(aic_recent)
    aic_result = []
    if aic_len == 0:
        return aic_result
    return ai_recent_rec(aic_recent, 0, aic_len, aic_result)
