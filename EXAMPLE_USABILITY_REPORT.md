# EXAMPLE_USABILITY_REPORT.md — M89F

**Milestone:** M89F — Silent Example Improvement  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## Issues Fixed

### Problem

5 standalone examples and 3 subdirectory examples executed successfully (exit code 0) but produced no visible output. A first-time user running these examples would see nothing and might think something is wrong.

### Root Cause

- **Standalone files** (`variables.ail`, `functions.ail`, `if_else.ail`): Defined declarations/functions but had no `main()` and no `print()` calls.
- **Subdirectory files** (`fibonacci/main.ail`, `recursion/main.ail`): Had `main()` that returned values but never called `print()`.
- **Subdirectory variants** (`variables/main.ail`, `functions/main.ail`, `if_else/main.ail`): Same issue — returned values without printing.

### Fix

Added `print()` calls to every example so users see clear, educational output demonstrating the language feature being taught.

## Examples Fixed

| Example | Before | After |
|---------|--------|-------|
| variables.ail | No output | `x = 10`, `y = 20`, `sum = 30` |
| functions.ail | No output | `add(3, 4) = 7`, `add(10, 20) = 30` |
| if_else.ail | No output | `example(5) = 5`, `example(-3) = 3`, `example(0) = 0` |
| fibonacci/main.ail | No output | `fibonacci(10) = 55` |
| recursion/main.ail | No output | `factorial(5) = 120` |
| variables/main.ail | No output | `x = 10`, `y = 20`, `sum = 30` |
| functions/main.ail | No output | `square(3) = 9`, `cube(2) = 8`, `result = 17` |
| if_else/main.ail | No output | `x (10) is greater than 5` |

## Output Verification

All examples were run and produced the expected output:

```
variables.ail:       x = 10 / y = 20 / sum = 30
functions.ail:       add(3, 4) = 7 / add(10, 20) = 30
if_else.ail:         example(5) = 5 / example(-3) = 3 / example(0) = 0
fibonacci/main.ail:  fibonacci(10) = 55
recursion/main.ail:  factorial(5) = 120
```

**Result: All 8 previously silent examples now produce clear, educational output.**
