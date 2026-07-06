"""Tests for the AILang source code formatter."""

from __future__ import annotations

from compiler.formatter import format_check, format_source

# =============================================================================
# Basic formatting
# =============================================================================


def test_format_simple_function() -> None:
    source = "fn add(a,b){return a+b;}"
    expected = "fn add(a, b) {\n    return a + b;\n}\n"
    assert format_source(source) == expected


def test_format_multiple_functions() -> None:
    source = "fn foo(){return 1;}fn bar(){return 2;}"
    expected = "fn foo() {\n    return 1;\n}\n\nfn bar() {\n    return 2;\n}\n"
    assert format_source(source) == expected


def test_format_variable_declaration() -> None:
    source = "fn main(){let x=10;let y=20;return x+y;}"
    expected = (
        "fn main() {\n"
        "    let x = 10;\n"
        "    let y = 20;\n"
        "    return x + y;\n"
        "}\n"
    )
    assert format_source(source) == expected


def test_format_imports() -> None:
    source = "import string;import math;fn main(){return 0;}"
    expected = "import string;\nimport math;\n\nfn main() {\n    return 0;\n}\n"
    assert format_source(source) == expected


def test_format_import_with_alias() -> None:
    source = "import math as m;fn main(){return 0;}"
    expected = "import math as m;\n\nfn main() {\n    return 0;\n}\n"
    assert format_source(source) == expected


# =============================================================================
# Operators and expressions
# =============================================================================


def test_spaces_around_binary_operators() -> None:
    source = "fn main(){let a=1+2;let b=3*4;let c=5/6;let d=7-8;let e=9%2;return a;}"
    expected = (
        "fn main() {\n"
        "    let a = 1 + 2;\n"
        "    let b = 3 * 4;\n"
        "    let c = 5 / 6;\n"
        "    let d = 7 - 8;\n"
        "    let e = 9 % 2;\n"
        "    return a;\n"
        "}\n"
    )
    assert format_source(source) == expected


def test_spaces_around_comparison_operators() -> None:
    source = (
        "fn main(){let a=1==2;let b=3!=4;let c=5<6;let d=7>8;let e=9<=2;let f=10>=3;}"
    )
    expected = (
        "fn main() {\n"
        "    let a = 1 == 2;\n"
        "    let b = 3 != 4;\n"
        "    let c = 5 < 6;\n"
        "    let d = 7 > 8;\n"
        "    let e = 9 <= 2;\n"
        "    let f = 10 >= 3;\n"
        "}\n"
    )
    assert format_source(source) == expected


def test_spaces_around_logical_operators() -> None:
    source = "fn main(){let a=true&&false;let b=true||false;}"
    expected = (
        "fn main() {\n"
        "    let a = true && false;\n"
        "    let b = true || false;\n"
        "}\n"
    )
    assert format_source(source) == expected


def test_unary_operators() -> None:
    source = "fn main(){let a=-42;let b=!true;return a;}"
    expected = "fn main() {\n    let a = -42;\n    let b = !true;\n    return a;\n}\n"
    assert format_source(source) == expected


# =============================================================================
# If/else formatting
# =============================================================================


def test_if_statement() -> None:
    source = "fn main(){if(x>0){return 1;}return 0;}"
    expected = (
        "fn main() {\n"
        "    if (x > 0) {\n"
        "        return 1;\n"
        "    }\n"
        "    return 0;\n"
        "}\n"
    )
    assert format_source(source) == expected


def test_if_else_statement() -> None:
    source = "fn main(){if(x>0){return 1;}else{return 0;}}"
    expected = (
        "fn main() {\n"
        "    if (x > 0) {\n"
        "        return 1;\n"
        "    } else {\n"
        "        return 0;\n"
        "    }\n"
        "}\n"
    )
    assert format_source(source) == expected


def test_if_else_if_chain() -> None:
    source = 'fn grade(s){if(s>=90){return"A";}if(s>=80){return"B";}return"F";}'
    expected = (
        "fn grade(s) {\n"
        "    if (s >= 90) {\n"
        '        return "A";\n'
        "    }\n"
        "    if (s >= 80) {\n"
        '        return "B";\n'
        "    }\n"
        '    return "F";\n'
        "}\n"
    )
    assert format_source(source) == expected


# =============================================================================
# Recursion
# =============================================================================


def test_recursive_function() -> None:
    source = "fn factorial(n){if(n==0){return 1;}return n*factorial(n-1);}"
    expected = (
        "fn factorial(n) {\n"
        "    if (n == 0) {\n"
        "        return 1;\n"
        "    }\n"
        "    return n * factorial(n - 1);\n"
        "}\n"
    )
    assert format_source(source) == expected


# =============================================================================
# Stdlib usage and member access
# =============================================================================


def test_member_access() -> None:
    source = 'fn main(){let s=string.uppercase("hello");print(s);}'
    expected = (
        "fn main() {\n"
        '    let s = string.uppercase("hello");\n'
        "    print(s);\n"
        "}\n"
    )
    assert format_source(source) == expected


def test_chained_member_access() -> None:
    source = 'fn main(){print(string.length("hello"));}'
    expected = "fn main() {\n" '    print(string.length("hello"));\n' "}\n"
    assert format_source(source) == expected


# =============================================================================
# Strings and literals
# =============================================================================


def test_string_literals() -> None:
    source = 'fn main(){let s="hello\\nworld";print(s);}'
    expected = "fn main() {\n" '    let s = "hello\\nworld";\n' "    print(s);\n" "}\n"
    assert format_source(source) == expected


def test_bool_literals() -> None:
    source = "fn main(){let t=true;let f=false;return 0;}"
    expected = (
        "fn main() {\n"
        "    let t = true;\n"
        "    let f = false;\n"
        "    return 0;\n"
        "}\n"
    )
    assert format_source(source) == expected


# =============================================================================
# Idempotency
# =============================================================================


def test_idempotent() -> None:
    sources = [
        "fn add(a, b) {\n    return a + b;\n}\n",
        "import string;\nimport math;\n\nfn main() {\n    return 0;\n}\n",
        "fn main() {\n    if (x > 0) {\n        return 1;\n    } else {\n        return 0;\n    }\n}\n",  # noqa: E501
    ]
    for source in sources:
        assert format_source(source) == source, f"Idempotency failed for:\n{source}"


# =============================================================================
# format_check
# =============================================================================


def test_format_check_formatted() -> None:
    source = "fn main() {\n    return 0;\n}\n"
    assert format_check(source) is True


def test_format_check_unformatted() -> None:
    source = "fn main(){return 0;}"
    assert format_check(source) is False


# =============================================================================
# Comments
# =============================================================================


def test_comments_preserved() -> None:
    source = "// hello\nfn main() {\n    return 0; // exit\n}\n"
    result = format_source(source)
    assert "// hello" in result
    assert "// exit" in result


def test_comments_between_functions() -> None:
    source = "// first\nfn foo() {\n    return 1;\n}\n// second\nfn bar() {\n    return 2;\n}\n"  # noqa: E501
    result = format_source(source)
    assert "// first" in result
    assert "// second" in result


# =============================================================================
# Error handling
# =============================================================================


def test_invalid_syntax_raises() -> None:
    source = "fn main() { let x = ; }"
    try:
        format_source(source)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


# =============================================================================
# Edge cases
# =============================================================================


def test_empty_block() -> None:
    source = "fn main() {}"
    expected = "fn main() {}\n"
    assert format_source(source) == expected


def test_no_trailing_whitespace() -> None:
    source = "fn main() {\n    return 0;   \n}\n"
    expected = "fn main() {\n    return 0;\n}\n"
    assert format_source(source) == expected


def test_blank_lines_removed() -> None:
    source = "fn foo() {\n    return 1;\n}\n\n\n\nfn bar() {\n    return 2;\n}\n"
    expected = "fn foo() {\n    return 1;\n}\n\nfn bar() {\n    return 2;\n}\n"
    assert format_source(source) == expected


def test_nested_expressions() -> None:
    source = "fn main(){let r=(1+2)*3;print(r);}"
    expected = "fn main() {\n" "    let r = (1 + 2) * 3;\n" "    print(r);\n" "}\n"
    assert format_source(source) == expected
