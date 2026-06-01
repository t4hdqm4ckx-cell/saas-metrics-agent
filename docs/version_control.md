# docs/version_control.md — Data Schema & Dashboard Change History

This file tracks changes specific to the **data schema**, **dashboard data contract**, and **visualization changes** — lower-level than VERSION_CONTROL.md in the root (which tracks the full product changelog).

---

## Schema History

### Schema v1.0 (2026-06-01)
- **Initial schema** — 24-month monthly snapshot format
- All fields listed in VERSION_CONTROL.md

### Planned Schema v1.1 (Q3 2026)
- Add `forecast` object alongside each month (P10, P50, P90)
- Add `alerts_fired` array per month (list of alert IDs that fired)
- Add `cohort_retention` embedded per month (array of retention at M+1 through M+12)

---

## Dashboard Data Contract

The dashboard reads from embedded JS arrays in `index.html`. Any schema change must:
1. Update `data/synthetic_data.json` (agent output)
2. Update the embedded `const` arrays in `dashboard/index.html`
3. Update `dashboard/assets/data/metrics.json` (copy)
4. Bump schema_version in the JSON
5. Add entry to this file and to root VERSION_CONTROL.md

---

## Change Log

| Date | Type | File Changed | Description |
|------|------|-------------|-------------|
| 2026-06-01 | CREATE | `data/synthetic_data.json` | Initial 24-month dataset, seed=42 |
| 2026-06-01 | CREATE | `dashboard/index.html` | Initial dashboard, all 10 chart types |
| 2026-06-01 | CREATE | `docs/executive_deck.html` | 10-slide board deck |

---

*See root VERSION_CONTROL.md for full product changelog.*
