import pyttsx3
import speech_recognition as sr

# Init TTS
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 175)

recognizer = sr.Recognizer()
mic = sr.Microphone()


def speak(text):
    engine.say(text)
    engine.runAndWait()


def wait_for_wake_word():
    speak("AI Buddy started. Say hello to wake me up.")
    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio).lower()
            print("Heard:", text)
            if "hello" in text:
                speak("Hi Abi, na ready iruken. Sollu.")
                return
        except:
            pass


def listen():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio).lower()
        print("You said:", text)
        return text
    except:
        speak("Sorry, puriyala. Thirumba sollu.")
        return ""
