import psutil
import os
import sys

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        SYSTEM_MONITORING_ENABLED = True

try:
    import pygetwindow as gw
except ImportError:
    gw = None

def get_system_status() -> dict:
    """Collects current system resource usage."""
    if not config.SYSTEM_MONITORING_ENABLED:
        return {"success": False, "error": "System monitoring is disabled."}

    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        battery = psutil.sensors_battery()
        
        active_window = "Unknown"
        if gw:
            try:
                win = gw.getActiveWindow()
                if win:
                    active_window = win.title
            except:
                pass

        # TTS Diagnostics
        tts_enabled = getattr(config, 'VOICE_OUTPUT_ENABLED', True)
        pyttsx3_status = "Available"
        try:
            import pyttsx3
        except ImportError:
            pyttsx3_status = "Not Installed"
            
        pythoncom_status = "Available"
        try:
            import pythoncom
        except ImportError:
            pythoncom_status = "Not Installed"

        from core.tts import get_last_tts_error, get_active_voice_info
        last_err = get_last_tts_error()
        voice_info = get_active_voice_info()

        # Tesseract / OCR Diagnostics
        tesseract_configured = bool(getattr(config, 'TESSERACT_CMD', ''))
        tesseract_path = getattr(config, 'TESSERACT_CMD', '')
        tesseract_exists = os.path.exists(tesseract_path) if (tesseract_configured and tesseract_path) else False
        ocr_available = getattr(config, 'OCR_ENABLED', True) and tesseract_configured and tesseract_exists

        return {
            "success": True,
            "cpu_percent": cpu_usage,
            "ram_percent": ram.percent,
            "ram_available_gb": round(ram.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "battery_percent": battery.percent if battery else None,
            "battery_plugged": battery.power_plugged if battery else None,
            "active_window": active_window,
            "tts_enabled": tts_enabled,
            "pyttsx3_status": pyttsx3_status,
            "pythoncom_status": pythoncom_status,
            "active_voice_name": voice_info.get("name", "None"),
            "active_voice_id": voice_info.get("id", "None"),
            "last_tts_error": last_err,
            "tesseract_configured": tesseract_configured,
            "tesseract_path": tesseract_path,
            "tesseract_exists": tesseract_exists,
            "ocr_available": ocr_available
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def summarize_system_status() -> str:
    """Returns a user-friendly string summary of the system status."""
    status = get_system_status()
    if not status["success"]:
        return f"Could not get system status: {status.get('error')}"

    summary = f"Your system is currently using {status['cpu_percent']}% of the CPU and {status['ram_percent']}% of the RAM. "
    summary += f"You have {status['ram_available_gb']} GB of memory available. "
    
    if status['battery_percent'] is not None:
        state = "plugged in" if status['battery_plugged'] else "on battery"
        summary += f"Your battery is at {status['battery_percent']}% and is {state}. "

    summary += f"The current active window is {status['active_window']}."
    summary += f" Voice output is {'enabled' if status.get('tts_enabled', True) else 'disabled'} (Active Voice: {status.get('active_voice_name', 'None')})."
    if status.get('last_tts_error'):
        summary += f" Note: Last speech error was: {status['last_tts_error']}."
    
    summary += f" Screen OCR is {'fully available' if status.get('ocr_available') else 'unavailable (configure Tesseract)'}."
    return summary
