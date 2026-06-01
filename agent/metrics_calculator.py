"""
metrics_calculator.py — FlowSync KPI Computation Layer

Computes derived SaaS metrics from raw monthly snapshots.
All division operations guard against zero denominators per ERROR_HANDLING.md E303.
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("flowsync.metrics_calculator")

SIGMA_THRESHOLD = 3.0  # E304: outlier detection


@dataclass
class MetricSummary:
    metric: str
    current: float
    prior_month: Optional[float]
    mom_change_pct: Optional[float]
    yoy_change_pct: Optional[float]
    trailing_3mo_avg: Optional[float]
    is_outlier: bool
    low_confidence: bool


class MetricsCalculator:
    def __init__(self, data: dict):
        self.raw = data
        self.months = data.get("months", [])

    def _safe_div(self, numerator: float, denominator: float, fallback=None):
        if denominator == 0 or denominator is None:
            logger.warning(f"E303: zero denominator in metric calculation — returning {fallback}")
            return fallback
        return numerator / denominator

    def _mom_change(self, values: list[float], idx: int) -> Optional[float]:
        if idx == 0 or values[idx - 1] == 0:
            return None
        return (values[idx] - values[idx - 1]) / values[idx - 1] * 100

    def _yoy_change(self, values: list[float], idx: int) -> Optional[float]:
        if idx < 12 or values[idx - 12] == 0:
            return None
        return (values[idx] - values[idx - 12]) / values[idx - 12] * 100

    def _trailing_avg(self, values: list[float], idx: int, window: int = 3) -> Optional[float]:
        start = max(0, idx - window + 1)
        slice_ = values[start:idx + 1]
        return sum(slice_) / len(slice_) if slice_ else None

    def _is_outlier(self, values: list[float], idx: int) -> bool:
        if len(values) < 4:
            return False
        import math
        prior = values[max(0, idx - 6):idx]
        if len(prior) < 3:
            return False
        mean = sum(prior) / len(prior)
        variance = sum((x - mean) ** 2 for x in prior) / len(prior)
        std = math.sqrt(variance) if variance > 0 else 0
        if std == 0:
            return False
        z = abs(values[idx] - mean) / std
        if z > SIGMA_THRESHOLD:
            logger.warning(f"E304: Outlier detected at index {idx} — z={z:.2f}")
            return True
        return False

    def summarize(self, field: str) -> list[MetricSummary]:
        values = [m.get(field, 0) for m in self.months]
        summaries = []
        for i, val in enumerate(values):
            summaries.append(MetricSummary(
                metric=field,
                current=val,
                prior_month=values[i - 1] if i > 0 else None,
                mom_change_pct=self._mom_change(values, i),
                yoy_change_pct=self._yoy_change(values, i),
                trailing_3mo_avg=self._trailing_avg(values, i),
                is_outlier=self._is_outlier(values, i),
                low_confidence=(self.months[i].get("total_customers", 999) < 30),
            ))
        return summaries

    def nrr_series(self) -> list[float]:
        result = []
        for i, m in enumerate(self.months):
            if i == 0:
                result.append(100.0)
                continue
            prior = self.months[i - 1]["mrr"]
            nrr = self._safe_div(
                prior + m["expansion_mrr"] - m["contraction_mrr"] - m["churned_mrr"],
                prior,
                fallback=None
            )
            result.append(round(nrr * 100, 2) if nrr is not None else None)
        return result

    def ltv_cac_series(self) -> list[dict]:
        result = []
        for m in self.months:
            ltv = m.get("ltv", 0)
            cac = m.get("cac", 0)
            ratio = self._safe_div(ltv, cac)
            result.append({
                "month": m["month"],
                "ltv": ltv,
                "cac": cac,
                "ratio": round(ratio, 2) if ratio is not None else None,
            })
        return result

    def cohort_retention_matrix(self) -> list[list[Optional[float]]]:
        """
        Simulates a cohort retention matrix from monthly data.
        Row = acquisition cohort (month index), Column = months since acquisition.
        Returns a 12×12 matrix (first 12 cohorts, up to 12 months retention).
        """
        import math
        matrix = []
        n_cohorts = min(12, len(self.months))
        for i in range(n_cohorts):
            churn_rate = self.months[i]["monthly_churn_rate"]
            row = []
            for t in range(12):
                if i + t >= len(self.months):
                    row.append(None)
                else:
                    retention = math.exp(-churn_rate * t * 1.2)
                    noise = 1 + (hash(f"{i}{t}") % 100 - 50) / 500.0
                    row.append(round(min(1.0, max(0.0, retention * noise)), 3))
            matrix.append(row)
        return matrix

    def waterfall_data(self) -> list[dict]:
        result = []
        for m in self.months:
            result.append({
                "month": m["month"],
                "new_mrr": m.get("new_mrr", 0),
                "expansion_mrr": m.get("expansion_mrr", 0),
                "contraction_mrr": -m.get("contraction_mrr", 0),
                "churned_mrr": -m.get("churned_mrr", 0),
                "net_new_mrr": (
                    m.get("new_mrr", 0)
                    + m.get("expansion_mrr", 0)
                    - m.get("contraction_mrr", 0)
                    - m.get("churned_mrr", 0)
                ),
            })
        return result

    def latest_snapshot(self) -> Optional[dict]:
        return self.months[-1] if self.months else None

    def growth_summary(self) -> dict:
        if len(self.months) < 2:
            return {}
        first = self.months[0]
        last = self.months[-1]
        return {
            "mrr_start": first["mrr"],
            "mrr_end": last["mrr"],
            "mrr_growth_total_pct": round(
                self._safe_div(last["mrr"] - first["mrr"], first["mrr"], 0) * 100, 1
            ),
            "customer_start": first["total_customers"],
            "customer_end": last["total_customers"],
            "customer_growth_total_pct": round(
                self._safe_div(
                    last["total_customers"] - first["total_customers"],
                    first["total_customers"], 0
                ) * 100, 1
            ),
            "avg_monthly_churn": round(
                sum(m["monthly_churn_rate"] for m in self.months) / len(self.months) * 100, 2
            ),
            "avg_nrr": round(
                sum(m["nrr"] for m in self.months) / len(self.months), 1
            ),
        }
