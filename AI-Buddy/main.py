from assistant.speech import wait_for_wake_word, listen, speak

print("AI Buddy Started")

wait_for_wake_word()

while True:
    command = listen()

    if "stop" in command:
        speak("Bye Abi")
        break
    else:
        speak(f"You said {command}")
