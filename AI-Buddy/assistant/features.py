import logging
import wikipedia
import pyjokes
import config

logger = logging.getLogger("ai_assistant.features")

def get_joke() -> str:
    """Retrieve a random programming/general joke."""
    try:
        joke = pyjokes.get_joke()
        logger.info(f"Retrieved joke: {joke}")
        return joke
    except Exception as e:
        logger.error(f"Failed to fetch joke: {e}")
        return "Why do programmers prefer dark mode? Because light attracts bugs!"

def search_wikipedia(query: str, sentences: int = 2) -> str:
    """Search Wikipedia and return a concise summary."""
    clean_query = query.strip()
    if not clean_query:
        return "Please specify a topic to search on Wikipedia."

    try:
        logger.info(f"Searching Wikipedia for: {clean_query}")
        summary = wikipedia.summary(clean_query, sentences=sentences)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        logger.info(f"Wikipedia disambiguation for {clean_query}: {e.options[:3]}")
        options = ", ".join(e.options[:3])
        if config.RESPONSE_MODE == "tanglish":
            return f"Idhula pala vishayam iruku. Example: {options}. Konjam specific-aa sollunga."
        return f"There are multiple topics for that. Such as {options}. Please be more specific."
    except wikipedia.exceptions.PageError:
        logger.warning(f"No Wikipedia page found for: {clean_query}")
        if config.RESPONSE_MODE == "tanglish":
            return f"Wikipedia-la '{clean_query}' pathi edhum kedaikala."
        return f"I couldn't find any Wikipedia article for '{clean_query}'."
    except Exception as e:
        logger.error(f"Wikipedia search error: {e}")
        return "An error occurred while retrieving Wikipedia information."
