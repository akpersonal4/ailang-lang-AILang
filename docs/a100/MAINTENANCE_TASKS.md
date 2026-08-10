# A100 Phase 2 — Maintenance / Change-Request Instructions (Exact Specification)

**Authoritative version:** `docs/roadmap/A100_COMMUNITY_VALIDATION.md` §Protocol, Phase 2.
**This document is the exact task text.** Identical for both languages. Apply the
change requests **in order, one at a time** against the application built in
Phase 1. Never skip a request to "save time" — each is a data point.

---

## 0. How to run this phase

1. Start a fresh timer and event log for the maintenance phase.
2. Read request **M1**. Implement it in your assigned language/order.
3. Demonstrate the requested behavior works (running the program is required,
   not just code review).
4. Record the event-log row for M1 (§4 of the data-collection form), then move
   to M2.
5. Continue through M6. The phase ends after M6.
6. Record the phase-level metrics (§4) and confidence rating.

Use the same AI-assisted workflow as Phase 1. Do not rewrite the application from
scratch — these are changes to the existing Phase 1 codebase.

---

## 1. Change Requests

### M1 — Add GST (goods and services tax)

All `summary` totals must now include a fixed tax rate of 10% applied to every
expense. `summary` prints the pre-tax total, the tax amount, and the grand total:

```
TOTAL <pre-tax sum>
TAX <10% of pre-tax sum>
GRAND <pre-tax sum + tax>
```

`add`, `list`, and `category` behavior is unchanged. The tax rate must live in a
single named constant at the top of the source file.

### M2 — Add discounts

A new optional `discount` column is added to the CSV: `date,category,description,amount,discount`.
The discount is a whole-number percentage (0–100), defaulting to 0 when the CSV
header has no discount column. When computing totals, the discount is applied
before tax:

```
discounted = amount - (amount * discount / 100)
tax = discounted * 0.10
grand = discounted + tax
```

`add` now accepts an optional 5th value (the discount percent). `list` and
`category` print the discount when present, and the original 4-column files must
still load.

### M3 — Add a new CSV column (`currency`)

A new required column is inserted after `amount`: `date,category,description,amount,currency`.
All existing commands still work. `summary` prints per-category totals and the
grand total as before; currency is currently display-only (always `USD`).

Existing files created before this change are still valid: any file whose header
is missing the `currency` column loads with all rows defaulting to `USD`. New
files written from `add` must include the full 5-column header.

### M4 — Role-based permissions

Two roles exist: `admin` and `viewer`. A role is selected by a command-line flag
`--role admin|viewer` (default `viewer`).

- `viewer` may run `list`, `category`, `summary`, `help`. Running `add` as
  `viewer` prints `ERROR: permission denied` and exits non-zero.
- `admin` may run all commands.
- The permission check happens before any file modification.

### M5 — Per-category tax rates

Replace the single flat 10% GST (from M1) with per-category rates. A
`tax-rates.csv` file (path given as a second optional command-line argument)
maps category to rate:

```
category,rate
food,0.05
travel,0.15
```

- Categories present in `tax-rates.csv` use their rate; categories absent use
  the default 0.10.
- If no `tax-rates.csv` argument is given, all categories use 0.10.
- `summary` output becomes:

```
TOTAL <pre-tax sum>
TAX <sum of per-category tax>
GRAND <pre-tax + tax>
```

This request intentionally removes the single-rate constant from M1.

### M6 — Approval workflow

`admin` can mark an expense as approved. `add` gains an optional trailing
`approved|pending` status (default `pending`):

- `list` and `category` show the status column at the end.
- A new command `approve <date> <category> <description> <amount>` flips the
  matching record to `approved`. Matching is exact on all four fields; if zero
  or more than one record matches, print `ERROR: ambiguous match` and exit
  non-zero without modifying the file.
- `summary` includes only `approved` expenses. `pending` records are counted
  and printed separately as `PENDING <count> <sum>`.

---

## 2. Constraints

- Apply changes to the existing Phase 1 codebase; do not start over.
- Preserve the CSV-format invariants stated in each request (old files must load;
  new writes include all columns).
- The two choice questions are answered only at the **very end of the study**
  (after both languages' M6), not after each language.

---

## 3. Definition of "Maintenance Phase Completed"

All six change requests (M1–M6) are implemented and each requested behavior is
demonstrated by running the program. Record the total wall-clock time.

---

## 4. After the run (Phase 2 metrics)

Record for **each change request M1–M6**:

- time for that request
- number of AI correction iterations for that request
- number of compiler errors (AILang) / runtime exceptions (Python) during that
  request
- whether any previously-working behavior broke (bugs introduced: yes/no + which)

Then record phase-level:

- total maintenance time
- confidence rating (1–5) that the final code is correct and complete
- the event log for the phase

---

## 5. Rules for the coordinator

- The requests in §1 are frozen. Do not clarify or alter them mid-study except to
  correct an error in this document (log the correction).
- Do not coach the participant toward a particular implementation of any request.
- Record which change requests each participant completed.
