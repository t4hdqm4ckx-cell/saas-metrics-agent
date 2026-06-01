"""
agent.py — FlowSync SaaS Metrics Agent Orchestrator

Entry point for the data generation and metrics computation pipeline.
DO NOT run this in production without setting environment variables.
See CLAUDE.md for environment variable reference.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

from data_generator import DataGenerator
from metrics_calculator import MetricsCalculator

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
SEED = int(os.getenv("FLOWSYNC_SEED", "42"))
MONTHS = int(os.getenv("FLOWSYNC_MONTHS", "24"))
OUTPUT_DIR = Path(os.getenv("FLOWSYNC_OUTPUT_DIR", "../data"))

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("../logs/app.log", mode="a"),
    ],
)
logger = logging.getLogger("flowsync.agent")


def run() -> int:
    logger.info("FlowSync Metrics Agent starting")
    logger.info(f"Config: seed={SEED}, months={MONTHS}, output={OUTPUT_DIR}")
    start_time = time.monotonic()

    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / "synthetic_data.json"

        logger.info("Phase 1: Generating synthetic data")
        gen = DataGenerator(seed=SEED, months=MONTHS)
        snapshots = gen.generate()
        data = gen.to_json(snapshots)

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Wrote {len(snapshots)} monthly snapshots to {output_path}")

        logger.info("Phase 2: Computing derived metrics")
        calc = MetricsCalculator(data)
        summary = calc.growth_summary()
        latest = calc.latest_snapshot()

        logger.info(
            f"Summary: MRR ${summary['mrr_start']:,.0f} → ${summary['mrr_end']:,.0f} "
            f"(+{summary['mrr_growth_total_pct']}%), "
            f"Customers {summary['customer_start']} → {summary['customer_end']}, "
            f"Avg NRR {summary['avg_nrr']}%"
        )

        if latest:
            logger.info(
                f"Latest ({latest['month']}): MRR=${latest['mrr']:,.0f}, "
                f"Churn={latest['monthly_churn_rate']*100:.1f}%, "
                f"LTV:CAC={latest['ltv_cac_ratio']:.1f}×"
            )

        elapsed = time.monotonic() - start_time
        logger.info(f"FlowSync Metrics Agent completed in {elapsed:.2f}s")
        return 0

    except Exception as e:
        logger.error(f"Unhandled exception in agent run: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(run())
