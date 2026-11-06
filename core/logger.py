"""
Core Logging Infrastructure.
Configures color-coded console logs and rotating daily file logging.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config.constants import LOGS_DIR

_logger_initialized = False

def get_logger(name: str = "CuteJARVIS") -> logging.Logger:
    """Return configured application logger."""
    global _logger_initialized
    logger = logging.getLogger(name)

    if not _logger_initialized:
        logger.setLevel(logging.DEBUG)

        # Formatters
        file_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        console_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )

        # Console Stream Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File Handler (5 MB max, 5 backups)
        log_file = LOGS_DIR / "jarvis.log"
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Avoid log propagation doubling
        logger.propagate = False
        _logger_initialized = True

    return logger
