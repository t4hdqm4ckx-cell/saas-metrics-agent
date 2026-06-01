# Skill: Alerting

**Category**: Monitoring & Observability  
**Version**: 1.0  
**Owner**: Platform Engineering

---

## Overview
The Alerting skill defines threshold rules, alert lifecycle management, and notification routing for FlowSync metric health monitoring. Alerts fire when key SaaS metrics deviate from expected ranges.

---

## Alert Thresholds

### Revenue Alerts

| Alert | Condition | Severity | Action |
|-------|-----------|---------|--------|
| MRR Decline | MRR < Prior Month MRR | HIGH | Notify revenue lead |
| MRR Growth Stall | MoM growth < 2% for 2 consecutive months | MEDIUM | Flag in dashboard, weekly standup |
| NRR Drop | NRR < 100% | HIGH | Immediate churn analysis |
| Churn Spike | Monthly churn rate > 5% | HIGH | Emergency customer success review |
| Churn Warning | Monthly churn rate > 3.5% | MEDIUM | Churn investigation ticket |
| NRR Exceptional | NRR > 125% | INFO | Celebrate, understand expansion driver |

### Customer Alerts

| Alert | Condition | Severity | Action |
|-------|-----------|---------|--------|
| Customer Count Decline | Net customers < 0 (churned > new) | CRITICAL | CEO + board notification |
| Acquisition Drop | New customers < 50% of prior month | HIGH | Marketing review |
| Trial Starts Drop | Trial starts < 70% of trailing 3-mo avg | MEDIUM | Top-of-funnel investigation |
| Trial Conversion Drop | Trial conversion rate < 12% | HIGH | Onboarding/activation review |

### Engagement Alerts

| Alert | Condition | Severity | Action |
|-------|-----------|---------|--------|
| MAU Decline | MAU < Prior Month MAU | HIGH | Product engagement review |
| Stickiness Drop | DAU/MAU < 25% | MEDIUM | Engagement feature audit |
| Stickiness Critical | DAU/MAU < 15% | HIGH | Emergency product response |
| Viral K Drop | K-factor < 0.3 for 2 months | MEDIUM | Referral program review |

### Unit Economics Alerts

| Alert | Condition | Severity | Action |
|-------|-----------|---------|--------|
| LTV:CAC Danger | LTV:CAC < 2× | CRITICAL | Freeze paid acquisition; review CAC |
| LTV:CAC Warning | LTV:CAC < 3× | HIGH | Optimization sprint |
| Payback Extended | Payback period > 18 months | HIGH | CAC reduction or ARPU improvement plan |
| Gross Margin Drop | Gross margin < 60% | HIGH | COGS analysis |
| Burn Spike | Month-over-month burn increase > 30% | MEDIUM | Finance review |

---

## Alert Configuration Schema

```json
{
  "alerts": [
    {
      "id": "ALERT_001",
      "name": "MRR Monthly Decline",
      "metric": "mrr",
      "condition": "current < prior_month",
      "severity": "HIGH",
      "cooldown_hours": 168,
      "notification_channels": ["slack_#metrics-alerts", "email_revenue_lead"],
      "enabled": true
    },
    {
      "id": "ALERT_002",
      "name": "Churn Rate Spike",
      "metric": "monthly_churn_rate",
      "condition": "current > 0.05",
      "severity": "HIGH",
      "cooldown_hours": 72,
      "notification_channels": ["slack_#cs-alerts", "pagerduty"],
      "enabled": true
    }
  ]
}
```

---

## Alert Lifecycle

```
INACTIVE → FIRING → ACKNOWLEDGED → RESOLVED
              ↓
          SILENCED (manual override, cooldown)
```

### States
| State | Description |
|-------|-------------|
| INACTIVE | Condition not met; all clear |
| FIRING | Condition met; notifications sent |
| ACKNOWLEDGED | Owner confirmed receipt; investigating |
| RESOLVED | Condition no longer met after FIRING |
| SILENCED | Manually suppressed (with expiry) |

### Cooldown Policy
- Alerts do not re-fire within the cooldown window (default: 7 days for monthly metrics)
- Escalation: If alert remains FIRING and unacknowledged after 24h, escalate severity by one level

---

## Notification Routing

| Channel | Used For | Format |
|---------|---------|--------|
| Slack `#metrics-alerts` | MEDIUM + HIGH | Block Kit message with chart thumbnail |
| Slack `#incidents` | CRITICAL | @channel mention with immediate context |
| PagerDuty | CRITICAL only | Short text + link to dashboard |
| Email | HIGH + CRITICAL | HTML report with full metric context |
| Dashboard banner | All severities | In-app notification badge on affected tab |

---

## Dashboard Alert Integration

The dashboard renders alert indicators inline:

```javascript
function renderAlertBadge(metricId, alerts) {
    const activeAlerts = alerts.filter(a => a.metric === metricId && a.state === 'FIRING');
    if (activeAlerts.length === 0) return;
    
    const severity = activeAlerts[0].severity;
    const colors = { CRITICAL: '#FF4757', HIGH: '#F59E0B', MEDIUM: '#A855F7' };
    
    // Render pulsing dot next to metric KPI card
    const badge = document.createElement('span');
    badge.className = 'alert-badge';
    badge.style.backgroundColor = colors[severity];
    badge.title = activeAlerts[0].name;
    document.getElementById(`kpi-${metricId}`).appendChild(badge);
}
```

---

## Tuning Guidance

### Avoiding Alert Fatigue
- Do not set thresholds at the expected value — leave headroom (e.g., churn threshold at 5%, not 3.2%)
- Use rolling averages for noisy metrics rather than single-month values
- Implement severity progression: warn at 3.5%, alert at 5%, critical at 8%
- Review and tune thresholds quarterly based on actual metric distributions

### Seasonal Adjustments
- Suppress acquisition-related alerts in August (summer slowdown) and January 1–7 (post-holiday)
- Adjust MAU/DAU thresholds by −15% in Q3 (summer seasonality)

---

*Last updated: 2026-06-01*
