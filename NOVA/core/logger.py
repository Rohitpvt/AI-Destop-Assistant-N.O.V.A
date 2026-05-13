import logging
import os
import sys

# Add the parent directory to sys.path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        LOG_FILE = "nova_test.log"

# Setup logging
logging.basicConfig(
    filename=config.LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_event(command, feature, status, error=None):
    """Logs an event with command details, feature used, status, and optional error."""
    msg = f"Command: {command} | Feature: {feature} | Status: {status}"
    if error:
        msg += f" | Error: {error}"
    logging.info(msg)
