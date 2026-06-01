"""
forecaster.py — FlowSync Trend Extrapolation Module

Implements the forecasting methods defined in skills/forecasting.md.
Provides 3, 6, and 12-month forward projections with confidence bands.

DO NOT use for financial decisions — this operates on synthetic data only.
"""

import math
import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class ForecastPoint:
    month_offset: int    # months ahead (1 = next month)
    p10: float           # pessimistic (10th percentile)
    p50: float           # median
    p90: float           # optimistic (90th percentile)
    method: str


@dataclass
class ForecastResult:
    metric: str
    horizon_months: int
    method: str
    points: list[ForecastPoint]
    note: str = ""


class Forecaster:
    def __init__(self, data: dict, seed: int = 42):
        self.months = data.get("months", [])
        self.seed = seed

    def _trailing_values(self, field: str, n: int = 6) -> list[float]:
        return [m.get(field, 0) for m in self.months[-n:]]

    def _growth_rates(self, values: list[float]) -> list[float]:
        rates = []
        for i in range(1, len(values)):
            if values[i - 1] > 0:
                rates.append((values[i] - values[i - 1]) / values[i - 1])
        return rates

    def forecast_mrr(self, horizon: int = 12, n_simulations: int = 1000) -> ForecastResult:
        """Monte Carlo MRR forecast using trailing 6-month growth distribution."""
        values = self._trailing_values("mrr", 6)
        rates = self._growth_rates(values)
        if not rates:
            return ForecastResult("mrr", horizon, "insufficient_data", [], "Not enough data")

        mean_g = sum(rates) / len(rates)
        std_g = math.sqrt(sum((r - mean_g) ** 2 for r in rates) / len(rates)) if len(rates) > 1 else 0.02
        current_mrr = values[-1]

        rng = random.Random(self.seed)
        points = []

        for t in range(1, horizon + 1):
            sim_values = []
            for _ in range(n_simulations):
                mrr = current_mrr
                for _ in range(t):
                    g = rng.gauss(mean_g, std_g)
                    mrr *= max(0.5, 1 + g)
                sim_values.append(mrr)
            sim_values.sort()
            points.append(ForecastPoint(
                month_offset=t,
                p10=sim_values[int(n_simulations * 0.10)],
                p50=sim_values[int(n_simulations * 0.50)],
                p90=sim_values[int(n_simulations * 0.90)],
                method="monte_carlo"
            ))

        return ForecastResult(
            metric="mrr",
            horizon_months=horizon,
            method="monte_carlo",
            points=points,
            note=f"Based on trailing 6-month mean growth {mean_g*100:.1f}% ± {std_g*100:.1f}%"
        )

    def forecast_churn(self, horizon: int = 6) -> ForecastResult:
        """Linear trend extrapolation for churn rate."""
        values = self._trailing_values("monthly_churn_rate", 12)
        if len(values) < 3:
            return ForecastResult("monthly_churn_rate", horizon, "insufficient_data", [])

        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        slope = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n)) / \
                max(sum((x[i] - x_mean) ** 2 for i in range(n)), 1e-10)
        intercept = y_mean - slope * x_mean

        points = []
        for t in range(1, horizon + 1):
            pred = intercept + slope * (n + t - 1)
            pred = max(0.005, min(0.20, pred))
            noise = abs(slope) * 0.5
            points.append(ForecastPoint(
                month_offset=t,
                p10=max(0.005, pred - noise * 2),
                p50=pred,
                p90=min(0.20, pred + noise * 2),
                method="linear_ols"
            ))

        return ForecastResult(
            metric="monthly_churn_rate",
            horizon_months=horizon,
            method="linear_ols",
            points=points,
            note=f"Slope {slope*100:.3f}pp/month over trailing 12 months"
        )

    def summary(self) -> dict:
        """Return forecast summaries for key metrics."""
        mrr_fc = self.forecast_mrr(horizon=6)
        churn_fc = self.forecast_churn(horizon=6)

        return {
            "mrr_6mo_median": round(mrr_fc.points[-1].p50, 2) if mrr_fc.points else None,
            "mrr_6mo_p10": round(mrr_fc.points[-1].p10, 2) if mrr_fc.points else None,
            "mrr_6mo_p90": round(mrr_fc.points[-1].p90, 2) if mrr_fc.points else None,
            "churn_6mo_forecast": round(churn_fc.points[-1].p50 * 100, 2) if churn_fc.points else None,
        }
