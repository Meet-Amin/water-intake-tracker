import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def log_message(message: str) -> None:
    """Log a standard info-level message."""
    logging.info(message)
