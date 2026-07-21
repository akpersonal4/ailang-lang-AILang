import time

_HELPERS_GLOBAL_SEQ = 0


def helpers_repeat_char(in_char, in_count):
    return in_char * max(0, in_count)


def helpers_pad_number(pad_num, pad_digits):
    pad_str = str(pad_num)
    pad_len = len(pad_str)
    if pad_len >= pad_digits:
        return pad_str
    return "0" * (pad_digits - pad_len) + pad_str


def helpers_current_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def helpers_unix_timestamp():
    return int(time.time())


def helpers_generate_id(id_prefix):
    global _HELPERS_GLOBAL_SEQ
    _HELPERS_GLOBAL_SEQ += 1
    id_seq = _HELPERS_GLOBAL_SEQ
    id_ts = helpers_unix_timestamp()
    id_padded = helpers_pad_number(id_seq, 4)
    return id_prefix + str(id_ts) + id_padded


def helpers_safe_string(str_value):
    if str_value is False or str_value is None:
        return ""
    return str(str_value)


def helpers_is_empty_list(list_to_check):
    if list_to_check is False or list_to_check is None:
        return True
    return len(list_to_check) == 0


def helpers_copy_map(hm_source):
    return dict(hm_source)


def helpers_get_map_value_safe(gv_map, gv_key, gv_default):
    if gv_map is False or gv_map is None:
        return gv_default
    return gv_map.get(gv_key, gv_default)


def helpers_find_in_list(fr_items, fr_key, fr_value):
    for fr_item in fr_items:
        fr_result = helpers_get_map_value_safe(fr_item, fr_key, False)
        if fr_result == fr_value:
            return fr_item
    return False


def helpers_list_contains(lc_items, lc_value):
    for lc_item in lc_items:
        if lc_item == lc_value:
            return True
    return False


def helpers_format_currency(amount):
    return "$" + str(amount)


def helpers_string_to_number(st_value):
    st_trimmed = st_value.strip()
    if st_trimmed == "":
        return 0
    return int(st_trimmed)
