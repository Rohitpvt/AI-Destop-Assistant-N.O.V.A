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
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

def get_client():
    """Returns an OpenAI-compatible client configured for NVIDIA's API."""
    if not OpenAI or not config.has_llm_credentials():
        return None
    try:
        client = OpenAI(
            base_url=config.NVIDIA_BASE_URL,
            api_key=config.NVIDIA_API_KEY,
            max_retries=0
        )
        return client
    except Exception as e:
        print(f"Error initializing AI client: {e}")
        return None

def call_llm(messages, temperature=0.2, max_tokens=500):
    """Makes a request to the LLM and returns the response content."""
    client = get_client()
    if not client:
        return "[Error] AI client not initialized. Check credentials or dependencies."

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
        return "[Error] Empty response from AI service."
    except Exception as e:
        err_msg = ""
        if openai:
            if isinstance(e, openai.APITimeoutError):
                err_msg = "[Error] AI request timed out. Please try again."
            elif isinstance(e, openai.AuthenticationError):
                err_msg = "[Error] Authentication failed. Check your NVIDIA_API_KEY."
            elif isinstance(e, openai.RateLimitError):
                err_msg = "[Error] Rate limit exceeded. Please try again later."
            elif isinstance(e, openai.APIConnectionError):
                err_msg = "[Error] Connection failed. Check your internet connection."
            elif isinstance(e, openai.APIStatusError):
                err_msg = f"[Error] API status error (Code: {getattr(e, 'status_code', 'unknown')})."
            elif isinstance(e, openai.APIError):
                err_msg = f"[Error] API error: {str(e)}"
            else:
                err_msg = f"[Error] Unexpected AI error: {str(e)}"
        else:
            err_msg = f"[Error] AI Error: {str(e)}"

        logging.error(f"LLM Call Error: {str(e)}")
        print(f"LLM Error: {str(e)}")
        return err_msg

