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


def test_error_message_no_semicolon_noise() -> None:
    """Regression: error message must not contain SEMICOLON noise.

    When there's a real syntax error, the error message should report
    only the real errors, not "Expected SEMICOLON" diagnostics from
    lines after the error.
    """
    source = "fn main() {\n    let x = \n    return x\n}\n"
    try:
        format_source(source)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        msg = str(e)
        assert (
            "Expected SEMICOLON" not in msg
        ), f"Error message contains SEMICOLON noise: {msg}"


def test_error_message_includes_real_error() -> None:
    """Regression: error message must include the real error.

    When the AST builder detects a problem (e.g. missing initializer),
    the error message should include that problem, not just SEMICOLON
    diagnostics.
    """
    source = "fn main() {\n    let x = ;\n    return x;\n}\n"
    try:
        format_source(source)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        msg = str(e)
        # Must include the actual error, not just SEMICOLON messages
        assert (
            "Expected SEMICOLON" not in msg
        ), f"Error message contains SEMICOLON noise: {msg}"
        assert (
            "initializer" in msg or "expression" in msg
        ), f"Error message missing real error: {msg}"


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


def test_empty_string() -> None:
    """Empty string should produce just a trailing newline."""
    assert format_source("") == "\n"


def test_only_imports_no_functions() -> None:
    """File with only imports should format correctly."""
    source = "import string;import math;"
    expected = "import string;\nimport math;\n"
    assert format_source(source) == expected


def test_import_without_semicolon() -> None:
    """Import without semicolon should be recovered."""
    source = "import string\nimport math\n"
    expected = "import string;\nimport math;\n"
    assert format_source(source) == expected


def test_additional_blank_lines_between_imports_and_functions() -> None:
    """Extra blank lines between imports and functions should be collapsed."""
    source = "import string;\n\n\n\nfn main() {\n    return 0;\n}\n"
    expected = "import string;\n\nfn main() {\n    return 0;\n}\n"
    assert format_source(source) == expected


def test_inline_comment_with_exclamation() -> None:
    """Inline comments with special characters should be preserved."""
    source = "fn main() {\n    return 0; // important!\n}\n"
    result = format_source(source)
    assert "// important!" in result


def test_block_comment_before_import() -> None:
    """Block comment before import should be preserved."""
    source = "// module docs\nimport string;\n\nfn main() {\n    return 0;\n}\n"
    result = format_source(source)
    assert "// module docs" in result
    assert "import string;" in result


def test_trailing_comment_only() -> None:
    """File with only trailing comment should produce just the comment."""
    source = "// just a comment\n"
    assert format_source(source) == "// just a comment\n"


def test_multiple_comments_between_functions() -> None:
    """Multiple consecutive comments between functions should be preserved."""
    source = "fn foo() {\n    return 1;\n}\n// step 1\n// step 2\nfn bar() {\n    return 2;\n}\n"
    result = format_source(source)
    assert "// step 1" in result
    assert "// step 2" in result


def test_else_if_chain() -> None:
    """Long else-if chain should format correctly."""
    source = 'fn grade(s){if(s>=90){return"A";}else if(s>=80){return"B";}else if(s>=70){return"C";}else{return"F";}}'
    expected = (
        "fn grade(s) {\n"
        "    if (s >= 90) {\n"
        '        return "A";\n'
        "    } else if (s >= 80) {\n"
        '        return "B";\n'
        "    } else if (s >= 70) {\n"
        '        return "C";\n'
        "    } else {\n"
        '        return "F";\n'
        "    }\n"
        "}\n"
    )
    assert format_source(source) == expected


def test_member_access_with_string_arg() -> None:
    """Member access with string argument should format correctly."""
    source = 'fn main(){let s=string.length("hello");print(s);}'
    expected = (
        "fn main() {\n" '    let s = string.length("hello");\n' "    print(s);\n" "}\n"
    )
    assert format_source(source) == expected


def test_format_check_accepts_formatted_source() -> None:
    """format_check returns True for sources that are already formatted."""
    assert format_check("fn main() {\n    return 0;\n}\n") is True


def test_format_check_rejects_unformatted_source() -> None:
    """format_check returns False for sources that need formatting."""
    assert format_check("fn main(){return 0;}") is False
