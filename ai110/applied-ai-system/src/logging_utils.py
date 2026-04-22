"""
Tiny JSONL logging helper.

Why JSONL: each line is a complete JSON object, so logs can be parsed line by
line without any custom parser (jq, pandas, etc.).
"""
import json
import logging
import time
from pathlib import Path
from typing import Any


def get_logger(
    name: str,
    log_path: str = "logs/recommender.jsonl",
) -> logging.Logger:
    """
    Return a logger that writes one JSON object per line to ``log_path``.

    Idempotent: calling twice with the same name returns the same logger and
    does not attach a duplicate handler.
    """
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Emit one structured log record as a single JSON line."""
    payload = {"ts": time.time(), "event": event, **fields}
    logger.info(json.dumps(payload, default=str))
