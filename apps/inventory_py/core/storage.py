_data = {}


def storage_list(coll_name):
    if coll_name not in _data:
        _data[coll_name] = []
    return _data[coll_name]


def storage_save(coll_name, coll_items):
    _data[coll_name] = coll_items
    return coll_items


def storage_add(coll_name, add_item):
    items = storage_list(coll_name)
    items.append(add_item)
    return storage_save(coll_name, items)


def storage_get_by_id(coll_name, get_id):
    items = storage_list(coll_name)
    for item in items:
        if item.get("id") == get_id:
            return item
    return False


def storage_update(coll_name, upd_id, upd_changes):
    items = storage_list(coll_name)
    for item in items:
        if item.get("id") == upd_id:
            item.update(upd_changes)
            return storage_save(coll_name, items)
    return False


def storage_delete(coll_name, del_id):
    items = storage_list(coll_name)
    filtered = [item for item in items if item.get("id") != del_id]
    return storage_save(coll_name, filtered)


def storage_clear_all():
    _data.clear()
