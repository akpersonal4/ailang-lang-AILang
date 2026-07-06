# Implementation Plan — Kanban Project Management System

## Architecture

### Data Model
- **Board**: `{ id, name, description, columns: [Column] }`
- **Column**: `{ id, name, tasks: [Task] }`
- **Task**: `{ id, title, desc, priority, due_date, assignee, labels: [str], created_at, updated_at, status }`

### Storage
- JSON file persistence (single JSON array of boards)
- Auto-save on every mutation

### CLI Interface
- Menu-driven: 1) Create Board, 2) Add Task, 3) Move Task, 4) Search, etc.
- Statistics/reports displayed on demand

---

## Function Dependency Graph

### Level 0 — Pure Utilities (no dependencies)
`is_empty`, `current_timestamp`, `id_counter`

### Level 1 — String Helpers (depend on stdlib only)
`find_substring`, `split_string`, `join_strings`, `string_in_list_pos`, `string_in_list_flag`

### Level 2 — Task Data Constructor
`make_task`, `task_set_labels`, `task_add_label`, `task_has_label`

### Level 3 — Column Operations
`make_column`, `find_task_in_column`, `remove_task_from_column`, `move_task_out`

### Level 4 — Board Operations
`make_board`, `find_column_id`, `board_total_tasks`, `add_task_to_column`, `delete_task_from_column`

### Level 5 — Persistence
`load_boards`, `save_boards`, `export_board_to_file`, `import_board_from_file`

### Level 6 — Task CRUD
`create_task`, `update_task_field`, `delete_task`, `move_task`

### Level 7 — Board CRUD
`create_board`, `delete_board`, `rename_board`

### Level 8 — Search & Filter
`search_tasks`, `filter_by_priority`, `filter_by_assignee`, `filter_by_label`, `list_tasks_in_column`

### Level 9 — Statistics & Reports
`count_by_column`, `count_by_priority`, `count_by_assignee`, `count_overdue`, `generate_report`

### Level 10 — Import/Export & Demo
`export_all_boards`, `import_all_boards`, `create_demo_board`

### Level 11 — UI
`main_menu`, `handle_create_board`, `handle_add_task`, `handle_move_task`, `handle_search`, `handle_stats`, `handle_export`

### Level N — `main()`

---

## Estimated Metrics
- **LOC:** ~1,200–1,500
- **Functions:** ~100–120
- **Modules:** 1
- **Imports:** list, map, string, json, file, time, convert

## Risk Analysis
| Risk | Mitigation |
|------|-----------|
| Forward references | Bottom-up ordering (Level 0 → N) |
| map.get without guard | All get() preceded by has() |
| Variable collision | `_pos`, `_idx`, `_acc` suffixes per function |
| concat with 3+ args | Use + operator |
| split/find missing | Copy from examples/patterns/ |
| No sort | Manual selection sort for lists of maps |
| Deep recursion | All recursions iterate over data lists (<100 depth) |
