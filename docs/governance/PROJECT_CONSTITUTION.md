# PROJECT_CONSTITUTION

## Immutable Rules

- Specification First
- TDD Mandatory
- One Source of Truth
- Explicit > Implicit
- Deterministic Behaviour
- No Breaking Changes without ADR
- No Hidden Magic
- Small Modules
- All Code Tested
- All PRs Pass Quality Gates

## Rule Enforcement
- Any new feature must begin with tests.
- Any implementation change must preserve or improve determinism.
- Any architectural decision that affects the project direction must be documented in ADR form.
- All quality gates must pass before merge.
- If a rule is violated, the change must be corrected before it is accepted.
- Repeated or material violations require escalation and a documented corrective action.
