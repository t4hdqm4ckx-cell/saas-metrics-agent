# Skill: Data Analysis

**Category**: Core Analytics  
**Version**: 1.0  
**Owner**: Data Engineering

---

## Overview
The Data Analysis skill enables the FlowSync agent to ingest, validate, clean, and compute KPIs from raw subscription event streams. It produces the monthly snapshots stored in `data/synthetic_data.json` that power the dashboard.

---

## Capabilities

### 1. Metric Computation

| Metric | Formula | Inputs Required |
|--------|---------|-----------------|
| MRR | Σ(active subscription monthly values) | Subscription records |
| ARR | MRR × 12 | MRR |
| Churn Rate | Churned MRR / Prior Month MRR | MRR, churned_mrr |
| NRR | (Prior MRR + Expansion − Contraction − Churn) / Prior MRR | MRR components |
| ARPU | MRR / Total Active Customers | MRR, customers |
| LTV | ARPU / Monthly Churn Rate | ARPU, churn_rate |
| CAC | Total Acquisition Spend / New Customers | Spend data, new customers |
| LTV:CAC | LTV / CAC | LTV, CAC |
| Payback Period | CAC / (ARPU × Gross Margin) | CAC, ARPU, gross margin |
| Stickiness | DAU / MAU | DAU, MAU |
| Viral K | Avg Invites Sent × Invite Conversion Rate | Invite events |

### 2. Cohort Analysis
- Groups customers by acquisition month
- Computes month-N retention for each cohort
- Identifies high-churn vs. sticky cohorts
- Outputs retention matrix (cohorts × months) for heatmap visualization

### 3. Seasonality Modeling
- Applies multiplicative seasonal factors to base metrics
- Q4 (Oct–Dec): +15% trial starts, +8% conversion (gifting season)
- August: −10% (summer slowdown)
- January: +12% (new year resolutions)

### 4. Outlier Detection
- Uses z-score (threshold: 3σ) to flag anomalous monthly values
- Logs warnings via ERROR_HANDLING.md E304 pattern
- Does not suppress outliers — surfaces them in the dashboard as annotated points

### 5. Growth Decomposition
Decomposes MRR growth into:
- New MRR (new customer subscriptions)
- Expansion MRR (upgrades: Starter→Pro, Pro→Business)
- Contraction MRR (downgrades)
- Churned MRR (cancellations)
- Net New MRR = New + Expansion − Contraction − Churned

---

## Input Schemas

### Raw Event (not stored — processed in-memory)
```python
@dataclass
class SubscriptionEvent:
    event_id: str
    customer_id: str
    event_type: str          # 'new' | 'upgrade' | 'downgrade' | 'churn'
    plan: str                # 'starter' | 'pro' | 'business'
    mrr_delta: float
    timestamp: str           # ISO-8601
```

### Monthly Snapshot (output)
See VERSION_CONTROL.md for full schema definition.

---

## Implementation Notes

### Churn Rate Calculation
Two methods are supported:
- **Logo churn**: Churned customers / Total customers at start of month
- **Revenue churn**: Churned MRR / MRR at start of month

The dashboard uses **revenue churn** as the primary metric; logo churn is shown as secondary.

### LTV Calculation
LTV uses the simple perpetuity formula: `LTV = ARPU / monthly_churn_rate`

This is appropriate for B2C SaaS with relatively stable churn. For more complex models:
- Use the Pareto/NBD model for non-contractual subscriptions
- Use the BG/NBD model for subscription businesses with explicit churn events

### Confidence Intervals
- Metrics computed from fewer than 30 customer events are flagged with `low_confidence: true`
- These months render with a dotted border on charts and an asterisk in tooltips

---

## Dependencies
- `numpy` ≥ 1.24 (statistical operations)
- `json` stdlib (I/O)
- `dataclasses` stdlib (type-safe data structures)
- `logging` stdlib (audit trail)

---

## Usage
```python
from agent.metrics_calculator import MetricsCalculator

calc = MetricsCalculator(data=monthly_events)
snapshots = calc.compute_all_months()
# snapshots: List[MonthlySnapshot]
```

---

## Testing
- Unit tests in `tests/test_metrics_calculator.py`
- Reference values validated against known SaaS benchmarks (OpenView, SaaStr, Bessemer)
- Edge cases: zero-customer month, 100% churn month, negative NRR

---

*Last updated: 2026-06-01*
