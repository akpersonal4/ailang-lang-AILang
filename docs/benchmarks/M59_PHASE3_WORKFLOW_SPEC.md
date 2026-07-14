# M59 Phase 3 — Workflow Engine Specification

**Frozen:** 2026-07-13
**Status:** FROZEN — ready for implementation
**Target LOC:** ~2,000 (comparable to Phase 1 Ticket System)

---

## 1. Overview

A CLI-based workflow/state-machine engine. Users define workflows with states and transitions, create instances of those workflows, and advance them through their lifecycle. This stresses AILang's recursion model differently than the Ticket System — state machines require nested data structures, conditional transitions, and history tracking.

---

## 2. Data Model

```
WorkflowDefinition:
  id: integer (auto-increment)
  name: string (unique, 1–100 chars)
  description: string (1–500 chars)
  states: list of string (e.g., ["pending", "approved", "rejected"])
  initial_state: string (must be in states)
  transitions: list of Transition
  created_at: timestamp

Transition:
  from_state: string
  to_state: string
  action: string (human-readable action name)
  conditions: list of string (condition names, evaluated at runtime)
  required_role: string (role needed to execute this transition)

WorkflowInstance:
  id: integer (auto-increment)
  workflow_id: integer (FK → WorkflowDefinition)
  current_state: string
  data: map (arbitrary key-value data attached to instance)
  created_by: integer (user ID)
  created_at: timestamp
  updated_at: timestamp

InstanceHistory:
  id: integer (auto-increment)
  instance_id: integer (FK → WorkflowInstance)
  from_state: string
  to_state: string
  action: string
  performed_by: integer (user ID)
  notes: string
  timestamp: timestamp

User:
  id: integer (auto-increment)
  username: string (unique, 3–50 chars)
  email: string (unique)
  role: enum (admin, operator, viewer)
  password_hash: string (SHA-256)
  created_at: timestamp
```

---

## 3. CLI Commands

| Command | Description | Auth Required |
|---------|-------------|:-------------:|
| `register <username> <email> <password>` | Create user account | No |
| `login <username> <password>` | Authenticate, start session | No |
| `logout` | End session | Yes |
| `create-workflow <name> <description>` | Create workflow definition (interactive: prompts for states, transitions) | Yes (admin) |
| `list-workflows` | List all workflow definitions | Yes |
| `view-workflow <id>` | Show workflow definition details | Yes |
| `delete-workflow <id>` | Delete workflow definition (only if no active instances) | Yes (admin) |
| `create-instance <workflow_id> <initial_data>` | Create instance of a workflow | Yes |
| `view-instance <id>` | Show instance details + current state + history | Yes |
| `list-instances <workflow_id>` | List all instances of a workflow | Yes |
| `list-my-instances` | List instances created by current user | Yes |
| `transition <instance_id> <action> [notes]` | Advance instance to next state | Yes |
| `set-data <instance_id> <key> <value>` | Update instance data | Yes |
| `cancel <instance_id> [notes]` | Cancel an instance (sets state to "cancelled") | Yes (admin) |
| `history <instance_id>` | Show full state transition history | Yes |
| `report-workflow <workflow_id>` | Count instances by state | Yes (operator+) |
| `report-activity` | Recent transitions (last 7 days) | Yes (operator+) |
| `export-workflows <filename>` | Export all workflow definitions to JSON | Yes (admin) |
| `import-workflows <filename>` | Import workflow definitions from JSON | Yes (admin) |
| `help` | Show available commands | No |

---

## 4. Built-in Conditions

The engine evaluates these conditions when checking if a transition is allowed:

| Condition | Logic |
|-----------|-------|
| `data_has_key:<key>` | Instance data must contain the specified key |
| `data_equals:<key>:<value>` | Instance data key must equal the specified value |
| `data_not_empty:<key>` | Instance data key must be a non-empty string |
| `created_by:<role>` | Instance creator must have the specified role |

Custom conditions can be added by extending the engine (not required for Phase 3).

---

## 5. Permissions Matrix

| Action | admin | operator | viewer |
|--------|:-----:|:--------:|:------:|
| Create workflow | ✅ | ❌ | ❌ |
| Delete workflow | ✅ | ❌ | ❌ |
| List workflows | ✅ | ✅ | ✅ |
| View workflow | ✅ | ✅ | ✅ |
| Create instance | ✅ | ✅ | ❌ |
| View instance | ✅ | ✅ | ✅ |
| Transition instance | ✅ | ✅ | ❌ |
| Set instance data | ✅ | ✅ | ❌ |
| Cancel instance | ✅ | ❌ | ❌ |
| View history | ✅ | ✅ | ✅ |
| View reports | ✅ | ✅ | ❌ |
| Export/import workflows | ✅ | ❌ | ❌ |
| Register/manage users | ✅ | ❌ | ❌ |

---

## 6. Acceptance Criteria

| # | Criterion | Pass/Fail |
|:-:|-----------|:---------:|
| 1 | All 19 commands implemented and functional | |
| 2 | All permission checks enforced | |
| 3 | Workflow definitions validate (initial_state in states, transitions reference valid states) | |
| 4 | Transitions validate (current_state matches from_state, conditions met, role authorized) | |
| 5 | Instance history records every transition | |
| 6 | Built-in conditions evaluate correctly | |
| 7 | Session management works (login/logout) | |
| 8 | Password hashing works (SHA-256) | |
| 9 | Reports produce correct counts | |
| 10 | CSV/JSON export/import round-trips correctly | |
| 11 | 30+ tests passing | |
| 12 | Builds/runs from clean state | |

---

## 7. Constraints

Same as M59 Protocol §2-§3:

- **AILang:** stdlib only, no loops, no forward references, bottom-up ordering, semicolons mandatory
- **Python:** stdlib only, no third-party packages
- **Both:** JSON persistence, CLI interface, no GUI, no async
- **AI Model:** Claude Sonnet 4, temp 0.0
- **No optimization:** measure baseline capability

---

## 8. Example Workflow

A simple approval workflow:

```
Workflow: "Expense Approval"
States: ["draft", "submitted", "approved", "rejected", "paid"]
Initial: "draft"

Transitions:
  submit:   draft → submitted   (role: any)
  approve:  submitted → approved (role: operator, conditions: [data_has_key:amount])
  reject:   submitted → rejected (role: operator)
  pay:      approved → paid      (role: operator)
  reopen:   rejected → draft     (role: admin)
```

Instance lifecycle:
```
1. create-instance 1 "{"amount": "500", "description": "Travel"}"
   → Instance #1 in state "draft"

2. transition 1 submit
   → Instance #1 moves to "submitted"

3. transition 1 approve "Looks good"
   → Instance #1 moves to "approved"

4. transition 1 pay
   → Instance #1 moves to "paid"

5. history 1
   → Shows: draft → submitted → approved → paid
```

---

## 9. Anti-Patterns to Avoid

Based on Phase 1 learnings:

| Anti-Pattern | Why | Correct Approach |
|--------------|-----|------------------|
| `&&` for conditional guards | Eager evaluation breaks short-circuit | Nested `if` statements |
| Forward references | `Undefined identifier` error | Bottom-up function ordering |
| Reusing variable names | Scope collision in recursive helpers | Unique names per function |
| `while` loops | Don't exist in AILang | Recursive helper functions |
| `return;` without value | Syntax error | `return true;` or `return false;` |
| `map.get` without `map.has` | Runtime crash on missing key | Always guard with `map.has` |

---

## 10. File Structure (Expected)

### AILang
```
apps/workflow_engine/
├── storage.ail          — JSON persistence layer
├── user.ail             — User model + auth + roles
├── workflow_def.ail     — Workflow definition CRUD + validation
├── instance.ail         — Instance CRUD + state management
├── history.ail          — Instance history tracking
├── conditions.ail       — Built-in condition evaluation
├── session.ail          — Session management
├── main.ail             — CLI dispatch (19 commands)
└── tests/
    ├── test_storage.ail
    ├── test_user.ail
    ├── test_workflow_def.ail
    ├── test_instance.ail
    ├── test_history.ail
    ├── test_conditions.ail
    ├── test_integration.ail
    └── runner.py
```

### Python
```
apps/workflow_engine_py/
├── storage.py
├── user.py
├── workflow_def.py
├── instance.py
├── history.py
├── conditions.py
├── session.py
├── main.py
└── tests/
    ├── test_storage.py
    ├── test_user.py
    ├── test_workflow_def.py
    ├── test_instance.py
    ├── test_history.py
    ├── test_conditions.py
    ├── test_integration.py
    └── conftest.py (or fixtures)
```

---

**Spec frozen. Ready for implementation.**
