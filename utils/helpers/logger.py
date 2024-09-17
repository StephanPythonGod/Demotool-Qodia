import logging


def setup_logger() -> logging.Logger:
    """Set up a logger for the application."""
    logger = logging.getLogger("qodia_koodierungstool")
    logger.setLevel(logging.INFO)

    # Create console handler and set level to INFO
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    logger.addHandler(ch)

    return logger


# Create and configure logger
logger = setup_logger()
