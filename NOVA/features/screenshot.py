import pyautogui
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        SCREENSHOT_DIR = os.getcwd()

from core.tts import speak
from core.logger import log_event

def take_screenshot():
    """Takes a screenshot and saves it in the configured directory."""
    try:
        if not os.path.exists(config.SCREENSHOT_DIR):
            os.makedirs(config.SCREENSHOT_DIR)
        
        img = pyautogui.screenshot()
        img_path = os.path.join(config.SCREENSHOT_DIR, "screenshot.png")
        img.save(img_path)
        speak(f"Screenshot saved as {img_path}.")
        print(f"Screenshot saved as {img_path}.")
        log_event("screenshot", "Screenshot", "Success")
    except Exception as e:
        speak(f"Could not take screenshot: {e}")
        print(f"Error taking screenshot: {e}")
        log_event("screenshot", "Screenshot", "Failure", str(e))
