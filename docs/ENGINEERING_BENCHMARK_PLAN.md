# Engineering Benchmark Plan

> **Purpose:** Define the methodology for provably and repeatably measuring
> AILang's engineering health. This document covers both the benchmark program
> (answering "does AILang reduce the cost of software engineering?") and the
> broader Engineering Validation Framework (answering "is AILang healthy as a
> project?").
>
> This document defines methodology only. Implementation is deferred until a
> dedicated benchmarking module exists.

---

## Guiding Principles

| Principle | Meaning |
|-----------|---------|
| Repeatable | Same input → same result on any machine at any time |
| Comparable | AILang benchmarked against at least one other language (Python as default baseline) |
| Quantitative | Every benchmark produces at least one number (time, tokens, iterations, errors) |
| Transparent | All inputs, outputs, and methodology published with results |
| Fair | Same task, same level of implementation complexity, same AI model |
| Minimal | Benchmark the smallest meaningful action — don't conflate metrics |

**Baseline language:** Python 3.x (most widely known, no compile step).
Additional baselines may be added (Rust, TypeScript, Go) if resources permit.

**AI models:** Each benchmark must be run with a minimum of 3 models (one
from each tier). Results must be reported per-model and aggregated.
- Tier 1: Claude (Anthropic)
- Tier 2: GPT (OpenAI)
- Tier 3: DeepSeek or Llama (open-weight)

---

## Benchmark 1: AI Understanding Benchmark

**Question:** How many tokens does an AI need to understand an AILang project
vs an equivalent project in Python?

**Methodology:**
1. Create equivalent implementations of 10 tasks in both AILang and Python.
2. For each task, construct an AI prompt that includes the full project source.
3. Count token consumption using the target model's tokenizer.
4. Ask a factual comprehension question about the code.
5. Measure:
   - Total tokens in prompt (source + instructions)
   - Comprehension accuracy (correct / incorrect / ambiguous)
   - Token ratio (AILang / Python)
   - Minimum context window required

**Success Criteria:**
- AILang requires ≤80% of Python's tokens for equivalent comprehension
- Comprehension accuracy ≥90% for both languages (no degradation)

**Controls:**
- Same AI model for both implementations
- Same comprehension question
- Same prompt structure (only source language differs)

---

## Benchmark 2: Feature Implementation Benchmark

**Question:** How many iterations (and tokens) does it take an AI to implement
a feature correctly from a spec, comparing AILang vs Python?

**Methodology:**
1. Define 10 features of varying complexity (L1: 1 function, ≤20 LOC; L2: 3-5
   functions, ≤100 LOC; L3: multiple files, ≤300 LOC).
2. Generate a specification for each feature (natural language, no code).
3. Feed the spec to an AI, asking it to produce an implementation.
4. For each attempt:
   - Record pass/fail on compile (AILang) or syntax-check (Python)
   - Record pass/fail on test suite
   - Record number of iterations until correct
   - Record total tokens consumed
   - Record total time
5. Report: mean iterations to correct, mean tokens, median time

**Success Criteria:**
- AILang requires fewer iterations to first compile than Python requires to
  first syntax-check-free run
- AILang requires ≤80% of Python's total token consumption to reach correct
  implementation

**Controls:**
- Same spec for both languages
- Same test suite (equivalent assertions, same edge cases)
- Same AI model with same temperature settings
- No few-shot examples in the prompt

---

## Benchmark 3: Bug Fix Benchmark

**Question:** How many iterations does it take an AI to fix a known bug,
comparing AILang vs Python?

**Methodology:**
1. Take 10 programs (5 AILang, 5 Python equivalence pairs) and introduce
   known bugs: off-by-one, undefined identifier, type mismatch (Python only),
   missing guard, infinite recursion guard.
2. For each buggy program, provide:
   - Source code
   - Error message or incorrect output
   - Expected behaviour (one sentence)
3. Ask AI to produce a fix.
4. Measure:
   - Number of fix attempts until correct
   - Whether first fix compiles (AILang) or parses (Python)
   - Whether first fix passes the test suite
   - Total tokens consumed

**Success Criteria:**
- AILang first-fix compile rate ≥ 80%
- AILang requires fewer fix iterations than Python (mean)
- No infinite-loop bugs in AILang fixes (structural guarantee against this
  class of bug)

**Controls:**
- Same bug categories across languages (where applicable)
- Same error reporting format
- Same AI model

---

## Benchmark 4: Refactoring Benchmark

**Question:** When asked to refactor a known codebase, does an AI introduce
fewer regressions in AILang vs Python?

**Methodology:**
1. Take 5 programs (1 each: small/medium/large) and define a refactoring task
   for each (rename, extract function, change data structure, reorder).
2. Ask AI to perform the refactoring without changing behaviour.
3. Measure:
   - Number of semantic regressions introduced (test failures)
   - Compile errors introduced
   - Time to produce correct refactoring
   - AI confidence score (if available)

**Success Criteria:**
- AILang refactors introduce fewer regressions than Python equivalents
  (statistically significant over 10 trials)
- AILang has zero compile errors after refactoring (structural guarantee)

**Controls:**
- Same refactoring task, same code equivalence
- Same AI model
- Same test suite
- Tool-assisted refactoring not permitted (manual AI generation only)

---

## Benchmark 5: Upgrade Benchmark

**Question:** When upgrading dependencies (stdlib functions, language
features), does AILang's integrated platform reduce the cost compared to
Python's ecosystem?

**Methodology:**
1. Define scenarios:
   - Major upgrade: breaking change in a stdlib function
   - Minor upgrade: new parameter added with default
   - Deprecation: function renamed but old name still works
2. For each scenario:
   - Upgrade the codebase
   - Measure: files changed, LOC changed, compile errors before fix,
     iterations to resolve, total tokens consumed
3. Repeat for AILang (stdlib version bump) and Python (PyPI package upgrade)

**Success Criteria:**
- AILang upgrades involve fewer files changed (mean) than Python equivalents
- AILang upgrades require fewer iterations to resolve compile errors
- No broken builds after AILang upgrade (all tests pass)

**Controls:**
- Same upgrade scope (same number of affected symbols)
- Same test suite
- Breaking changes of equivalent severity

---

## Benchmark 6: Maintenance Benchmark

**Question:** Over a simulated maintenance period (adding features + fixing
bugs + refactoring), does AILang exhibit lower cumulative cost than Python?

**Methodology:**
1. Create a medium-sized project in both AILang and Python (~500 LOC, 5-8
   files, 5+ functions, data structures, file I/O, control flow).
2. Simulate a 6-month maintenance cycle:
   - Month 1-2: Add 3 features
   - Month 3-4: Fix 5 bugs (introduced after features)
   - Month 5-6: Refactor 2 modules
3. For each operation, record:
   - AI iterations to correct
   - Tokens consumed
   - Human review time (if available)
   - Test regressions introduced
4. Report cumulative metrics:
   - Total AI cost (tokens × rate)
   - Total iterations
   - Total regressions
   - Final code quality metrics (LOC, cyclomatic complexity proxy)

**Success Criteria:**
- AILang cumulative AI iterations ≤ 60% of Python
- AILang cumulative test regressions ≤ 50% of Python
- AILang code compiles after every operation (no broken intermediate states)

**Controls:**
- Same maintenance schedule
- Same features, bugs, and refactoring tasks
- Same AI model throughout
- No human intervention beyond triggering the AI

---

## Benchmark 7: AI Context Benchmark

**Question:** Does providing structured AILang context (dependency graph,
type information, spec references) improve the quality of AI-generated code
compared to plain source?

**Methodology:**
1. Define 10 code-generation tasks.
2. For each task, run with two context types:
   - **Context A:** Plain source files only
   - **Context B:** Source files + AILang structured context (generated by
     the platform's context-generator tool, future)
3. Measure:
   - First-attempt compile rate
   - First-attempt test pass rate
   - Iterations to correct
   - Token consumption (context + generation)
   - Quality score (1-5, defined rubric: spec compliance, correctness,
     style, edge case handling)
4. Report: does context B outperform context A?

**Success Criteria:**
- Context B improves first-attempt compile rate by ≥20 percentage points
  over Context A
- Context B reduces iterations to correct by ≥30% over Context A
- Effect consistent across ≥2 AI models

**Controls:**
- Same task, same model, same temperature
- Context B must be generated automatically (no human curation)
- Context B must add ≤25% overhead to total token count

---

## Reporting Format

Every benchmark run must produce a report containing:

```
## Benchmark: <Name>
Date: YYYY-MM-DD
Run by: <entity>
AI Model: <model name> @ <version>
Baseline: Python 3.<x>

### Results
| Metric | AILang | Python | Ratio |
|--------|--------|--------|-------|
| Mean iterations | X | Y | X/Y |

### Raw Data
Link to CSV or structured data file.

### Observations
- Qualitative notes about surprising findings

### Threats to Validity
- What might make this measurement misleading?
```

---

## Phased Rollout

| Phase | Benchmarks | Prerequisites |
|-------|-----------|---------------|
| 1 | AI Understanding (B1) | Tokenizer integration, 10 equivalent programs |
| 2 | Feature Implementation (B2), Bug Fix (B3) | Test framework, AI harness |
| 3 | Refactoring (B4), Upgrade (B5) | Multi-file codebase support |
| 4 | Maintenance (B6) | Continuous benchmark runner |
| 5 | AI Context (B7) | Context generator tool |

---

## Future: Engineering Validation Framework

The benchmark program (B1–B7 above) is one component of a broader Engineering
Validation Framework. The framework produces four independent reports that
collectively assess overall project health.

### Four Validation Reports

| Report | Scope | Measures |
|--------|-------|----------|
| **Product Validation** | Correctness and functionality | Test pass rate, compile success rate, regression count |
| **Architecture Compliance** | Implementation follows intended design | ADR adherence, module boundaries, dependency direction |
| **Governance & Documentation Compliance** | Canonical documents, ownership, workflow consistency | Canonical First rule adherence, cross-reference freshness, drift detection |
| **Vision Validation** | Progress toward stated mission, using benchmark evidence | Benchmark coverage (% of planned), hypothesis status (confirmed/refuted/unmeasured) |

### Future `ail validate` Command

When implemented, this command would run all four validations and produce a
single engineering health report:

```
AILang Engineering Validation Report

Product Quality .................. PASS
Architecture Compliance ......... PASS
Documentation Consistency ....... PASS
Governance Compliance ........... PASS
Benchmark Coverage .............. PASS
Vision Progress ................. 68%

Overall Engineering Health ...... A
```

### Relationship to This Document

| Component | Coverage |
|-----------|----------|
| **Benchmark methodology (B1–B7)** | Fully defined in this document, awaiting execution |
| **Product Validation** | Automated by existing test suite; framework standardizes reporting |
| **Architecture Compliance** | Not yet designed — requires ADR audit tooling |
| **Governance & Documentation Compliance** | Automated by M19 canonicalization; drift detection not yet designed |
| **Vision Validation** | Reuses B1–B7 results mapped to hypotheses in `VISION_AND_DIFFERENTIATION.md` |

**Priority:** Complete benchmark execution (B1–B7) before designing the remaining
validation reports. The framework should be built on proven measurement
infrastructure, not designed in advance of it.

---

## Threat Model

| Threat | Mitigation |
|--------|------------|
| AI model improvement over time skews results | Pin model version per benchmark |
| Prompt engineering skill differences | Use a fixed prompt template per benchmark |
| AILang implementing fewer features (advantage by omission) | Benchmark only features implementable in both languages |
| Human bias in task selection | Publish task specs before results |
| Small sample size | Minimum 10 trials per metric |
| Learning effect (AI sees the same problem twice) | Generate unique but equivalent tasks for each trial |

---

## Related Documents

- [Vision and Differentiation](governance/VISION_AND_DIFFERENTIATION.md) — What must be proven
- [AI Benchmark Matrix](benchmarks/AI_BENCHMARK_MATRIX.md) — Existing AI-generation results
- [AI Benchmark Whitepaper](benchmarks/AILANG_BENCHMARK_WHITEPAPER.md) — Benchmark results and analysis
- [Inventory Scalability Benchmark](benchmarks/INVENTORY_SCALABILITY_BENCHMARK.md) — 8,515 LOC AILang inventory system
- [Inventory Python Comparison](benchmarks/INVENTORY_PYTHON_COMPARISON.md) — Empirical AILang vs Python head-to-head
- [Inventory Benchmark Harness](benchmarks/INVENTORY_BENCHMARK_HARNESS.md) — B2–B6 execution protocol (exact prompts, models, stopping conditions)
- [Constitution](governance/PROJECT_CONSTITUTION.md) — Immutable design rules
