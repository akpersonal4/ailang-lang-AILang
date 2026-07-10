from audit.audit import audit_log
from audit.audit_trail import audit_trail_list_by_date_range, audit_trail_list_by_user, audit_trail_summary_by_action, audit_trail_recent
from core.helpers import helpers_get_map_value_safe


def test_audit_trail_list_by_date_range():
    td_old = {}
    td_new = {}
    td_new["status"] = "active"
    audit_log("create", "customer", "CUST-DR-001", td_old, td_new, "date_range_user")
    td_results = audit_trail_list_by_date_range("2000-01-01", "2100-12-31")
    if td_results == False:
        print("FAIL: audit_trail_list_by_date_range returned false")
        return False
    td_len = len(td_results)
    if td_len == 0:
        print("FAIL: audit_trail_list_by_date_range - no results")
        return False
    print("PASS: audit_trail_list_by_date_range (" + str(td_len) + " items)")
    return True


def test_audit_trail_list_by_user():
    tu_old = {}
    tu_new = {}
    tu_new["name"] = "User Test Item"
    audit_log("update", "product", "PROD-USR-001", tu_old, tu_new, "test_user_at")
    audit_log("update", "product", "PROD-USR-002", tu_old, tu_new, "test_user_at")
    tu_results = audit_trail_list_by_user("test_user_at")
    if tu_results == False:
        print("FAIL: audit_trail_list_by_user returned false")
        return False
    tu_len = len(tu_results)
    if tu_len < 2:
        print("FAIL: audit_trail_list_by_user - expected at least 2, got " + str(tu_len))
        return False
    print("PASS: audit_trail_list_by_user (" + str(tu_len) + " items)")
    return True


def test_audit_trail_summary_by_action():
    ts_old = {}
    ts_new = {}
    ts_new["qty"] = 10
    audit_log("create", "inventory", "INV-SUM-001", ts_old, ts_new, "summary_user")
    audit_log("create", "inventory", "INV-SUM-002", ts_old, ts_new, "summary_user")
    audit_log("update", "inventory", "INV-SUM-003", ts_old, ts_new, "summary_user")
    ts_summary = audit_trail_summary_by_action()
    if ts_summary == False:
        print("FAIL: audit_trail_summary_by_action returned false")
        return False
    ts_create_count = helpers_get_map_value_safe(ts_summary, "create", 0)
    if ts_create_count < 2:
        print("FAIL: audit_trail_summary_by_action - expected create >= 2, got " + str(ts_create_count))
        return False
    ts_update_count = helpers_get_map_value_safe(ts_summary, "update", 0)
    if ts_update_count < 1:
        print("FAIL: audit_trail_summary_by_action - expected update >= 1, got " + str(ts_update_count))
        return False
    print("PASS: audit_trail_summary_by_action (create=" + str(ts_create_count) + ", update=" + str(ts_update_count) + ")")
    return True


def test_audit_trail_recent():
    tr_old = {}
    tr_new = {}
    tr_new["price"] = 99
    audit_log("update", "product", "PROD-REC-001", tr_old, tr_new, "recent_user")
    tr_results = audit_trail_recent(5)
    if tr_results == False:
        print("FAIL: audit_trail_recent returned false")
        return False
    tr_len = len(tr_results)
    if tr_len == 0:
        print("FAIL: audit_trail_recent - no results")
        return False
    print("PASS: audit_trail_recent (" + str(tr_len) + " items)")
    return True


def test_audit_trail_list_by_user_empty():
    te_results = audit_trail_list_by_user("nonexistent_user_xyz")
    if te_results == False:
        print("FAIL: audit_trail_list_by_user_empty returned false")
        return False
    te_len = len(te_results)
    if te_len != 0:
        print("FAIL: audit_trail_list_by_user_empty - expected 0, got " + str(te_len))
        return False
    print("PASS: audit_trail_list_by_user_empty")
    return True


def main():
    tt1 = test_audit_trail_list_by_date_range()
    if tt1 == False:
        return 1
    tt2 = test_audit_trail_list_by_user()
    if tt2 == False:
        return 1
    tt3 = test_audit_trail_summary_by_action()
    if tt3 == False:
        return 1
    tt4 = test_audit_trail_recent()
    if tt4 == False:
        return 1
    tt5 = test_audit_trail_list_by_user_empty()
    if tt5 == False:
        return 1
    print("ALL AUDIT TRAIL TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
