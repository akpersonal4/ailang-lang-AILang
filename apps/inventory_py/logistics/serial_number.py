from core.helpers import (
    helpers_current_timestamp,
    helpers_generate_id,
    helpers_get_map_value_safe,
)
from core.storage import storage_add, storage_get_by_id, storage_list, storage_update


def serial_find_rec(sfr_items, sfr_product_id, sfr_serial_num, sfr_idx):
    for sfr_item in sfr_items:
        sfr_item_product_id = helpers_get_map_value_safe(sfr_item, "product_id", "")
        sfr_item_serial_num = helpers_get_map_value_safe(sfr_item, "serial_number", "")
        if (
            sfr_item_product_id == sfr_product_id
            and sfr_item_serial_num == sfr_serial_num
        ):
            return sfr_item
    return False


def serial_list_by_product_rec(slbpr_items, slbpr_product_id, slbpr_idx, slbpr_acc):
    for slbpr_item in slbpr_items:
        slbpr_item_product_id = helpers_get_map_value_safe(slbpr_item, "product_id", "")
        if slbpr_item_product_id == slbpr_product_id:
            slbpr_acc.append(slbpr_item)
    return slbpr_acc


def serial_list_by_status_rec(slbsr_items, slbsr_status, slbsr_idx, slbsr_acc):
    for slbsr_item in slbsr_items:
        slbsr_item_status = helpers_get_map_value_safe(slbsr_item, "status", "")
        if slbsr_item_status == slbsr_status:
            slbsr_acc.append(slbsr_item)
    return slbsr_acc


def serial_list_available_rec(slar_items, slar_product_id, slar_idx, slar_acc):
    for slar_item in slar_items:
        slar_item_product_id = helpers_get_map_value_safe(slar_item, "product_id", "")
        slar_item_status = helpers_get_map_value_safe(slar_item, "status", "")
        if slar_item_product_id == slar_product_id and slar_item_status == "available":
            slar_acc.append(slar_item)
    return slar_acc


def serial_register(sr_product_id, sr_serial_number, sr_batch_id):
    sr_entry = {}
    sr_id = helpers_generate_id("SER-")
    sr_now = helpers_current_timestamp()
    sr_entry["id"] = sr_id
    sr_entry["product_id"] = sr_product_id
    sr_entry["serial_number"] = sr_serial_number
    sr_entry["batch_id"] = sr_batch_id
    sr_entry["status"] = "available"
    sr_entry["created_at"] = sr_now
    storage_add("serial_numbers", sr_entry)
    return sr_entry


def serial_get_by_id(sn_serial_id):
    return storage_get_by_id("serial_numbers", sn_serial_id)


def serial_find_by_serial(sfbs_product_id, sfbs_serial_number):
    sfbs_all = storage_list("serial_numbers")
    return serial_find_rec(sfbs_all, sfbs_product_id, sfbs_serial_number, 0)


def serial_list_by_product(sn_product_id):
    sn_all = storage_list("serial_numbers")
    sn_results = []
    return serial_list_by_product_rec(sn_all, sn_product_id, 0, sn_results)


def serial_list_by_status(sn_status):
    sn_all = storage_list("serial_numbers")
    sn_results = []
    return serial_list_by_status_rec(sn_all, sn_status, 0, sn_results)


def serial_update_status(sus_serial_id, sus_new_status):
    sus_changes = {"status": sus_new_status}
    return storage_update("serial_numbers", sus_serial_id, sus_changes)


def serial_list_available(sn_product_id):
    sn_all = storage_list("serial_numbers")
    sn_results = []
    return serial_list_available_rec(sn_all, sn_product_id, 0, sn_results)
