import os
import sys
import logging

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        NVIDIA_API_KEY = ""
        NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
        NVIDIA_MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
        LLM_TIMEOUT = 20

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def get_client():
    """Returns an OpenAI-compatible client configured for NVIDIA's API."""
    if not OpenAI or not config.has_llm_credentials():
        return None
    try:
        client = OpenAI(
            base_url=config.NVIDIA_BASE_URL,
            api_key=config.NVIDIA_API_KEY
        )
        return client
    except Exception as e:
        print(f"Error initializing AI client: {e}")
        return None

def call_llm(messages, temperature=0.2, max_tokens=500):
    """Makes a request to the LLM and returns the response content."""
    client = get_client()
    if not client:
        return None

    try:
        response = client.chat.completions.create(
            model=config.NVIDIA_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=config.LLM_TIMEOUT
        )
        if response and response.choices:
            return response.choices[0].message.content
        return None
    except Exception as e:
        # Log error safely without exposing key
        logging.error(f"LLM API Call Error: {str(e)}")
        print(f"LLM Error: {str(e)}")
        return None
