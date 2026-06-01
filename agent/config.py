"""
config.py — FlowSync Agent Configuration

Centralized configuration with environment variable loading and validation.
All agent modules should import settings from here rather than reading
environment variables directly.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentConfig:
    """Immutable agent configuration loaded from environment."""

    seed: int = 42
    months: int = 24
    start_year: int = 2024
    start_month: int = 6
    output_dir: str = "data"
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/app.log"

    plan_prices: dict = field(default_factory=lambda: {
        "starter": 12.0,
        "pro": 29.0,
        "business": 79.0,
    })

    @classmethod
    def from_env(cls) -> "AgentConfig":
        return cls(
            seed=int(os.getenv("FLOWSYNC_SEED", "42")),
            months=int(os.getenv("FLOWSYNC_MONTHS", "24")),
            start_year=int(os.getenv("FLOWSYNC_START_YEAR", "2024")),
            start_month=int(os.getenv("FLOWSYNC_START_MONTH", "6")),
            output_dir=os.getenv("FLOWSYNC_OUTPUT_DIR", "data"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            log_file=os.getenv("FLOWSYNC_LOG_FILE", "logs/app.log") or None,
        )

    def validate(self) -> list[str]:
        """Returns list of validation error messages. Empty = valid."""
        errors = []
        if self.months < 1 or self.months > 120:
            errors.append(f"months must be 1–120, got {self.months}")
        if self.start_month < 1 or self.start_month > 12:
            errors.append(f"start_month must be 1–12, got {self.start_month}")
        if self.start_year < 2000 or self.start_year > 2100:
            errors.append(f"start_year must be 2000–2100, got {self.start_year}")
        if self.log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            errors.append(f"invalid log_level: {self.log_level}")
        return errors


DEFAULT_CONFIG = AgentConfig()
