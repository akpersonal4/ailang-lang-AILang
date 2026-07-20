from audit.audit import audit_log
from audit.audit_integration import (
    audit_integration_full_report,
    audit_integration_recent_activity,
    audit_integration_summary_by_entity,
)
from core.helpers import helpers_get_map_value_safe


def test_ai_full_report():
    taifr_old = {}
    taifr_new = {}
    taifr_new["status"] = "active"
    audit_log("create", "product", "AIPROD-1", taifr_old, taifr_new, "test_user_ai")
    audit_log("update", "product", "AIPROD-2", taifr_old, taifr_new, "test_user_ai")
    taifr_report = audit_integration_full_report()
    if taifr_report == False:
        print("FAIL: audit_integration_full_report returned false")
        return False
    taifr_len = len(taifr_report)
    if taifr_len == 0:
        print("FAIL: audit_integration_full_report returned empty string")
        return False
    print("PASS: ai_full_report (length=" + str(taifr_len) + ")")
    return True


def test_ai_summary_by_entity():
    taise_old = {}
    taise_new = {}
    taise_new["name"] = "Entity Test"
    audit_log("create", "customer", "CUST-AI-1", taise_old, taise_new, "entity_user")
    audit_log("create", "customer", "CUST-AI-2", taise_old, taise_new, "entity_user")
    audit_log("create", "product", "PROD-AI-1", taise_old, taise_new, "entity_user")
    taise_summary = audit_integration_summary_by_entity()
    if taise_summary == False:
        print("FAIL: audit_integration_summary_by_entity returned false")
        return False
    taise_customer_count = helpers_get_map_value_safe(taise_summary, "customer", 0)
    if taise_customer_count < 2:
        print("FAIL: expected customer >= 2, got " + str(taise_customer_count))
        return False
    taise_product_count = helpers_get_map_value_safe(taise_summary, "product", 0)
    if taise_product_count < 1:
        print("FAIL: expected product >= 1, got " + str(taise_product_count))
        return False
    print(
        "PASS: ai_summary_by_entity (customer="
        + str(taise_customer_count)
        + ", product="
        + str(taise_product_count)
        + ")"
    )
    return True


def test_ai_recent_activity():
    taira_old = {}
    taira_new = {}
    taira_new["qty"] = 50
    audit_log("update", "inventory", "INV-AI-1", taira_old, taira_new, "recent_user")
    taira_results = audit_integration_recent_activity(5)
    if taira_results == False:
        print("FAIL: audit_integration_recent_activity returned false")
        return False
    taira_len = len(taira_results)
    if taira_len == 0:
        print("FAIL: audit_integration_recent_activity returned empty list")
        return False
    taira_first = taira_results[0]
    if taira_first == False:
        print("FAIL: recent activity entry is false")
        return False
    taira_first_str = str(taira_first)
    if taira_first_str == "":
        print("FAIL: recent activity entry is empty")
        return False
    print("PASS: ai_recent_activity (" + str(taira_len) + " items)")
    return True


def main():
    ta1 = test_ai_full_report()
    if ta1 == False:
        return 1
    ta2 = test_ai_summary_by_entity()
    if ta2 == False:
        return 1
    ta3 = test_ai_recent_activity()
    if ta3 == False:
        return 1
    print("ALL AUDIT INTEGRATION TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
