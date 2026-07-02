# MASTER_ENGINEERING_PROMPT

## Purpose
Use this document as the canonical operating manual for all future development work on AILang.

## Repository
- Root: C:\Users\aleckhan\Projects\AiLang_New
- All changes must stay inside this repository.

## Folder Structure
- docs/ for project governance and milestones
- compiler/ for implementation modules
- tests/ for automated tests
- examples/ for sample code
- scripts/ for helper scripts

## Coding Style
- Prefer small modules and small functions.
- Prefer explicit control flow and readable names.
- Avoid hidden state, magic values, and overengineering.

## Python Rules
- Target Python 3.11+
- Use dataclasses where appropriate.
- Keep implementation deterministic.
- Follow strict typing.

## Git Workflow
- Work from the develop branch.
- Create a feature branch for each component.
- Commit after each completed milestone.
- Keep commit messages descriptive and scoped.

## Testing Workflow
- Write tests before implementation when possible.
- Run pytest, black, ruff, and mypy before considering a milestone complete.

## Review Process
- Review changes for correctness, clarity, and test coverage.
- Avoid breaking changes without a documented ADR.

## Milestone Process
- Read the current milestone document.
- Implement the smallest complete change.
- Add or update tests.
- Run quality gates.
- Update roadmap and milestone status.

## Commit Rules
- Use conventional scopes such as feat, fix, test, and docs.
- Example: feat(diagnostics): add diagnostic dataclass
