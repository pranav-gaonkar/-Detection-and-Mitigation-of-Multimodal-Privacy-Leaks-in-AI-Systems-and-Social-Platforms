"""Logging helpers for LeakWatch."""

from __future__ import annotations

import logging
from pathlib import Path

_LOGGER: logging.Logger | None = None


def get_logger(name: str = "leakwatch") -> logging.Logger:
    global _LOGGER
    if _LOGGER is None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
        _LOGGER = logging.getLogger(name)
    return logging.getLogger(name)


def ensure_dir(path: Path) -> None:
    """Create parent directory if missing."""

    path.parent.mkdir(parents=True, exist_ok=True)
