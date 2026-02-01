def speak(text):
    engine.stop()
    engine.say(text)
    engine.runAndWait()
