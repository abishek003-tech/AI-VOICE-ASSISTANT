import logging
import os
import config

logger = logging.getLogger("ai_assistant.brain")

_client = None

def _get_client():
    global _client
    api_key = config.OPENAI_API_KEY
    if not api_key or api_key == "your_api_key_here":
        return None
    if _client is None:
        try:
            from openai import OpenAI
            _client = OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {type(e).__name__}")
            return None
    return _client

def is_ai_available() -> bool:
    """Check if OpenAI API key is configured."""
    return bool(config.OPENAI_API_KEY and config.OPENAI_API_KEY != "your_api_key_here")

def ai_reply(text: str) -> str:
    """Generate conversational AI response using OpenAI API, with safe fallback."""
    if not is_ai_available():
        logger.info("OpenAI API key is missing; returning fallback response.")
        if config.RESPONSE_MODE == "tanglish":
            return "OpenAI API key set panala Abi. Local commands mattum dhaan work aagum."
        return "OpenAI API key is not configured. I can only perform local commands right now."

    client = _get_client()
    if client is None:
        if config.RESPONSE_MODE == "tanglish":
            return "AI service connect panna mudiyala. Config check pannunga."
        return "Unable to connect to the AI service. Please check your configuration."

    try:
        system_instruction = (
            "You are a helpful desktop voice assistant. Keep answers concise, "
            "clear, conversational, and within 1 to 2 sentences so they are easy to speak aloud."
        )
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": text}
            ],
            timeout=10
        )
        reply = response.choices[0].message.content.strip()
        return reply
    except Exception as e:
        error_name = type(e).__name__
        logger.error(f"OpenAI API call failed with {error_name}")
        if "AuthenticationError" in error_name:
            if config.RESPONSE_MODE == "tanglish":
                return "API key thappa iruku. Please check your OpenAI API key."
            return "Your OpenAI API key appears to be invalid. Please check your credentials."
        elif "RateLimitError" in error_name:
            return "OpenAI rate limit reached. Please try again in a moment."
        elif "APIConnectionError" in error_name or "Timeout" in error_name:
            return "Network connection to AI service failed. Please check your internet."
        else:
            return "Sorry, I encountered an error while processing that with AI."
