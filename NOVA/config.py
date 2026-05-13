import os
import sys
from dotenv import load_dotenv

# Base directory of the project
# This assumes the config.py is in the NOVA/ folder
NOVA_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(NOVA_DIR)

# Load environment variables from .env file
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# --- Project Paths ---
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# --- Assistant Identity ---
DEFAULT_NAME = os.getenv("NOVA_ASSISTANT_NAME", "NOVA")
NAME_FILE = os.path.join(DATA_DIR, "assistant_name.txt")

# --- Feature Directories ---
MUSIC_DIR = os.getenv("NOVA_MUSIC_DIR") or os.path.expanduser("~\\Music")
NOTES_DIR = os.getenv("NOVA_NOTES_DIR") or os.path.join(PROJECT_ROOT, "notes")
SCREENSHOT_DIR = os.getenv("NOVA_SCREENSHOT_DIR") or os.path.join(PROJECT_ROOT, "screenshots")

# --- Memory Settings ---
MEMORY_DB_PATH = os.path.join(DATA_DIR, "nova_memory.db")
MEMORY_ENABLED = os.getenv("NOVA_MEMORY_ENABLED", "true").lower() == "true"
MEMORY_MAX_RECENT = int(os.getenv("NOVA_MEMORY_MAX_RECENT", "10"))

# --- AI/LLM Settings ---
LLM_ENABLED = os.getenv("NOVA_LLM_ENABLED", "false").lower() == "true"
LLM_TIMEOUT = int(os.getenv("NOVA_LLM_TIMEOUT", "20"))
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1.5")

def has_llm_credentials():
    """Returns True if LLM is enabled and an API key is provided."""
    return LLM_ENABLED and bool(NVIDIA_API_KEY)

# --- Logging Settings ---
LOG_FILE = os.path.join(LOG_DIR, "nova.log")
LOG_LEVEL = os.getenv("NOVA_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
MAX_LOG_SIZE_MB = 5
LOG_BACKUP_COUNT = 3

# --- Application Paths ---
APP_PATHS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vscode": os.path.expanduser("~\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
}

# --- Browser Settings ---
CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"

# --- Automatic Directory Creation ---
def ensure_directories():
    """Creates required project directories if they don't exist."""
    dirs = [DATA_DIR, LOG_DIR, NOTES_DIR, SCREENSHOT_DIR]
    for d in dirs:
        if not os.path.exists(d):
            try:
                os.makedirs(d)
                print(f"Created directory: {d}")
            except Exception as e:
                print(f"Warning: Could not create directory {d}: {e}")

# Run setup
ensure_directories()
