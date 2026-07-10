# PROJECT_CONSTITUTION

## Immutable Rules

- Specification First — Every feature starts with a written specification, not an implementation.
- TDD Mandatory — Tests before implementation. Every feature begins with tests.
- One Source of Truth — Every engineering concept has exactly one canonical document. Other documents may reference that canonical source but shall not duplicate normative content.
- Canonical First — Before creating any new document, search for an existing canonical document. Extend it if appropriate. Only create a new document if the information represents a genuinely new responsibility.
- Explicit > Implicit — Everything that matters is visible in the code. No hidden state, no magic, no implicit behaviour.
- Deterministic Behaviour — Same input always produces the same output. Non-determinism is a defect.
- No Breaking Changes without ADR
- No Hidden Magic — No implicit type conversions, no implicit variable declaration, no truthy/falsy coercion, no operator overloading.
- Small Modules — The language has the smallest possible feature set that solves the problems it sets out to solve. Every new feature must justify its existence against the evidence bar.
- All Code Tested
- All PRs Pass Quality Gates

## Rule Enforcement
- Any new feature must begin with tests.
- Any implementation change must preserve or improve determinism.
- Any architectural decision that affects the project direction must be documented in ADR form.
- All quality gates must pass before merge.
- If a rule is violated, the change must be corrected before it is accepted.
- Repeated or material violations require escalation and a documented corrective action.

## Decision-Making Usage

This constitution guides every decision:

1. **When evaluating a proposal**: Does it align with the immutable rules? If no, reject.
2. **When designing a feature**: Is it deterministic? Is it explicit? Is it spec-first? Is it minimal? If no, redesign.
3. **When rejecting a request**: Cite the relevant rule. Record it in `LANGUAGE_EVOLUTION.md`.
4. **When contributing**: Read this document first. If a change conflicts with the constitution, it will not be accepted.
