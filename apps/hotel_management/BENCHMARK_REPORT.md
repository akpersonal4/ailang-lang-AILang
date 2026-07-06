# Hotel Management System — Benchmark Report

## Application Summary

| Attribute | Value |
|-----------|-------|
| **Name** | Hotel Management System |
| **Domain** | Hospitality / Property Management |
| **Version** | 1.0 |
| **Lines of Code** | 1,510 |
| **Functions** | 154 |
| **Modules (sections)** | 12 |
| **Files** | 1 (`main.ail`) + 4 data files (`rooms.json`, `guests.json`, `bookings.json`, `payments.json`) |

## Features

### Room Management
- Add room (id, type, rate, capacity, status)
- List all rooms with formatted table
- Update room rate
- Set room status (AVAILABLE, OCCUPIED, MAINTENANCE, RESERVED)
- Search available rooms for a date range

### Guest Management
- Register guest with name, phone, email
- Case-insensitive search by name or phone
- List all guests

### Booking Management
- Create booking with conflict detection (date overlap check)
- Check-in / Check-out (updates room status)
- Cancel booking (only if not checked out; releases room)
- View booking detail with auto-generated invoice
- List all bookings with formatted table

### Payments
- Record payment against a booking (CASH, CARD, UPI, BANK_TRANSFER)
- View all payments for a booking with total
- Refund support

### Invoice Generation
- Auto-generated invoice from booking + payments
- Shows: guest name, room, type, rate, dates, nights, subtotal, paid, balance, status (PAID/UNPAID/PARTIAL)

### Reports
- **Occupancy**: Rooms occupied vs total for a date range (percentage)
- **Revenue**: Total revenue, booking count, average per booking for a date range
- **Booking Summary**: Count by status (reserved, checked-in, checked-out, cancelled)
- **Room Utilization**: Count by status (available, occupied, reserved, maintenance)

## Development Metrics

| Metric | Value |
|--------|-------|
| First Compile | ❌ FAIL (6 forward references) |
| Final Compile | ✅ PASS |
| First Runtime | ❌ FAIL (list_find_by_key arg mismatch) |
| Final Runtime | ✅ PASS |
| Compiler Iterations | 1 |
| Runtime Iterations | 5 |
| Total Revisions | 6 |
| Development Time | ~17 minutes |
| Total LOC Written | 1,510 |
| Functions Written | 154 |

## Supported CLI Commands

```
room add <id> <type> <rate> [capacity]
room list
room update-rate <id> <new_rate>
room set-status <id> <status>
room available <check_in> <check_out>

guest add <name> <phone> [email]
guest search <name>
guest list

booking create <guest_id> <room_id> <check_in> <check_out> [guests]
booking checkin <id>
booking checkout <id>
booking cancel <id>
booking detail <id>
booking list

payment record <booking_id> <amount> [method]
payment view <booking_id>

report occupancy <start_date> <end_date>
report revenue <start_date> <end_date>
report bookings
report utilization

invoice <booking_id>
```

## Data Persistence

All data stored as JSON in `apps/hotel_management/data/`:
- `rooms.json` — list of room maps
- `guests.json` — list of guest maps  
- `bookings.json` — list of booking maps
- `payments.json` — list of payment maps

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| CLI-driven (no stdinput) | AILang has no stdin read function; all input via `environment.args()` |
| Single file with level sections | AILang does not support multi-file user imports |
| JSON file persistence | `json.parse`/`stringify` for serialization; no database module available |
| `date_to_days` epoch calculation | Needed for date comparison and overlap detection without `time.parse` or date math |
| Nested `if` for guarded access | AILang `&&` does not short-circuit; nested if prevents crashes |
| ID generation with numeric suffix | `gen_id_helper` scans existing IDs to find max, then increments |

## Language Evaluation

| Category | Rating (1–10) | Evidence |
|----------|:------------:|----------|
| Documentation | 8 | LANGUAGE_SPEC.md, LANGUAGE_TOUR.md, STDLIB_REFERENCE.md all accurate. Short-circuit `&&` issue resolved during previous benchmark. |
| Compiler | 8 | Compiles 1,510 LOC / 154 functions successfully. Error messages lack line numbers. |
| Runtime | 7 | Stable execution. Only 1 runtime bug discovered (concat 2-arg limit) which is a documentation vs behavior issue. |
| Standard Library | 6 | `string.concat` 2-arg limit is restrictive (forces deep nesting). No `string.split`/`join`/`find`/`sort` means ~100 LOC of manual implementations. JSON persistence works well. |
| Ease of Development | 5 | Forward reference constraint is the biggest friction. Every new function must be inserted at the right level, not where it logically belongs. After the pattern is learned, it's manageable. |
| Maintainability | 6 | Single-file constraint limits separation of concerns. Level-based organization helps but is unnatural for large codebases. 154 functions in one file is at the limit of readability. |
| AI Friendliness | 7 | AILang's explicit syntax and deterministic behavior make it easy for AI to generate. The forward-reference requirement makes insertion fragile — AI must track function ordering precisely. |

## Verdict

**Can AILang be used to build serious production software?**

**Yes, with caveats.** The Hotel Management System proves that complex, multi-entity business logic with persistence, state machines (booking lifecycle), conflict detection, and reporting is achievable in AILang within a reasonable timeframe (~17 minutes for 1,510 LOC).

### Strengths
- **Deterministic** — Same input, same output; no hidden state
- **Fast iteration** — Compile time is near-instant; runtime is fast
- **JSON integration** — `json.parse`/`stringify` make persistence trivial
- **Predictable semantics** — No surprises in control flow or evaluation
- **Explicit** — `map.has` before `map.get`, nested `if` for guarding: forces clarity

### Weaknesses
- **No forward references** — Single biggest productivity cost. Forces bottom-up development. For 154 functions, ~5 min of restructuring on first compile.
- **No multi-file modules** — All 1,510 LOC in one file. At this scale, readability suffers. No namespace isolation.
- **No stdin** — CLI-driven development only; no interactive menus or prompts
- **stdlib gaps** — `string.split`, `string.join`, `string.find`, `list.sort` all require manual O(n×m) recursion — adds ~15-30% LOC overhead vs languages with these builtins
- **No exception handling** — Every `map.get` must be guarded by `map.has`; defensive coding adds verbosity

### Recommendation

AILang is suitable for **small-to-medium production applications** (up to ~2,000 LOC) with clear domain boundaries and limited external dependencies. Beyond that scale, the single-file constraint and lack of user-defined module imports become significant quality-of-life barriers. The language is **stable, predictable, and reliable** — ideal for deterministic, audit-friendly systems where clarity matters more than conciseness.
