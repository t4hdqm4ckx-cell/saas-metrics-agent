# Architecture Overview — FlowSync SaaS Metrics Agent

## System Diagram

```
┌─────────────────────────────────────────────────────┐
│                   FlowSync Agent                     │
│                                                       │
│  ┌──────────────┐    ┌──────────────────────────┐    │
│  │ config.py    │───▶│ data_generator.py        │    │
│  │ (env vars)   │    │ - 24 months synthetic     │    │
│  └──────────────┘    │ - 3 tiers, seasonality   │    │
│                      │ - tapering growth         │    │
│                      └────────────┬─────────────┘    │
│                                   │                   │
│                                   ▼                   │
│                      ┌──────────────────────────┐    │
│                      │ schema.py (validation)   │    │
│                      └────────────┬─────────────┘    │
│                                   │                   │
│                                   ▼                   │
│                      ┌──────────────────────────┐    │
│                      │ metrics_calculator.py    │    │
│                      │ - NRR, LTV:CAC, cohort   │    │
│                      │ - waterfall, outliers    │    │
│                      └────────────┬─────────────┘    │
│                                   │                   │
│                                   ▼                   │
│                      ┌──────────────────────────┐    │
│  ┌──────────────┐    │ data/synthetic_data.json │    │
│  │ logs/app.log │◀───│ (24-month JSON output)   │    │
│  └──────────────┘    └────────────┬─────────────┘    │
└───────────────────────────────────┼─────────────────┘
                                    │
                     ┌──────────────▼──────────────┐
                     │      Frontend Layer          │
                     │                              │
                     │  ┌────────────────────────┐  │
                     │  │ dashboard/index.html   │  │
                     │  │ - 4-tab dark UI        │  │
                     │  │ - Chart.js 4.4          │  │
                     │  │ - 10+ chart types       │  │
                     │  │ - Inline JSON data      │  │
                     │  └────────────────────────┘  │
                     │                              │
                     │  ┌────────────────────────┐  │
                     │  │ docs/executive_deck.html│  │
                     │  │ - 10-slide board deck   │  │
                     │  │ - Print → PDF export    │  │
                     │  └────────────────────────┘  │
                     └──────────────────────────────┘
```

## Data Flow

1. **Config** (`config.py`) loads env vars → validates → produces `AgentConfig`
2. **Generator** (`data_generator.py`) uses config to produce `List[MonthlySnapshot]`
3. **Schema validator** (`schema.py`) validates the output JSON before writing
4. **Calculator** (`metrics_calculator.py`) computes derived metrics (NRR, cohort matrix, etc.)
5. **Output**: `data/synthetic_data.json` — baked into dashboard JS arrays

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Self-contained HTML dashboard | No server, no build step, works from `file://` URL |
| Inline JSON in dashboard | Avoids CORS issues with file:// protocol |
| Python `random` not numpy | Avoids heavy dependency; reproducible with `random.seed()` |
| Tapering growth model | More realistic than constant growth for B2C lifecycle modeling |
| CSS custom properties | Easy theming, dark/light switch without JS |
| Chart.js over D3 | Lower complexity, adequate for 10-chart dashboard scope |

## Security Posture (v1.0)

- No server, no auth surface, no user input → minimal attack surface
- No secrets in code or data
- SRI hash on CDN script
- See SECURITY.md for full posture

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Data generation (24 mo) | ~0.3s | Python 3.10, seed=42 |
| Dashboard initial load | ~200ms | CDN cached Chart.js |
| Tab switch | ~50ms | Charts lazy-init on first visit |
| Cohort heatmap render | ~30ms | Pure DOM, 144 cells |
