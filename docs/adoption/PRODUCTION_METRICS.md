# Production Validation Metrics

**Date:** 2026-07-10  
**Application:** Inventory System (`apps/inventory/`)  
**Tracking Period:** 2026-07-10 to 2026-10-10 (12 weeks / 3 months)  
**Goal:** Determine whether AILang is suitable for production CRUD applications

---

## 1. Instrumentation Approach

### Philosophy

Track only what informs the decision. Every metric must directly answer at least one of:

- "Would we choose AILang again?"
- "What would need to change for AILang to be production-ready?"
- "Is the codebase getting healthier or sicker?"

### Collection Method

| Method | Applies To | Effort |
|:-------|:-----------|:-------|
| **Automatic** (scripted) | LOC, compile time, test count, regressions | Zero — run once per week |
| **Manual** (change log) | Bugs, features, rollbacks, incidents | 2 min per change |
| **Survey** (user feedback) | Satisfaction, friction points | 5 min per week |

### Instrumentation Script

A Python script (`apps/inventory/tools/metrics.py` — 40 LOC) collects automatic metrics:

```python
# apps/inventory/tools/metrics.py
# Run: python tools/metrics.py
# Outputs: JSON to metrics/data/YYYY-MM-DD.json

import json, os, subprocess, sys, time
from datetime import date

def count_loc(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.ail'):
                with open(os.path.join(root, f)) as fp:
                    total += len(fp.readlines())
    return total

def count_tests(path):
    # Count test functions (fn test_*)
    count = 0
    for root, dirs, files in os.walk(os.path.join(path, 'tests')):
        for f in files:
            if f.endswith('.ail'):
                with open(os.path.join(root, f)) as fp:
                    for line in fp:
                        if line.strip().startswith('fn test_'):
                            count += 1
    return count

def measure_build_time(path):
    start = time.time()
    result = subprocess.run(
        ['python', '-m', 'compiler.cli.main', 'build', path],
        capture_output=True, text=True, timeout=30
    )
    duration = time.time() - start
    return {
        'success': result.returncode == 0,
        'duration_seconds': round(duration, 3),
        'stderr': result.stderr[:500] if result.stderr else ''
    }

# ... collection continues
```

Create directory structure:
```
metrics/
  data/          ← Daily snapshots (auto-generated)
    2026-07-10.json
    2026-07-17.json
    ...
  reports/       ← Monthly reports (manually compiled)
    month_1.md
    month_2.md
    month_3.md
```

---

## 2. Metric Definitions

### 2.1 Bugs

| Field | Definition |
|:------|:-----------|
| Bug ID | `BUG-PROD-NNN` (sequential) |
| Severity | **Critical** (data loss, crash), **Major** (wrong result), **Minor** (cosmetic, UX) |
| Origin | **AILang bug** (compiler/runtime), **Logic bug** (application code), **Data bug** (corruption) |
| Detection | **Compile-time** (ail build caught), **Test-time** (test suite caught), **Runtime** (user reported) |
| Fix duration | Wall clock from report to deploy (hours) |
| Fix LOC | Lines changed to fix |

**Collection:** Manual entry into `metrics/bugs.json`:

```json
[
  {
    "id": "BUG-PROD-001",
    "date_reported": "2026-07-15",
    "date_fixed": "2026-07-15",
    "severity": "major",
    "origin": "logic",
    "detection": "runtime",
    "description": "Stock adjustment allows negative quantity with wrong sign",
    "fix_duration_hours": 0.5,
    "fix_loc": 3,
    "fix_files": ["stock_adjustment.ail"],
    "root_cause": "Incorrect comparison operator in validation"
  }
]
```

### 2.2 Fix Duration

| Metric | Definition | Target |
|:-------|:-----------|:-------|
| Mean time to fix | Average hours from report to deploy | < 4 hours |
| Critical fix time | 90th percentile for critical bugs | < 1 hour |
| Fixes within 24h | % of bugs fixed within 1 day | > 90% |

### 2.3 Feature Requests

| Field | Definition |
|:------|:-----------|
| Feature ID | `FR-PROD-NNN` |
| Source | User request, self-identified |
| Complexity | **S** (≤50 LOC), **M** (50–200 LOC), **L** (200–500 LOC) |
| Implementation LOC | Lines of AILang written |
| Compile cycles | Number of `ail build` runs until success |
| AI iterations | Number of AI prompt/response cycles if AI-assisted |

**Collection:** Manual entry into `metrics/features.json`:

```json
[
  {
    "id": "FR-PROD-001",
    "date_requested": "2026-07-20",
    "date_delivered": "2026-07-22",
    "complexity": "S",
    "impl_loc": 35,
    "compile_cycles": 2,
    "ai_iterations": 1,
    "description": "Add product search by SKU prefix"
  }
]
```

### 2.4 LOC Growth

| Metric | Collection | Frequency |
|:-------|:-----------|:----------|
| Total production LOC | `count_loc('apps/inventory')` — excludes tests | Weekly |
| Total test LOC | `count_loc('apps/inventory/tests')` | Weekly |
| Total files | `len(list_files('*.ail'))` | Weekly |
| Mean LOC per file | Total LOC / Total files | Weekly |
| Largest file | `max(LOC per file)` | Weekly |

### 2.5 Compile Cycles

| Metric | Definition |
|:-------|:-----------|
| Builds per change | Number of `ail build` runs for a single logical change |
| First-pass success | % of changes that compile on first try |
| Error types | Distribution of error codes (PAR, SEM, TYP, MOD, LEX) |

**Collection:** The `metrics.py` script logs each build attempt to `metrics/builds.json`:

```json
[
  {
    "date": "2026-07-15",
    "change_id": "CHANGE-042",
    "attempt": 1,
    "success": false,
    "error_code": "SEM002",
    "error_message": "Undefined identifier: productList"
  }
]
```

### 2.6 AI Iterations

If AI (Claude, GPT, etc.) is used to write or modify AILang code:

| Metric | Definition |
|:-------|:-----------|
| Prompt count | Number of AI prompts per change |
| First-pass compile | Did the first AI output compile? |
| First-pass correct | Did the first AI output produce correct results? |
| Error types | What did the AI get wrong most often? |

**Collection:** Manual log in `metrics/ai_iterations.json`:

```json
[
  {
    "date": "2026-07-18",
    "change_id": "CHANGE-045",
    "prompts": 2,
    "first_compile": false,
    "errors": ["SEM002: undefined identifier"],
    "first_correct": true
  }
]
```

### 2.7 Build Duration

| Metric | Collection | Frequency |
|:-------|:-----------|:----------|
| Mean build time | `measure_build_time('main.ail')` — 10 samples | Weekly |
| Build time trend | Running 4-week average | Monthly |
| Max build time | Worst build in period | Weekly |

**Target:** Build time < 1 second for the full inventory codebase.

### 2.8 Regressions

| Metric | Definition |
|:-------|:-----------|
| Test count | Total passing tests |
| Regression count | Tests that passed before but fail after a change |
| Regression LOC | LOC changed that caused the regression |
| Regression recovery | Time between regression introduction and fix |

**Collection:** Run full test suite before and after each change:

```
Before:  python tests/test_compile.py  →  38/38 pass
After:   python tests/test_compile.py  →  37/38 pass  ← REGRESSION
```

### 2.9 Rollback Events

| Field | Definition |
|:------|:-----------|
| Rollback ID | `RB-PROD-NNN` |
| Cause | Bug, data loss, performance, user complaint |
| Duration | Minutes between deploy and rollback |
| Data loss | Was data lost? (yes/no) |
| Recovery action | What was needed to recover? |

### 2.10 User Satisfaction

| Metric | Collection | Frequency |
|:-------|:-----------|:----------|
| NPS score | "Would you recommend?" (0–10) | Monthly |
| Friction points | "What frustrated you this month?" | Monthly |
| Missing features | "What do you wish the system did?" | Monthly |
| Crash frequency | "How many times did it crash?" | Monthly |

---

## 3. Monthly Report Template

### Month N (YYYY-MM-DD to YYYY-MM-DD)

#### 3.1 Summary

| Metric | This Month | Previous Month | Change |
|:-------|:----------:|:--------------:|:------:|
| Bugs reported | | | |
| Bugs fixed | | | |
| Mean fix duration | | | |
| Feature requests | | | |
| Features delivered | | | |
| Production LOC | | | |
| Test LOC | | | |
| Build time (mean) | | | |
| Test pass rate | | | |
| Rollbacks | | | |
| User satisfaction | | | |

#### 3.2 Bug Report

```
Total bugs reported:  N
  Critical: N
  Major:    N
  Minor:    N

By origin:
  AILang compiler/runtime: N
  Application logic:       N
  Data corruption:         N

By detection:
  Compile-time:  N
  Test-time:     N
  Runtime:       N

Fix duration:
  Mean:    X.X hours
  Median:  X.X hours
  90th pctile: X.X hours
  % within 24h: X%

Top 3 bugs by impact:
  1. BUG-PROD-NNN — description — severity — fix duration
  2. BUG-PROD-NNN — description — severity — fix duration
  3. BUG-PROD-NNN — description — severity — fix duration
```

#### 3.3 Feature Delivery

```
Total features delivered: N
  Small (≤50 LOC):    N
  Medium (50–200):    N
  Large (200–500):    N

Mean implementation LOC:    XX
Mean compile cycles:        X.X
Mean AI iterations:         X.X  (if AI-assisted)
Mean delivery time:         X.X days

Top 3 features by user value:
  1. FR-PROD-NNN — description
  2. FR-PROD-NNN — description
  3. FR-PROD-NNN — description
```

#### 3.4 Code Health

```
Production LOC:       XXXX  (+/-XX this month)
Test LOC:             XXXX  (+/-XX this month)
Total files:          XX    (+/-X this month)
Mean LOC per file:    XXX
Largest file:         XXX   (filename.ail)
Functions per file:   X.X  (mean)

Compile first-pass rate:   XX%
Most common compile error: XXX (N occurrences)
```

#### 3.5 Performance

```
Build time:
  Mean:     X.XXXs
  Median:   X.XXXs
  Max:      X.XXXs
  vs month 1: +/-X.XXXs

Test suite:
  Tests:    XX/XX passing
  Run time: X.XXs
```

#### 3.6 Incidents

```
Rollbacks:          N
  Duration (mean):  X min
  Data loss:        Yes/No (details)
  Root causes:
    - Cause 1
    - Cause 2

User satisfaction:
  NPS:       X/10
  Crashes:   N
  Friction:  (user quotes)
```

#### 3.7 AILang-Specific Observations

```
Patterns that worked well:
  - Pattern 1
  - Pattern 2

Patterns that caused friction:
  - Pattern 1 (e.g., "recursion made X harder than expected")
  - Pattern 2 (e.g., "eager && caused a bug in Y")

Stdlib gaps discovered:
  - Missing function Z — worked around by...
  - Missing module W — worked around by...

Compiler/runtime issues encountered:
  - Issue 1
  - Issue 2

Unexpected findings:
  - "Surprising benefit of AILang: ..."
  - "Surprising limitation: ..."
```

#### 3.8 Action Items for Next Month

```
Priority 1: ...
Priority 2: ...
Priority 3: ...
```

---

## 4. Monthly Report — Month 1

**Period:** 2026-07-10 to 2026-08-10

### 4.1 Summary

| Metric | Value |
|:-------|:------|
| Bugs reported | TBD |
| Bugs fixed | TBD |
| Mean fix duration | TBD |
| Feature requests | TBD |
| Features delivered | TBD |
| Production LOC | TBD |
| Test LOC | TBD |
| Build time (mean) | TBD |
| Test pass rate | TBD |
| Rollbacks | TBD |
| User satisfaction | TBD |

### 4.2 Bug Report

*To be completed during Month 1.*

### 4.3 Feature Delivery

*To be completed during Month 1.*

### 4.4 Code Health

| Metric | Baseline (Day 0) | Month 1 End |
|:-------|:----------------:|:-----------:|
| Production LOC | 9,543 | TBD |
| Test LOC | ~4,500 | TBD |
| Total files | 80 | TBD |
| Mean LOC/file | ~119 | TBD |
| Largest file | main.ail (351) | TBD |
| New files | — | login.ail, backup.ail, validation.ail, import_csv.ail, integrity.ail |

### 4.5 Performance

| Metric | Baseline | Month 1 End |
|:-------|:--------:|:-----------:|
| Build time (mean) | 0.219s | TBD |
| Test pass rate | 38/38 | TBD |

### 4.6 AILang-Specific Observations

*To be completed during Month 1. Key questions:*

1. Did the auth module (login.ail) require any compiler workarounds?
2. Did the JSON persistence layer need changes for production reliability?
3. Did any AILang limitation block a feature?
4. How many compile cycles per change on average?
5. Were error messages helpful or confusing?

### 4.7 Action Items for Month 2

*To be determined based on Month 1 findings.*

---

## 5. Monthly Report — Month 2

**Period:** 2026-08-10 to 2026-09-10

*Template — to be completed during Month 2.*

### 5.1 Summary

| Metric | Month 1 | Month 2 | Change |
|:-------|:-------:|:-------:|:------:|

### 5.2 AILang-Specific Observations

*Key questions:*
1. Has the bug rate changed from Month 1? (learning curve flattening?)
2. Are new features faster to implement? (codebase familiarity?)
3. Are there recurring compiler friction points?
4. Has code quality improved or degraded?

---

## 6. Monthly Report — Month 3

**Period:** 2026-09-10 to 2026-10-10

*Template — to be completed during Month 3.*

### 6.1 Summary

| Metric | Month 1 | Month 2 | Month 3 | Trend |
|:-------|:-------:|:-------:|:-------:|:-----:|

### 6.2 Final AILang-Specific Observations

*Key questions:*
1. After 3 months, what is the overall impression of AILang for CRUD?
2. What single change would most improve the language for production use?
3. Would you, as the maintainer, choose to continue using AILang?

---

## 7. Decision Framework

### 7.1 Criteria

At the end of Month 3, evaluate the following dimensions:

| Dimension | Weight | Measures | Threshold for YES |
|:----------|:------:|:---------|:-----------------:|
| **Bug Resistance** | 25% | % bugs caught at compile vs runtime; regression rate | > 50% caught at compile; < 5% regression rate |
| **Change Velocity** | 25% | Mean fix duration; feature delivery time | Fixes < 4 hours; S features < 2 days |
| **Code Health** | 20% | LOC growth trend; test coverage; build time trend | LOC stable or declining; tests ≥ 95% pass; build < 1s |
| **Expressiveness** | 15% | Features blocked by language; workaround frequency | < 3 blocked features; workarounds feel natural |
| **User Satisfaction** | 15% | NPS; crash frequency; friction points | NPS ≥ 7; crashes < 1/month; friction ≤ 2 items |

### 7.2 Scoring

| Score | Meaning |
|:-----:|:--------|
| 1 | Strongly negative — would not use AILang again |
| 2 | Negative — would only use with significant changes |
| 3 | Neutral — could go either way |
| 4 | Positive — would use again with minor reservations |
| 5 | Strongly positive — would choose AILang first |

### 7.3 Final Decision Thresholds

| Total Score (weighted) | Decision |
|:----------------------:|:---------|
| 4.0 – 5.0 | ✅ **YES** — Would choose AILang again |
| 3.0 – 3.9 | 🤔 **MAYBE** — Would use again conditionally |
| 1.0 – 2.9 | ❌ **NO** — Would not choose AILang again |

### 7.4 Evidence Requirements

Each dimension must include specific evidence, not general impressions:

**Bug Resistance Evidence:**
- List of all bugs with detection method (compile/test/runtime)
- Count of bugs by detection method
- Specific examples where AILang prevented a bug that Python would not have

**Change Velocity Evidence:**
- Fix duration histogram (how many fixes in each time bucket)
- Feature delivery timeline (request date → delivery date per feature)
- Comparison to Python mirror if maintained

**Code Health Evidence:**
- LOC trend chart (weekly snapshots)
- Test count trend
- Build time trend
- Worst files by LOC

**Expressiveness Evidence:**
- List of features that required workarounds
- List of features that were impossible or abandoned
- Count of "I wish AILang had X" moments
- Comparison: "In Python, this would have been..."

**User Satisfaction Evidence:**
- Raw user quotes (anonymized)
- NPS score and trend
- Feature request backlog size

---

## 8. Collection Tools

### 8.1 Automatic Collection Script

**File:** `apps/inventory/tools/metrics.py` (to be created)

```python
#!/usr/bin/env python3
"""Daily metrics collection for inventory production deployment.

Usage:
    python tools/metrics.py                      # Collect and save
    python tools/metrics.py --report             # Generate report
    python tools/metrics.py --trend              # Show trends

Output:
    metrics/data/YYYY-MM-DD.json                 # Daily snapshot
"""

import json, os, subprocess, sys, time
from datetime import date, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'metrics', 'data')
BUILD_LOG = os.path.join(BASE, 'metrics', 'builds.json')
BUG_FILE = os.path.join(BASE, 'metrics', 'bugs.json')
FEATURE_FILE = os.path.join(BASE, 'metrics', 'features.json')

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)

def count_loc(path):
    """Count lines of AILang code recursively."""
    total = 0
    file_counts = {}
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.ail'):
                fp = os.path.join(root, f)
                with open(fp) as fh:
                    lines = len(fh.readlines())
                total += lines
                file_counts[f] = lines
    return total, file_counts

def count_tests(path):
    """Count test functions (fn test_*) in tests directory."""
    count = 0
    test_dir = os.path.join(path, 'tests')
    if not os.path.exists(test_dir):
        return 0
    for root, dirs, files in os.walk(test_dir):
        for f in files:
            if f.endswith('.ail'):
                fp = os.path.join(root, f)
                with open(fp) as fh:
                    for line in fh:
                        stripped = line.strip()
                        if stripped.startswith('fn test_') and stripped.endswith('{'):
                            count += 1
    return count

def measure_build(path):
    """Time `ail build` and capture result."""
    main_file = os.path.join(path, 'main.ail')
    if not os.path.exists(main_file):
        return {'success': False, 'duration_seconds': 0, 'error': 'main.ail not found'}
    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'compiler.cli.main', 'build', main_file],
            capture_output=True, text=True, timeout=60
        )
        duration = time.time() - start
        return {
            'success': result.returncode == 0,
            'duration_seconds': round(duration, 3),
            'stderr': result.stderr[:1000] if result.stderr else '',
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'duration_seconds': 60.0, 'error': 'timeout'}
    except Exception as e:
        return {'success': False, 'duration_seconds': 0, 'error': str(e)}

def collect_snapshot():
    """Collect all automatic metrics for today."""
    today = date.today().isoformat()
    prod_loc, prod_files = count_loc(BASE)
    test_loc, _ = count_loc(os.path.join(BASE, 'tests'))
    test_fn_count = count_tests(BASE)
    build = measure_build(BASE)
    
    snapshot = {
        'date': today,
        'production_loc': prod_loc,
        'production_files': len(prod_files),
        'largest_file': max(prod_files.items(), key=lambda x: x[1]) if prod_files else ('', 0),
        'test_loc': test_loc,
        'test_functions': test_fn_count,
        'build_success': build['success'],
        'build_duration_seconds': build['duration_seconds'],
        'build_error': build.get('error', build.get('stderr', '')),
        'collected_at': datetime.now().isoformat()
    }
    
    # Save
    with open(os.path.join(DATA_DIR, today + '.json'), 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    return snapshot

def load_bugs():
    if os.path.exists(BUG_FILE):
        with open(BUG_FILE) as f:
            return json.load(f)
    return []

def load_features():
    if os.path.exists(FEATURE_FILE):
        with open(FEATURE_FILE) as f:
            return json.load(f)
    return []

def generate_report():
    """Generate a summary from all collected data."""
    # Load all daily snapshots
    snapshots = []
    for f in sorted(os.listdir(DATA_DIR)):
        if f.endswith('.json'):
            with open(os.path.join(DATA_DIR, f)) as fh:
                snapshots.append(json.load(fh))
    
    bugs = load_bugs()
    features = load_features()
    
    report = {
        'period': {
            'start': snapshots[0]['date'] if snapshots else 'N/A',
            'end': snapshots[-1]['date'] if snapshots else 'N/A',
        },
        'snapshots': len(snapshots),
        'latest': snapshots[-1] if snapshots else {},
        'bugs': {
            'total': len(bugs),
            'open': len([b for b in bugs if b.get('date_fixed') is None]),
            'fixed': len([b for b in bugs if b.get('date_fixed')]),
            'critical': len([b for b in bugs if b.get('severity') == 'critical']),
            'major': len([b for b in bugs if b.get('severity') == 'major']),
            'minor': len([b for b in bugs if b.get('severity') == 'minor']),
            'avg_fix_hours': _avg_fix_hours(bugs),
        },
        'features': {
            'total': len(features),
            'delivered': len([f for f in features if f.get('date_delivered')]),
            'total_loc': sum(f.get('impl_loc', 0) for f in features if f.get('impl_loc')),
            'avg_compile_cycles': _avg_compile_cycles(features),
        },
    }
    
    return report

def _avg_fix_hours(bugs):
    fixed = [b for b in bugs if b.get('fix_duration_hours') is not None]
    if not fixed:
        return 0
    return round(sum(b['fix_duration_hours'] for b in fixed) / len(fixed), 1)

def _avg_compile_cycles(features):
    with_cycles = [f for f in features if f.get('compile_cycles') is not None]
    if not with_cycles:
        return 0
    return round(sum(f['compile_cycles'] for f in with_cycles) / len(with_cycles), 1)

if __name__ == '__main__':
    ensure_dirs()
    if '--report' in sys.argv:
        report = generate_report()
        print(json.dumps(report, indent=2))
    elif '--trend' in sys.argv:
        snapshots = []
        for f in sorted(os.listdir(DATA_DIR)):
            if f.endswith('.json'):
                with open(os.path.join(DATA_DIR, f)) as fh:
                    snapshots.append(json.load(fh))
        print(f"{'Date':<15} {'Prod LOC':<10} {'Build (s)':<10} {'Tests':<8}")
        print('-' * 45)
        for s in snapshots:
            print(f"{s['date']:<15} {s['production_loc']:<10} {s['build_duration_seconds']:<10} {s['test_functions']:<8}")
    else:
        snapshot = collect_snapshot()
        print(f"Collected metrics for {snapshot['date']}")
        print(f"  Production LOC: {snapshot['production_loc']}")
        print(f"  Build duration: {snapshot['build_duration_seconds']}s")
        print(f"  Test functions: {snapshot['test_functions']}")
```

### 8.2 Manual Logs

**Bug log:** `metrics/bugs.json`
**Feature log:** `metrics/features.json`
**Build log:** `metrics/builds.json`
**AI iteration log:** `metrics/ai_iterations.json`
**Incident log:** `metrics/incidents.json`

### 8.3 Collection Schedule

| What | When | Who |
|:-----|:-----|:----|
| Run `python tools/metrics.py` | Every Monday 09:00 | Cron / manual |
| Log new bugs | Within 1 hour of report | Maintainer |
| Log new features | Within 1 day of request | Maintainer |
| Log build attempts | Automatic via wrapper | tools/metrics.py |
| Log AI iterations | Per AI session | Maintainer |
| User satisfaction survey | Last day of month | Maintainer interviews user |

---

## 9. Expected Baselines

### Pre-Production Baseline (Day 0 — 2026-07-10)

| Metric | Baseline |
|:-------|:--------:|
| Production LOC | 9,543 |
| Test LOC | ~4,500 |
| Total files | 80 |
| Largest file | main.ail (351 LOC) |
| Build time | 0.219s |
| Test pass rate | 38/38 |
| Test functions | ~200 |
| Compile first-pass rate | Unknown (benchmark data suggests ~80%) |

### End-of-Month 3 Targets

| Metric | Target | Stretch Target |
|:-------|:------:|:--------------:|
| Production LOC | < 12,000 | < 11,000 |
| Build time | < 0.5s | < 0.3s |
| Bug fix mean duration | < 4 hours | < 2 hours |
| Compile first-pass rate | > 80% | > 90% |
| Test pass rate | 100% | 100% |
| Rollbacks | < 3 | 0 |
| User NPS | ≥ 7 | ≥ 8 |
| Features blocked by AILang | < 3 | 0 |

---

## 10. Decision Worksheet

To be completed at end of Month 3 (2026-10-10).

### Dimension 1: Bug Resistance (Weight: 25%)

| Measure | Value | Score (1–5) |
|:--------|:-----:|:-----------:|
| % bugs caught at compile time | % | /5 |
| % bugs caught at test time | % | /5 |
| % bugs found at runtime | % | /5 |
| Regression rate | % | /5 |
| **Dimension score** | **Weighted avg** | **/5** |

### Dimension 2: Change Velocity (Weight: 25%)

| Measure | Value | Score (1–5) |
|:--------|:-----:|:-----------:|
| Mean fix duration | hours | /5 |
| Mean S feature delivery | days | /5 |
| Mean M feature delivery | days | /5 |
| Compile cycles per change | N | /5 |
| **Dimension score** | **Weighted avg** | **/5** |

### Dimension 3: Code Health (Weight: 20%)

| Measure | Value | Score (1–5) |
|:--------|:-----:|:-----------:|
| LOC growth rate (weekly) | % | /5 |
| Build time trend | seconds (trend) | /5 |
| Test pass rate | % | /5 |
| Largest file trend | LOC (trend) | /5 |
| **Dimension score** | **Weighted avg** | **/5** |

### Dimension 4: Expressiveness (Weight: 15%)

| Measure | Value | Score (1–5) |
|:--------|:-----:|:-----------:|
| Features impossible to implement | N | /5 |
| Workarounds per feature | N | /5 |
| "I wish AILang had X" moments | N | /5 |
| Python comparison delta | % more LOC | /5 |
| **Dimension score** | **Weighted avg** | **/5** |

### Dimension 5: User Satisfaction (Weight: 15%)

| Measure | Value | Score (1–5) |
|:--------|:-----:|:-----------:|
| NPS score | /10 | /5 |
| Crash frequency | N/month | /5 |
| Friction items | N | /5 |
| "Would you recommend?" | yes/no | /5 |
| **Dimension score** | **Weighted avg** | **/5** |

### Final Score

| Dimension | Score | Weight | Weighted |
|:----------|:----:|:------:|:--------:|
| Bug Resistance | /5 | 25% | |
| Change Velocity | /5 | 25% | |
| Code Health | /5 | 20% | |
| Expressiveness | /5 | 15% | |
| User Satisfaction | /5 | 15% | |
| **Total** | | **100%** | **/5** |

### Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  FINAL DECISION:                                             ║
║                                                              ║
║  Score: X.X / 5.0                                            ║
║                                                              ║
║  Decision: YES / MAYBE / NO                                  ║
║                                                              ║
║  Evidence Summary:                                           ║
║  -                                                           ║
║  -                                                           ║
║  -                                                           ║
║                                                              ║
║  Key Factors:                                                ║
║  1.                                                          ║
║  2.                                                          ║
║  3.                                                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 11. Quick Reference Card

### Daily (2 min)

```
□ Check for user issues
□ Log any bugs in metrics/bugs.json
```

### Weekly (5 min)

```
□ Run: python tools/metrics.py          (auto-collect)
□ Review: python tools/metrics.py --trend (trend check)
□ Log any feature requests received this week
```

### Monthly (15 min)

```
□ Run: python tools/metrics.py --report  (generate report)
□ Complete the monthly report section above
□ Interview user for satisfaction
□ Review action items from previous month
□ Set action items for next month
```

### End of Quarter (30 min)

```
□ Compile all 3 monthly reports
□ Complete the Decision Worksheet (§10)
□ Document final decision with evidence
□ Publish findings
```

---

## 12. Appendix: JSON Schemas

### Bug Entry (`bugs.json`)

```json
{
  "id": "BUG-PROD-NNN",
  "date_reported": "2026-07-15",
  "date_fixed": "2026-07-15",
  "severity": "critical|major|minor",
  "origin": "compiler|logic|data",
  "detection": "compile|test|runtime",
  "description": "Brief description",
  "fix_duration_hours": 0.5,
  "fix_loc": 3,
  "fix_files": ["file1.ail"],
  "root_cause": "Explanation",
  "preventable_by_ailang": false
}
```

### Feature Entry (`features.json`)

```json
{
  "id": "FR-PROD-NNN",
  "date_requested": "2026-07-20",
  "date_delivered": "2026-07-22",
  "complexity": "S|M|L",
  "impl_loc": 35,
  "compile_cycles": 2,
  "ai_iterations": 1,
  "description": "Brief description",
  "blocked_by_ailang": false,
  "workaround_notes": ""
}
```

### Build Entry (`builds.json`)

```json
{
  "date": "2026-07-15",
  "change_id": "CHANGE-NNN",
  "attempt": 1,
  "success": false,
  "error_code": "SEM002",
  "error_message": "Undefined identifier: productList"
}
```

### Incident Entry (`incidents.json`)

```json
{
  "id": "INC-PROD-NNN",
  "date": "2026-07-20",
  "type": "rollback|crash|data_loss|performance",
  "duration_minutes": 15,
  "root_cause": "Explanation",
  "data_lost": false,
  "user_impacted": true,
  "resolution": "Restored from backup"
}
```
