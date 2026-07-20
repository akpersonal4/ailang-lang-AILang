from core.helpers import helpers_get_map_value_safe
from logistics.serial_number import (
    serial_find_by_serial,
    serial_get_by_id,
    serial_list_available,
    serial_list_by_product,
    serial_register,
    serial_update_status,
)


def test_serial_register():
    tsrResult = serial_register("PRD-SR-001", "SN-100001", "BAT-SR-001")
    if tsrResult is False:
        print("FAIL: serial_register returned false")
        return False
    tsrId = helpers_get_map_value_safe(tsrResult, "id", "")
    if tsrId == "":
        print("FAIL: serial_register - serial id missing")
        return False
    tsrStatus = helpers_get_map_value_safe(tsrResult, "status", "")
    if tsrStatus != "available":
        print("FAIL: serial_register - expected status available, got " + tsrStatus)
        return False
    tsrSerialNum = helpers_get_map_value_safe(tsrResult, "serial_number", "")
    if tsrSerialNum != "SN-100001":
        print("FAIL: serial_register - expected SN-100001, got " + tsrSerialNum)
        return False
    print("PASS: serial_register")
    return True


def test_serial_get_by_id_missing():
    tsgmResult = serial_get_by_id("NONEXISTENT-SERIAL-ID")
    if tsgmResult is not False:
        print("FAIL: serial_get_by_id_missing - expected false")
        return False
    print("PASS: serial_get_by_id_missing")
    return True


def test_serial_find_by_serial():
    serial_register("PRD-FIND-001", "SN-FIND-001", "BAT-FIND-001")
    tsfbsFound = serial_find_by_serial("PRD-FIND-001", "SN-FIND-001")
    if tsfbsFound is False:
        print("FAIL: serial_find_by_serial returned false")
        return False
    tsfbsSerialNum = helpers_get_map_value_safe(tsfbsFound, "serial_number", "")
    if tsfbsSerialNum != "SN-FIND-001":
        print(
            "FAIL: serial_find_by_serial - expected SN-FIND-001, got " + tsfbsSerialNum
        )
        return False
    print("PASS: serial_find_by_serial")
    return True


def test_serial_list_by_product():
    serial_register("PRD-LIST-002", "SN-LIST-001", "BAT-LIST-001")
    serial_register("PRD-LIST-002", "SN-LIST-002", "BAT-LIST-001")
    tslbpResults = serial_list_by_product("PRD-LIST-002")
    tslbpLen = len(tslbpResults)
    if tslbpLen < 2:
        print(
            "FAIL: serial_list_by_product - expected at least 2, got " + str(tslbpLen)
        )
        return False
    print("PASS: serial_list_by_product (" + str(tslbpLen) + " items)")
    return True


def test_serial_update_status():
    tsusReg = serial_register("PRD-UPD-002", "SN-UPD-001", "BAT-UPD-001")
    tsusId = helpers_get_map_value_safe(tsusReg, "id", "")
    tsusResult = serial_update_status(tsusId, "sold")
    if tsusResult is False:
        print("FAIL: serial_update_status returned false")
        return False
    tsusUpdated = serial_get_by_id(tsusId)
    if tsusUpdated is False:
        print("FAIL: serial_update_status - not found after update")
        return False
    tsusNewStatus = helpers_get_map_value_safe(tsusUpdated, "status", "")
    if tsusNewStatus != "sold":
        print("FAIL: serial_update_status - expected sold, got " + tsusNewStatus)
        return False
    print("PASS: serial_update_status")
    return True


def test_serial_list_available():
    serial_register("PRD-AVAIL-001", "SN-AVAIL-001", "BAT-AVAIL-001")
    tslaSold = serial_register("PRD-AVAIL-001", "SN-AVAIL-002", "BAT-AVAIL-001")
    tslaSoldId = helpers_get_map_value_safe(tslaSold, "id", "")
    serial_update_status(tslaSoldId, "sold")
    tslaResults = serial_list_available("PRD-AVAIL-001")
    tslaLen = len(tslaResults)
    if tslaLen == 0:
        print("FAIL: serial_list_available - expected at least 1 available")
        return False
    tslaFirst = tslaResults[0]
    tslaFirstStatus = helpers_get_map_value_safe(tslaFirst, "status", "")
    if tslaFirstStatus != "available":
        print("FAIL: serial_list_available - found non-available serial")
        return False
    print("PASS: serial_list_available (" + str(tslaLen) + " available)")
    return True


def main():
    ts1 = test_serial_register()
    if ts1 is False:
        return 1
    ts2 = test_serial_get_by_id_missing()
    if ts2 is False:
        return 1
    ts3 = test_serial_find_by_serial()
    if ts3 is False:
        return 1
    ts4 = test_serial_list_by_product()
    if ts4 is False:
        return 1
    ts5 = test_serial_update_status()
    if ts5 is False:
        return 1
    ts6 = test_serial_list_available()
    if ts6 is False:
        return 1
    print("ALL SERIAL NUMBER TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
