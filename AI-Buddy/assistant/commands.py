from assistant.speak import speak
from assistant.brain import ai_reply
import datetime, sys, subprocess

def handle_command(text):

    if "stop" in text or "exit" in text:
        speak("Goodbye Abi")
        sys.exit()

    elif "time" in text:
        speak(datetime.datetime.now().strftime("%I:%M %p"))

    elif "open chrome" in text:
        subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        speak("Opening Chrome")

    else:
        reply = ai_reply(text)
        speak(reply)
