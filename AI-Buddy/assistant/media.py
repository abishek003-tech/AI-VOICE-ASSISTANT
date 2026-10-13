import logging
import urllib.parse
import webbrowser
import config
from assistant.actions import ActionResult

logger = logging.getLogger("ai_assistant.media")

def open_youtube() -> ActionResult:
    """Open YouTube home page in the default web browser."""
    try:
        webbrowser.open("https://www.youtube.com")
        if config.RESPONSE_MODE == "tanglish":
            msg = "YouTube open panniten."
        else:
            msg = "YouTube is open."
        return ActionResult(success=True, message=msg, detail="Opened YouTube homepage")
    except Exception as e:
        logger.error(f"Failed to open YouTube: {e}")
        fail_msg = "Sorry, YouTube open panna mudiyala." if config.RESPONSE_MODE == "tanglish" else "Sorry, I couldn't open YouTube."
        return ActionResult(success=False, message=fail_msg, detail=str(e))

def play_youtube(query: str) -> ActionResult:
    """Search for and play a video or song on YouTube."""
    clean_query = query.strip()
    # Remove redundant command prefixes
    prefixes_to_strip = [
        "open youtube and play",
        "search youtube for",
        "search for",
        "play on youtube",
        "play youtube",
        "play"
    ]
    for prefix in prefixes_to_strip:
        if clean_query.lower().startswith(prefix):
            clean_query = clean_query[len(prefix):].strip()
            break

    # Strip suffix 'on youtube' if present
    if clean_query.lower().endswith("on youtube"):
        clean_query = clean_query[:-10].strip()

    if not clean_query:
        if config.RESPONSE_MODE == "tanglish":
            msg = "Enna paatu play pannanum? Sollunga."
        else:
            msg = "What song or video would you like me to play?"
        return ActionResult(success=False, message=msg, detail="Query was empty")

    try:
        import pywhatkit
        logger.info(f"Dispatching YouTube playback for query: {clean_query}")
        pywhatkit.playonyt(clean_query)
        if config.RESPONSE_MODE == "tanglish":
            msg = f"Ippo {clean_query} play panren."
        else:
            msg = f"Playing {clean_query} now."
        return ActionResult(success=True, message=msg, detail=f"Dispatched pywhatkit playback for '{clean_query}'")
    except Exception as e:
        logger.warning(f"pywhatkit.playonyt failed ({e}); falling back to browser search URL.")
        try:
            encoded = urllib.parse.quote_plus(clean_query)
            search_url = f"https://www.youtube.com/results?search_query={encoded}"
            webbrowser.open(search_url)
            if config.RESPONSE_MODE == "tanglish":
                msg = f"Ippo {clean_query} play panren."
            else:
                msg = f"Playing {clean_query} now."
            return ActionResult(success=True, message=msg, detail=f"Fallback search URL opened: {search_url}")
        except Exception as browser_err:
            logger.error(f"Failed to open YouTube search URL: {browser_err}")
            fail_msg = f"Sorry, YouTube-la {clean_query} theda mudiyala." if config.RESPONSE_MODE == "tanglish" else f"Sorry, I couldn't play {clean_query} on YouTube."
            return ActionResult(success=False, message=fail_msg, detail=str(browser_err))
