from business.permission import (
    permission_add_action,
    permission_check,
    permission_define,
    permission_list_roles,
    permission_remove_action,
)
from core.helpers import helpers_get_map_value_safe, helpers_list_contains


def test_permission_define():
    tpActions = ["create", "read", "update"]
    tpResult = permission_define("admin", "product", tpActions)
    if tpResult == False:
        print("FAIL: permission_define returned false")
        return False
    tpId = helpers_get_map_value_safe(tpResult, "id", "")
    if tpId == "":
        print("FAIL: permission_define - no id")
        return False
    tpRole = helpers_get_map_value_safe(tpResult, "role", "")
    if tpRole != "admin":
        print("FAIL: permission_define - role mismatch")
        return False
    tpResource = helpers_get_map_value_safe(tpResult, "resource", "")
    if tpResource != "product":
        print("FAIL: permission_define - resource mismatch")
        return False
    print("PASS: permission_define")
    return True


def test_permission_check_exists():
    tcActions = ["create", "read", "update"]
    permission_define("editor", "article", tcActions)
    tcResult = permission_check("editor", "article", "read")
    if tcResult != True:
        print("FAIL: permission_check_exists - expected true, got false")
        return False
    print("PASS: permission_check_exists")
    return True


def test_permission_check_missing():
    tcResult = permission_check("editor", "article", "delete")
    if tcResult != False:
        print("FAIL: permission_check_missing - expected false, got true")
        return False
    print("PASS: permission_check_missing")
    return True


def test_permission_add_action_and_check():
    taActions = ["create", "read"]
    permission_define("manager", "report", taActions)
    taResult = permission_check("manager", "report", "delete")
    if taResult != False:
        print("FAIL: permission_add_action - expected false before add")
        return False
    permission_add_action("manager", "report", "delete")
    taCheckAfter = permission_check("manager", "report", "delete")
    if taCheckAfter != True:
        print("FAIL: permission_add_action - expected true after add")
        return False
    print("PASS: permission_add_action_and_check")
    return True


def test_permission_remove_action():
    trActions = ["create", "read", "update"]
    permission_define("operator", "machine", trActions)
    trBefore = permission_check("operator", "machine", "update")
    if trBefore != True:
        print("FAIL: permission_remove_action - expected true before remove")
        return False
    permission_remove_action("operator", "machine", "update")
    trAfter = permission_check("operator", "machine", "update")
    if trAfter != False:
        print("FAIL: permission_remove_action - expected false after remove")
        return False
    print("PASS: permission_remove_action")
    return True


def test_permission_list_roles():
    tlActions = ["read"]
    permission_define("viewer", "dashboard", tlActions)
    permission_define("viewer", "report", tlActions)
    tlRoles = permission_list_roles()
    tlLen = len(tlRoles)
    if tlLen == 0:
        print("FAIL: permission_list_roles - empty list")
        return False
    tlFoundViewer = helpers_list_contains(tlRoles, "viewer")
    if tlFoundViewer == False:
        print("FAIL: permission_list_roles - viewer not found")
        return False
    print("PASS: permission_list_roles (" + str(tlLen) + " roles)")
    return True


def main():
    tpr1 = test_permission_define()
    if tpr1 == False:
        return 1
    tpr2 = test_permission_check_exists()
    if tpr2 == False:
        return 1
    tpr3 = test_permission_check_missing()
    if tpr3 == False:
        return 1
    tpr4 = test_permission_add_action_and_check()
    if tpr4 == False:
        return 1
    tpr5 = test_permission_remove_action()
    if tpr5 == False:
        return 1
    tpr6 = test_permission_list_roles()
    if tpr6 == False:
        return 1
    print("ALL PERMISSION TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
