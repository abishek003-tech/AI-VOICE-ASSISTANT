import logging
import os
import sys
import time
from pathlib import Path

# Ensure AI-Buddy directory is on sys.path for direct imports
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

import config
from assistant.commands import handle_command
from assistant.speech import calibrate_noise, listen, speak, wait_for_wake_word
from assistant.state import AssistantState, AssistantStateMachine

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ai_assistant.main")

def main():
    timeout_mins = config.ACTIVE_LISTENING_TIMEOUT_SECONDS / 60.0
    print("=" * 60)
    print(f"      {config.ASSISTANT_NAME} - AI Voice Assistant (Active)")
    print(f"  Wake Word           : '{config.WAKE_WORD}'")
    print(f"  Voice Mode          : {config.RESPONSE_MODE.title()}")
    print(f"  Inactivity Timeout  : {config.ACTIVE_LISTENING_TIMEOUT_SECONDS}s ({timeout_mins:.1f} mins)")
    print("=" * 60)

    # Initial ambient noise calibration
    calibrate_noise(duration=1.0)

    # Initialize state machine
    state_machine = AssistantStateMachine(timeout_seconds=config.ACTIVE_LISTENING_TIMEOUT_SECONDS)

    # Startup announcement
    startup_msg = f"{config.ASSISTANT_NAME} is online. Say '{config.WAKE_WORD}' to get started."
    speak(startup_msg)

    try:
        while True:
            # -----------------------------------------------------------
            # STATE 1: WAKE_WORD_MODE
            # -----------------------------------------------------------
            if state_machine.state == AssistantState.WAKE_WORD_MODE:
                logger.info(f"State: WAKE_WORD_MODE. Waiting for '{config.WAKE_WORD}'...")
                detected, initial_cmd = wait_for_wake_word()

                if not detected:
                    continue

                # Transition into Active Listening Mode
                state_machine.on_wake_word_detected()

                # If the user spoke a command in the same breath (e.g. 'hello launch notepad')
                if initial_cmd:
                    logger.info(f"Direct command with wake word: '{initial_cmd}'")
                    should_exit, _ = handle_command(initial_cmd)
                    state_machine.on_command_executed()
                    if should_exit:
                        logger.info("Shutdown command received. Exiting.")
                        break
                # Otherwise, user already heard greeting ('Yes, how can I help?')

            # -----------------------------------------------------------
            # STATE 2: ACTIVE_LISTENING_MODE
            # -----------------------------------------------------------
            elif state_machine.state == AssistantState.ACTIVE_LISTENING_MODE:
                # Check if user has been inactive for the configured timeout
                if state_machine.check_inactivity_timeout():
                    mins = int(state_machine.timeout_seconds // 60)
                    print(f"\n[Inactivity timeout reached ({mins} mins). Returning to Wake Word Mode.]")
                    if config.RESPONSE_MODE == "tanglish":
                        speak("Inactivity timeout aayiduchu. Wake word solli activate pannunga.")
                    else:
                        speak("Inactivity timeout. Say hello when you need me.")
                    continue

                # Calculate remaining seconds for this chunk
                remaining_secs = state_machine.time_remaining()
                chunk_timeout = min(5, max(1, int(remaining_secs)))

                print(f"[Active Listening | {remaining_secs:.0f}s until sleep...]")

                # Listen for next command without audibly interrupting on minor room noise
                command = listen(timeout=chunk_timeout, prompt_on_unknown=False)

                if not command:
                    # Silence or unintelligible noise: loop to re-check timeout
                    continue

                # If user says the wake word again while already active
                if command.lower() == config.WAKE_WORD:
                    state_machine.record_interaction()
                    ack = "Na ready-aa dhaan iruken, sollunga." if config.RESPONSE_MODE == "tanglish" else "I'm already listening. What can I do for you?"
                    speak(ack)
                    continue

                # Valid user command received
                logger.info(f"Command received in ACTIVE_LISTENING_MODE: '{command}'")

                # Execution time must NOT be penalized as user inactivity:
                should_exit, _ = handle_command(command)

                # Reset inactivity timer immediately after command completes
                state_machine.on_command_executed()

                if should_exit:
                    logger.info("Shutdown command received. Exiting.")
                    break

    except KeyboardInterrupt:
        print("\n[Application interrupted by user. Exiting cleanly.]")
    except Exception as e:
        logger.error(f"Fatal error in main loop: {e}", exc_info=True)
    finally:
        print(f"[{config.ASSISTANT_NAME} session closed.]")

if __name__ == "__main__":
    main()
