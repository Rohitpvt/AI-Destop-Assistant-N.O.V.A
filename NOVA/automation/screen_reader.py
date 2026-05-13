import os
import sys
import mss
import mss.tools
from PIL import Image
import pytesseract
import logging

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        SCREENSHOT_ANALYSIS_FILE = "data/latest_screen.png"
        OCR_ENABLED = True
        OCR_LANGUAGE = "eng"
        TESSERACT_CMD = ""
        SCREEN_AWARENESS_ENABLED = True

from core.logger import log_event, log_info
from memory.memory_db import scrub_sensitive_text
from ai import intent_classifier

def setup_tesseract():
    """Configures the Tesseract path if provided in config."""
    if config.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

def capture_screen(save_path=None) -> dict:
    """Captures the current primary monitor screenshot."""
    if not config.SCREEN_AWARENESS_ENABLED:
        return {"success": False, "error": "Screen awareness is disabled."}

    save_path = save_path or config.SCREENSHOT_ANALYSIS_FILE
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with mss.mss() as sct:
            # Use the first monitor index
            sct.shot(mon=1, output=save_path)
            
        log_info(f"Screen captured and saved to {save_path}")
        return {"success": True, "path": save_path}
    except Exception as e:
        log_event("capture_screen", "Screen Reader", "Failure", str(e))
        return {"success": False, "error": str(e)}

def extract_text_from_screen(image_path=None) -> dict:
    """Extracts text from a screenshot using OCR."""
    if not config.OCR_ENABLED:
        return {"success": False, "error": "OCR is disabled."}

    image_path = image_path or config.SCREENSHOT_ANALYSIS_FILE
    
    if not os.path.exists(image_path):
        return {"success": False, "error": "Screenshot file not found."}

    try:
        setup_tesseract()
        # Open the image
        img = Image.open(image_path)
        # Perform OCR
        text = pytesseract.image_to_string(img, lang=config.OCR_LANGUAGE)
        
        # Scrub sensitive data immediately
        clean_text = scrub_sensitive_text(text)
        
        return {"success": True, "text": clean_text}
    except Exception as e:
        error_msg = str(e)
        if "tesseract is not installed" in error_msg.lower():
            error_msg = "Tesseract OCR is not installed or not in PATH. Please configure TESSERACT_CMD in .env."
        log_event("extract_text", "Screen Reader", "Failure", error_msg)
        return {"success": False, "error": error_msg}

def analyze_screen_text(text: str) -> str:
    """Summarizes extracted screen text using rule-based logic or LLM."""
    if not text or not text.strip():
        return "The screen appears to be empty or contains no readable text."

    # If LLM is enabled and configured, use it for a smart summary
    from config import has_llm_credentials
    if has_llm_credentials():
        prompt = f"Summarize the following text extracted from a user's screen in 2 sentences. Focus on the main apps, topics, or headings visible:\n\n{text[:2000]}"
        # We can use a lightweight chat call here
        summary = intent_classifier.generate_chat_response(prompt)
        if summary:
            return summary

    # Rule-based fallback summary
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    num_chars = len(text)
    num_lines = len(lines)
    preview = " | ".join(lines[:5])
    
    summary = f"I detected {num_lines} lines of text ({num_chars} characters). "
    if num_lines > 0:
        summary += f"Visible content includes: {preview}..."
    
    return summary

def get_screen_context() -> dict:
    """Full pipeline: Capture -> OCR -> Analyze."""
    capture_res = capture_screen()
    if not capture_res["success"]:
        return capture_res

    ocr_res = extract_text_from_screen(capture_res["path"])
    if not ocr_res["success"]:
        return ocr_res

    summary = analyze_screen_text(ocr_res["text"])
    
    return {
        "success": True,
        "summary": summary,
        "raw_text": ocr_res["text"]
    }
