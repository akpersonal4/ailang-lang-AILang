from core.helpers import helpers_get_map_value_safe
from orders.returns import (
    returns_approve,
    returns_complete,
    returns_create,
    returns_get_by_id,
    returns_list_by_order,
    returns_reject,
)


def test_returns_create():
    trcResult = returns_create(
        "SO-TEST-001", "PRD-TEST-001", 2, "Damaged in transit", "John Doe"
    )
    if trcResult == False:
        print("FAIL: returns_create returned false")
        return False
    trcId = helpers_get_map_value_safe(trcResult, "id", "")
    if trcId == "":
        print("FAIL: returns_create - no id generated")
        return False
    trcStatus = helpers_get_map_value_safe(trcResult, "status", "")
    if trcStatus != "pending":
        print("FAIL: returns_create - expected status pending, got " + trcStatus)
        return False
    trcQty = helpers_get_map_value_safe(trcResult, "quantity", 0)
    if trcQty != 2:
        print("FAIL: returns_create - expected quantity 2, got " + str(trcQty))
        return False
    trcOrderId = helpers_get_map_value_safe(trcResult, "order_id", "")
    if trcOrderId != "SO-TEST-001":
        print("FAIL: returns_create - order_id mismatch")
        return False
    print("PASS: returns_create")
    return True


def test_returns_get_by_id_missing():
    trgmResult = returns_get_by_id("NONEXISTENT-RETURN-ID")
    if trgmResult != False:
        print("FAIL: returns_get_by_id_missing - expected false")
        return False
    print("PASS: returns_get_by_id_missing")
    return True


def test_returns_approve():
    traCreated = returns_create(
        "SO-TEST-002", "PRD-TEST-002", 1, "Wrong item", "Jane Doe"
    )
    traId = helpers_get_map_value_safe(traCreated, "id", "")
    traUpdated = returns_approve(traId)
    if traUpdated == False:
        print("FAIL: returns_approve returned false")
        return False
    traFetched = returns_get_by_id(traId)
    traStatus = helpers_get_map_value_safe(traFetched, "status", "")
    if traStatus != "approved":
        print("FAIL: returns_approve - expected status approved, got " + traStatus)
        return False
    print("PASS: returns_approve")
    return True


def test_returns_reject():
    trrCreated = returns_create(
        "SO-TEST-003", "PRD-TEST-003", 3, "Defective", "Bob Smith"
    )
    trrId = helpers_get_map_value_safe(trrCreated, "id", "")
    trrUpdated = returns_reject(trrId, "Return window expired")
    if trrUpdated == False:
        print("FAIL: returns_reject returned false")
        return False
    trrFetched = returns_get_by_id(trrId)
    trrStatus = helpers_get_map_value_safe(trrFetched, "status", "")
    if trrStatus != "rejected":
        print("FAIL: returns_reject - expected status rejected, got " + trrStatus)
        return False
    trrReason = helpers_get_map_value_safe(trrFetched, "rejection_reason", "")
    if trrReason != "Return window expired":
        print("FAIL: returns_reject - rejection reason mismatch")
        return False
    print("PASS: returns_reject")
    return True


def test_returns_list_by_order():
    trlo1 = returns_create("SO-LIST", "PRD-LIST-1", 1, "Test reason 1", "User A")
    trlo2 = returns_create("SO-LIST", "PRD-LIST-2", 2, "Test reason 2", "User B")
    trloOrderResults = returns_list_by_order("SO-LIST")
    trloLen = len(trloOrderResults)
    if trloLen < 2:
        print("FAIL: returns_list_by_order - expected at least 2, got " + str(trloLen))
        return False
    print("PASS: returns_list_by_order (" + str(trloLen) + " items)")
    return True


def test_returns_complete():
    trcmpCreated = returns_create(
        "SO-TEST-004", "PRD-TEST-004", 1, "Change of mind", "Alice W"
    )
    trcmpId = helpers_get_map_value_safe(trcmpCreated, "id", "")
    returns_approve(trcmpId)
    trcmpUpdated = returns_complete(trcmpId)
    if trcmpUpdated == False:
        print("FAIL: returns_complete returned false")
        return False
    trcmpFetched = returns_get_by_id(trcmpId)
    trcmpStatus = helpers_get_map_value_safe(trcmpFetched, "status", "")
    if trcmpStatus != "completed":
        print("FAIL: returns_complete - expected status completed, got " + trcmpStatus)
        return False
    print("PASS: returns_complete")
    return True


def main():
    tr1 = test_returns_create()
    if tr1 == False:
        return 1
    tr2 = test_returns_get_by_id_missing()
    if tr2 == False:
        return 1
    tr3 = test_returns_approve()
    if tr3 == False:
        return 1
    tr4 = test_returns_reject()
    if tr4 == False:
        return 1
    tr5 = test_returns_list_by_order()
    if tr5 == False:
        return 1
    tr6 = test_returns_complete()
    if tr6 == False:
        return 1
    print("ALL RETURNS TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
