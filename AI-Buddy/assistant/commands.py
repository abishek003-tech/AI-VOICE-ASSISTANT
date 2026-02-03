from assistant.speech import speak
from assistant.ai_brain import ai_reply
from assistant.features import get_joke, search_wikipedia
import datetime, sys, subprocess

def handle_command(text):

    if "stop" in text or "exit" in text:
        speak("Goodbye Abi")
        sys.exit()

    elif "time" in text:
        speak(datetime.datetime.now().strftime("%I:%M %p"))

    elif "joke" in text:
        joke = get_joke()
        print("Joke:", joke)
        speak(joke)

    elif "wikipedia" in text:
        query = text.replace("wikipedia", "").strip()
        speak(f"Searching Wikipedia for {query}")
        result = search_wikipedia(query)
        print("Wiki result:", result)
        speak(result)

    elif "open chrome" in text:
        subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        speak("Opening Chrome")

    else:
        reply = ai_reply(text)
        speak(reply)
