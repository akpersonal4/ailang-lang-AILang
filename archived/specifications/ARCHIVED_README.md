# Archived Specifications

This directory contains the original design specifications for AILang compiler phases.

## Status: Superseded

All specifications in this directory have been consolidated into the canonical
[`LANGUAGE_SPEC.md`](../LANGUAGE_SPEC.md) at the repository root.

The canonical `LANGUAGE_SPEC.md` is the single source of truth for:
- Language syntax and semantics
- Lexical structure
- Grammar
- Type system
- Standard Library API
- Error codes
- CLI reference

## Contents

| File | Original Purpose | Notes |
|------|------------------|-------|
| `language/LANGUAGE_SPEC.md` | Language specification (early draft) | Superseded by root `LANGUAGE_SPEC.md` |
| `lexer_specification.md` | Lexer design specification | Content merged into canonical spec |
| `lexer/LEXER_SPEC.md` | Lexer contract | Content merged into canonical spec |
| `parser/PARSER_SPEC.md` | Parser design contract | Content merged into canonical spec |
| `parser/GRAMMAR.md` | Formal grammar | Grammar content merged into canonical spec |
| `parser/CST_SPEC.md` | Concrete Syntax Tree design | Implementation reference only |
| `parser/AST_SPEC.md` | Abstract Syntax Tree design | Implementation reference only |
| `ir/IR_SPEC.md` | Intermediate Representation design | Implementation reference only |
| `stdlib_v1_final.md` | Standard Library v1.0 design | Content merged into `docs/STDLIB_REFERENCE.md` |

## Why Archived

These files were created during the initial design phase of AILang. As the
language matured, several of these specs became outdated, incomplete, or
contradictory. Rather than edit nine separate documents, all content has been
merged into one authoritative, implementation-verified specification.

## For Implementers

- `ir/IR_SPEC.md` remains the most detailed reference for IR node structure.
- `parser/CST_SPEC.md` and `parser/AST_SPEC.md` describe the internal compiler
  data structures that are not part of the language spec itself.
- The canonical spec at `../LANGUAGE_SPEC.md` should be consulted first for any
  language-level questions.
