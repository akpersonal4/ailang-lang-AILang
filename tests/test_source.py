from pathlib import Path

from compiler.source import Source


def test_source_from_file_reads_text(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.ail"
    file_path.write_text("let x = 1\n", encoding="utf-8")

    source = Source.from_file(file_path)

    assert source.path == file_path
    assert source.text == "let x = 1\n"
    assert len(source) == len("let x = 1\n")


def test_source_line_access() -> None:
    source = Source(path=Path("test.ail"), text="alpha\nbeta")

    assert source.line(1) == "alpha"
    assert source.line(2) == "beta"

    try:
        source.line(3)
    except IndexError:
        pass
    else:
        raise AssertionError("expected IndexError")
