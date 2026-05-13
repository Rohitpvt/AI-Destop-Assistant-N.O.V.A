import logging
from logging.handlers import RotatingFileHandler
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        LOG_FILE = "nova.log"
        LOG_LEVEL = "INFO"
        LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
        MAX_LOG_SIZE_MB = 5
        LOG_BACKUP_COUNT = 3

# Setup Logger
logger = logging.getLogger("NOVA")
logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

# File Handler (Rotating)
file_handler = RotatingFileHandler(
    config.LOG_FILE,
    maxBytes=config.MAX_LOG_SIZE_MB * 1024 * 1024,
    backupCount=config.LOG_BACKUP_COUNT
)
file_formatter = logging.Formatter(config.LOG_FORMAT)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console Handler
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)
# logger.addHandler(console_handler) # Keep terminal output handled by print for now as per project style

def log_event(command, feature, status, error=None):
    """Logs an event with command details, feature used, status, and optional error."""
    msg = f"Command: [{command}] | Feature: [{feature}] | Status: [{status}]"
    if error:
        msg += f" | Error: {error}"
    
    if status.lower() == "failure" or error:
        logger.error(msg)
    else:
        logger.info(msg)

def log_info(msg):
    logger.info(msg)

def log_error(msg):
    logger.error(msg)
