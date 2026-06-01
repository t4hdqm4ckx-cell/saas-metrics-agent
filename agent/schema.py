"""
schema.py — FlowSync Data Schema Definitions

Pydantic-free schema validation for the synthetic_data.json output.
Uses dataclasses and manual validation to avoid external dependencies.
"""

from dataclasses import dataclass, fields as dc_fields
from typing import Optional


SCHEMA_VERSION = "1.0"

REQUIRED_MONTH_FIELDS = [
    "month", "mrr", "arr", "new_mrr", "expansion_mrr", "contraction_mrr",
    "churned_mrr", "nrr", "total_customers", "new_customers", "churned_customers",
    "trial_starts", "trial_conversions", "trial_conversion_rate",
    "mau", "dau", "stickiness", "viral_k",
    "ltv", "cac", "ltv_cac_ratio", "payback_months",
    "gross_margin", "burn_rate", "runway_months", "arpu",
    "monthly_churn_rate", "plan_breakdown",
]

REQUIRED_PLAN_BREAKDOWN_KEYS = ["starter", "pro", "business"]


def validate_month(month: dict, index: int) -> list[str]:
    """Validate a single monthly snapshot dict. Returns list of error strings."""
    errors = []

    for field in REQUIRED_MONTH_FIELDS:
        if field not in month:
            errors.append(f"[month {index}] Missing required field: {field}")

    if "mrr" in month and month["mrr"] < 0:
        errors.append(f"[month {index}] MRR cannot be negative: {month['mrr']}")

    if "monthly_churn_rate" in month:
        cr = month["monthly_churn_rate"]
        if not (0 <= cr <= 1):
            errors.append(f"[month {index}] churn_rate must be 0–1: {cr}")

    if "gross_margin" in month:
        gm = month["gross_margin"]
        if not (0 <= gm <= 1):
            errors.append(f"[month {index}] gross_margin must be 0–1: {gm}")

    if "plan_breakdown" in month:
        for plan in REQUIRED_PLAN_BREAKDOWN_KEYS:
            if plan not in month["plan_breakdown"]:
                errors.append(f"[month {index}] Missing plan: {plan}")
            elif "customers" not in month["plan_breakdown"][plan]:
                errors.append(f"[month {index}] plan {plan} missing 'customers'")

    return errors


def validate_dataset(data: dict) -> list[str]:
    """Validate the full synthetic_data.json structure. Returns error list."""
    errors = []

    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"Unexpected schema_version: {data.get('schema_version')}")

    months = data.get("months", [])
    if not months:
        errors.append("Dataset contains no monthly snapshots")
        return errors

    for i, month in enumerate(months):
        errors.extend(validate_month(month, i))

    return errors


if __name__ == "__main__":
    import json
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "../data/synthetic_data.json"
    with open(path) as f:
        data = json.load(f)

    errors = validate_dataset(data)
    if errors:
        print(f"Schema validation FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print(f"Schema validation PASSED — {len(data['months'])} months, schema v{data['schema_version']}")
