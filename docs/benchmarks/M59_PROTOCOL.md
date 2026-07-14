# M59 — Large Application Validation Protocol

**Date:** 2026-07-13
**Status:** DRAFT — requires approval before execution
**Purpose:** Definitive head-to-head comparison of AILang vs Python on 2,000–3,000 LOC business applications

---

## 1. Question

> After six months of maintenance, which codebase would the team rather own?

Secondary questions:
- Does AILang's compile-time advantage hold at 2,000+ LOC across multiple application types?
- Does the AI collaboration advantage (fewer iterations, fewer hallucinations) generalize beyond inventory?
- Where does AILang's recursion-only model break down?

---

## 2. Frozen Environment

### 2.1 Hardware

| Component | Value |
|-----------|-------|
| Machine | [RECORD BEFORE START] |
| OS | Windows 11 |
| CPU | [RECORD BEFORE START] |
| RAM | [RECORD BEFORE START] |
| Disk | [RECORD BEFORE START] |

### 2.2 Software

| Component | Version |
|-----------|---------|
| AILang | v1.0.0 (this repository, commit `a20bbc8`) |
| Python | 3.12.x |
| Node.js | [if needed for tooling] |
| VS Code | [if used] |

### 2.3 AI Model

| Parameter | Value |
|-----------|-------|
| Primary model | `claude-sonnet-4-20250514` |
| Temperature | `0.0` |
| System prompt | None (empty) |
| Max tokens per response | 4,096 |
| Context window | 200,000 tokens |

**Rationale:** Single-model evaluation first. Multi-model replication is future work.

### 2.4 Allowed Libraries

**AILang:**
- Standard library only (string, math, list, map, set, file, path, json, csv, time, random, environment, convert, io, system)
- Package manager (`ail add`) for any published packages — but must document which and why

**Python:**
- Standard library only (no pip packages)
- `json`, `csv`, `os`, `sys`, `datetime`, `hashlib`, `pathlib`, `collections`, `re`, `unittest`
- No Django, Flask, FastAPI, SQLAlchemy, or any third-party framework

**Rationale:** Measuring language capability, not ecosystem breadth.

---

## 3. Application Specifications

### 3.1 Ticket Management System (Target: ~2,000 LOC)

#### 3.1.1 Data Model

```
Ticket:
  id: integer (auto-increment)
  title: string (1–200 chars)
  description: string (1–5000 chars)
  status: enum (open, in_progress, resolved, closed)
  priority: enum (low, medium, high, critical)
  creator_id: integer (FK → User)
  assignee_id: integer (FK → User, nullable)
  category: string (bug, feature, task, question)
  created_at: timestamp
  updated_at: timestamp
  resolved_at: timestamp (nullable)

User:
  id: integer (auto-increment)
  username: string (unique, 3–50 chars)
  email: string (unique)
  role: enum (admin, manager, agent, viewer)
  password_hash: string (SHA-256)
  created_at: timestamp

Comment:
  id: integer (auto-increment)
  ticket_id: integer (FK → Ticket)
  author_id: integer (FK → User)
  content: string (1–2000 chars)
  created_at: timestamp

AuditLog:
  id: integer (auto-increment)
  ticket_id: integer (FK → Ticket)
  user_id: integer (FK → User)
  action: string (created, updated, status_changed, assigned, commented)
  old_value: string (nullable)
  new_value: string (nullable)
  timestamp: timestamp
```

#### 3.1.2 Commands (CLI)

| Command | Description | Auth Required |
|---------|-------------|:-------------:|
| `register <username> <email> <password>` | Create user account | No |
| `login <username> <password>` | Authenticate, start session | No |
| `logout` | End session | Yes |
| `create-ticket <title> <priority> <category> <description>` | Create new ticket | Yes |
| `update-ticket <id> <field> <value>` | Update ticket field | Yes |
| `assign-ticket <id> <username>` | Assign ticket to agent | Yes (manager+) |
| `resolve-ticket <id>` | Mark ticket resolved | Yes (agent+) |
| `close-ticket <id>` | Mark ticket closed | Yes (agent+) |
| `reopen-ticket <id>` | Reopen resolved/closed ticket | Yes (agent+) |
| `add-comment <ticket_id> <content>` | Add comment to ticket | Yes |
| `view-ticket <id>` | Show ticket details + comments | Yes |
| `search-tickets <query>` | Search by title/description | Yes |
| `filter-tickets <field> <value>` | Filter by status/priority/assignee/category | Yes |
| `my-tickets` | List tickets assigned to current user | Yes |
| `report-status` | Count by status | Yes (manager+) |
| `report-priority` | Count by priority | Yes (manager+) |
| `report-agent` | Tickets per agent | Yes (manager+) |
| `report-daily` | Tickets created/resolved per day (last 7 days) | Yes (manager+) |
| `export-csv <filename>` | Export all tickets to CSV | Yes (admin) |
| `import-csv <filename>` | Import tickets from CSV | Yes (admin) |
| `list-users` | List all users | Yes (admin) |
| `delete-ticket <id>` | Soft-delete ticket | Yes (admin) |

#### 3.1.3 Escalation Rules

| Rule | Trigger | Action |
|------|---------|--------|
| **SLA breach** | Ticket priority=critical and status!=resolved after 4 hours, or priority=high after 24 hours | Auto-escalate to manager, add audit log entry, set priority=critical |
| **Unassigned critical** | Ticket created with priority=critical and assignee is null for >30 minutes | Auto-notify all managers, add audit log entry |

#### 3.1.4 Permissions Matrix

| Action | admin | manager | agent | viewer |
|--------|:-----:|:-------:|:-----:|:------:|
| Create ticket | ✅ | ✅ | ✅ | ❌ |
| Update own ticket | ✅ | ✅ | ✅ | ❌ |
| Update any ticket | ✅ | ✅ | ❌ | ❌ |
| Assign ticket | ✅ | ✅ | ❌ | ❌ |
| Resolve ticket | ✅ | ✅ | ✅ | ❌ |
| Close ticket | ✅ | ✅ | ✅ | ❌ |
| Reopen ticket | ✅ | ✅ | ✅ | ❌ |
| Add comment | ✅ | ✅ | ✅ | ❌ |
| View ticket | ✅ | ✅ | ✅ | ✅ |
| Search tickets | ✅ | ✅ | ✅ | ✅ |
| View reports | ✅ | ✅ | ❌ | ❌ |
| Export CSV | ✅ | ❌ | ❌ | ❌ |
| Import CSV | ✅ | ❌ | ❌ | ❌ |
| Delete ticket | ✅ | ❌ | ❌ | ❌ |
| Manage users | ✅ | ❌ | ❌ | ❌ |

#### 3.1.5 Acceptance Criteria

| # | Criterion | Pass/Fail |
|:-:|-----------|:---------:|
| 1 | All 22 commands implemented and functional | |
| 2 | All permission checks enforced | |
| 3 | Audit log records every mutation | |
| 4 | Search returns correct results | |
| 5 | CSV export/import round-trips correctly | |
| 6 | Reports produce correct counts | |
| 7 | Session management works (login/logout) | |
| 8 | Password hashing works (SHA-256) | |
| 9 | Escalation rules fire correctly (SLA breach, unassigned critical) | |
| 10 | 30+ tests passing | |
| 11 | Builds/runs from clean state | |

---

### 3.2 Mini CRM (Target: ~2,500 LOC)

**[Frozen after Ticket System completes — see §5]**

---

### 3.3 Helpdesk + Workflow Engine (Target: ~3,000 LOC)

**[Frozen after Mini CRM completes — see §5]**

---

## 4. Metrics

### 4.1 Development Metrics

| Metric | How Measured |
|--------|--------------|
| **LOC** | `wc -l` or equivalent (excluding blank lines and comments) |
| **Files** | Count of source files |
| **Build attempts** | Number of `ail build` / `python -c "import ast; ..."` calls |
| **AI iterations** | Number of prompt→response cycles to reach passing state |
| **AI correction cycles** | Number of times AI had to fix its own previous output |
| **Compile errors** (AILang) | Distinct compiler errors encountered |
| **Runtime errors** | Distinct runtime errors encountered |
| **Refactor effort** | LOC changed to add one new feature after initial implementation |
| **Time to add feature** | Wall-clock time from spec to passing test for one feature |
| **Cognitive load score** | 1–5 rating of implementation complexity (1=trivial, 5=requires careful design) |

### 4.2 Runtime Metrics

| Metric | How Measured |
|--------|--------------|
| **Cold start** | Time from `ail run` / `python main.py` to first output |
| **Warm latency** | Average command response time over 100 commands |
| **Peak RAM** | Maximum resident set size during 1,000-command stress test |
| **Search latency** | Time to search 10,000 tickets by description substring |
| **Report generation** | Time to generate status/priority/agent/daily reports |
| **CSV import** | Time to import 1,000 tickets from CSV |
| **CSV export** | Time to export 1,000 tickets to CSV |

### 4.3 AI Collaboration Metrics

| Metric | How Measured |
|--------|--------------|
| **Hallucinated fixes** | Number of AI responses that suggested non-existent APIs or features |
| **Wrong refactors** | Number of AI responses that broke working code |
| **Compile cycles** | Total build→fix cycles to reach stable state |
| **Context resets** | Number of times conversation context was lost and had to be restarted |
| **Broken imports** | Number of times AI generated incorrect import paths |
| **Runtime surprises** | Number of errors only caught at runtime (not compile time) |

---

## 5. Execution Order

### Phase 1: Ticket Management System

1. Freeze this protocol
2. Build AILang implementation
3. Build Python implementation
4. Measure all metrics
5. Write results to `docs/benchmarks/M59_TICKET_RESULTS.md`

**Decision gate:** Review results. If AILang shows clear advantage in AI collaboration or maintainability, proceed to Phase 2. If not, stop and analyze why.

### Phase 2: Mini CRM

1. Freeze Mini CRM spec (based on Phase 1 learnings)
2. Build both implementations
3. Measure
4. Write results to `docs/benchmarks/M59_CRM_RESULTS.md`

**Decision gate:** Same as Phase 1.

### Phase 3: Helpdesk + Workflow Engine

1. Freeze workflow spec
2. Build both implementations
3. Measure
4. Write results to `docs/benchmarks/M59_WORKFLOW_RESULTS.md`

### Final Report

Aggregate all results into `docs/benchmarks/M59_FINAL_REPORT.md`.

---

## 6. Prompt Protocol

### 6.1 Initial Build Prompt

```
You are building a {APPLICATION_NAME} in {LANGUAGE}.

REQUIREMENTS:
{full_spec_from_this_document}

CONSTRAINTS:
- {LANGUAGE_CONSTRAINTS}
- No third-party libraries
- CLI interface only (no GUI)
- JSON file persistence
- All functions at top level (AILang) or modular (Python)
- Complete test suite required

PRODUCE:
1. All source files
2. All test files
3. A brief summary of the architecture

START WITH:
The data model and storage layer, then build outward.
```

### 6.2 Iteration Prompt (on failure)

```
The previous implementation failed:

ERROR:
{error_message}

CURRENT STATE:
{file_list_and_structure}

FIX:
Resolve the error while preserving all passing tests.
```

### 6.3 Feature Addition Prompt

```
Add the following feature to the existing codebase:

FEATURE:
{feature_description}

CURRENT CODEBASE:
{file_list}

CONSTRAINTS:
- All existing tests must continue passing
- New feature must have its own tests
- Follow existing code patterns

PRODUCE:
The modified files and new test file.
```

---

## 7. Stopping Conditions

| Condition | Rule |
|-----------|------|
| **All tests pass** | Both `ail build` + `ail run` (AILang) or `pytest` (Python) exit 0 |
| **Max iterations** | 15 attempts per feature addition |
| **Max tokens** | 200,000 total prompt + completion tokens per application |
| **Timeout** | 60 minutes wall-clock per application |
| **Diminishing returns** | 3 consecutive iterations with no progress |

If max iterations is reached, record as **FAILED** and note the failure mode.

---

## 8. Data Recording

### 8.1 Per-Trial Log

```json
{
  "trial_id": "M59-TICKET-AILANG-001",
  "application": "ticket_management",
  "language": "ailang",
  "model": "claude-sonnet-4-20250514",
  "timestamp_start": "2026-07-13T10:00:00Z",
  "timestamp_end": "2026-07-13T11:30:00Z",

  "iterations": 8,
  "compile_attempts": 6,
  "runtime_attempts": 2,
  "first_compile_pass": false,
  "first_test_pass": false,

  "prompt_tokens": 45230,
  "completion_tokens": 12410,
  "total_tokens": 57640,

  "hallucinated_fixes": 1,
  "wrong_refactors": 0,
  "ai_correction_cycles": 3,
  "broken_imports": 2,
  "runtime_surprises": 1,
  "context_resets": 0,
  "cognitive_load_score": 3,

  "final_loc": 2100,
  "final_files": 12,
  "tests_passing": 32,
  "tests_total": 35,

  "cold_start_ms": 45,
  "warm_latency_ms": 12,
  "peak_ram_mb": 28,
  "search_latency_ms": 120,
  "report_generation_ms": 85,
  "csv_import_ms": 210,
  "csv_export_ms": 180
}
```

### 8.2 Aggregated Results

After each phase, produce a comparison table:

| Metric | AILang | Python | Delta | Winner |
|--------|--------|--------|-------|--------|
| LOC | | | | |
| Files | | | | |
| AI iterations | | | | |
| AI correction cycles | | | | |
| Compile/runtime errors | | | | |
| Hallucinated fixes | | | | |
| Cognitive load score | | | | |
| Cold start | | | | |
| Warm latency | | | | |
| Peak RAM | | | | |
| Search latency | | | | |

---

## 9. Success Criteria

### 9.1 AILang Wins If

| Criterion | Threshold |
|-----------|-----------|
| AI iterations | ≤50% of Python's |
| AI correction cycles | ≤50% of Python's |
| Compile-time error detection | ≥90% of errors caught before runtime |
| Refactor safety | Zero regressions on feature addition |
| Hallucinated fixes | ≤50% of Python's |
| Cognitive load score | ≤ Python's score |

### 9.2 Python Wins If

| Criterion | Threshold |
|-----------|-----------|
| Runtime speed | ≥3× faster than AILang |
| Warm latency | ≤3× AILang's |
| Memory | ≤2× AILang's |
| Throughput | ≥30% better than AILang |
| LOC | ≤70% of AILang's |
| Feature velocity (human) | ≤80% of AILang's time |

### 9.3 Tie

If neither language clearly wins on its strengths, the result is **inconclusive** and the benchmark should be repeated with additional applications.

---

## 10. Out of Scope

| Item | Reason |
|------|--------|
| GUI / Web interface | Measuring UI frameworks, not language capability |
| Web frameworks (Django, Flask, FastAPI) | Framework comparison, not language comparison |
| ML / Data science | AILang has no NumPy/Pandas equivalent; unfair comparison |
| Distributed systems | Operational complexity, not language complexity |
| Async networking | AILang has no async model; measuring language design, not I/O |
| Database (SQLite, PostgreSQL) | JSON persistence is the AILang standard; fair comparison uses equivalent |
| Authentication frameworks | Custom SHA-256 hashing is sufficient for CRUD apps |
| Deployment / Docker | Operational complexity, not language complexity |
| Multi-model evaluation | Single-model first; multi-model replication is future work |
| Performance optimization | Measuring baseline, not optimized code |

---

## 11. Optimization Rules

Both languages receive **equal treatment** — no language gets preferential optimization.

| Rule | AILang | Python |
|------|--------|--------|
| **Allowed optimizations** | Compiler-level only (what the language provides) | Standard library only (what the language provides) |
| **Manual optimization** | Forbidden — measure the language as-is | Forbidden — measure the language as-is |
| **Algorithm choice** | AI chooses freely | AI chooses freely |
| **Data structures** | stdlib only (list, map, set) | stdlib only (list, dict, set) |
| **I/O pattern** | Synchronous (AILang has no async) | Synchronous (match AILang's model) |
| **Caching** | Forbidden — measure raw performance | Forbidden — measure raw performance |

**Rationale:** The benchmark measures language capability, not developer optimization skill. Both implementations must use idiomatic, straightforward code. If one language requires clever tricks to perform well, that itself is a finding.

---

## 12. Approval

| Role | Name | Approved |
|------|------|:--------:|
| CTO | | ☐ |
| Architecture | | ☐ |
| Benchmark Lead | | ☐ |

**Next step:** Get approval, then execute Phase 1 (Ticket Management System).
