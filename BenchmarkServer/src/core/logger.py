import logging
import os
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
    """Simple logger with file and console output"""
    logger = logging.getLogger(name)
    if logger.handlers:  # Return existing logger if already configured
        return logger

    logger.setLevel(logging.INFO)

    # Create logs directory
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # File handler
    file_handler = logging.FileHandler(
        os.path.join(logs_dir, f'benchmark_{datetime.now().strftime("%Y%m%d")}.log')
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger 