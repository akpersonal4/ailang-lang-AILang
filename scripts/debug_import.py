#!/usr/bin/env python
"""Debug import parsing."""

import tempfile
from pathlib import Path

from compiler.lexer import Lexer
from compiler.parser import Parser

with tempfile.TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir)

    main_file = tmp_path / "main.ail"
    main_file.write_text("import math.add;\nfn main() { return math.add(10, 20); }")

    source = main_file.read_text()
    lexer = Lexer()
    cst = Parser(lexer.tokenize(source)).parse_program()

    for child in cst.children:
        kind = child.kind if hasattr(child, "kind") else child.__class__.__name__
        print(f"Child kind: {kind}")
        if hasattr(child, "kind") and child.kind == "ImportDeclaration":
            print("  Import segments:")
            for segment_node in child.children[0].children:
                print(f"    segment: {segment_node}")
                if hasattr(segment_node, "token") and segment_node.token:
                    print(f"      token value: {segment_node.token.value}")
