import logging
import sys

from src.config.settings import settings


def configure_logging() -> None:
    """Configure structured logging for the application."""
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )
