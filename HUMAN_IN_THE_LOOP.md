# Human-in-the-Loop Policy — FlowSync SaaS Metrics Agent

## Purpose

This document defines where human oversight is required in the FlowSync SaaS Metrics Agent pipeline, what decisions must not be made autonomously, and how to escalate or override automated outputs.

---

## Scope

This policy applies to:
- The data generation agent (`agent/agent.py` and related modules)
- The alerting engine (`agent/alerter.py`)
- The forecasting module (`agent/forecaster.py`)
- Any future automation built on top of this codebase

---

## Decision Authority Matrix

| Decision | Can Agent Act Alone? | Human Required? | Escalation Path |
|----------|---------------------|-----------------|-----------------|
| Regenerate synthetic data (same seed) | ✅ Yes | No | — |
| Change RNG seed (produces different data) | ⚠️ With notice | Review output | Data owner |
| Modify alert thresholds | ❌ No | Yes — always | Analytics lead |
| Suppress or silence a CRITICAL alert | ❌ No | Yes — always | On-call + CEO |
| Publish or share generated data externally | ❌ No | Yes — always | Legal + data owner |
| Deploy dashboard to a live URL | ❌ No | Yes — always | Engineering lead |
| Add new metric definitions or KPI formulas | ❌ No | Yes — review | Analytics lead |
| Interpret forecasts as financial projections | ❌ No | Yes — always | CFO / leadership |
| Send alert notifications to external channels | ❌ No | Yes in v1.0 | On-call engineer |

---

## CRITICAL: What This Agent Must Never Do Autonomously

1. **Act on forecasts** — Forecasts from `forecaster.py` are informational only. No business, financial, or operational decision should be made based solely on agent output without human review.

2. **Silence alerts** — A CRITICAL or HIGH alert must never be suppressed without explicit human sign-off from the metric owner and Engineering Lead.

3. **Modify production data contracts** — Schema changes to `synthetic_data.json` require human review of all downstream consumers (dashboard, deck, tests) before merging.

4. **Publish or distribute data** — Even though all data is synthetic, any external publication (blog, API, shared link) requires a human to confirm the data contains no inadvertently real information.

5. **Make hiring, pricing, or strategic decisions** — Agent outputs (churn forecasts, LTV projections, growth rates) are analytical inputs. All resulting business decisions require human judgment.

---

## Alert Escalation Protocol

When `alerter.py` fires an alert:

```
CRITICAL alert fired
    → Immediate human review required
    → Do not auto-remediate
    → Notify: on-call engineer + CEO
    → Acknowledge within 5 minutes
    → Document in AUDIT.md

HIGH alert fired
    → Human review within 15 minutes
    → Notify: team lead + metric owner
    → Acknowledge before any automated response

MEDIUM alert fired
    → Human review within 24 hours
    → Log in GitHub Issues
    → No automated action

LOW alert fired
    → Log only
    → Human reviews at next standup
```

---

## Forecast Disclaimer

All outputs from `agent/forecaster.py` carry the following implicit disclaimer:

> *These projections are based entirely on synthetic data generated with a fixed random seed. They do not represent real business performance, are not suitable for financial reporting or investor communications, and should not be used as the basis for any consequential decision without independent analysis.*

Any use of forecasts in presentations, documents, or communications must include this disclaimer or an equivalent statement.

---

## Override Procedures

### Overriding an Alert
```python
# Example: silence a non-actionable alert for one cycle
# Requires: written approval from metric owner stored in AUDIT.md
SILENCED_ALERTS = ["A013"]  # add rule ID + expiry date + approver
```

Override must be:
1. Documented in `AUDIT.md` with approver name and expiry date
2. Time-limited (maximum 30 days)
3. Reviewed at the next quarterly audit

### Overriding a Forecast
Forecasts cannot be "overridden" — they are advisory only. If a forecast appears anomalous, regenerate with a different trailing window or flag with `low_confidence: true` in the output.

---

## Human Review Checkpoints

The following actions require a human checkpoint before the agent proceeds (in any future automated/scheduled version):

- [ ] Before writing any output file to a shared or production location
- [ ] Before sending any notification to an external channel (Slack, email, PagerDuty)
- [ ] Before publishing any report or deck externally
- [ ] After any change to alert thresholds or metric definitions
- [ ] After any change to the data schema (`schema_version` bump)

---

## Accountability

| Role | Responsibility |
|------|---------------|
| Data Owner | Approves schema changes, data regeneration with new seeds |
| Analytics Lead | Owns alert thresholds and metric definitions |
| Engineering Lead | Approves agent deployments and automation expansions |
| On-Call Engineer | Responds to CRITICAL/HIGH alerts within SLA |
| Project Lead (Kamil_K) | Final override authority for all decisions |

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-06-01 | Initial policy — v1.0 | Kamil_K |

---

*This policy must be reviewed whenever the agent gains new capabilities, is connected to external systems, or is scheduled to run automatically. Review cycle: at every major version bump.*
