import datetime
import logging
import sys
from typing import Tuple

import config
from assistant.actions import ActionResult
from assistant.ai_brain import ai_reply
from assistant.app_control import close_application, launch_application, resolve_app_key
from assistant.calculator import solve_math_expression
from assistant.features import get_joke, search_wikipedia
from assistant.intent import IntentType, parse_intent
from assistant.media import open_youtube, play_youtube
from assistant.speech import speak

logger = logging.getLogger("ai_assistant.commands")

def handle_command(text: str) -> Tuple[bool, str]:
    """
    Process recognized user speech with dynamic spoken status updates and verified outcomes.
    Communicates primarily through natural speech across all supported commands.

    Returns:
        (should_exit: bool, response_text: str)
    """
    if not text or not text.strip():
        return False, ""

    parsed = parse_intent(text)
    logger.info(f"Parsed intent: {parsed.intent_type.name}, entity: '{parsed.entity}'")

    # 1. Stop / Exit
    if parsed.intent_type == IntentType.STOP:
        if config.RESPONSE_MODE == "tanglish":
            msg = "Goodbye Abi, ungalukku help panna mudinjadhula sandhosham."
        else:
            msg = "Goodbye Abi, shutting down."
        speak(msg)
        return True, msg

    # 2. Calculations & Mathematical questions (Fast, safe AST solver)
    elif parsed.intent_type == IntentType.CALCULATION:
        res = solve_math_expression(parsed.entity or text)
        speak(res.message)
        return False, res.message

    # 3. Time
    elif parsed.intent_type == IntentType.TIME:
        now_str = datetime.datetime.now().strftime("%I:%M %p")
        if config.RESPONSE_MODE == "tanglish":
            msg = f"Ippo time {now_str}."
        else:
            msg = f"The current time is {now_str}."
        speak(msg)
        return False, msg

    # 4. Joke
    elif parsed.intent_type == IntentType.JOKE:
        if config.RESPONSE_MODE == "tanglish":
            intro = "Ungalukku oru joke."
        else:
            intro = "Here's a joke for you."
        speak(intro)

        joke = get_joke()
        speak(joke)
        return False, joke

    # 5. Wikipedia / Information
    elif parsed.intent_type == IntentType.WIKIPEDIA:
        query = parsed.entity or ""
        if not query:
            msg = "Enna pathi thedanum? Sollunga." if config.RESPONSE_MODE == "tanglish" else "What topic should I search for on Wikipedia?"
            speak(msg)
            return False, msg

        if config.RESPONSE_MODE == "tanglish":
            status_msg = f"Wikipedia-la {query} theduren."
        else:
            status_msg = f"Searching Wikipedia for {query}."
        speak(status_msg)

        result = search_wikipedia(query)
        speak(result)
        return False, result

    # 6. Media: Open YouTube homepage
    elif parsed.intent_type == IntentType.MEDIA_OPEN:
        status_msg = "YouTube open panren." if config.RESPONSE_MODE == "tanglish" else "Opening YouTube."
        speak(status_msg)

        res = open_youtube()
        speak(res.message)
        return False, res.message

    # 7. Media: Play YouTube song / artist / video dynamically
    elif parsed.intent_type == IntentType.MEDIA_PLAY:
        query = (parsed.entity or "").strip()
        if not query:
            msg = "Enna paatu play pannanum? Sollunga." if config.RESPONSE_MODE == "tanglish" else "What song or video would you like me to play?"
            speak(msg)
            return False, msg

        # Dynamic spoken status announcement before starting search
        if config.RESPONSE_MODE == "tanglish":
            status_msg = f"Sure, YouTube-la {query} theduren."
        else:
            status_msg = f"Searching YouTube for {query}."
        speak(status_msg)

        res = play_youtube(query)
        # Truthful outcome announcement (e.g. "Playing Kalyani song now." or unconfirmed search fallback)
        speak(res.message)
        return False, res.message

    # 8. Application Launching (Dynamic application targets)
    elif parsed.intent_type == IntentType.APP_OPEN:
        app_name = parsed.entity or ""
        app_key = resolve_app_key(app_name)
        display_name = config.APP_REGISTRY[app_key]["display_name"] if app_key else app_name.title()

        # Dynamic status announcement before launching
        if config.RESPONSE_MODE == "tanglish":
            status_msg = f"{display_name} open panren."
        else:
            status_msg = f"Opening {display_name}."
        speak(status_msg)

        res = launch_application(app_name)
        # Verified outcome announcement (e.g. "Chrome is open." or failure message)
        speak(res.message)
        return False, res.message

    # 9. Application Closing (Dynamic application targets)
    elif parsed.intent_type == IntentType.APP_CLOSE:
        app_name = parsed.entity or ""
        app_key = resolve_app_key(app_name)
        display_name = config.APP_REGISTRY[app_key]["display_name"] if app_key else app_name.title()

        # Dynamic status announcement before closing
        if config.RESPONSE_MODE == "tanglish":
            status_msg = f"{display_name} close panren."
        else:
            status_msg = f"Closing {display_name}."
        speak(status_msg)

        res = close_application(app_name)
        # Verified outcome announcement (e.g. "Chrome is closed." or "Chrome is not open.")
        speak(res.message)
        return False, res.message

    # 10. Cultural / Personality Easter Eggs
    elif parsed.intent_type == IntentType.WHO_IS_GOD:
        msg = "Ajitheyyy Kadavuleyy"
        speak(msg)
        return False, msg

    elif parsed.intent_type == IntentType.NAME:
        msg = f"My name is {config.ASSISTANT_NAME}, your personal Artificial Intelligence."
        speak(msg)
        return False, msg

    # 11. General AI Conversation / Fallback
    else:
        reply = ai_reply(text)
        speak(reply)
        return False, reply
