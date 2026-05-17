import speech_recognition as sr
import os
import sys
import logging

# Ensure parent directory is in system path for clean imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        MIC_DEVICE_INDEX = None
        MIC_ENERGY_THRESHOLD = 300
        MIC_DYNAMIC_ENERGY_THRESHOLD = True
        MIC_PAUSE_THRESHOLD = 0.8
        MIC_LISTEN_TIMEOUT_SECONDS = 8
        MIC_PHRASE_TIME_LIMIT_SECONDS = 12
        MIC_AMBIENT_NOISE_DURATION = 1.0

from core.logger import log_info, log_event

def list_microphones():
    """Lists all available input audio devices on the system.
    
    Returns a dictionary with status, lists of microhpones, or error details.
    """
    try:
        import pyaudio
    except ImportError:
        return {
            "success": False,
            "error_type": "pyaudio_missing",
            "message": "PyAudio is missing or microphone input is unavailable.",
            "devices": []
        }

    try:
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount', 0)
        devices = []
        for i in range(0, numdevices):
            device_info = p.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels', 0) > 0:
                devices.append({
                    "index": i,
                    "name": device_info.get('name', 'Unknown Microphone')
                })
        p.terminate()
        return {
            "success": True,
            "devices": devices,
            "message": f"Successfully listed {len(devices)} input device(s)."
        }
    except Exception as e:
        return {
            "success": False,
            "error_type": "microphone_error",
            "message": f"Failed to query microphone devices: {str(e)}",
            "devices": []
        }

def listen_once(timeout=None, phrase_time_limit=None, device_index=None):
    """Listens once to the microphone and returns a structured diagnostic dictionary.
    
    Returns:
        dict: {
            "success": bool,
            "text": str (recognized query or empty),
            "error_type": str ("timeout" | "unknown_speech" | "request_error" | "microphone_error" | "pyaudio_missing" | "unknown" | None),
            "message": str (friendly diagnostic or success explanation)
        }
    """
    # 1. Check PyAudio dependency early
    try:
        import pyaudio
    except ImportError:
        log_event("listen_once", "Speech", "Failure", "PyAudio is missing.")
        return {
            "success": False,
            "text": "",
            "error_type": "pyaudio_missing",
            "message": "Speech engine requires PyAudio. Please check dependencies."
        }

    # 2. Configure Recognizer
    r = sr.Recognizer()
    r.energy_threshold = getattr(config, "MIC_ENERGY_THRESHOLD", 300)
    r.dynamic_energy_threshold = getattr(config, "MIC_DYNAMIC_ENERGY_THRESHOLD", True)
    r.pause_threshold = getattr(config, "MIC_PAUSE_THRESHOLD", 0.8)

    target_device = device_index if device_index is not None else getattr(config, "MIC_DEVICE_INDEX", None)
    
    # 3. Open Microphone Context
    try:
        mic = sr.Microphone(device_index=target_device)
    except Exception as e:
        log_event("listen_once", "Speech", "Failure", f"Microphone construction error: {str(e)}")
        return {
            "success": False,
            "text": "",
            "error_type": "microphone_error",
            "message": f"Microphone is unavailable (Index: {target_device}). Check device connection."
        }

    # 4. Listen and Transcribe
    try:
        with mic as source:
            # Calibrate for ambient noise
            cal_duration = getattr(config, "MIC_AMBIENT_NOISE_DURATION", 1.0)
            r.adjust_for_ambient_noise(source, duration=cal_duration)
            
            # Listen for phrase
            listen_timeout = timeout if timeout is not None else getattr(config, "MIC_LISTEN_TIMEOUT_SECONDS", 8)
            phrase_limit = phrase_time_limit if phrase_time_limit is not None else getattr(config, "MIC_PHRASE_TIME_LIMIT_SECONDS", 12)
            
            audio = r.listen(source, timeout=listen_timeout, phrase_time_limit=phrase_limit)
    except sr.WaitTimeoutError:
        return {
            "success": False,
            "text": "",
            "error_type": "timeout",
            "message": "I did not hear anything. Please check your microphone or speak closer."
        }
    except Exception as e:
        log_event("listen_once", "Speech", "Failure", f"Microphone capture error: {str(e)}")
        return {
            "success": False,
            "text": "",
            "error_type": "microphone_error",
            "message": f"Microphone error occurred: {str(e)}"
        }

    # 5. Recognize Speech
    try:
        query = r.recognize_google(audio, language='en-in')
        recognized_text = query.strip()
        log_info(f"Speech recognized successfully: [{recognized_text}]")
        return {
            "success": True,
            "text": recognized_text,
            "error_type": None,
            "message": "Speech successfully recognized."
        }
    except sr.UnknownValueError:
        return {
            "success": False,
            "text": "",
            "error_type": "unknown_speech",
            "message": "I heard something, but could not understand it."
        }
    except sr.RequestError as e:
        log_event("listen_once", "Speech", "Failure", f"Google recognition API error: {str(e)}")
        return {
            "success": False,
            "text": "",
            "error_type": "request_error",
            "message": f"Speech recognition service failed: {str(e)}"
        }
    except Exception as e:
        log_event("listen_once", "Speech", "Failure", f"Unexpected recognition error: {str(e)}")
        return {
            "success": False,
            "text": "",
            "error_type": "unknown",
            "message": f"An unexpected speech error occurred: {str(e)}"
        }

def takecommand(force_text=False) -> str:
    """Listens for a command from the microphone and returns it as a string.
    
    Maintains backward compatibility with legacy CLI/Voice modes.
    """
    if force_text:
        return input("Enter command: ").lower().strip()

    result = listen_once()
    if result["success"]:
        return result["text"].lower().strip()
    return ""
