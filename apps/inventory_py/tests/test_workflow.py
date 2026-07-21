from business.workflow import (
    workflow_approve_director,
    workflow_approve_manager,
    workflow_close,
    workflow_create,
    workflow_fulfill,
    workflow_get_by_id,
    workflow_get_by_order,
    workflow_get_stage,
    workflow_reject,
)
from core.helpers import helpers_get_map_value_safe


def test_wf_create_and_get():
    twfWf = workflow_create("WF-TEST-ORDER-1", "sales", 1000, "test_user")
    if twfWf == False:
        print("FAIL: workflow_create returned false")
        return False
    twfId = helpers_get_map_value_safe(twfWf, "id", "")
    if twfId == "":
        print("FAIL: workflow has no id")
        return False
    twfFetched = workflow_get_by_id(twfId)
    if twfFetched == False:
        print("FAIL: could not fetch workflow by id")
        return False
    twfStage = helpers_get_map_value_safe(twfFetched, "stage", "")
    if twfStage != "pending":
        print("FAIL: expected stage pending, got " + twfStage)
        return False
    print("PASS: workflow_create and get_by_id")
    return True


def test_wf_get_by_order():
    twgoWf = workflow_create("WF-TEST-ORDER-2", "purchase", 2000, "test_user")
    twgoFound = workflow_get_by_order("WF-TEST-ORDER-2")
    if twgoFound == False:
        print("FAIL: could not find workflow by order")
        return False
    print("PASS: workflow_get_by_order")
    return True


def test_wf_approve_manager_auto():
    twamWf = workflow_create("WF-TEST-ORDER-3", "sales", 3000, "test_user")
    twamId = helpers_get_map_value_safe(twamWf, "id", "")
    twamResult = workflow_approve_manager(twamId, "manager1")
    if twamResult == False:
        print("FAIL: approve_manager returned false")
        return False
    twamStage = workflow_get_stage(twamId)
    if twamStage != "approved":
        print("FAIL: expected auto-approve stage approved, got " + twamStage)
        return False
    print("PASS: workflow_approve_manager auto-approve")
    return True


def test_wf_approve_manager_pending():
    twampWf = workflow_create("WF-TEST-ORDER-4", "sales", 10000, "test_user")
    twampId = helpers_get_map_value_safe(twampWf, "id", "")
    twampResult = workflow_approve_manager(twampId, "manager1")
    if twampResult == False:
        print("FAIL: approve_manager returned false")
        return False
    twampStage = workflow_get_stage(twampId)
    if twampStage != "approved_by_manager":
        print("FAIL: expected stage approved_by_manager, got " + twampStage)
        return False
    twampDirResult = workflow_approve_director(twampId, "director1")
    if twampDirResult == False:
        print("FAIL: approve_director returned false")
        return False
    twampDirStage = workflow_get_stage(twampId)
    if twampDirStage != "approved_by_director":
        print("FAIL: expected stage approved_by_director, got " + twampDirStage)
        return False
    print("PASS: workflow_approve_manager and director")
    return True


def test_wf_fulfill_and_close():
    twfcWf = workflow_create("WF-TEST-ORDER-5", "sales", 500, "test_user")
    twfcId = helpers_get_map_value_safe(twfcWf, "id", "")
    workflow_approve_manager(twfcId, "manager1")
    twfcFulfill = workflow_fulfill(twfcId)
    if twfcFulfill == False:
        print("FAIL: fulfill returned false")
        return False
    twfcStage = workflow_get_stage(twfcId)
    if twfcStage != "fulfilled":
        print("FAIL: expected stage fulfilled, got " + twfcStage)
        return False
    twfcClose = workflow_close(twfcId)
    if twfcClose == False:
        print("FAIL: close returned false")
        return False
    twfcClosedStage = workflow_get_stage(twfcId)
    if twfcClosedStage != "closed":
        print("FAIL: expected stage closed, got " + twfcClosedStage)
        return False
    print("PASS: workflow_fulfill and close")
    return True


def test_wf_reject():
    twrWf = workflow_create("WF-TEST-ORDER-6", "purchase", 15000, "test_user")
    twrId = helpers_get_map_value_safe(twrWf, "id", "")
    twrResult = workflow_reject(twrId, "Budget exceeded")
    if twrResult == False:
        print("FAIL: reject returned false")
        return False
    twrStage = workflow_get_stage(twrId)
    if twrStage != "rejected":
        print("FAIL: expected stage rejected, got " + twrStage)
        return False
    print("PASS: workflow_reject")
    return True


def main():
    tw1 = test_wf_create_and_get()
    if tw1 == False:
        return 1
    tw2 = test_wf_get_by_order()
    if tw2 == False:
        return 1
    tw3 = test_wf_approve_manager_auto()
    if tw3 == False:
        return 1
    tw4 = test_wf_approve_manager_pending()
    if tw4 == False:
        return 1
    tw5 = test_wf_fulfill_and_close()
    if tw5 == False:
        return 1
    tw6 = test_wf_reject()
    if tw6 == False:
        return 1
    print("ALL WORKFLOW TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
