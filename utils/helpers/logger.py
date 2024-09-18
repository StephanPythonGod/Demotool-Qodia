import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "qodia_koodierungstool",
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger for the application.

    This function configures a logger with the specified name, log level,
    format, and optional file output.

    Args:
        name (str): The name of the logger. Defaults to "qodia_koodierungstool".
        level (int): The logging level. Defaults to logging.INFO.
        log_format (Optional[str]): The log message format. If None, a default format is used.
        log_file (Optional[str]): The path to a log file. If provided, logs will be written to this file.

    Returns:
        logging.Logger: A configured logger instance.

    Raises:
        ValueError: If an invalid logging level is provided.
    """
    if not isinstance(level, int):
        raise ValueError("Invalid logging level. Must be an integer.")

    logger = logging.getLogger(name)

    # Prevent adding handlers multiple times
    if not logger.hasHandlers():
        logger.setLevel(level)

        # Use default format if none is provided
        if log_format is None:
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        formatter = logging.Formatter(log_format)

        # Create console handler and set level
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # If a log file is specified, add a file handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


# Create and configure logger
logger = setup_logger()
