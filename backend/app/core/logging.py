"""Shared logging setup used by both the API (main.py) and the pipeline (run.py)."""

import logging

from app.config import settings

# Noisy third-party libraries whose DEBUG-level logs (raw HTTP/2 frames, header
# tables, etc.) are almost never useful and can blow up log output by orders
# of magnitude. Capped at WARNING regardless of our own log level below.
_NOISY_LOGGERS = ("httpx", "httpcore", "hpack", "openai")


def setup_logging() -> None:
    level = logging.DEBUG if settings.environment == "development" else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
        force=True,
    )

    for logger_name in _NOISY_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
