from core.storage import storage_add, storage_list, storage_get_by_id, storage_update, storage_delete
from core.helpers import helpers_get_map_value_safe


def test_storage_add():
    ts_item = {"id": "TEST-001", "name": "test item", "value": 100}
    ts_result = storage_add("test_collection", ts_item)
    if ts_result == False:
        print("FAIL: storage_add returned false")
        return False
    ts_loaded = storage_list("test_collection")
    if len(ts_loaded) != 1:
        print("FAIL: expected 1 item, got " + str(len(ts_loaded)))
        return False
    ts_first = ts_loaded[0]
    ts_id = helpers_get_map_value_safe(ts_first, "id", "")
    if ts_id != "TEST-001":
        print("FAIL: expected TEST-001, got " + ts_id)
        return False
    print("PASS: storage_add")
    return True


def test_storage_list_empty():
    te_loaded = storage_list("nonexistent")
    if len(te_loaded) != 0:
        print("FAIL: expected 0 items for nonexistent collection")
        return False
    print("PASS: storage_list_empty")
    return True


def test_storage_get_by_id_missing():
    tg_not_found = storage_get_by_id("test_collection", "NONEXISTENT")
    if tg_not_found != False:
        print("FAIL: expected false for missing ID")
        return False
    print("PASS: storage_get_by_id_missing")
    return True


def test_storage_get_by_id():
    tg_item = {"id": "TEST-002", "name": "get_by_id test"}
    storage_add("test_collection", tg_item)
    tg_found = storage_get_by_id("test_collection", "TEST-002")
    if tg_found == False:
        print("FAIL: storage_get_by_id returned false")
        return False
    tg_name = helpers_get_map_value_safe(tg_found, "name", "")
    if tg_name != "get_by_id test":
        print("FAIL: expected 'get_by_id test', got " + tg_name)
        return False
    print("PASS: storage_get_by_id")
    return True


def test_storage_update():
    tu_changes = {"value": 200}
    tu_result = storage_update("test_collection", "TEST-001", tu_changes)
    if tu_result == False:
        print("FAIL: storage_update returned false")
        return False
    tu_updated = storage_get_by_id("test_collection", "TEST-001")
    tu_val = helpers_get_map_value_safe(tu_updated, "value", 0)
    if tu_val != 200:
        print("FAIL: expected value 200, got " + str(tu_val))
        return False
    print("PASS: storage_update")
    return True


def test_storage_delete_missing():
    td_result = storage_delete("test_collection", "NONEXISTENT")
    if td_result == False:
        print("FAIL: storage_delete on missing ID returned false")
        return False
    print("PASS: storage_delete_missing")
    return True


def test_storage_delete():
    td_result = storage_delete("test_collection", "TEST-002")
    if td_result == False:
        print("FAIL: storage_delete returned false")
        return False
    td_remaining = storage_list("test_collection")
    td_found = storage_get_by_id("test_collection", "TEST-002")
    if td_found != False:
        print("FAIL: deleted item still exists")
        return False
    print("PASS: storage_delete")
    return True


def main():
    tt1 = test_storage_list_empty()
    if tt1 == False:
        return 1
    tt2 = test_storage_add()
    if tt2 == False:
        return 1
    tt3 = test_storage_get_by_id_missing()
    if tt3 == False:
        return 1
    tt4 = test_storage_get_by_id()
    if tt4 == False:
        return 1
    tt5 = test_storage_update()
    if tt5 == False:
        return 1
    tt6 = test_storage_delete_missing()
    if tt6 == False:
        return 1
    tt7 = test_storage_delete()
    if tt7 == False:
        return 1
    print("ALL STORAGE TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
