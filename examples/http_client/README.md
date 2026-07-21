# HTTP Client

Simulates HTTP request construction and validation logic with hardcoded values (no actual network calls).

## Concepts Demonstrated

- String equality for HTTP method validation
- Input validation (URL, method)
- Multi-branch if/else for method checking
- Function composition for request building

## How to Run

```bash
ail run main.ail
```

## What to Try

- Add support for additional HTTP methods (PATCH, HEAD) in `validate_method()`
- Add a function to construct request headers as key-value pairs
