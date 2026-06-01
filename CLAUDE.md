# CLAUDE.md — FlowSync SaaS Metrics Agent

## Project Overview
FlowSync SaaS Metrics Dashboard Agent is a self-contained B2C SaaS analytics platform that generates synthetic subscription data, computes core SaaS KPIs, and renders an interactive dark-mode HTML dashboard. No external database or live API is required — all data is generated in-memory via `agent/data_generator.py` and baked into `data/synthetic_data.json`.

## Repository Structure
```
saas-metrics-agent/
├── dashboard/              # Frontend dashboard (HTML/CSS/JS)
│   ├── index.html          # Main interactive dashboard
│   └── assets/
│       ├── css/            # Stylesheets
│       ├── js/             # Chart logic and data binding
│       └── data/           # Baked-in JSON snapshots
├── agent/                  # Python data-generation agent
│   ├── agent.py            # Orchestration entry point (do not run in prod without config)
│   ├── data_generator.py   # Synthetic SaaS data engine
│   └── metrics_calculator.py # KPI computation layer
├── data/                   # Output data artifacts
│   └── synthetic_data.json
├── docs/                   # Documentation and reporting
│   ├── executive_deck.html # Executive board presentation
│   └── version_control.md  # Tracked change log
├── logs/                   # Runtime logs
│   └── app.log
├── skills/                 # Reusable agent skill definitions
│   ├── data_analysis.md
│   ├── visualization.md
│   ├── reporting.md
│   ├── forecasting.md
│   └── alerting.md
├── CLAUDE.md               # This file
├── README.md               # Project overview and setup
├── ERROR_HANDLING.md       # Error taxonomy and handling patterns
├── BUG_REPORTING.md        # Bug triage and reporting workflow
├── SECURITY.md             # Security posture and controls
├── AUDIT.md                # Audit log and compliance notes
└── VERSION_CONTROL.md      # Change tracking document
```

## Key Architecture Decisions
- **Self-contained**: The dashboard is a single HTML file with embedded JS and inline Chart.js CDN. No build step required.
- **Synthetic data**: All metrics are procedurally generated with realistic seasonality, cohort effects, and growth curves mimicking a B2C SaaS product (3 tiers: Starter $12, Pro $29, Business $79).
- **Agent layer**: `agent/` contains Python modules for regenerating data. The agent is idempotent — running it overwrites `data/synthetic_data.json`.
- **No live dependencies**: Dashboard reads from the baked JSON file. No API keys, no database connections.

## Running the Dashboard
```bash
# Open directly in browser — no server needed
open dashboard/index.html

# Or serve locally (optional)
python3 -m http.server 8080
# Then visit http://localhost:8080/dashboard/
```

## Regenerating Synthetic Data (do not run in this session)
```bash
cd agent
python3 data_generator.py --months 24 --output ../data/synthetic_data.json
```

## Coding Conventions
- Python: PEP 8, type hints throughout, no third-party deps beyond `numpy` and `json`
- JavaScript: ES6+, no framework (vanilla JS + Chart.js)
- CSS: CSS custom properties (variables) for theming, BEM naming
- Commits: conventional commit format (`feat:`, `fix:`, `docs:`, `chore:`, `data:`)

## Metrics Reference
| Metric | Definition | Target |
|--------|-----------|--------|
| MRR | Monthly Recurring Revenue | > $300K |
| ARR | MRR × 12 | > $3.6M |
| NRR | Net Revenue Retention | > 110% |
| Churn Rate | Churned MRR / Prior MRR | < 3% |
| LTV | ARPU / Churn Rate | > $500 |
| CAC | Sales & Marketing Spend / New Customers | < $80 |
| LTV:CAC | LTV / CAC | > 3× |
| Payback | CAC / (ARPU × Gross Margin) | < 12 mo |
| DAU/MAU | Daily / Monthly Active Users | > 40% |
| Viral K | Invites sent × Conversion rate | > 0.5 |

## Environment Variables (agent only)
```
FLOWSYNC_SEED=42          # RNG seed for reproducible data
FLOWSYNC_MONTHS=24        # Number of months to generate
FLOWSYNC_OUTPUT_DIR=data/ # Output directory for JSON artifacts
LOG_LEVEL=INFO            # Logging verbosity
```
