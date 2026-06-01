# Instructions — FlowSync SaaS Metrics Agent

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | Required for the agent layer only |
| numpy | ≥1.24 | Only external dependency |
| Browser | Any modern | Chrome / Firefox / Safari for dashboard |
| Git | Any | For cloning |

No Node.js, no npm, no build step, no API keys required.

---

## 1. Clone the Repository

```bash
git clone https://github.com/t4hdqm4ckx-cell/saas-metrics-agent.git
cd saas-metrics-agent
```

---

## 2. View the Dashboard (No Setup Required)

```bash
open dashboard/index.html
```

Or serve locally if you prefer a URL:

```bash
python3 -m http.server 8080
# Visit http://localhost:8080/dashboard/
```

The dashboard is fully self-contained — all chart data is embedded inline. No server or network connection required after the page loads (Chart.js loads from CDN on first visit).

---

## 3. View the Executive Board Deck

```bash
open docs/executive_deck.html
```

**To export as PDF:**
1. Open in Chrome or Firefox
2. File → Print (or `Cmd+P`)
3. Destination → Save as PDF
4. Layout: Landscape · Scale: 100% · Background graphics: ON

---

## 4. Install Agent Dependencies (Optional)

Only needed if you want to regenerate the synthetic data.

```bash
pip install numpy>=1.24
```

---

## 5. Regenerate Synthetic Data

```bash
make data
# or manually:
python3 agent/data_generator.py --months 24 --seed 42 --output data/synthetic_data.json
```

After regenerating, the dashboard reads the new data automatically on next open.

---

## 6. Validate the Data Schema

```bash
make validate
# or:
python3 agent/schema.py data/synthetic_data.json
```

---

## 7. Run the Test Suite

```bash
make test
# or individually:
python3 agent/tests/test_data_generator.py
python3 agent/tests/test_metrics_calculator.py
python3 agent/tests/test_alerter.py
python3 agent/tests/test_reporter.py
```

All 33 tests should pass.

---

## 8. Run Forecasting & Alerts (Optional)

```bash
python3 - <<'EOF'
import json, sys
sys.path.insert(0, 'agent')
from forecaster import Forecaster
from alerter import alert_summary

with open('data/synthetic_data.json') as f:
    data = json.load(f)

fc = Forecaster(data)
print("6-month MRR forecast:", fc.summary())

alerts = alert_summary(data['months'])
print("Active alerts:", alerts)
EOF
```

---

## Key Files

| File / Folder | Purpose |
|---------------|---------|
| `dashboard/index.html` | Main interactive dashboard — open this |
| `docs/executive_deck.html` | 10-slide board presentation |
| `data/synthetic_data.json` | 24-month synthetic dataset |
| `agent/data_generator.py` | Regenerate synthetic data |
| `agent/metrics_calculator.py` | KPI computation (NRR, LTV:CAC, cohort) |
| `agent/forecaster.py` | 6/12-month MRR & churn forecasting |
| `agent/alerter.py` | 14-rule metric threshold alerting |
| `agent/reporter.py` | Plain-English narrative summaries |
| `agent/schema.py` | JSON schema validator |
| `agent/config.py` | Centralized env-var configuration |
| `skills/` | Agent capability definitions (Markdown) |
| `logs/app.log` | Agent run log output |
| `Makefile` | Common workflow shortcuts |

---

## Environment Variables (Agent Only)

| Variable | Default | Description |
|----------|---------|-------------|
| `FLOWSYNC_SEED` | `42` | RNG seed for reproducible data |
| `FLOWSYNC_MONTHS` | `24` | Number of months to generate |
| `FLOWSYNC_START_YEAR` | `2024` | Start year |
| `FLOWSYNC_START_MONTH` | `6` | Start month (1–12) |
| `FLOWSYNC_OUTPUT_DIR` | `data` | Output directory for JSON |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Makefile Targets

```
make data       — Regenerate synthetic_data.json and copy to dashboard assets
make validate   — Validate JSON schema
make test       — Run all 4 test suites (33 tests)
make dashboard  — Open dashboard in browser
make deck       — Open executive deck in browser
make serve      — Start local HTTP server on port 8080
make clean      — Remove __pycache__ and .pyc files
```

---

## Troubleshooting

**Dashboard shows blank charts**
- Ensure Chart.js CDN loaded (requires internet on first visit)
- Check browser console for errors — all errors are prefixed `[FlowSync Dashboard]`
- Try serving locally with `make serve` instead of `file://`

**Agent import errors**
- Ensure you're running from the repo root: `python3 agent/...`
- Or `cd agent && python3 data_generator.py`

**Tests fail with `FileNotFoundError`**
- Run tests from the repo root, not from inside `agent/tests/`

---

*For bugs see [BUG_REPORTING.md](BUG_REPORTING.md) · For security issues see [SECURITY.md](SECURITY.md)*
