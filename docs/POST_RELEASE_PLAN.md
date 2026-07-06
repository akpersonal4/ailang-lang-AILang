# Post-Release Plan

**Date:** 2026-07-05  
**Version:** v0.1.1 → v0.2.0  

---

## v0.1.2 Bug-Fix Policy

**v0.1.x releases are patch-only.** No new features, no breaking changes, no stdlib additions.

| Change Type | Allowed | Process |
|-------------|---------|---------|
| Compiler crash fixes | ✅ | Direct merge after quality gates |
| Runtime crash fixes | ✅ | Direct merge after quality gates |
| Incorrect output fixes | ✅ | Direct merge after quality gates |
| Diagnostic improvements | ✅ | Direct merge after quality gates |
| Documentation fixes | ✅ | Direct merge |
| New stdlib functions | ❌ | Deferred to v0.2.0 |
| Language features | ❌ | Deferred to v0.2.0 |
| Breaking changes | ❌ | Never in patch releases |

**Bug reporting:** All bugs must include an AILang program demonstrating the defect. See `GOVERNANCE.md` for the defect reporting process.

---

## v0.2 Roadmap

### Prerequisites for v0.2.0

Before any v0.2.0 planning, the following must be satisfied:

1. **v0.1.1 release complete**
2. **Community feedback collected** (minimum 3 months of real-world usage)
3. **Evidence gathered** (minimum 3 independent applications requesting each new feature)
4. **Governance review** completed

### Potential Enhancements (Evidence-Driven)

Any v0.2.0 changes must follow the evidence bar in `GOVERNANCE.md`:

| Feature Category | Evidence Required | Current Candidates |
|------------------|-------------------|-------------------|
| Language features | ≥3 apps demonstrating necessity | None (language frozen) |
| Stdlib additions | ≥2 apps or documented gap | `list.iter`, `list.sum`, `list.find` |
| Tooling | Project lead discretion | LSP, REPL, PyPI package |

---

## Benchmark Schedule

### Quarterly Benchmark Requirements

| Quarter | Focus | Requirements |
|---------|-------|--------------|
| Q3 2025 | Baseline | Document v0.1.1 performance (compile time, memory, determinism) |
| Q4 2025 | Monitoring | Confirm no regressions, collect application metrics |
| Q1 2026 | Validation | Analyze real-world applications, measure API usage |
| Q2 2026 | Planning | Feed into v0.2.0 evidence requirements |

### Metrics to Track

- Compile time for 100/500/1000/5000 LOC
- Peak memory usage for large programs
- IR determinism (SHA-256 hash verification)
- Application count and complexity
- Stdlib function usage frequency

---

## Community Feedback Process

### Feedback Channels

| Channel | Purpose | Response Time |
|---------|---------|---------------|
| GitHub Issues | Bug reports, feature requests | 7 days |
| GitHub Discussions | General feedback, questions | 14 days |
| Documentation site comments | Doc clarifications | 7 days |

### Feedback Requirements

All feedback must follow `GOVERNANCE.md`:

1. **Bug reports** — Include failing program and expected output
2. **Feature requests** — Include ≥3 applications that need the feature
3. **Stdlib requests** — Include ≥2 applications or documented gap

### Evidence Collection

All valid feedback is recorded in `docs/LANGUAGE_EVOLUTION.md` with:
- Feature description
- Requesting application(s)
- Evidence status (pending/approved/rejected)
- Target version (if approved)

---

## Governance Review Schedule

### Monthly Reviews

| Month | Review Item | Outcome |
|-------|-------------|---------|
| August 2025 | Feedback analysis | Update LANGUAGE_EVOLUTION.md |
| September 2025 | Evidence assessment | Mark features as ready/not ready |
| October 2025 | Phase 12 completion | Declare v0.1.1 fully stable |

### Quarterly Governance Updates

| Quarter | Item | Action |
|---------|------|--------|
| Q3 2025 | Process effectiveness | Review GOVERNANCE.md, propose improvements |
| Q1 2026 | v0.2.0 preparation | Evidence review, feature prioritization |

---

## Release Cadence

### Standard Cadence

| Release Type | Cadence | Trigger |
|--------------|---------|---------|
| Patch (0.1.x) | As needed | Bug fixes only |
| Minor (0.x.0) | Every 6-12 months | Evidence-based improvements, tool additions |
| Major (x.0.0) | Years | Breaking changes only |

### Current Schedule

- **v0.1.2** — Bug fixes only, as needed
- **v0.1.3** — Bug fixes only, as needed
- **v0.2.0** — Evidence-driven improvements (target: Q2 2026)

---

## Deprecation Policy

### Current Status (v0.1.x)

No deprecations planned. The language is frozen.

### Post-1.0 Policy

After v1.0.0:

1. **Deprecation announced** in minor release with warning diagnostic
2. **Migration guide** provided in documentation
3. **Deprecated feature remains** for one major version cycle
4. **Removal** in subsequent major release

### Deprecation Procedure

```
v1.1.0: Deprecation warning added
v1.2.0: Warning refined, migration guide published
v2.0.0: Deprecated feature removed
```

---

## Summary

This document bridges v0.1.1 (first public release) to v0.2.0 (evidence-based improvements). Development remains disciplined through:

- **Specification-first** approach maintained
- **Evidence-driven** feature planning
- **Quarterly benchmarking** for performance stability
- **Community feedback** with structured evidence requirements
- **Regular governance** review and updates

All changes feed into `docs/LANGUAGE_EVOLUTION.md` for permanent record.