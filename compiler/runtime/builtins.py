"""Built-in runtime functions for AILang."""

from __future__ import annotations

import csv as _csv
import io as _io
import json as _json
import os
import random as _random
import sys
import time as _time
from typing import Any, cast

from .values import RuntimeValue

# Will be set by CLI before running a program so env_args() returns
# only the user's arguments, not the CLI-internal plumbing.
_program_argv: list[str] | None = None


def print_builtin(args: tuple[RuntimeValue, ...]) -> None:
    if not args:
        print()
        return
    print(*args)


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
    with open(str(args[0]), "w", encoding="utf-8") as f:
        return f.write(str(args[1]))


def file_append(args: tuple[RuntimeValue, ...]) -> int:
    with open(str(args[0]), "a", encoding="utf-8") as f:
        return f.write(str(args[1]))


def file_remove(args: tuple[RuntimeValue, ...]) -> None:
    os.remove(str(args[0]))


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
    return _json.loads(str(args[0]))


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


def system_exit(args: tuple[RuntimeValue, ...]) -> None:
    """Exit the process with the given exit code."""
    code = int(args[0]) if args else 0
    sys.exit(code)


BUILTINS: dict[str, Any] = {
    "print": print_builtin,
    "list_new": list_new,
    "list_append": list_append,
    "list_len": list_len,
    "list_get": list_get,
    "list_contains": list_contains,
    "list_remove": list_remove,
    "list_clear": list_clear,
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
    "__native_to_int": native_to_int,
    "__native_to_string": native_to_string,
    "system_exit": system_exit,
}
