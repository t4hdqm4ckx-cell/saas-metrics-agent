# VERSION_CONTROL.md — FlowSync SaaS Metrics Agent

## Versioning Strategy
This project follows [Semantic Versioning 2.0.0](https://semver.org/):
- **MAJOR**: Breaking changes to data schema, agent API, or dashboard data contract
- **MINOR**: New features, new metrics, new dashboard tabs (backwards-compatible)
- **PATCH**: Bug fixes, UI polish, documentation updates

---

## Changelog

---

### [1.0.0] — 2026-06-01 (Initial Release)

**Type**: Major Release

#### Added
- `dashboard/index.html` — Full 4-tab interactive dark-mode SaaS metrics dashboard
  - Revenue Overview tab (MRR, ARR, NRR, Gross Margin, waterfall chart)
  - Customer Metrics tab (acquisition, churn, trial conversion funnel)
  - Engagement tab (MAU/DAU, cohort retention heatmap, viral K-factor)
  - Unit Economics tab (LTV, CAC, LTV:CAC ratio, payback period)
- `dashboard/assets/css/styles.css` — Dark-mode design system with CSS custom properties
- `dashboard/assets/js/dashboard.js` — Chart.js integration, tab navigation, data binding
- `dashboard/assets/data/metrics.json` — Baked-in monthly metrics for 24 months
- `agent/data_generator.py` — B2C SaaS synthetic data engine (24 months, 3 tiers)
- `agent/metrics_calculator.py` — KPI computation: NRR, LTV, CAC, payback period, churn
- `agent/agent.py` — Orchestration entry point with CLI flags
- `data/synthetic_data.json` — 24-month dataset (Jun 2024 – May 2026, seed=42)
- `docs/executive_deck.html` — Board-ready executive presentation (10 slides)
- `logs/app.log` — Structured JSON log output from agent runs
- `skills/data_analysis.md` — Statistical analysis capability spec
- `skills/visualization.md` — Chart selection and rendering guidelines
- `skills/reporting.md` — Executive summary generation patterns
- `skills/forecasting.md` — Trend extrapolation and scenario planning
- `skills/alerting.md` — Threshold-based metric alerting rules
- `CLAUDE.md` — AI assistant instructions and project architecture
- `README.md` — Full project documentation
- `ERROR_HANDLING.md` — Error taxonomy (E1xx–E5xx) and handling patterns
- `BUG_REPORTING.md` — Bug triage workflow and severity definitions
- `SECURITY.md` — Security policy, vulnerability reporting, controls
- `AUDIT.md` — Audit log and compliance posture

#### Data Schema (v1.0)
```json
{
  "generated_at": "ISO-8601 timestamp",
  "schema_version": "1.0",
  "company": "FlowSync",
  "months": [
    {
      "month": "YYYY-MM",
      "mrr": 0,
      "arr": 0,
      "new_mrr": 0,
      "expansion_mrr": 0,
      "contraction_mrr": 0,
      "churned_mrr": 0,
      "nrr": 0,
      "total_customers": 0,
      "new_customers": 0,
      "churned_customers": 0,
      "trial_starts": 0,
      "trial_conversions": 0,
      "trial_conversion_rate": 0,
      "mau": 0,
      "dau": 0,
      "stickiness": 0,
      "viral_k": 0,
      "ltv": 0,
      "cac": 0,
      "ltv_cac_ratio": 0,
      "payback_months": 0,
      "gross_margin": 0,
      "burn_rate": 0,
      "runway_months": 0,
      "arpu": 0,
      "monthly_churn_rate": 0,
      "plan_breakdown": {
        "starter": {"customers": 0, "mrr": 0},
        "pro": {"customers": 0, "mrr": 0},
        "business": {"customers": 0, "mrr": 0}
      }
    }
  ]
}
```

#### Synthetic Data Characteristics (v1.0)
| Parameter | Value |
|-----------|-------|
| Start month | 2024-06 |
| End month | 2026-05 |
| Total months | 24 |
| RNG seed | 42 |
| Starting MRR | ~$18,500 |
| Ending MRR | ~$347,820 |
| Starting customers | 412 |
| Ending customers | 8,214 |
| Average monthly growth | ~14% (early) tapering to ~5% |
| Churn rate range | 5.8% (early) → 3.1% (mature) |
| Trial conversion range | 15% → 22% |
| Viral K range | 0.32 → 0.62 |
| Gross margin range | 65% → 78% |

---

## Upcoming (v1.1.0 — Planned)

| Feature | Type | Priority |
|---------|------|---------|
| Monthly alert thresholds configurable via JSON | Minor | High |
| CSV export for all chart data | Minor | Medium |
| 12-month forecast overlay on revenue chart | Minor | High |
| SRI hash pinning for Chart.js CDN | Patch | High (security) |
| Bandit SAST integration in CI | Patch | Medium |
| Dark/light mode toggle | Minor | Low |

---

## Breaking Change Policy

- **Schema changes** that remove or rename fields are MAJOR version bumps
- **Schema additions** (new fields) are MINOR version bumps
- The `schema_version` field in `synthetic_data.json` MUST be updated with any schema change
- Dashboard JS that reads schema fields MUST be updated in the same PR as schema changes

---

## Migration Guides

### v0.x → v1.0
*(Not applicable — v1.0 is the initial release)*

---

## Contributors

| Version | Contributor | Role |
|---------|------------|------|
| 1.0.0 | Kamil_K | Project Lead, Initial Implementation |

---

*Last updated: 2026-06-01 | Maintained by: Engineering Lead*

---

### [1.0.1] — 2026-06-01 (Patch)

**Type**: Patch

#### Added
- `agent/config.py` — Centralized env-var config with validation
- `agent/schema.py` — JSON schema validator (runnable as CLI)
- `agent/forecaster.py` — Monte Carlo MRR + OLS churn forecasting
- `agent/alerter.py` — 14-rule metric threshold alert engine
- `agent/reporter.py` — Template-based narrative report generator
- `agent/tests/test_alerter.py` — 7 alerter tests
- `docs/architecture.md` — System diagram and data flow documentation
- `CONTRIBUTING.md` — Development setup and contribution guidelines
- `LICENSE` — MIT
- `Makefile` — Common workflow targets
- `.github/` — Issue and PR templates

#### Fixed
- README metrics updated to match actual seed=42 generated data
