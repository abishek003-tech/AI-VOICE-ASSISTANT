from enum import Enum, auto
import re
from typing import NamedTuple, Optional
import config

class IntentType(Enum):
    APP_OPEN = auto()
    APP_CLOSE = auto()
    MEDIA_OPEN = auto()
    MEDIA_PLAY = auto()
    CALCULATION = auto()
    TIME = auto()
    JOKE = auto()
    WIKIPEDIA = auto()
    WHO_IS_GOD = auto()
    NAME = auto()
    STOP = auto()
    GENERAL_AI = auto()

class ParsedIntent(NamedTuple):
    intent_type: IntentType
    entity: Optional[str] = None
    raw_text: str = ""

def parse_intent(text: str) -> ParsedIntent:
    """Classify user's spoken command into a structured intent and extract relevant entities."""
    raw = text.strip()
    clean = raw.lower()

    # 1. Stop / Exit commands
    if clean in ["stop", "exit", "quit", "bye", "goodbye"] or clean.startswith("stop ") or clean.startswith("exit "):
        return ParsedIntent(IntentType.STOP, raw_text=raw)

    # 2. Cultural Easter Eggs / Preserved Persona Responses
    if "who is god" in clean:
        return ParsedIntent(IntentType.WHO_IS_GOD, raw_text=raw)
    if "what is your name" in clean or "who are you" in clean:
        return ParsedIntent(IntentType.NAME, raw_text=raw)

    # 3. Time queries
    if re.search(r"\b(time|what time is it|current time)\b", clean):
        return ParsedIntent(IntentType.TIME, raw_text=raw)

    # 4. Joke queries
    if "joke" in clean:
        return ParsedIntent(IntentType.JOKE, raw_text=raw)

    # 5. Wikipedia queries
    if "wikipedia" in clean:
        query = clean.replace("wikipedia", "").replace("search", "").replace("for", "").strip()
        return ParsedIntent(IntentType.WIKIPEDIA, entity=query, raw_text=raw)

    # 6. YouTube & Media commands (Check before generic 'open' commands)
    # Check "open youtube and play <song>" or "search youtube for <song>" or "play <song> on youtube"
    if "youtube and play" in clean:
        query = clean.split("youtube and play")[-1].strip()
        query = re.sub(r"\s+(on|in)\s+youtube$", "", query).strip()
        return ParsedIntent(IntentType.MEDIA_PLAY, entity=query, raw_text=raw)

    if clean.startswith("play ") or " play " in clean:
        # Extract query after 'play'
        match = re.search(r"\bplay\s+(.*)", clean)
        query = match.group(1).strip() if match else ""
        query = re.sub(r"\s+(on|in)\s+youtube$", "", query).strip()
        return ParsedIntent(IntentType.MEDIA_PLAY, entity=query, raw_text=raw)

    if "on youtube" in clean or clean.startswith("search youtube"):
        # e.g., "search youtube for kalyani songs" or "kalyani songs on youtube"
        query = clean.replace("search youtube for", "").replace("search youtube", "").replace("on youtube", "").strip()
        query = re.sub(r"\s+(on|in)\s+youtube$", "", query).strip()
        return ParsedIntent(IntentType.MEDIA_PLAY, entity=query, raw_text=raw)

    if clean in ["open youtube", "launch youtube", "youtube"]:
        return ParsedIntent(IntentType.MEDIA_OPEN, raw_text=raw)

    # 7. Calculations and mathematical questions
    if ("square root" in clean or "sqrt" in clean or 
        clean.startswith("calculate") or clean.startswith("solve") or
        re.search(r"\b(plus|minus|times|multiplied by|divided by|into)\b", clean)):
        # Ensure this is not an explicit app launch/close command like "open calculator"
        if not re.search(r"\b(open|launch|start|run|close|terminate|kill|shut down)\s+(calculator|calc)\b", clean):
            return ParsedIntent(IntentType.CALCULATION, entity=raw, raw_text=raw)

    # 8. Application Launching
    # Matches: "open chrome", "can you launch notepad", "please start calculator", "run vs code"
    open_match = re.search(r"\b(open|launch|start|run)\s+(.+)", clean)
    if open_match:
        app_name = open_match.group(2).strip()
        # Remove polite filler words
        for filler in ["please", "can you", "could you", "the", "program", "app", "application"]:
            app_name = re.sub(rf"\b{filler}\b", "", app_name).strip()

        # Check if the requested app is actually in APP_REGISTRY
        for reg_key in config.APP_REGISTRY:
            if reg_key in app_name or app_name in reg_key:
                return ParsedIntent(IntentType.APP_OPEN, entity=reg_key, raw_text=raw)

    # Check direct app mentions (e.g., "notepad", "calculator")
    for reg_key in config.APP_REGISTRY:
        if clean == reg_key or clean == f"open {reg_key}":
            return ParsedIntent(IntentType.APP_OPEN, entity=reg_key, raw_text=raw)

    # 8. Application Closing
    close_match = re.search(r"\b(close|exit|terminate|kill|shut down|quit)\s+(.+)", clean)
    if close_match:
        app_name = close_match.group(2).strip()
        for filler in ["please", "the", "program", "app", "application"]:
            app_name = re.sub(rf"\b{filler}\b", "", app_name).strip()

        for reg_key in config.APP_REGISTRY:
            if reg_key in app_name or app_name in reg_key:
                return ParsedIntent(IntentType.APP_CLOSE, entity=reg_key, raw_text=raw)

    # 9. Fallback to General AI / LLM
    return ParsedIntent(IntentType.GENERAL_AI, entity=raw, raw_text=raw)
