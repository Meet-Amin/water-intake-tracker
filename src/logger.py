import logging

logging.basicConfig(
    filename="app.log",
    level=logging.info,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def log_message(message):
    logging.info(message)


def log_error(error_message):
    logging.error(error_message)
