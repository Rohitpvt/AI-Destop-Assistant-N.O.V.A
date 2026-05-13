import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Folders
MUSIC_DIR = os.path.expanduser("~\\Music")
SCREENSHOT_DIR = BASE_DIR
NOTES_DIR = BASE_DIR

# Files
LOG_FILE = os.path.join(BASE_DIR, "nova_test.log")
NAME_FILE = os.path.join(BASE_DIR, "assistant_name.txt")
DEFAULT_NAME = "NOVA"

# App Paths (Customize these for your system)
APP_PATHS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vscode": os.path.expanduser("~\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
}

# Browser Settings
CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
