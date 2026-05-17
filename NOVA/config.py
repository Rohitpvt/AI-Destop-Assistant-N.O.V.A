import os
import sys
from dotenv import load_dotenv

# Base directory detection
if getattr(sys, 'frozen', False):
    # Running as a bundled executable
    PROJECT_ROOT = os.path.dirname(sys.executable)
    # When bundled, NOVA folder is inside the _internal folder or beside exe
    # But PROJECT_ROOT is where .env and data/ should live.
else:
    # Running as a normal Python script
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

env_path = os.path.join(PROJECT_ROOT, '.env')
print("--- NOVA CONFIGURATION INITIALIZING ---")
print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"Loading .env from: {env_path} (Exists: {os.path.exists(env_path)})")
print(f"NOVA_LLM_ENABLED: {LLM_ENABLED}")
print(f"NVIDIA_API_KEY Present: {bool(NVIDIA_API_KEY) and NVIDIA_API_KEY != 'your_actual_nvidia_key_here'}")
print(f"NVIDIA_BASE_URL: {NVIDIA_BASE_URL}")
print(f"NVIDIA_MODEL: {NVIDIA_MODEL}")
print("---------------------------------------")


def has_llm_credentials():
    """Returns True if LLM is enabled and a valid API key is provided."""
    return LLM_ENABLED and bool(NVIDIA_API_KEY) and NVIDIA_API_KEY != "your_actual_nvidia_key_here"

# --- Screen Awareness / OCR Settings ---
SCREEN_AWARENESS_ENABLED = os.getenv("NOVA_SCREEN_AWARENESS_ENABLED", "true").lower() == "true"
SCREENSHOT_ANALYSIS_FILE = os.path.join(DATA_DIR, "latest_screen.png")
OCR_ENABLED = os.getenv("NOVA_OCR_ENABLED", "true").lower() == "true"
OCR_LANGUAGE = os.getenv("NOVA_OCR_LANGUAGE", "eng")
TESSERACT_CMD = os.getenv("TESSERACT_CMD", os.getenv("NOVA_TESSERACT_CMD", "")).strip()

# --- Safe Automation & Monitoring Settings ---
AUTOMATION_ENABLED = os.getenv("NOVA_AUTOMATION_ENABLED", "true").lower() == "true"
REQUIRE_CONFIRMATION_FOR_ACTIONS = os.getenv("NOVA_REQUIRE_CONFIRMATION_FOR_ACTIONS", "true").lower() == "true"
SYSTEM_MONITORING_ENABLED = os.getenv("NOVA_SYSTEM_MONITORING_ENABLED", "true").lower() == "true"
PYAUTOGUI_FAILSAFE = True
AUTOMATION_PAUSE_SECONDS = 0.2

# --- Skill System Settings ---
SKILLS_ENABLED = os.getenv("NOVA_SKILLS_ENABLED", "true").lower() == "true"
SKILL_CONFIRMATION_REQUIRED = os.getenv("NOVA_SKILL_CONFIRMATION_REQUIRED", "true").lower() == "true"
MAX_SKILL_STEPS = int(os.getenv("NOVA_MAX_SKILL_STEPS", "5"))
SAVE_SKILL_OUTPUTS = os.getenv("NOVA_SAVE_SKILL_OUTPUTS", "true").lower() == "true"

# --- Voice Wake Mode Settings ---
WAKE_MODE_ENABLED = os.getenv("NOVA_WAKE_MODE_ENABLED", "false").lower() == "true"
WAKE_WORDS = [w.strip().lower() for w in os.getenv("NOVA_WAKE_WORDS", "nova,hey nova,wake up nova").split(",")]
SLEEP_WORDS = [w.strip().lower() for w in os.getenv("NOVA_SLEEP_WORDS", "sleep,go to sleep,stop listening").split(",")]
EXIT_WORDS = [w.strip().lower() for w in os.getenv("NOVA_EXIT_WORDS", "exit,quit,shutdown nova").split(",")]
def _parse_int_env(key, default):
    val = os.getenv(key, "")
    return int(val) if val.strip().isdigit() else default

def _parse_float_env(key, default):
    val = os.getenv(key, "")
    try:
        return float(val)
    except ValueError:
        return default

def _parse_bool_env(key, default):
    val = os.getenv(key, "").strip().lower()
    if not val:
        return default
    return val == "true"

def _parse_mic_index(key, default):
    val = os.getenv(key, "").strip()
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        return default

MIC_DEVICE_INDEX = _parse_mic_index("NOVA_MIC_DEVICE_INDEX", None)
MIC_ENERGY_THRESHOLD = _parse_int_env("NOVA_MIC_ENERGY_THRESHOLD", 300)
MIC_DYNAMIC_ENERGY_THRESHOLD = _parse_bool_env("NOVA_MIC_DYNAMIC_ENERGY_THRESHOLD", True)
MIC_PAUSE_THRESHOLD = _parse_float_env("NOVA_MIC_PAUSE_THRESHOLD", 0.8)
MIC_LISTEN_TIMEOUT_SECONDS = _parse_int_env("NOVA_MIC_LISTEN_TIMEOUT_SECONDS", 8)
MIC_PHRASE_TIME_LIMIT_SECONDS = _parse_int_env("NOVA_PHRASE_TIME_LIMIT_SECONDS", 12)
MIC_AMBIENT_NOISE_DURATION = _parse_float_env("NOVA_MIC_AMBIENT_NOISE_DURATION", 1.0)

# Backward-compatible references for older codebases
LISTEN_TIMEOUT_SECONDS = MIC_LISTEN_TIMEOUT_SECONDS
PHRASE_TIME_LIMIT_SECONDS = MIC_PHRASE_TIME_LIMIT_SECONDS
WAKE_LISTEN_INTERVAL_SECONDS = 1
VOICE_CONFIRMATION_ENABLED = os.getenv("NOVA_VOICE_CONFIRMATION_ENABLED", "true").lower() == "true"
VOICE_OUTPUT_ENABLED = os.getenv("NOVA_VOICE_OUTPUT_ENABLED", "true").lower() == "true"

# --- GUI Settings ---
GUI_ENABLED = os.getenv("NOVA_GUI_ENABLED", "true").lower() == "true"
GUI_THEME = os.getenv("NOVA_GUI_THEME", "dark")
GUI_WINDOW_TITLE = os.getenv("NOVA_GUI_WINDOW_TITLE", "NOVA Desktop Assistant")
GUI_WIDTH = int(os.getenv("NOVA_GUI_WIDTH", "1000"))
GUI_HEIGHT = int(os.getenv("NOVA_GUI_HEIGHT", "700"))
GUI_SHOW_LOG_PANEL = os.getenv("NOVA_GUI_SHOW_LOG_PANEL", "true").lower() == "true"
GUI_SHOW_MEMORY_PANEL = os.getenv("NOVA_GUI_SHOW_MEMORY_PANEL", "true").lower() == "true"

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
