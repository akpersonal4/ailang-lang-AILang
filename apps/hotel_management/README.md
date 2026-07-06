# Hotel Management System

Production-quality hotel management system implemented in AILang. CLI-driven with JSON persistence.

## Quick Start

```bash
# Add rooms
ail run apps/hotel_management/main.ail room add 101 DELUXE 1500 2
ail run apps/hotel_management/main.ail room add 102 STANDARD 800 2

# Add guests
ail run apps/hotel_management/main.ail guest add "John Doe" "555-0100" john@test.com

# Create booking
ail run apps/hotel_management/main.ail booking create G001 101 2026-08-01 2026-08-05 2

# Check in, pay, check out
ail run apps/hotel_management/main.ail booking checkin B001
ail run apps/hotel_management/main.ail payment record B001 7200 CARD
ail run apps/hotel_management/main.ail booking checkout B001

# Generate invoice
ail run apps/hotel_management/main.ail invoice B001

# Reports
ail run apps/hotel_management/main.ail report occupancy 2026-08-01 2026-08-31
ail run apps/hotel_management/main.ail report revenue 2026-08-01 2026-08-31
```

## Commands

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for full command reference.

## Metrics

- 1,510 LOC
- 154 functions
- 12 modules (sections)
- 4 data stores (rooms, guests, bookings, payments)
- 22 CLI commands
- ~17 min development time
- 1 compiler iteration + 5 runtime iterations

## Data

Persisted as JSON in `data/` directory. Created on first use.
