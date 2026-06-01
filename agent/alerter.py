"""
alerter.py — FlowSync Metric Alert Engine

Evaluates the alert thresholds defined in skills/alerting.md against
the latest monthly snapshot and returns a list of active alerts.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AlertRule:
    id: str
    name: str
    metric: str
    severity: str          # CRITICAL | HIGH | MEDIUM | LOW
    threshold: float
    operator: str          # 'gt' | 'lt' | 'gte' | 'lte'
    message_template: str
    cooldown_months: int = 1


@dataclass
class FiredAlert:
    rule: AlertRule
    metric: str
    current_value: float
    threshold: float
    message: str
    month: str


ALERT_RULES = [
    AlertRule("A001", "Customer Count Decline",    "net_new_customers", "CRITICAL", 0,    "lt",  "Net customers went negative: {value:.0f} — churned > new"),
    AlertRule("A002", "Churn Rate Critical",        "monthly_churn_rate","CRITICAL", 0.08, "gt",  "Churn rate {value:.1%} exceeds critical threshold of 8%"),
    AlertRule("A003", "Churn Rate Spike",            "monthly_churn_rate","HIGH",     0.05, "gt",  "Churn rate {value:.1%} exceeds 5% alert threshold"),
    AlertRule("A004", "Churn Rate Warning",          "monthly_churn_rate","MEDIUM",   0.035,"gt",  "Churn rate {value:.1%} above 3.5% warning level"),
    AlertRule("A005", "NRR Below 100%",              "nrr",               "HIGH",     100,  "lt",  "NRR {value:.1f}% below 100% — losing revenue from existing customers"),
    AlertRule("A006", "MRR Month-on-Month Decline",  "mrr_mom_change",    "HIGH",     0,    "lt",  "MRR declined {value:.1f}% MoM — immediate investigation needed"),
    AlertRule("A007", "Trial Conversion Drop",       "trial_conversion_rate","HIGH",  0.12, "lt",  "Trial conversion {value:.1%} dropped below 12% minimum"),
    AlertRule("A008", "Stickiness Critical",         "stickiness",        "HIGH",     0.15, "lt",  "DAU/MAU stickiness {value:.1%} below 15% critical threshold"),
    AlertRule("A009", "LTV:CAC Danger Zone",         "ltv_cac_ratio",     "CRITICAL", 2.0,  "lt",  "LTV:CAC {value:.1f}× below 2× — freeze paid acquisition immediately"),
    AlertRule("A010", "LTV:CAC Warning",             "ltv_cac_ratio",     "HIGH",     3.0,  "lt",  "LTV:CAC {value:.1f}× below 3× minimum target"),
    AlertRule("A011", "Payback Period Extended",     "payback_months",    "HIGH",     18.0, "gt",  "CAC payback {value:.1f} months exceeds 18-month threshold"),
    AlertRule("A012", "Gross Margin Drop",           "gross_margin",      "HIGH",     0.60, "lt",  "Gross margin {value:.1%} below 60% — COGS analysis required"),
    AlertRule("A013", "MAU Decline",                 "mau_mom_pct",       "HIGH",     0,    "lt",  "MAU declined {value:.1f}% MoM — product engagement review"),
    AlertRule("A014", "Viral K Factor Drop",         "viral_k",           "MEDIUM",   0.3,  "lt",  "Viral K-factor {value:.2f} below 0.3 — referral program review"),
]


def _compare(value: float, threshold: float, operator: str) -> bool:
    ops = {
        "gt":  value >  threshold,
        "lt":  value <  threshold,
        "gte": value >= threshold,
        "lte": value <= threshold,
    }
    return ops.get(operator, False)


def evaluate_alerts(months: list[dict]) -> list[FiredAlert]:
    """
    Evaluates all alert rules against the latest monthly snapshot.
    Returns list of FiredAlert instances for rules that are triggered.
    """
    if not months or len(months) < 2:
        return []

    current = months[-1]
    prior   = months[-2]

    net_new = current.get("new_customers", 0) - current.get("churned_customers", 0)
    mrr_mom = (current["mrr"] - prior["mrr"]) / prior["mrr"] * 100 if prior["mrr"] > 0 else 0
    mau_mom = (current["mau"] - prior["mau"]) / prior["mau"] * 100 if prior["mau"] > 0 else 0

    derived = {
        **current,
        "net_new_customers": net_new,
        "mrr_mom_change": mrr_mom,
        "mau_mom_pct": mau_mom,
    }

    fired = []
    for rule in ALERT_RULES:
        val = derived.get(rule.metric)
        if val is None:
            continue
        if _compare(val, rule.threshold, rule.operator):
            fired.append(FiredAlert(
                rule=rule,
                metric=rule.metric,
                current_value=val,
                threshold=rule.threshold,
                message=rule.message_template.format(value=val),
                month=current["month"],
            ))

    return fired


def alert_summary(months: list[dict]) -> dict:
    alerts = evaluate_alerts(months)
    by_severity = {}
    for a in alerts:
        sev = a.rule.severity
        by_severity.setdefault(sev, []).append(a.message)

    return {
        "month": months[-1]["month"] if months else None,
        "total_fired": len(alerts),
        "by_severity": by_severity,
        "critical_count": len(by_severity.get("CRITICAL", [])),
        "high_count": len(by_severity.get("HIGH", [])),
    }
