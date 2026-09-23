"""
Centralized logging configuration.

Every module in the project should import the logger from here.

Example:
    from config.logging_config import logger
"""

import sys
from pathlib import Path

from loguru import logger

from config.settings import LOG_DIR, settings


def configure_logging() -> None:
    """
    Configure Loguru for console and file logging.
    """

    logger.remove()

    # Console Logger
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
    )

    # File Logger
    logger.add(
        Path(LOG_DIR) / "app.log",
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        level=settings.LOG_LEVEL,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )


configure_logging()


