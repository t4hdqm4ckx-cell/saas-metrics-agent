"""
reporter.py — FlowSync Narrative Report Generator

Template-based executive summary generation following skills/reporting.md rules.
Produces plain-English summaries without requiring an LLM.
"""

from typing import Optional


def _direction(pct_change: float, positive_is_good: bool = True) -> str:
    if pct_change > 0.5:
        return "increased" if positive_is_good else "worsened"
    if pct_change < -0.5:
        return "decreased" if positive_is_good else "improved"
    return "held steady"


def revenue_narrative(current: dict, prior: dict) -> str:
    if not prior or prior.get("mrr", 0) == 0:
        return f"MRR stands at ${current['mrr']:,.0f} (no prior period for comparison)."

    delta_pct = (current["mrr"] - prior["mrr"]) / prior["mrr"] * 100
    nrr = current.get("nrr", 0)

    if delta_pct > 15:
        momentum = "exceptional"
    elif delta_pct > 5:
        momentum = "healthy"
    elif delta_pct > 0:
        momentum = "moderate"
    else:
        momentum = "declining"

    nrr_desc = "strong" if nrr > 110 else "adequate" if nrr > 100 else "below-target"

    return (
        f"MRR {'grew' if delta_pct > 0 else 'declined'} {abs(delta_pct):.1f}% MoM "
        f"to ${current['mrr']:,.0f} ({momentum} momentum). "
        f"Net Revenue Retention of {nrr:.1f}% reflects {nrr_desc} expansion dynamics. "
        f"Churned MRR of ${current.get('churned_mrr', 0):,.0f} remained the primary revenue headwind."
    )


def churn_narrative(current: dict, prior: Optional[dict] = None) -> str:
    rate = current.get("monthly_churn_rate", 0) * 100
    churned = current.get("churned_customers", 0)

    if rate < 3:
        assessment = "Churn remained well-controlled"
        action = "No immediate action required."
    elif rate < 4:
        assessment = f"Churn of {rate:.1f}% warrants monitoring"
        action = "Review month-3 cohort onboarding completion rates."
    elif rate < 6:
        assessment = f"Churn elevated at {rate:.1f}%"
        action = "Initiate win-back campaign for recently churned accounts."
    else:
        assessment = f"⚠️ Churn spike to {rate:.1f}%"
        action = "Immediate investigation required — escalate to CS leadership."

    mom_note = ""
    if prior:
        prior_rate = prior.get("monthly_churn_rate", 0) * 100
        delta = rate - prior_rate
        mom_note = f" ({'+' if delta >= 0 else ''}{delta:.2f}pp MoM)."

    return f"{assessment} at {rate:.1f}%{mom_note} ({churned} customers). {action}"


def engagement_narrative(current: dict) -> str:
    stickiness = current.get("stickiness", 0) * 100
    viral_k = current.get("viral_k", 0)
    mau = current.get("mau", 0)
    dau = current.get("dau", 0)

    stick_desc = "excellent" if stickiness > 40 else "healthy" if stickiness > 25 else "below target"
    viral_desc = "strong viral component" if viral_k > 0.5 else "moderate referral activity"

    return (
        f"MAU of {mau:,} with {dau:,} daily active users yields {stickiness:.1f}% stickiness ({stick_desc}). "
        f"Viral K-factor of {viral_k:.2f} indicates {viral_desc} in growth."
    )


def unit_economics_narrative(current: dict) -> str:
    ltv = current.get("ltv", 0)
    cac = current.get("cac", 0)
    ratio = current.get("ltv_cac_ratio", 0)
    payback = current.get("payback_months", 0)

    ratio_desc = "world-class" if ratio > 10 else "excellent" if ratio > 5 else "healthy" if ratio > 3 else "below target"

    return (
        f"LTV of ${ltv:,.0f} against CAC of ${cac:.0f} yields a {ratio:.1f}× ratio ({ratio_desc}). "
        f"CAC payback period of {payback:.1f} months is "
        f"{'exceptional (target <12 months)' if payback < 6 else 'on target' if payback < 12 else 'above 12-month target'}."
    )


def monthly_report(months: list[dict]) -> dict:
    """Generate a complete monthly narrative report."""
    if not months:
        return {}

    current = months[-1]
    prior = months[-2] if len(months) >= 2 else None

    return {
        "month": current["month"],
        "revenue": revenue_narrative(current, prior),
        "churn": churn_narrative(current, prior),
        "engagement": engagement_narrative(current),
        "unit_economics": unit_economics_narrative(current),
        "headline_kpis": {
            "mrr": current.get("mrr"),
            "arr": current.get("arr"),
            "customers": current.get("total_customers"),
            "nrr": current.get("nrr"),
            "churn_rate_pct": round(current.get("monthly_churn_rate", 0) * 100, 2),
            "ltv_cac": current.get("ltv_cac_ratio"),
        }
    }
