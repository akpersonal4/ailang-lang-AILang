# Benchmark Validation Report — AILang v0.1.3

## Results

| Metric | Value |
|--------|-------|
| Total apps | 42 |
| Build successes | 42 / 42 (100%) |
| Run successes | 42 / 42 (100%) |
| `ail fmt --check` passes | 2 / 42 (4.8%) |

## App List (all 42)

| # | App | Build | Run | Fmt |
|--:|-----|:-----:|:---:|:---:|
| 1 | banking_ledger | ✓ | ✓ | ✗ |
| 2 | bmi_calculator | ✓ | ✓ | ✗ |
| 3 | calculator | ✓ | ✓ | ✗ |
| 4 | calendar_app | ✓ | ✓ | ✗ |
| 5 | config_reader | ✓ | ✓ | ✗ |
| 6 | contact_book | ✓ | ✓ | ✗ |
| 7 | csv_analyzer | ✓ | ✓ | ✗ |
| 8 | dice_roller | ✓ | ✓ | ✗ |
| 9 | employee_management | ✓ | ✓ | ✗ |
| 10 | expense_tracker | ✓ | ✓ | ✗ |
| 11 | file_copy | ✓ | ✓ | ✗ |
| 12 | file_search | ✓ | ✓ | ✗ |
| 13 | grade_calculator | ✓ | ✓ | ✗ |
| 14 | hangman_game | ✓ | ✓ | ✗ |
| 15 | hotel_management | ✓ | ✓ | ✗ |
| 16 | http_request_parser | ✓ | ✓ | ✗ |
| 17 | inventory | ✓ | ✓ | ✗ |
| 18 | inventory_mgmt | ✓ | ✓ | ✓ |
| 19 | invoice_generator | ✓ | ✓ | ✗ |
| 20 | json_formatter | ✓ | ✓ | ✗ |
| 21 | kanban | ✓ | ✓ | ✓ |
| 22 | library_management | ✓ | ✓ | ✗ |
| 23 | log_analyzer | ✓ | ✓ | ✗ |
| 24 | markdown_parser | ✓ | ✓ | ✗ |
| 25 | markdown_stats | ✓ | ✓ | ✗ |
| 26 | mini_sql | ✓ | ✓ | ✗ |
| 27 | note_taking | ✓ | ✓ | ✗ |
| 28 | number_base | ✓ | ✓ | ✗ |
| 29 | number_guessing_game | ✓ | ✓ | ✗ |
| 30 | password_generator | ✓ | ✓ | ✗ |
| 31 | random_data_generator | ✓ | ✓ | ✗ |
| 32 | rps_game | ✓ | ✓ | ✗ |
| 33 | scientific_calculator | ✓ | ✓ | ✗ |
| 34 | simple_quiz | ✓ | ✓ | ✗ |
| 35 | student_management | ✓ | ✓ | ✗ |
| 36 | temperature_converter | ✓ | ✓ | ✗ |
| 37 | text_search | ✓ | ✓ | ✗ |
| 38 | tictactoe_game | ✓ | ✓ | ✗ |
| 39 | todo_manager | ✓ | ✓ | ✗ |
| 40 | unit_converter | ✓ | ✓ | ✗ |
| 41 | word_counter | ✓ | ✓ | ✗ |
| 42 | wordle_game | ✓ | ✓ | ✗ |

## Findings

### All 42 apps compile and run correctly
No build failures, no runtime errors. Every app produces its expected output.

### 40/42 apps fail `ail fmt --check`
These 40 apps have missing semicolons in source files (primarily on `return`
statements). The formatter now self-heals during `ail fmt` by tolerating
"Expected SEMICOLON" parse errors and adding the missing semicolons in its
output. The original source files are not modified unless `ail fmt` (without
`--check`) is run.

The 2 apps that pass `fmt --check` — **kanban** and **inventory_mgmt** — were
previously formatted by the fixed formatter in earlier testing.

### No multi-module apps
All 42 apps are single-file (`main.ail` only). No app uses sub-modules.
Multi-module support is exercised only by tests.

### Impact on release
- **Build/Run:** No blockers.
- **Fmt:** A project-wide `ail fmt apps/` should be run before tagging v0.1.3
  to normalize all source files. This can be done as a single batch operation.
