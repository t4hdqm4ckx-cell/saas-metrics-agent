# BUG_REPORTING.md — FlowSync SaaS Metrics Agent

## Overview
This document defines the process for identifying, reporting, triaging, and resolving bugs in the FlowSync SaaS Metrics Agent. All team members are expected to follow this workflow.

---

## Bug Report Template

When filing a GitHub Issue, use the following template (also available as `.github/ISSUE_TEMPLATE/bug_report.md`):

```markdown
## Bug Report

**Summary**: One-line description of the problem

**Severity**: [ ] Critical  [ ] High  [ ] Medium  [ ] Low

**Component**: [ ] Data Generator  [ ] Metrics Calculator  [ ] Dashboard  [ ] Agent Orchestration  [ ] Docs

---

### Environment
- OS: 
- Python version (if agent):
- Browser (if dashboard):
- Data file date: (check `data/synthetic_data.json` → `generated_at` field)

### Steps to Reproduce
1. 
2. 
3. 

### Expected Behavior


### Actual Behavior


### Screenshots / Logs
(Paste relevant lines from `logs/app.log` or browser console)

### Possible Root Cause
(Optional — your hypothesis)

### Workaround Available?
[ ] Yes — describe:  [ ] No
```

---

## Triage Process

### Step 1 — Report
- File a GitHub Issue with the bug template above
- Add labels: `bug` + severity label (`critical`, `high`, `medium`, `low`)
- Assign to the component owner if known

### Step 2 — Triage (within SLA)

| Severity | Triage SLA | Fix SLA |
|----------|-----------|---------|
| Critical | 1 hour | Same day |
| High | 4 hours | 2 business days |
| Medium | 1 business day | 1 sprint |
| Low | 1 week | Backlog |

### Step 3 — Reproduce
- Assignee must confirm reproduction before starting fix
- If cannot reproduce: request more info from reporter, add `needs-info` label
- If intermittent: add `flaky` label, instrument extra logging

### Step 4 — Fix
- Branch naming: `fix/short-description` (e.g., `fix/nrr-zero-division`)
- Reference issue in commit: `fix: prevent zero-division in NRR calc (closes #42)`
- Include regression test covering the bug scenario
- Update ERROR_HANDLING.md if a new error code is needed

### Step 5 — Verify
- PR must include reproduction steps in description
- At least one reviewer must confirm fix locally
- CI must pass (linting + tests)

### Step 6 — Close
- Merge to `main`
- Close issue with a comment linking to the merged PR
- Add entry to VERSION_CONTROL.md

---

## Bug Severity Definitions

### Critical
- Dashboard fails to load entirely
- Data generation produces corrupted JSON
- Metrics display values that are off by > 20% from expected
- Any security vulnerability (see SECURITY.md for handling)

### High
- A full dashboard tab fails to render
- Charts display incorrect data for specific months
- Agent crashes mid-run and produces partial output
- MRR/ARR values are inconsistent across views

### Medium
- A single chart fails to render (others work)
- Filter or tab navigation is broken
- Tooltip shows wrong values
- Exported executive deck has formatting issues

### Low
- Minor visual glitches (clipping, overflow)
- Hover effects not working in specific browser
- Typo in chart label or axis
- Console warnings (not errors)

---

## Known Issues & Workarounds

| Issue | Status | Workaround |
|-------|--------|------------|
| Safari: gradient fills in area charts may appear washed out | Open | Use Chrome/Firefox for best rendering |
| Very large monitors (> 2560px): KPI card grid may overflow | Open | Use browser zoom 90% |
| Firefox: cohort heatmap tooltip positioning off by 8px | In Progress | No workaround needed; visual only |

---

## Regression Testing Policy

- Every merged bug fix MUST include a test that would have caught the bug
- Dashboard bugs may use visual regression screenshots stored in `tests/snapshots/`
- Python bugs must have a `pytest` test in `tests/` mirroring the reproduction steps

---

## Security Bugs

**Do not file security vulnerabilities as public GitHub Issues.**

Instead, follow the process in [SECURITY.md](SECURITY.md) — report privately via GitHub's security advisory feature or email the address in SECURITY.md.

---

## Bug Metrics (tracked monthly)

| Metric | Target |
|--------|--------|
| Mean time to triage (MTTT) | < 4 hours (critical/high) |
| Mean time to resolution (MTTR) | < 2 days (critical/high) |
| Bug escape rate (found in prod vs dev) | < 15% |
| Open critical/high bugs | 0 at any time |

---

*Last updated: 2026-06-01 | Owner: Engineering Lead*
