import time as _time

HELPERS_GLOBAL_SEQ = [0]


def helpers_repeat_char(ch, count, acc):
    if count <= 0:
        return acc
    return helpers_repeat_char(ch, count - 1, acc + ch)


def helpers_pad_number(num, digits):
    s = str(num)
    if len(s) >= digits:
        return s
    return helpers_repeat_char("0", digits - len(s), "") + s


def helpers_current_timestamp():
    return _time.time()


def helpers_unix_timestamp():
    return int(_time.time())


def helpers_generate_id(prefix):
    HELPERS_GLOBAL_SEQ[0] += 1
    return (
        prefix
        + str(helpers_unix_timestamp())
        + helpers_pad_number(HELPERS_GLOBAL_SEQ[0], 4)
    )


def helpers_safe_string(val):
    if val is False:
        return ""
    return str(val)


def helpers_is_empty_list(lst):
    if lst is False:
        return True
    return len(lst) == 0


def helpers_copy_map(source):
    return dict(source)


def helpers_get_map_value_safe(obj, key, default):
    if isinstance(obj, dict) and key in obj:
        return obj[key]
    return default


def helpers_find_in_list_rec(items, key, value, idx):
    item = items[idx]
    result = helpers_get_map_value_safe(item, key, False)
    if result == value:
        return item
    return helpers_find_in_list_rec(items, key, value, idx + 1)


def helpers_find_in_list(items, key, value):
    return helpers_find_in_list_rec(items, key, value, 0)


def helpers_list_contains(items, value):
    return value in items


def helpers_format_currency(amount):
    return f"${amount}"


def helpers_string_to_number(val):
    s = str(val).strip()
    if s == "":
        return 0
    return int(s)
