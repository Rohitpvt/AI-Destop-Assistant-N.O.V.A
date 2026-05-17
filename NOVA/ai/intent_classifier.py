import json
import logging
from ai import llm_client, prompts

def classify_intent_with_llm(command: str, recent_memory=None) -> dict:
    """Uses the LLM to classify user intent into a structured JSON format."""
    if not command:
        return {"intent": "unknown", "confidence": 0.0}

    messages = [
        {"role": "system", "content": prompts.INTENT_CLASSIFICATION_PROMPT},
    ]
    
    if recent_memory:
        history_text = "\n".join([f"User: {m[1]} | Assistant: {m[2]}" for m in recent_memory])
        messages.append({"role": "system", "content": f"Recent Context:\n{history_text}"})
    
    messages.append({"role": "user", "content": command})

    response_text = llm_client.call_llm(messages)
    
    if not response_text:
        return {"intent": "unknown", "confidence": 0.0, "reasoning": "LLM failed to respond."}

    if response_text.startswith("[Error]"):
        return {"intent": "unknown", "confidence": 0.0, "reasoning": response_text}


    # Clean the response in case the LLM included markdown or extra text
    clean_json = response_text.strip()
    if clean_json.startswith("```json"):
        clean_json = clean_json[7:-3].strip()
    elif clean_json.startswith("```"):
        clean_json = clean_json[3:-3].strip()

    try:
        classification = json.loads(clean_json)
        # Ensure minimal keys exist
        if "intent" not in classification:
            classification["intent"] = "unknown"
        if "confidence" not in classification:
            classification["confidence"] = 0.5
        return classification
    except json.JSONDecodeError:
        logging.error(f"Failed to parse LLM JSON response: {response_text}")
        return {"intent": "unknown", "confidence": 0.0, "reasoning": "Invalid JSON from LLM."}

def generate_chat_response(command, recent_memory=None):
    """Generates a conversational response for general chat queries."""
    messages = [
        {"role": "system", "content": prompts.CHAT_RESPONSE_PROMPT},
    ]
    
    if recent_memory:
        history_text = "\n".join([f"User: {m[1]} | Assistant: {m[2]}" for m in recent_memory])
        messages.append({"role": "system", "content": f"Recent Context:\n{history_text}"})
    
    messages.append({"role": "user", "content": command})

    return llm_client.call_llm(messages, temperature=0.6)
