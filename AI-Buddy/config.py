import os
import sys
from pathlib import Path

# Load .env file if available
try:
    from dotenv import load_dotenv
    # Look for .env in current directory, parent directory, or AI-Buddy directory
    current_dir = Path(__file__).resolve().parent
    env_paths = [
        current_dir / ".env",
        current_dir.parent / ".env",
        Path.cwd() / ".env"
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    pass

# Assistant Identity
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "AIBuddy")
WAKE_WORD = os.getenv("WAKE_WORD", "hello").lower().strip()

# Audio & Microphone
_raw_mic_index = os.getenv("MIC_INDEX", "")
MIC_INDEX = int(_raw_mic_index) if _raw_mic_index.strip().isdigit() else None
SPEECH_LANGUAGE = os.getenv("SPEECH_LANGUAGE", "en-US")
ENERGY_THRESHOLD = int(os.getenv("ENERGY_THRESHOLD", "300"))
DYNAMIC_ENERGY_THRESHOLD = os.getenv("DYNAMIC_ENERGY_THRESHOLD", "True").lower() == "true"
PAUSE_THRESHOLD = float(os.getenv("PAUSE_THRESHOLD", "0.8"))
PHRASE_TIME_LIMIT = int(os.getenv("PHRASE_TIME_LIMIT", "8"))
WAKE_WORD_TIMEOUT = int(os.getenv("WAKE_WORD_TIMEOUT", "5"))

# Active Listening & Inactivity Timeout (in seconds)
# Default: 300 seconds (5 minutes). Change to 600 for 10 minutes.
ACTIVE_LISTENING_TIMEOUT_SECONDS = int(os.getenv("ACTIVE_LISTENING_TIMEOUT_SECONDS", "300"))

# Text-to-Speech Settings
VOICE_INDEX = int(os.getenv("VOICE_INDEX", "1"))
TTS_RATE = int(os.getenv("TTS_RATE", "160"))
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "1.0"))
RESPONSE_MODE = os.getenv("RESPONSE_MODE", "tanglish").lower()  # "tanglish" or "english"

# OpenAI / AI Brain Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Controlled Application Registry
# Maps common voice aliases to executable names, URIs, and process names for safe launching and closing
APP_REGISTRY = {
    "chrome": {
        "display_name": "Google Chrome",
        "executables": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "chrome.exe"
        ],
        "uri": "chrome://newtab",
        "process_names": ["chrome.exe"],
        "confirm_close": False
    },
    "edge": {
        "display_name": "Microsoft Edge",
        "executables": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            "msedge.exe"
        ],
        "uri": "microsoft-edge:",
        "process_names": ["msedge.exe"],
        "confirm_close": False
    },
    "microsoft edge": {
        "display_name": "Microsoft Edge",
        "executables": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            "msedge.exe"
        ],
        "uri": "microsoft-edge:",
        "process_names": ["msedge.exe"],
        "confirm_close": False
    },
    "notepad": {
        "display_name": "Notepad",
        "executables": ["notepad.exe"],
        "uri": None,
        "process_names": ["notepad.exe"],
        "confirm_close": True
    },
    "calculator": {
        "display_name": "Calculator",
        "executables": ["calc.exe"],
        "uri": "calculator:",
        "process_names": ["CalculatorApp.exe", "calc.exe", "Calculator.exe"],
        "confirm_close": False
    },
    "vs code": {
        "display_name": "Visual Studio Code",
        "executables": ["code.cmd", "code.exe"],
        "uri": "vscode:",
        "process_names": ["Code.exe"],
        "confirm_close": False
    },
    "vscode": {
        "display_name": "Visual Studio Code",
        "executables": ["code.cmd", "code.exe"],
        "uri": "vscode:",
        "process_names": ["Code.exe"],
        "confirm_close": False
    },
    "command prompt": {
        "display_name": "Command Prompt",
        "executables": ["cmd.exe"],
        "uri": None,
        "process_names": ["cmd.exe"],
        "confirm_close": False
    },
    "cmd": {
        "display_name": "Command Prompt",
        "executables": ["cmd.exe"],
        "uri": None,
        "process_names": ["cmd.exe"],
        "confirm_close": False
    },
    "explorer": {
        "display_name": "File Explorer",
        "executables": ["explorer.exe"],
        "uri": None,
        "process_names": ["explorer.exe"],
        "confirm_close": False
    }
}
