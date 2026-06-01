# ERROR_HANDLING.md — FlowSync SaaS Metrics Agent

## Overview
This document defines the error taxonomy, handling strategies, and recovery procedures for the FlowSync SaaS Metrics Agent. All errors are classified by severity, layer, and recoverability.

---

## Error Taxonomy

### Severity Levels

| Level | Code | Description | Action Required |
|-------|------|-------------|-----------------|
| CRITICAL | E1xx | System cannot continue operation | Immediate page + rollback |
| HIGH | E2xx | Core functionality degraded | Alert on-call within 15 min |
| MEDIUM | E3xx | Non-critical feature impaired | Ticket within 24 hours |
| LOW | E4xx | Cosmetic or informational | Log and monitor |
| INFO | E5xx | Expected operational event | Log only |

---

## Error Categories by Layer

### Data Generation Layer (`agent/data_generator.py`)

| Code | Error | Cause | Recovery |
|------|-------|-------|----------|
| E101 | `DataGenerationFailure` | Invalid parameters (e.g., months < 1) | Validate inputs, raise with context |
| E102 | `SeedCollisionError` | Duplicate RNG seed produces inconsistent state | Re-seed with timestamp fallback |
| E103 | `OutputWriteError` | Cannot write to `data/` directory | Check permissions; log path, re-raise |
| E201 | `SchemaValidationError` | Generated JSON fails schema check | Log invalid fields, regenerate with defaults |
| E202 | `CohortComputationError` | Division by zero in cohort retention calc | Guard with `max(denominator, 1)` |

### Metrics Calculation Layer (`agent/metrics_calculator.py`)

| Code | Error | Cause | Recovery |
|------|-------|-------|----------|
| E301 | `MissingMetricError` | Required field absent from input data | Use cached prior-month value |
| E302 | `NegativeRevenueError` | MRR delta produces impossible negative | Clamp to 0, flag in audit log |
| E303 | `DivisionByZeroMetric` | Zero denominator in ratio (e.g., CAC with 0 new customers) | Return `None`, render as `—` in UI |
| E304 | `OutlierDetectedWarning` | Value > 5σ from rolling average | Log warning, do not suppress — surface in dashboard |

### Dashboard Layer (`dashboard/assets/js/`)

| Code | Error | Cause | Recovery |
|------|-------|-------|----------|
| E401 | `ChartRenderError` | Chart.js canvas not found in DOM | Retry after 100ms; log if persists |
| E402 | `DataBindingError` | JSON field missing when binding chart data | Render chart with zero-filled placeholder |
| E403 | `TabNavigationError` | Tab content panel missing from DOM | Fallback to first tab, log in console |
| E501 | `StaleDataWarning` | `synthetic_data.json` older than 30 days | Show banner: "Data last updated X days ago" |

---

## Error Handling Patterns

### Python: Structured Error Context
```python
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("flowsync.agent")

@dataclass
class AgentError(Exception):
    code: str
    message: str
    context: Optional[dict] = None
    recoverable: bool = True

    def log(self):
        logger.error(
            f"[{self.code}] {self.message}",
            extra={"context": self.context, "recoverable": self.recoverable}
        )

# Usage
try:
    result = compute_nrr(current_mrr, prior_mrr)
except ZeroDivisionError:
    raise AgentError(
        code="E303",
        message="Cannot compute NRR: prior_mrr is zero",
        context={"month": current_month, "prior_mrr": prior_mrr},
        recoverable=True
    )
```

### JavaScript: Dashboard Error Boundary
```javascript
function safeRenderChart(canvasId, config) {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) throw new Error(`E401: Canvas #${canvasId} not found`);
        return new Chart(canvas, config);
    } catch (err) {
        console.error('[FlowSync Dashboard]', err.message);
        const fallback = document.getElementById(`${canvasId}-fallback`);
        if (fallback) fallback.style.display = 'block';
        return null;
    }
}
```

### Retry Logic (Agent)
```python
import time
from functools import wraps

def retry(max_attempts=3, backoff_seconds=1.0, recoverable_only=True):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except AgentError as e:
                    if not e.recoverable or attempt == max_attempts - 1:
                        e.log()
                        raise
                    time.sleep(backoff_seconds * (2 ** attempt))
        return wrapper
    return decorator
```

---

## Logging Standards

All log entries must include:
- **Timestamp** (ISO 8601 UTC)
- **Error code** (Exxx)
- **Layer** (agent | metrics | dashboard)
- **Severity**
- **Context dict** (relevant parameters at time of failure)

### Log Format
```
2026-05-01T14:32:11Z | ERROR | E202 | metrics | CohortComputationError | {"month": "2026-04", "cohort_id": "2025-11", "denominator": 0}
```

### Log Destinations
| Environment | Destination |
|-------------|-------------|
| Local dev | `logs/app.log` (rotating, 10MB max, 5 backups) |
| CI/CD | stdout (captured by runner) |
| Production | (future) CloudWatch / Datadog |

---

## Escalation Matrix

| Severity | Response Time | Owner | Channel |
|----------|---------------|-------|---------|
| CRITICAL | 5 minutes | On-call engineer | PagerDuty |
| HIGH | 15 minutes | Team lead | Slack #alerts |
| MEDIUM | 24 hours | Assigned dev | GitHub Issue |
| LOW | 1 week | Any team member | GitHub Issue |

---

## Unhandled Exception Policy

- All unhandled exceptions in the agent MUST be caught at the top-level `agent.py` entry point
- Unhandled exceptions MUST log full stack trace with `exc_info=True`
- The agent MUST exit with a non-zero status code on unhandled exceptions
- Dashboard JS errors MUST be caught by a global `window.onerror` handler and reported to the browser console with the `[FlowSync]` prefix

---

*Last updated: 2026-06-01 | Owner: Platform Engineering*
