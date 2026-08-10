# A100 Phase 1 — Greenfield Task Instructions (Exact Specification)

**Authoritative version:** `docs/roadmap/A100_COMMUNITY_VALIDATION.md` §Protocol, Phase 1.
**This document is the exact task text.** It is identical for both runs (Python
and AILang) — the only difference between runs is the environment, never the spec.
Do not read per-language variants; there are none.

---

## 0. How to run this phase

1. Confirm your environment is ready (Python 3.11+; `ail --version` prints
   `AILang v1.1.17`). If not, stop and contact the coordinator.
2. Start your timer and event log (see data-collection form).
3. Build the application described in §1 below, in your assigned language/order.
4. "First working version" = the application runs end-to-end and satisfies every
   acceptance criterion in §3.
5. Stop the timer at first working version. Record the event log.

Use your normal AI-assisted workflow (AI authors code, you direct/review). You
are measuring a realistic workflow, not a sprint.

---

## 1. Application Specification — Expense Tracker

Build a command-line **expense tracker** with the following requirements.

### 1.1 Data

- An expense record has: **date**, **category**, **description**, **amount**.
- Expenses are loaded from and saved to a **CSV file** at a path given as a
  command-line argument.
- If the CSV file does not exist, the application starts with an empty ledger and
  creates the file on first save.
- The CSV has a header row: `date,category,description,amount`.
- Amounts are positive decimal numbers (e.g., `12.50`).

### 1.2 Commands (CLI)

The application accepts a command as its first argument:

- `add <date> <category> <description> <amount>` — append a new expense and save.
- `list` — print all expenses, one per line, in file order, as
  `date | category | description | amount`.
- `category <name>` — print only expenses in the given category.
- `summary` — print the total of all expenses and the total per category,
  formatted as `TOTAL <sum>` and `<category> <sum>`.
- `help` — print a short usage summary.

### 1.3 Validation

- `add` with fewer than 4 values after the command, or a non-numeric amount,
  prints `ERROR: invalid arguments` and exits non-zero without modifying the file.
- `add` with a negative or zero amount prints the same error and exits non-zero.
- `category` or `list` on an empty ledger prints `(no expenses)`.
- The program exits `0` on success and a non-zero code on any error.

### 1.4 Acceptance Criteria (all must pass for "first working version")

1. `add` persists a record to the CSV and `list` shows it.
2. A second run of the program reads the same CSV and still lists the record.
3. `summary` totals match the individual records (e.g., two `12.50` expenses
   total `25.00`).
4. `category` filters correctly; a category with no records prints
   `(no expenses)`.
5. Invalid `add` arguments produce the exact `ERROR: invalid arguments` message
   and do not corrupt the file.
6. Starting with a missing file works; starting with a pre-filled CSV works.

---

## 2. Constraints

- CLI-only. No GUI, no web server.
- The CSV format must remain exactly `date,category,description,amount` with the
  header row.
- Data must survive program restarts (file persistence, not in-memory only).
- You may use any standard library of the language and any external packages
  your normal AI workflow would use.
- Testing your own acceptance criteria (with test code or ad-hoc runs) is
  allowed and encouraged.

---

## 3. Definition of "First Working Version"

All six acceptance criteria in §1.4 pass, demonstrated by running the program
(not just by code review). Record the wall-clock time from task start to this
point as **time to first working version**.

---

## 4. After the run

- Stop the timer.
- Complete the Phase 1 section of the data-collection form:
  - time to first working version
  - number of AI correction iterations (times you asked the AI to fix/redo work)
  - count of compiler errors (AILang) / runtime exceptions (Python) encountered
  - frustration rating (1–5)
  - the event log (what you did, in order, with rough timestamps)
- Then answer: **"Which was easier to build?"** (recorded, not discussed.)

Do not discuss your experience with the coordinator until the maintenance phase
for the same language is complete, to avoid biasing later runs.

---

## 5. Rules for the coordinator

- The spec in §1 is frozen. Do not clarify or alter it mid-study except to
  correct an error in this document (log the correction).
- Record the participant's assigned order (Python-first or AILang-first).
- Do not coach the participant toward a particular implementation.
