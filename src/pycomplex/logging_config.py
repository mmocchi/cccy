"""Logging configuration for pycomplex."""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "WARNING",
    format_string: Optional[str] = None,
    enable_file_logging: bool = False,
    log_file: str = "pycomplex.log",
) -> None:
    """Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        enable_file_logging: Whether to enable file logging
        log_file: Path to log file (if file logging is enabled)

    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.WARNING)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=format_string,
        handlers=[],  # Start with no handlers
    )

    # Add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(format_string)
    console_handler.setFormatter(console_formatter)

    # Get the root logger and add console handler
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)

    # Add file handler if requested
    if enable_file_logging:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Name for the logger (typically __name__)

    Returns:
        Logger instance

    """
    return logging.getLogger(name)
