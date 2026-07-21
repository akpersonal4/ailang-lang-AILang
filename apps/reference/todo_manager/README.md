# Todo Manager

A simple todo list application demonstrating AILang's list, map, json, and file modules.

## Features
- Add tasks with titles
- Mark tasks as complete
- Delete tasks by index
- Count pending tasks
- Save/load to JSON file

## Architecture
- Data: List of maps, each map has "title" (string) and "done" (boolean)
- Persistence: JSON file via `json.stringify`/`json.parse` + `file.write`/`file.read`
- Recursion: `_helper` pattern with index accumulator for iteration

## LOC
~85

## stdlib Modules Used
- `list` — dynamic array operations
- `map` — key-value storage per todo
- `json` — serialization/deserialization
- `file` — file I/O
- `io` — output
- `convert` — type conversion

## Run
```bash
ail run apps/reference/todo_manager/main.ail
```
