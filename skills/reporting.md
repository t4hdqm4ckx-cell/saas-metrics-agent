# Skill: Reporting

**Category**: Business Intelligence  
**Version**: 1.0  
**Owner**: Analytics & Strategy

---

## Overview
The Reporting skill defines how the FlowSync agent generates structured business summaries from computed metrics. It covers report formats, narrative generation rules, executive deck construction, and delivery mechanisms.

---

## Report Types

### 1. Monthly Metrics Report
- **Frequency**: Monthly (generated on the 1st business day)
- **Audience**: Internal operators, team leads
- **Format**: Structured JSON + rendered HTML section in dashboard
- **Scope**: Single-month snapshot with MoM and YoY comparisons

**Required Sections:**
1. Executive Summary (3 bullets: wins, concerns, actions)
2. Revenue Summary (MRR, ARR, NRR, gross margin)
3. Customer Summary (acquisitions, churn, net adds)
4. Engagement Summary (MAU, DAU, stickiness)
5. Unit Economics (LTV, CAC, payback)
6. Notable Anomalies (E304 outliers surfaced here)

### 2. Quarterly Business Review (QBR)
- **Frequency**: Quarterly
- **Audience**: Leadership, investors
- **Format**: Executive deck (`docs/executive_deck.html`) + PDF export
- **Scope**: Rolling 3-month performance + YTD + outlook

**Deck Structure (10 slides):**
1. Cover — Company name, quarter, date
2. Performance Highlights — 3 headline KPIs (MRR, NRR, customers)
3. Revenue Deep-Dive — MRR waterfall, ARR bridge
4. Customer Metrics — Growth, churn, cohort retention
5. Engagement — MAU/DAU, stickiness, viral K
6. Unit Economics — LTV:CAC, payback period, gross margin
7. Benchmark Comparison — vs. industry benchmarks
8. Risks & Watchlist — Metrics trending in wrong direction
9. Initiatives & Roadmap — Top 3 growth levers
10. Appendix — Full data tables

### 3. Alert Report
- **Trigger**: Metric crosses defined threshold (see `skills/alerting.md`)
- **Audience**: On-call, metric owner
- **Format**: Structured dict (suitable for Slack/email webhook)
- **Latency target**: < 5 minutes from threshold crossing

---

## Narrative Generation Rules

The agent generates plain-English summaries using template-based composition (no LLM required at v1.0). Rules:

### Revenue Narrative
```python
def revenue_summary(current: MonthlySnapshot, prior: MonthlySnapshot) -> str:
    delta_pct = (current.mrr - prior.mrr) / prior.mrr * 100
    direction = "grew" if delta_pct > 0 else "declined"
    health = "strong" if current.nrr > 110 else "stable" if current.nrr > 100 else "concerning"
    return (
        f"MRR {direction} {abs(delta_pct):.1f}% MoM to ${current.mrr:,.0f}. "
        f"Net Revenue Retention of {current.nrr:.0f}% reflects {health} expansion dynamics. "
        f"Churn contributed ${current.churned_mrr:,.0f} headwind."
    )
```

### Churn Narrative
- Churn rate < 3%: "Churn remained well-controlled at X%, below the 3% target."
- Churn rate 3–5%: "Churn of X% warrants attention — up Y bps MoM. Cohort analysis points to [month] acquisition cohort as primary driver."
- Churn rate > 5%: "⚠️ Churn spiked to X% — immediate investigation required."

### Growth Narrative
- MoM growth > 15%: "Exceptional growth of X% driven by [new/expansion/viral] dynamics."
- MoM growth 5–15%: "Healthy growth of X% MoM, on track for annual targets."
- MoM growth < 5%: "Growth decelerated to X% MoM — review acquisition and expansion channels."

---

## Benchmark Reference (B2C SaaS)

Used in QBR benchmark slides. Source: OpenView Partners, SaaStr, Bessemer Venture Partners.

| Metric | Seed/Early | Series A | Series B+ |
|--------|-----------|---------|----------|
| Monthly churn | < 8% | < 5% | < 3% |
| NRR | > 90% | > 100% | > 110% |
| LTV:CAC | > 1× | > 3× | > 5× |
| Payback period | < 24 mo | < 18 mo | < 12 mo |
| DAU/MAU stickiness | > 20% | > 30% | > 40% |
| Trial conversion | > 10% | > 15% | > 20% |
| Gross margin | > 50% | > 65% | > 70% |

---

## Report Delivery (Future v1.1)

```python
class ReportDelivery:
    """Future: deliver reports via webhook"""
    
    def deliver_slack(self, report: dict, webhook_url: str) -> bool:
        # POST formatted Slack Block Kit message
        pass
    
    def deliver_email(self, report: dict, recipients: list[str]) -> bool:
        # Send HTML report via SendGrid / SES
        pass
    
    def export_pdf(self, html_path: str, output_path: str) -> bool:
        # Convert executive_deck.html to PDF via headless Chrome
        pass
```

---

## Output File Formats

| Report | Format | Location |
|--------|--------|---------|
| Monthly snapshot | JSON | `data/synthetic_data.json` |
| Dashboard | HTML (self-contained) | `dashboard/index.html` |
| Executive deck | HTML (print-to-PDF) | `docs/executive_deck.html` |
| Agent log | Structured JSON log | `logs/app.log` |
| Version history | Markdown | `VERSION_CONTROL.md` |

---

*Last updated: 2026-06-01*
