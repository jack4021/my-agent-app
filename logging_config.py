"""Logging configuration for the agent application.

This module sets up structured logging with both file and console handlers,
using rotation to prevent excessive log file growth.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("../logs")
LOG_FILE = LOG_DIR / "agent.log"
MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 3


def setup_logging():
    """Configure logging with file and console handlers.

    Sets up a rotating file handler and console handler with formatted output.
    Also reduces verbosity for third-party libraries (httpx, primp, chainlit).

    Returns:
        logging.Logger: The configured root logger instance.
    """
    LOG_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("primp").setLevel(logging.WARNING)
    logging.getLogger("chainlit").setLevel(logging.WARNING)

    return logger


logger = setup_logging()
