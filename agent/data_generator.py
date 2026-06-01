"""
data_generator.py — FlowSync Synthetic B2C SaaS Data Engine

Generates 24 months of realistic SaaS subscription metrics for FlowSync,
a fictional B2C productivity app with three tiers (Starter $12, Pro $29, Business $79).

DO NOT run in production without configuring FLOWSYNC_SEED and output paths.
"""

import json
import math
import random
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Optional
import os

logger = logging.getLogger("flowsync.data_generator")

PLAN_PRICES = {"starter": 12.0, "pro": 29.0, "business": 79.0}
PLAN_MIX_MATURE = {"starter": 0.52, "pro": 0.35, "business": 0.13}

SEASONALITY = {
    1: 1.10,   # Jan: new year
    2: 0.97,
    3: 1.02,
    4: 1.05,
    5: 1.03,
    6: 0.98,
    7: 0.93,
    8: 0.88,   # Aug: summer slowdown
    9: 1.02,
    10: 1.08,
    11: 1.14,  # Nov: pre-holiday
    12: 1.18,  # Dec: gifting / resolutions
}


@dataclass
class PlanBreakdown:
    customers: int
    mrr: float


@dataclass
class MonthlySnapshot:
    month: str
    mrr: float
    arr: float
    new_mrr: float
    expansion_mrr: float
    contraction_mrr: float
    churned_mrr: float
    nrr: float
    total_customers: int
    new_customers: int
    churned_customers: int
    trial_starts: int
    trial_conversions: int
    trial_conversion_rate: float
    mau: int
    dau: int
    stickiness: float
    viral_k: float
    ltv: float
    cac: float
    ltv_cac_ratio: float
    payback_months: float
    gross_margin: float
    burn_rate: float
    runway_months: float
    arpu: float
    monthly_churn_rate: float
    plan_breakdown: dict

    def to_dict(self) -> dict:
        d = asdict(self)
        d["plan_breakdown"] = {
            k: {"customers": v["customers"], "mrr": round(v["mrr"], 2)}
            for k, v in d["plan_breakdown"].items()
        }
        for field in ["mrr", "arr", "new_mrr", "expansion_mrr", "contraction_mrr",
                      "churned_mrr", "nrr", "arpu", "ltv", "cac", "ltv_cac_ratio",
                      "payback_months", "gross_margin", "burn_rate"]:
            d[field] = round(d[field], 2)
        d["viral_k"] = round(d["viral_k"], 3)
        d["stickiness"] = round(d["stickiness"], 3)
        d["trial_conversion_rate"] = round(d["trial_conversion_rate"], 4)
        d["monthly_churn_rate"] = round(d["monthly_churn_rate"], 4)
        return d


class DataGenerator:
    def __init__(self, seed: int = 42, months: int = 24, start_year: int = 2024, start_month: int = 6):
        self.seed = seed
        self.months = months
        self.start_year = start_year
        self.start_month = start_month
        random.seed(seed)

    def _month_label(self, offset: int) -> str:
        y = self.start_year + (self.start_month - 1 + offset) // 12
        m = (self.start_month - 1 + offset) % 12 + 1
        return f"{y}-{m:02d}"

    def _seasonal_factor(self, offset: int) -> float:
        m = (self.start_month - 1 + offset) % 12 + 1
        return SEASONALITY[m]

    def _growth_rate(self, offset: int) -> float:
        """Tapering growth: starts high (~18%), decays to ~5% by month 24."""
        base = 0.18 * math.exp(-0.07 * offset) + 0.045
        noise = random.gauss(0, 0.015)
        return max(0.01, base + noise)

    def _churn_rate(self, offset: int) -> float:
        """Churn improves over time: 5.8% → 3.1%."""
        base = 0.031 + (0.027 * math.exp(-0.09 * offset))
        noise = random.gauss(0, 0.003)
        return max(0.015, min(0.10, base + noise))

    def _trial_conversion(self, offset: int) -> float:
        """Trial conversion improves as onboarding matures: 15% → 22%."""
        base = 0.22 - (0.07 * math.exp(-0.08 * offset))
        noise = random.gauss(0, 0.015)
        return max(0.08, min(0.35, base + noise))

    def _gross_margin(self, offset: int) -> float:
        """Gross margin scales with revenue: 65% → 78%."""
        base = 0.78 - (0.13 * math.exp(-0.10 * offset))
        noise = random.gauss(0, 0.008)
        return max(0.55, min(0.85, base + noise))

    def _viral_k(self, offset: int) -> float:
        """Viral coefficient grows with product maturity: 0.32 → 0.62."""
        base = 0.62 - (0.30 * math.exp(-0.07 * offset))
        noise = random.gauss(0, 0.03)
        return max(0.10, min(0.95, base + noise))

    def generate(self) -> list[MonthlySnapshot]:
        snapshots = []

        customers = 412
        mrr = 18500.0
        cash_reserve = 2_400_000.0

        plan_mix = {
            "starter": {"frac": 0.65, "customers": 0, "mrr": 0.0},
            "pro":     {"frac": 0.28, "customers": 0, "mrr": 0.0},
            "business":{"frac": 0.07, "customers": 0, "mrr": 0.0},
        }

        for offset in range(self.months):
            month_label = self._month_label(offset)
            seasonal = self._seasonal_factor(offset)
            churn_rate = self._churn_rate(offset)
            conv_rate = self._trial_conversion(offset)
            gross_margin = self._gross_margin(offset)
            viral_k = self._viral_k(offset)

            # --- Churn ---
            churned_customers = max(1, int(round(customers * churn_rate * random.uniform(0.9, 1.1))))
            churned_mrr = churned_customers * (mrr / max(customers, 1))

            # --- Trials ---
            base_trials = int(60 + offset * 18 + random.gauss(0, 10))
            trial_starts = max(20, int(base_trials * seasonal))
            trial_conversions = int(trial_starts * conv_rate)

            # --- Viral new customers ---
            viral_new = int(customers * viral_k * 0.008 * seasonal)

            # --- Organic growth ---
            new_customers = trial_conversions + viral_new + random.randint(5, 25)
            net_customers = new_customers - churned_customers
            customers = max(50, customers + net_customers)

            # --- Expansion / Contraction ---
            expansion_customers = int(customers * 0.018 * seasonal)
            contraction_customers = int(customers * 0.006)
            expansion_mrr = expansion_customers * (PLAN_PRICES["business"] - PLAN_PRICES["pro"]) * 0.5
            contraction_mrr = contraction_customers * (PLAN_PRICES["pro"] - PLAN_PRICES["starter"])

            # --- Revenue growth ---
            growth = self._growth_rate(offset) * seasonal
            new_mrr = new_customers * (mrr / max(customers, 1)) * 1.05
            prior_mrr = mrr
            mrr = max(mrr * (1 + growth * 0.3),
                      prior_mrr + new_mrr + expansion_mrr - contraction_mrr - churned_mrr)

            arr = mrr * 12
            nrr = (prior_mrr + expansion_mrr - contraction_mrr - churned_mrr) / max(prior_mrr, 1) * 100
            arpu = mrr / max(customers, 1)

            # --- Plan breakdown ---
            t = min(1.0, offset / 18.0)
            starter_frac = 0.65 * (1 - t) + 0.52 * t
            pro_frac = 0.28 * (1 - t) + 0.35 * t
            biz_frac = 1 - starter_frac - pro_frac

            starter_c = int(customers * starter_frac)
            pro_c = int(customers * pro_frac)
            biz_c = max(0, customers - starter_c - pro_c)

            plan_breakdown = {
                "starter": {"customers": starter_c, "mrr": starter_c * PLAN_PRICES["starter"]},
                "pro":     {"customers": pro_c,     "mrr": pro_c * PLAN_PRICES["pro"]},
                "business":{"customers": biz_c,     "mrr": biz_c * PLAN_PRICES["business"]},
            }

            # --- Engagement ---
            mau = int(customers * random.uniform(3.2, 4.1) + random.gauss(0, 80))
            stickiness = min(0.65, 0.38 + offset * 0.003 + random.gauss(0, 0.02))
            dau = int(mau * stickiness)

            # --- Unit economics ---
            cac_spend = new_customers * random.uniform(60, 90)
            cac = cac_spend / max(new_customers, 1)
            ltv = arpu / max(churn_rate, 0.001)
            ltv_cac = ltv / max(cac, 1)
            payback = cac / max(arpu * gross_margin, 0.01)

            # --- Burn ---
            opex = mrr * 0.85 * (1 - gross_margin)
            burn_rate = max(0, opex - mrr * gross_margin * 0.1)
            cash_reserve -= burn_rate
            runway = cash_reserve / max(burn_rate, 1)

            snapshot = MonthlySnapshot(
                month=month_label,
                mrr=round(mrr, 2),
                arr=round(arr, 2),
                new_mrr=round(new_mrr, 2),
                expansion_mrr=round(expansion_mrr, 2),
                contraction_mrr=round(contraction_mrr, 2),
                churned_mrr=round(churned_mrr, 2),
                nrr=round(nrr, 2),
                total_customers=customers,
                new_customers=new_customers,
                churned_customers=churned_customers,
                trial_starts=trial_starts,
                trial_conversions=trial_conversions,
                trial_conversion_rate=round(conv_rate, 4),
                mau=mau,
                dau=dau,
                stickiness=round(stickiness, 3),
                viral_k=round(viral_k, 3),
                ltv=round(ltv, 2),
                cac=round(cac, 2),
                ltv_cac_ratio=round(ltv_cac, 2),
                payback_months=round(payback, 2),
                gross_margin=round(gross_margin, 4),
                burn_rate=round(burn_rate, 2),
                runway_months=round(min(runway, 999), 1),
                arpu=round(arpu, 2),
                monthly_churn_rate=round(churn_rate, 4),
                plan_breakdown=plan_breakdown,
            )
            snapshots.append(snapshot)
            logger.debug(f"Generated {month_label}: MRR=${mrr:,.0f}, Customers={customers}")

        return snapshots

    def to_json(self, snapshots: list[MonthlySnapshot]) -> dict:
        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "schema_version": "1.0",
            "company": "FlowSync",
            "seed": self.seed,
            "months_generated": self.months,
            "start_month": f"{self.start_year}-{self.start_month:02d}",
            "plan_prices": PLAN_PRICES,
            "months": [s.to_dict() for s in snapshots],
        }

    def save(self, output_path: str) -> None:
        snapshots = self.generate()
        data = self.to_json(snapshots)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(snapshots)} months to {output_path}")
        print(f"[data_generator] Generated {len(snapshots)} months → {output_path}")


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

    parser = argparse.ArgumentParser(description="FlowSync synthetic data generator")
    parser.add_argument("--months", type=int, default=24)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default="../data/synthetic_data.json")
    args = parser.parse_args()

    gen = DataGenerator(seed=args.seed, months=args.months)
    gen.save(args.output)
