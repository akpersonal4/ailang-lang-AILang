# DX-016 — Watch Mode (`ail watch`)

## Usage

```bash
ail watch [<entry_file>] [options]
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--poll` | Use polling instead of filesystem events | `false` |
| `--poll-interval MS` | Polling interval in milliseconds | `500` |
| `--json` | Machine-readable JSON output | `false` |
| `--no-initial` | Skip initial full build | `false` |

## Exit Codes

| Code | Meaning |
|:----:|---------|
| 0 | Watch mode terminated (user Ctrl+C) |
| 1 | Initial build failed |

## Examples

```bash
# Watch current directory
ail watch

# Watch a specific entry point
ail watch main.ail

# Use polling (network filesystem)
ail watch --poll

# Machine-readable output for AI tooling
ail watch --json

# Skip initial build
ail watch --no-initial
```

## Performance

| Scenario | Target Latency |
|----------|:--------------:|
| Single-file edit, no dependents | <50 ms |
| Single-file edit, 3 dependents | <200 ms |
| False positive watcher event | <1 ms |
| Initial full build | <3,000 ms |

## Architecture

- Uses `watchdog` for cross-platform filesystem monitoring
- SHA-256 hash-based change detection filters spurious events
- 200ms debounce prevents redundant compiles during burst edits
- Incremental recompilation re-parses and re-analyzes only changed modules and their transitive dependents
- Polling fallback for network filesystems (NFS, Docker, WSL)
