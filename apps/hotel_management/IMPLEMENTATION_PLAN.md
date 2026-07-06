# Hotel Management System — Implementation Plan

## Overview

A production-quality hotel management system with persistent storage, complex business logic (availability checking, booking lifecycle, payment tracking, invoice generation), and multi-format reporting.

## Domain

Manage hotel operations: room inventory, guest profiles, bookings, payments, and invoices — all via a CLI menu-driven interface with JSON file persistence.

## Target Metrics

| Metric | Target |
|--------|--------|
| Lines of Code | 1,500–2,500 |
| Functions | 100–180 |
| Modules | 9 |
| Files | 9 `.ail` + data files |

## Architecture

```
main.ail  (CLI menu, entry point)
  |
  +-- validation.ail   (string utils, date validation, input parsing)
  |
  +-- storage.ail      (JSON file persistence: load/save/generate IDs)
  |
  +-- room.ail         (room CRUD, availability, status management)
  |
  +-- guest.ail        (guest CRUD, search by name/phone)
  |
  +-- booking.ail      (booking lifecycle: create, check-in, check-out, cancel, modify, conflicts)
  |
  +-- payment.ail      (payment recording, refunds, per-booking view)
  |
  +-- invoice.ail      (invoice generation from booking + payments)
  |
  +-- report.ail       (occupancy, revenue, booking statistics)
```

## Data Structures (AILang maps + lists)

### Room
```ail
{
  "id": "101",
  "type": "DELUXE",
  "rate": 1500,
  "capacity": 2,
  "status": "AVAILABLE"
}
```
Types: `STANDARD`, `DELUXE`, `SUITE`, `PENTHOUSE`
Statuses: `AVAILABLE`, `OCCUPIED`, `MAINTENANCE`, `RESERVED`

### Guest
```ail
{
  "id": "G001",
  "name": "John Doe",
  "phone": "555-1234",
  "email": "john@example.com",
  "address": "123 Main St",
  "id_doc": "P123456",
  "created": "2026-07-05"
}
```

### Booking
```ail
{
  "id": "B001",
  "guest_id": "G001",
  "room_id": "101",
  "check_in": "2026-07-10",
  "check_out": "2026-07-15",
  "status": "RESERVED",
  "total": 7500,
  "created": "2026-07-05",
  "guests": 2
}
```
Statuses: `RESERVED`, `CHECKED_IN`, `CHECKED_OUT`, `CANCELLED`

### Payment
```ail
{
  "id": "P001",
  "booking_id": "B001",
  "guest_id": "G001",
  "amount": 7500,
  "method": "CARD",
  "status": "COMPLETED",
  "date": "2026-07-05"
}
```
Methods: `CASH`, `CARD`, `UPI`, `BANK_TRANSFER`
Statuses: `PENDING`, `COMPLETED`, `REFUNDED`

### Invoice
```ail
{
  "id": "I001",
  "booking_id": "B001",
  "guest_name": "John Doe",
  "room_id": "101",
  "room_type": "DELUXE",
  "rate_per_night": 1500,
  "check_in": "2026-07-10",
  "check_out": "2026-07-15",
  "nights": 5,
  "subtotal": 7500,
  "total_paid": 7500,
  "balance": 0,
  "status": "PAID"
}
```
Statuses: `PAID`, `UNPAID`, `PARTIAL`

## Storage

Each entity type stored as a JSON list in its own file under `apps/hotel_management/data/`:

| File | Content |
|------|---------|
| `data/rooms.json` | List of room maps |
| `data/guests.json` | List of guest maps |
| `data/bookings.json` | List of booking maps |
| `data/payments.json` | List of payment maps |

### Storage Functions

- `load_rooms()` → list of room maps (empty list if file missing)
- `save_rooms(rooms)` → writes JSON to file
- `load_guests()` → list of guest maps
- `save_guests(guests)` → writes JSON to file
- `load_bookings()` → list of booking maps
- `save_bookings(bookings)` → writes JSON to file
- `load_payments()` → list of payment maps
- `save_payments(payments)` → writes JSON to file
- `generate_id(prefix, items)` → `"B001"`, `"B002"`, etc.

## Booking Conflict Detection

A room is unavailable for a new booking if an existing RESERVED or CHECKED_IN booking has overlapping dates:

```
Overlap condition: new_check_in < existing_check_out
                 AND new_check_out > existing_check_in
```

## CLI Menu

```
=== HOTEL MANAGEMENT SYSTEM ===
1. Room Management
2. Guest Management
3. Booking Management
4. Payments
5. Reports
6. Exit

> _
```

### Sub-menus

**Room Management:**
1. Add Room
2. List All Rooms
3. Update Room Rate
4. Set Room Status
5. View Available Rooms
6. Back

**Guest Management:**
1. Add Guest
2. Search Guest (by name)
3. List All Guests
4. Back

**Booking Management:**
1. Create Booking
2. Check In
3. Check Out
4. Cancel Booking
5. View Booking Details
6. List All Bookings
7. Back

**Payments:**
1. Record Payment
2. View Payments for Booking
3. Back

**Reports:**
1. Occupancy Report (by date range)
2. Revenue Report (by date range)
3. Booking Summary (by status)
4. Room Utilization
5. Back

## Implementation Order

| Step | Module | Description |
|------|--------|-------------|
| 1 | `validation.ail` | String utilities, date parsing/validation, input helpers |
| 2 | `storage.ail` | JSON file load/save/generate_id for all entity types |
| 3 | `room.ail` | Room CRUD, availability checks, status management |
| 4 | `guest.ail` | Guest CRUD, search by name/phone |
| 5 | `booking.ail` | Booking lifecycle, conflict detection, date overlap |
| 6 | `payment.ail` | Payment recording, refund logic |
| 7 | `invoice.ail` | Invoice generation from booking + payments |
| 8 | `report.ail` | Occupancy, revenue, utilization statistics |
| 9 | `main.ail` | CLI menu system, input routing, error handling |

## Dependency Graph

```
validation.ail → storage.ail
                    ↓
              room.ail  guest.ail
                    ↓    ↓
              booking.ail
                    ↓
              payment.ail
                    ↓
              invoice.ail
                    ↓
              report.ail
                    ↓
              main.ail
```

## AILang Features Used

- **string**: `concat`, `contains`, `equals`, `length`, `starts_with`, `substring`, `trim`, `uppercase`, `lowercase`, `ends_with`
- **list**: `new`, `append`, `get`, `len`, `contains`, `remove`, `clear`
- **map**: `new`, `set`, `get`, `has`, `delete`, `keys`, `clear`
- **convert**: `to_int`, `to_string`, `to_bool`
- **json**: `parse`, `stringify`
- **file**: `exists`, `read`, `write`
- **io**: `write`, `writeln`, `println`
- **environment**: `args`
- **system**: `exit`
- `print` builtin
- Recursion for all iteration
- `if/else` for control flow
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Logical: `&&`, `||`, `!` (eager evaluation — use nested `if` for guarded access)
- Arithmetic: `+`, `-`

## Known Language Limitations

| Limitation | Impact |
|------------|--------|
| No loops | All iteration via recursion; +20-30% LOC vs loop-based |
| No `string.split()` | Custom `split_string` via `find_substring` recursion |
| No `string.find()` | Custom `find_substring` — O(n×m) per call |
| No `string.join()` | Custom `join_list` via recursion |
| No `string.replace()` | Custom `replace_substring` via recursion |
| No date/time math | Date comparison via custom `parse_date`/`date_diff` string parsing |
| No short-circuit `&&` | Nested `if` for guarded list/map access |
| No exception handling | Explicit `map.has` checks before every `map.get` |
| No `None` literal | `json.parse("null")` for absent values |
| No `while`/`for` | Recursion depth limited (~1200 frames with reclimit 10000) |
| No regex | All pattern matching is manual character-by-character |

## Complexity Estimate

| Module | Functions | LOC (est.) | Complexity |
|--------|-----------|-----------|------------|
| validation.ail | ~15 | ~100 | Low: string utilities, helpers |
| storage.ail | ~15 | ~150 | Low: file I/O, JSON serialization |
| room.ail | ~15 | ~180 | Medium: CRUD + availability |
| guest.ail | ~12 | ~150 | Medium: CRUD + search |
| booking.ail | ~25 | ~350 | High: lifecycle states, conflict detection, date overlap |
| payment.ail | ~12 | ~150 | Medium: payment recording |
| invoice.ail | ~12 | ~200 | Medium: computation from booking + payments |
| report.ail | ~15 | ~250 | High: multi-entity aggregation, statistics |
| main.ail | ~15 | ~300 | Medium: CLI menu, input routing, error handling |
| **Total** | **~136** | **~1,830** | |
