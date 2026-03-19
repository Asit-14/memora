import logging
import sys
import os
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_FILE = "logs/app.log"

def setup_logger():
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT)

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Console handler (for dev)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler (for saving logs)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)

    # Prevent duplicate logs
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()