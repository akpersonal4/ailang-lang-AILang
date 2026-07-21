# INI Parser

Simulates parsing INI configuration sections with port validation logic.

## Concepts Demonstrated

- Functions returning typed values (string, integer)
- Range validation with nested if/else
- Section-based data access pattern

## How to Run

```bash
ail run main.ail
```

## What to Try

- Add more INI sections (e.g., `[server]` with host and timeout values)
- Extend `ini_port_valid()` to reject privileged ports (below 1024)
