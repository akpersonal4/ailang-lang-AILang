"""Built-in runtime functions for AILang."""

from __future__ import annotations

import csv as _csv
import io as _io
import json as _json
import os
import random as _random
import sys
import time as _time
from pathlib import Path
from typing import Any, cast

from .values import RuntimeValue

# Will be set by CLI before running a program so env_args() returns
# only the user's arguments, not the CLI-internal plumbing.
_program_argv: list[str] | None = None


def print_builtin(args: tuple[RuntimeValue, ...]) -> None:
    if not args:
        print(flush=True)
        return
    print(*args, flush=True)


def list_new(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    return []


def list_append(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    values = cast(list[RuntimeValue], args[0])
    values.append(args[1])
    return values


def list_len(args: tuple[RuntimeValue, ...]) -> int:
    return len(args[0])


def list_get(args: tuple[RuntimeValue, ...]) -> RuntimeValue:
    return args[0][args[1]]


def list_contains(args: tuple[RuntimeValue, ...]) -> bool:
    return args[1] in args[0]


def list_remove(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    values = cast(list[RuntimeValue], args[0])
    try:
        values.remove(args[1])
    except ValueError:
        pass
    return values


def list_sum(args: tuple[RuntimeValue, ...]) -> int:
    total = 0
    for item in args[0]:
        total += int(item)
    return total


def list_find_by_key(args: tuple[RuntimeValue, ...]) -> RuntimeValue:
    items = args[0]
    key = args[1]
    value = args[2]
    for item in items:
        if isinstance(item, dict) and item.get(key) == value:
            return item
    return False


def list_sort(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    items = args[0]
    if len(args) > 1:
        key = str(args[1])
        return sorted(items, key=lambda x: x.get(key, "") if isinstance(x, dict) else x)
    return sorted(items)


def list_copy(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    return list(args[0])


def list_filter_by_key(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    items = args[0]
    key = str(args[1])
    value = args[2]
    return [item for item in items if isinstance(item, dict) and item.get(key) == value]


def list_filter_by_contains(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    items = args[0]
    key = str(args[1])
    substring = str(args[2])
    return [
        item
        for item in items
        if isinstance(item, dict) and substring in str(item.get(key, ""))
    ]


def list_collect_key(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    items = args[0]
    key = str(args[1])
    return [item[key] for item in items if isinstance(item, dict) and key in item]


def map_get_or_default(args: tuple[RuntimeValue, ...]) -> RuntimeValue:
    values = cast(dict[RuntimeValue, RuntimeValue], args[0])
    key = args[1]
    default = args[2] if len(args) > 2 else False
    return values.get(key, default)


def dict_values(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    values = cast(dict[RuntimeValue, RuntimeValue], args[0])
    return list(values.values())


def list_group_by_key(
    args: tuple[RuntimeValue, ...],
) -> dict[RuntimeValue, list[RuntimeValue]]:
    items = args[0]
    key = str(args[1])
    groups: dict[RuntimeValue, list[RuntimeValue]] = {}
    for item in items:
        if isinstance(item, dict) and key in item:
            group_key = item[key]
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(item)
    return groups


def list_sum_by_key(args: tuple[RuntimeValue, ...]) -> int:
    items = args[0]
    key = str(args[1])
    total = 0
    for item in items:
        if isinstance(item, dict) and key in item:
            total += int(item[key])
    return total


def list_take(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    items = args[0]
    n = int(args[1])
    return items[:n]


def list_skip(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    items = args[0]
    n = int(args[1])
    return items[n:]


def list_search_by_name(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    items = args[0]
    query = str(args[1]).lower()
    return [
        item
        for item in items
        if isinstance(item, dict)
        and "name" in item
        and query in str(item["name"]).lower()
    ]


def list_exists_by_key(args: tuple[RuntimeValue, ...]) -> bool:
    items = args[0]
    key = str(args[1])
    value = args[2]
    for item in items:
        if isinstance(item, dict) and item.get(key) == value:
            return True
    return False


def string_join(args: tuple[RuntimeValue, ...]) -> str:
    separator = str(args[1]) if len(args) > 1 else ""
    return separator.join(str(v) for v in args[0])


def list_clear(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    values = cast(list[RuntimeValue], args[0])
    values.clear()
    return values


def dict_new(args: tuple[RuntimeValue, ...]) -> dict[RuntimeValue, RuntimeValue]:
    return {}


def dict_set(args: tuple[RuntimeValue, ...]) -> dict[RuntimeValue, RuntimeValue]:
    values = cast(dict[RuntimeValue, RuntimeValue], args[0])
    values[args[1]] = args[2]
    return values


def dict_get(args: tuple[RuntimeValue, ...]) -> RuntimeValue:
    return args[0][args[1]]


def dict_has(args: tuple[RuntimeValue, ...]) -> bool:
    return args[1] in args[0]


def dict_delete(args: tuple[RuntimeValue, ...]) -> dict[RuntimeValue, RuntimeValue]:
    values = cast(dict[RuntimeValue, RuntimeValue], args[0])
    if args[1] in values:
        del values[args[1]]
    return values


def dict_keys(args: tuple[RuntimeValue, ...]) -> list[RuntimeValue]:
    values = cast(dict[RuntimeValue, RuntimeValue], args[0])
    return list(values.keys())


def dict_clear(args: tuple[RuntimeValue, ...]) -> dict[RuntimeValue, RuntimeValue]:
    values = cast(dict[RuntimeValue, RuntimeValue], args[0])
    values.clear()
    return values


def set_new(args: tuple[RuntimeValue, ...]) -> set[RuntimeValue]:
    return set()


def native_to_int(args: tuple[RuntimeValue, ...]) -> int:
    if len(args) != 1:
        raise TypeError("to_int expects 1 argument")
    value = args[0]
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    if isinstance(value, float):
        return int(value)
    raise TypeError("to_int expects a string or int")


def native_to_string(args: tuple[RuntimeValue, ...]) -> str:
    if len(args) != 1:
        raise TypeError("to_string expects 1 argument")
    return str(args[0])


def set_add(args: tuple[RuntimeValue, ...]) -> set[RuntimeValue]:
    values = cast(set[RuntimeValue], args[0])
    values.add(args[1])
    return values


def set_contains(args: tuple[RuntimeValue, ...]) -> bool:
    return args[1] in args[0]


def set_len(args: tuple[RuntimeValue, ...]) -> int:
    return len(args[0])


def set_remove(args: tuple[RuntimeValue, ...]) -> set[RuntimeValue]:
    values = cast(set[RuntimeValue], args[0])
    values.discard(args[1])
    return values


def set_clear(args: tuple[RuntimeValue, ...]) -> set[RuntimeValue]:
    values = cast(set[RuntimeValue], args[0])
    values.clear()
    return values


def file_exists(args: tuple[RuntimeValue, ...]) -> bool:
    return os.path.exists(str(args[0]))


def file_read(args: tuple[RuntimeValue, ...]) -> str:
    with open(str(args[0]), encoding="utf-8") as f:
        return f.read()


def file_write(args: tuple[RuntimeValue, ...]) -> int:
    Path(str(args[0])).parent.mkdir(parents=True, exist_ok=True)
    with open(str(args[0]), "w", encoding="utf-8") as f:
        return f.write(str(args[1]))


def file_append(args: tuple[RuntimeValue, ...]) -> int:
    Path(str(args[0])).parent.mkdir(parents=True, exist_ok=True)
    with open(str(args[0]), "a", encoding="utf-8") as f:
        return f.write(str(args[1]))


def file_remove(args: tuple[RuntimeValue, ...]) -> None:
    os.remove(str(args[0]))


def file_listdir(args: tuple[RuntimeValue, ...]) -> list[str]:
    return sorted(os.listdir(str(args[0])))


def path_join(args: tuple[RuntimeValue, ...]) -> str:
    return os.path.join(*(str(a) for a in args))


def path_basename(args: tuple[RuntimeValue, ...]) -> str:
    return os.path.basename(str(args[0]))


def path_dirname(args: tuple[RuntimeValue, ...]) -> str:
    return os.path.dirname(str(args[0]))


def path_extension(args: tuple[RuntimeValue, ...]) -> str:
    _, ext = os.path.splitext(str(args[0]))
    return ext


def path_normalize(args: tuple[RuntimeValue, ...]) -> str:
    return os.path.normpath(str(args[0]))


def time_now(args: tuple[RuntimeValue, ...]) -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def time_timestamp(args: tuple[RuntimeValue, ...]) -> int:
    return int(_time.time())


def time_sleep(args: tuple[RuntimeValue, ...]) -> None:
    _time.sleep(args[0] / 1000.0)


def time_format(args: tuple[RuntimeValue, ...]) -> str:
    from datetime import datetime

    return datetime.fromtimestamp(args[0]).strftime("%Y-%m-%d %H:%M:%S")


def env_get(args: tuple[RuntimeValue, ...]) -> str:
    return os.environ.get(str(args[0]), "")


def env_cwd(args: tuple[RuntimeValue, ...]) -> str:
    return os.getcwd()


def env_args(args: tuple[RuntimeValue, ...]) -> list[str]:
    if _program_argv is not None:
        return list(_program_argv)
    return list(sys.argv)


def random_int(args: tuple[RuntimeValue, ...]) -> int:
    return _random.randint(int(args[0]), int(args[1]))


def random_float(args: tuple[RuntimeValue, ...]) -> float:
    return _random.random()


def random_choice(args: tuple[RuntimeValue, ...]) -> RuntimeValue:
    return _random.choice(args[0])


def json_parse(args: tuple[RuntimeValue, ...]) -> RuntimeValue:
    try:
        return _json.loads(str(args[0]))
    except (_json.JSONDecodeError, ValueError):
        return False


class _SetEncoder(_json.JSONEncoder):
    def default(self, obj: object) -> object:
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


def json_stringify(args: tuple[RuntimeValue, ...]) -> str:
    return _json.dumps(args[0], cls=_SetEncoder)


def csv_parse(args: tuple[RuntimeValue, ...]) -> list[list[str]]:
    return [list(row) for row in _csv.reader(_io.StringIO(str(args[0])))]


def csv_parse_header(args: tuple[RuntimeValue, ...]) -> list[dict[str, str]]:
    return [dict(row) for row in _csv.DictReader(_io.StringIO(str(args[0])))]


def csv_stringify(args: tuple[RuntimeValue, ...]) -> str:
    output = _io.StringIO()
    writer = _csv.writer(output, lineterminator="\n")
    writer.writerows(args[0])
    return output.getvalue()


def string_substring(args: tuple[RuntimeValue, ...]) -> str:
    s = str(args[0])
    start = int(args[1])
    end = int(args[2])
    return s[start:end]


def string_find(args: tuple[RuntimeValue, ...]) -> int:
    s = str(args[0])
    needle = str(args[1])
    start = int(args[2]) if len(args) > 2 else 0
    return s.find(needle, start)


def string_split(args: tuple[RuntimeValue, ...]) -> list[str]:
    s = str(args[0])
    delim = str(args[1]) if len(args) > 1 else "\n"
    return s.split(delim)


def system_exit(args: tuple[RuntimeValue, ...]) -> None:
    """Exit the process with the given exit code."""
    code = int(args[0]) if args else 0
    sys.exit(code)


def io_read(args: tuple[RuntimeValue, ...]) -> str:
    """Read a line from stdin."""
    try:
        return input()
    except EOFError:
        return ""


BUILTINS: dict[str, Any] = {
    "print": print_builtin,
    "list_new": list_new,
    "list_append": list_append,
    "list_len": list_len,
    "list_get": list_get,
    "list_contains": list_contains,
    "list_remove": list_remove,
    "list_sort": list_sort,
    "list_copy": list_copy,
    "list_filter_by_key": list_filter_by_key,
    "list_filter_by_contains": list_filter_by_contains,
    "list_collect_key": list_collect_key,
    "list_clear": list_clear,
    "list_sum": list_sum,
    "list_find_by_key": list_find_by_key,
    "list_group_by_key": list_group_by_key,
    "list_sum_by_key": list_sum_by_key,
    "list_take": list_take,
    "list_skip": list_skip,
    "list_search_by_name": list_search_by_name,
    "list_exists_by_key": list_exists_by_key,
    "dict_values": dict_values,
    "map_get_or_default": map_get_or_default,
    "string_join": string_join,
    "dict_new": dict_new,
    "dict_set": dict_set,
    "dict_get": dict_get,
    "dict_has": dict_has,
    "dict_delete": dict_delete,
    "dict_keys": dict_keys,
    "dict_clear": dict_clear,
    "set_new": set_new,
    "set_add": set_add,
    "set_contains": set_contains,
    "set_len": set_len,
    "set_remove": set_remove,
    "set_clear": set_clear,
    "file_exists": file_exists,
    "file_read": file_read,
    "file_write": file_write,
    "file_append": file_append,
    "file_remove": file_remove,
    "file_listdir": file_listdir,
    "path_join": path_join,
    "path_basename": path_basename,
    "path_dirname": path_dirname,
    "path_extension": path_extension,
    "path_normalize": path_normalize,
    "time_now": time_now,
    "time_timestamp": time_timestamp,
    "time_sleep": time_sleep,
    "time_format": time_format,
    "env_get": env_get,
    "env_cwd": env_cwd,
    "env_args": env_args,
    "random_int": random_int,
    "random_float": random_float,
    "random_choice": random_choice,
    "json_parse": json_parse,
    "json_stringify": json_stringify,
    "csv_parse": csv_parse,
    "csv_parse_header": csv_parse_header,
    "csv_stringify": csv_stringify,
    "string_substring": string_substring,
    "string_find": string_find,
    "string_split": string_split,
    "__native_to_int": native_to_int,
    "__native_to_string": native_to_string,
    "system_exit": system_exit,
    "io_read": io_read,
}
