# Hotel Management System — Development Log

## Overview
Production-grade hotel management system: room inventory, guest profiles, booking lifecycle (reserve/check-in/check-out/cancel), payment recording, invoice generation, and multi-format reports — all via CLI commands.

## Iterations

### Iteration 1 — First Compile (Compiler Iteration)
- **Attempt**: Compile 1,510 LOC / 154 functions in single `main.ail`
- **Result**: ❌ FAIL — 6 "Undefined identifier" errors
- **Causes**: All forward references:
  - `gen_id_helper` called by `generate_id` (simple swap)
  - `booking_filter_by_room_on_dates` called by `room_is_available_on_dates` (cross-module dependency)
  - `payment_sum_helper` called by `payment_sum_for_booking`
  - `invoice_build_list` called by `invoice_list_by_guest`
  - `report_occupied_rooms` called by `report_occupancy`
  - `report_sum_revenue` called by `report_revenue`
- **Fix**: All 6 resolved by reordering callee-before-caller. Most complex: `booking_filter_by_room_on_dates` moved to before room module (between storage and room). Created `list_find_by_key_step` + `list_find_by_key` wrapper to solve 3-arg vs 4-arg discrepancy.
- **Time**: ~8 min

### Iteration 2 — First Runtime Test (Runtime Iteration)
- **Attempt**: `room add 101 DELUXE 1500 2`
- **Result**: ❌ FAIL — "Function list_find_by_key expected 4 arguments, got 3"
- **Cause**: `list_find_by_key` defined with 4 params (items, key, value, i) but all callers passed 3 args
- **Fix**: Renamed 4-arg version to `list_find_by_key_step`, added `list_find_by_key(items, key, value)` wrapper that calls step with i=0
- **Time**: ~2 min

### Iteration 3 — Room Management Test
- **Attempt**: `room add`, `room list`, `room update-rate`, `room set-status`
- **Result**: ⚠️ PARTIAL — `room add 101` succeeded, `room add 102` succeeded, `room list` worked, `room update-rate` worked, `room set-status` failed
- **Cause**: `string.concat(room_id, " status set to ", status)` — AILang's `string.concat` accepts exactly 2 arguments. The 3-arg form crashes at runtime.
- **Fix**: Nested to `string.concat("Room ", string.concat(room_id, string.concat(" status set to ", status)))`
- **Time**: ~3 min

### Iteration 4 — Booking + Payment + Invoice Test
- **Attempt**: Full workflow: guest add → booking create → checkin → payment → checkout → invoice
- **Result**: ✅ PASS — All operations completed
- **Found**: Same `string.concat` 3-arg bug in `booking_update_status` (line 790)
- **Fix**: Nested to 2-arg form
- **Time**: ~2 min

### Iteration 5 — Reports Test
- **Attempt**: `report occupancy`, `report revenue`, `report bookings`, `report utilization`
- **Result**: ✅ PASS — All 4 reports generated correct output with real data
- **Time**: ~1 min

### Iteration 6 — Edge Cases
- **Attempt**: Available room search on dates, guest search by partial name, cancel booking
- **Result**: ✅ PASS — Available rooms correctly excluded occupied/reserved, case-insensitive search worked, cancellation updated room status
- **Time**: ~1 min

## Summary

| Metric | Value |
|--------|-------|
| Compiler Iterations | 1 |
| Runtime Iterations | 5 |
| Total Revisions | 6 |
| Total Functions | 154 |
| Total LOC | 1,510 |
| Development Time | ~17 min total |
| First Compile | ❌ FAIL |
| Final Compile | ✅ PASS |
| First Runtime | ❌ FAIL |
| Final Runtime | ✅ PASS |

## Errors Encountered

| # | Type | Category | Issue | Fix |
|:-:|------|----------|-------|-----|
| 1 | Compile | Language Characteristic | 6 forward references: gen_id_helper, booking_filter_by_room_on_dates, payment_sum_helper, invoice_build_list, report_occupied_rooms, report_sum_revenue | Reorder callee-before-caller; moved booking_filter_by_room_on_dates between storage and room modules |
| 2 | Runtime | Developer Error | `list_find_by_key` expected 4 args, callers passed 3 | Added 3-arg wrapper `list_find_by_key` calling 4-arg `list_find_by_key_step` |
| 3 | Runtime | Language Characteristic | `string.concat` with 3 args crashes (2-arg only) | Nested concat calls; found in 2 locations |
