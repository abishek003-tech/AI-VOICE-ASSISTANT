from assistant.speech import wait_for_wake_word, listen
from assistant.commands import handle_command

print("AI Buddy Started")

wait_for_wake_word()

while True:
    command = listen()
    if command:
        handle_command(command)
