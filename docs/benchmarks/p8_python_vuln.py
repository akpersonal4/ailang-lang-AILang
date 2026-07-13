"""P8 Security Vulnerability Test — Python 3.11 + Full Tooling
Each function contains one vulnerability pattern (V1-V10).
We measure: mypy detection, ruff detection, runtime detection, or undetected.
"""
from typing import Optional


# --- V1: Null dereference ---
# Python: None is a valid value. mypy catches Optional misuse.
def v1_null_dereference() -> None:
    val: Optional[str] = None
    # mypy with --strict catches this:
    # error: Item "None" of "Optional[str]" has no attribute "upper"
    print(val.upper())  # Runtime: AttributeError


# --- V2: Missing existence check ---
# Python: dict access without .get() raises KeyError at runtime
def v2_missing_guard() -> None:
    contacts = {"alice": "555-0100"}
    # No "bob" key -> Runtime KeyError
    phone = contacts["bob"]
    print(phone)


# --- V3: Type confusion ---
# Python: dynamic typing allows reassignment to different types
def v3_type_confusion() -> None:
    val = 42          # type: int
    val = "hello"     # Reassignment allowed (dynamic typing)
    val2 = val + 42   # Runtime: TypeError (str + int)
    print(val2)


# --- V4: Implicit coercion ---
# Python: implicit coercion raises TypeError at runtime
def v4_implicit_coercion() -> None:
    num = 42
    text = " items"
    result = num + text  # Runtime: TypeError
    print(result)


# --- V5: Division by zero ---
# Python: Runtime ZeroDivisionError
def v5_division_by_zero() -> None:
    x = 10
    y = 0
    result = x / y  # Runtime: ZeroDivisionError
    print(result)


# --- V6: List index out of bounds ---
# Python: Runtime IndexError
def v6_out_of_bounds() -> None:
    items = [42]
    val = items[5]  # Runtime: IndexError
    print(val)


# --- V7: Unvalidated input in path ---
# Python: no detection of path traversal
def v7_unvalidated_input() -> None:
    user_input = "../secret.txt"
    path = "/data/" + user_input
    print(f"V7: Path not validated: {path}")


# --- V8: SQL injection ---
# Python: no static detection of SQL injection risk
def v8_sql_injection(user_id: str) -> None:
    # String formatting in SQL — undetected by mypy/ruff
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    print(f"V8: SQL injection risk: {query}")


# --- V9: Infinite recursion ---
# Python: Runtime RecursionError
def v9_infinite_recursion(counter: int) -> None:
    print(f"V9: count = {counter}")
    v9_infinite_recursion(counter + 1)


# --- V10: Variable shadowing ---
# Python: shadowing is allowed; ruff/flake8 may warn
def v10_variable_shadowing() -> None:
    x = 1
    x = 2  # Reassignment, not shadowing
    # Actual shadowing:
    for i in range(3):
        print(i)
    # i is still defined here — ruff catches this with flake8
    print(f"V10: i leaked to outer scope: {i}")


def main() -> None:
    print("=== P8 Security Vulnerability Test — Python ===")
    print("")
    # V1 is commented out — will crash at runtime
    # print("--- V1: Null Dereference ---")
    # v1_null_dereference()
    # V2 is commented out
    # print("--- V2: Missing Guard ---")
    # v2_missing_guard()
    # V3 is commented out
    # print("--- V3: Type Confusion ---")
    # v3_type_confusion()
    # V4 is commented out
    # print("--- V4: Implicit Coercion ---")
    # v4_implicit_coercion()
    # V5 is commented out
    # print("--- V5: Division by Zero ---")
    # v5_division_by_zero()
    # V6 is commented out
    # print("--- V6: Out of Bounds ---")
    # v6_out_of_bounds()

    print("--- V7: Path Traversal ---")
    v7_unvalidated_input()

    print("--- V8: SQL Injection ---")
    v8_sql_injection("' OR '1'='1")

    # V9 is commented out — will loop forever
    # print("--- V9: Infinite Recursion ---")
    # v9_infinite_recursion(0)

    print("--- V10: Variable Shadowing ---")
    v10_variable_shadowing()

    print("")
    print("=== P8 Python Security Test Complete ===")


if __name__ == "__main__":
    main()
