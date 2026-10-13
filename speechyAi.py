"""
speechyAi.py - Root Launcher & Backwards-Compatible Interface

This file bridges the root workspace entry point directly to the authoritative,
modular AI-Buddy assistant architecture.
"""

import os
import sys
from pathlib import Path

# Ensure AI-Buddy package is accessible
ai_buddy_dir = Path(__file__).resolve().parent / "AI-Buddy"
if str(ai_buddy_dir) not in sys.path:
    sys.path.insert(0, str(ai_buddy_dir))

import config
from assistant.app_control import close_application, launch_application
from assistant.commands import handle_command
from assistant.media import play_youtube
from assistant.speech import calibrate_noise, listen, speak, wait_for_wake_word

# Backwards-compatible function aliases
def open_software(software_name: str):
    """Launch software or YouTube playback via the new action registry."""
    if "play" in software_name.lower():
        res = play_youtube(software_name)
    else:
        res = launch_application(software_name)
    speak(res.message)
    return res.success

def close_software(software_name: str):
    """Close software using safe process discovery."""
    res = close_application(software_name)
    speak(res.message)
    return res.success

def listen_for_wake_word():
    """Wait for the configured wake word."""
    return wait_for_wake_word()

def cmd() -> bool:
    """Capture a single command and process it."""
    text = listen(timeout=6)
    if not text:
        return False
    should_exit, _ = handle_command(text)
    return should_exit

def main():
    """Main execution loop delegating to AI-Buddy."""
    from main import main as run_assistant
    run_assistant()

if __name__ == "__main__":
    main()
