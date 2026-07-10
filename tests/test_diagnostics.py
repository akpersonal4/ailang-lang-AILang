from compiler.diagnostics import (
    Diagnostic,
    DiagnosticFormatter,
    DiagnosticReporter,
    ErrorCode,
    Severity,
)


def test_severity_and_error_code_are_stable() -> None:
    severity = Severity.ERROR
    code = ErrorCode("E001", "Unexpected token")

    assert severity.name == "ERROR"
    assert code.code == "E001"
    assert code.message == "Unexpected token"


def test_diagnostic_contains_location_and_message() -> None:
    diagnostic = Diagnostic(
        severity=Severity.ERROR,
        error_code=ErrorCode("E002", "Unexpected token"),
        message="Unexpected token '}'",
        line=3,
        column=8,
    )

    assert diagnostic.severity is Severity.ERROR
    assert diagnostic.line == 3
    assert diagnostic.column == 8
    assert diagnostic.message == "Unexpected token '}'"


def test_diagnostic_reporter_collects_and_counts_diagnostics() -> None:
    reporter = DiagnosticReporter()
    reporter.report(
        Diagnostic(
            severity=Severity.ERROR,
            error_code=ErrorCode("E003", "Unexpected token"),
            message="Unexpected token '}'",
        )
    )
    reporter.report(
        Diagnostic(
            severity=Severity.WARNING,
            error_code=ErrorCode("W001", "Unused value"),
            message="Value is never used",
        )
    )

    assert len(reporter.diagnostics) == 2
    assert reporter.error_count == 1
    assert reporter.warning_count == 1


def test_formatter_emits_deterministic_output() -> None:
    formatter = DiagnosticFormatter()
    diagnostic = Diagnostic(
        severity=Severity.ERROR,
        error_code=ErrorCode("E004", "Unexpected token"),
        message="Unexpected token ';'",
        line=4,
        column=2,
    )

    rendered = formatter.format(diagnostic)

    assert rendered == "(line 4, column 2)  ERROR E004: Unexpected token ';'"
