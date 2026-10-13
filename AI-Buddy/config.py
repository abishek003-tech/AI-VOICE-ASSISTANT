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

# ============================================================ #
# Controlled Application Registry                              #
# Maps common voice aliases to executable info and process     #
# names for safe launching and closing via voice commands.     #
#                                                              #
# Keys are lowercase voice aliases (what the user might say).  #
# Multiple aliases can point to the same application.          #
# ============================================================ #
APP_REGISTRY = {

    # ---------------------------------------------------------- #
    # Browsers                                                    #
    # ---------------------------------------------------------- #
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
    "google chrome": {
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
    "firefox": {
        "display_name": "Mozilla Firefox",
        "executables": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            "firefox.exe"
        ],
        "uri": None,
        "process_names": ["firefox.exe"],
        "confirm_close": False
    },
    "mozilla firefox": {
        "display_name": "Mozilla Firefox",
        "executables": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            "firefox.exe"
        ],
        "uri": None,
        "process_names": ["firefox.exe"],
        "confirm_close": False
    },

    # ---------------------------------------------------------- #
    # Text Editors & Basic Tools                                  #
    # ---------------------------------------------------------- #
    "notepad": {
        "display_name": "Notepad",
        "executables": ["notepad.exe"],
        "uri": None,
        "process_names": ["notepad.exe"],
        "confirm_close": True
    },
    "wordpad": {
        "display_name": "WordPad",
        "executables": [
            r"C:\Program Files\Windows NT\Accessories\wordpad.exe",
            "wordpad.exe"
        ],
        "uri": None,
        "process_names": ["wordpad.exe"],
        "confirm_close": True
    },
    "calculator": {
        "display_name": "Calculator",
        "executables": ["calc.exe"],
        "uri": "calculator:",
        "process_names": ["CalculatorApp.exe", "calc.exe", "Calculator.exe"],
        "confirm_close": False
    },

    # ---------------------------------------------------------- #
    # Microsoft Office Suite                                      #
    # ---------------------------------------------------------- #
    "word": {
        "display_name": "Microsoft Word",
        "executables": [
            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
            "WINWORD.EXE"
        ],
        "uri": None,
        "process_names": ["WINWORD.EXE"],
        "confirm_close": True
    },
    "microsoft word": {
        "display_name": "Microsoft Word",
        "executables": [
            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
            "WINWORD.EXE"
        ],
        "uri": None,
        "process_names": ["WINWORD.EXE"],
        "confirm_close": True
    },
    "excel": {
        "display_name": "Microsoft Excel",
        "executables": [
            r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
            r"C:\Program Files\Microsoft Office\Office16\EXCEL.EXE",
            "EXCEL.EXE"
        ],
        "uri": None,
        "process_names": ["EXCEL.EXE"],
        "confirm_close": True
    },
    "microsoft excel": {
        "display_name": "Microsoft Excel",
        "executables": [
            r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
            "EXCEL.EXE"
        ],
        "uri": None,
        "process_names": ["EXCEL.EXE"],
        "confirm_close": True
    },
    "powerpoint": {
        "display_name": "Microsoft PowerPoint",
        "executables": [
            r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
            r"C:\Program Files\Microsoft Office\Office16\POWERPNT.EXE",
            "POWERPNT.EXE"
        ],
        "uri": None,
        "process_names": ["POWERPNT.EXE"],
        "confirm_close": True
    },
    "microsoft powerpoint": {
        "display_name": "Microsoft PowerPoint",
        "executables": [
            r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
            "POWERPNT.EXE"
        ],
        "uri": None,
        "process_names": ["POWERPNT.EXE"],
        "confirm_close": True
    },
    "outlook": {
        "display_name": "Microsoft Outlook",
        "executables": [
            r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\OUTLOOK.EXE",
            "OUTLOOK.EXE"
        ],
        "uri": None,
        "process_names": ["OUTLOOK.EXE"],
        "confirm_close": False
    },
    "microsoft outlook": {
        "display_name": "Microsoft Outlook",
        "executables": [
            r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
            "OUTLOOK.EXE"
        ],
        "uri": None,
        "process_names": ["OUTLOOK.EXE"],
        "confirm_close": False
    },
    "onenote": {
        "display_name": "Microsoft OneNote",
        "executables": [
            r"C:\Program Files\Microsoft Office\root\Office16\ONENOTE.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\ONENOTE.EXE",
            "ONENOTE.EXE"
        ],
        "uri": "onenote:",
        "process_names": ["ONENOTE.EXE", "OneNote.exe"],
        "confirm_close": False
    },
    "one note": {
        "display_name": "Microsoft OneNote",
        "executables": [
            r"C:\Program Files\Microsoft Office\root\Office16\ONENOTE.EXE",
            "ONENOTE.EXE"
        ],
        "uri": "onenote:",
        "process_names": ["ONENOTE.EXE", "OneNote.exe"],
        "confirm_close": False
    },

    # ---------------------------------------------------------- #
    # Communication & Collaboration                               #
    # ---------------------------------------------------------- #
    "teams": {
        "display_name": "Microsoft Teams",
        "executables": [
            r"C:\Users\Lenovo\AppData\Local\Microsoft\Teams\current\Teams.exe",
            r"C:\Program Files\Microsoft\Teams\current\Teams.exe",
            "Teams.exe"
        ],
        "uri": "msteams:",
        "process_names": ["Teams.exe"],
        "confirm_close": False
    },
    "microsoft teams": {
        "display_name": "Microsoft Teams",
        "executables": [
            r"C:\Users\Lenovo\AppData\Local\Microsoft\Teams\current\Teams.exe",
            "Teams.exe"
        ],
        "uri": "msteams:",
        "process_names": ["Teams.exe"],
        "confirm_close": False
    },
    "zoom": {
        "display_name": "Zoom",
        "executables": [
            r"C:\Users\Lenovo\AppData\Roaming\Zoom\bin\Zoom.exe",
            r"C:\Program Files\Zoom\bin\Zoom.exe",
            "Zoom.exe"
        ],
        "uri": None,
        "process_names": ["Zoom.exe"],
        "confirm_close": False
    },
    "discord": {
        "display_name": "Discord",
        "executables": [
            r"C:\Users\Lenovo\AppData\Local\Discord\Update.exe",
            r"C:\Users\Lenovo\AppData\Local\Discord\app-1.0.9035\Discord.exe",
            "Discord.exe"
        ],
        "uri": None,
        "process_names": ["Discord.exe"],
        "confirm_close": False
    },
    "skype": {
        "display_name": "Skype",
        "executables": [
            r"C:\Program Files (x86)\Microsoft\Skype for Desktop\Skype.exe",
            r"C:\Program Files\Microsoft\Skype for Desktop\Skype.exe",
            "Skype.exe"
        ],
        "uri": "skype:",
        "process_names": ["Skype.exe"],
        "confirm_close": False
    },
    "telegram": {
        "display_name": "Telegram",
        "executables": [
            r"C:\Users\Lenovo\AppData\Roaming\Telegram Desktop\Telegram.exe",
            r"C:\Program Files\Telegram Desktop\Telegram.exe",
            "Telegram.exe"
        ],
        "uri": None,
        "process_names": ["Telegram.exe"],
        "confirm_close": False
    },
    "whatsapp": {
        "display_name": "WhatsApp",
        "executables": [
            r"C:\Users\Lenovo\AppData\Local\WhatsApp\WhatsApp.exe",
            "WhatsApp.exe"
        ],
        "uri": "whatsapp:",
        "process_names": ["WhatsApp.exe"],
        "confirm_close": False
    },
    "whats app": {
        "display_name": "WhatsApp",
        "executables": [
            r"C:\Users\Lenovo\AppData\Local\WhatsApp\WhatsApp.exe",
            "WhatsApp.exe"
        ],
        "uri": "whatsapp:",
        "process_names": ["WhatsApp.exe"],
        "confirm_close": False
    },

    # ---------------------------------------------------------- #
    # Media & Entertainment                                       #
    # ---------------------------------------------------------- #
    "spotify": {
        "display_name": "Spotify",
        "executables": [
            r"C:\Users\Lenovo\AppData\Roaming\Spotify\Spotify.exe",
            "Spotify.exe"
        ],
        "uri": "spotify:",
        "process_names": ["Spotify.exe"],
        "confirm_close": False
    },
    "vlc": {
        "display_name": "VLC Media Player",
        "executables": [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            "vlc.exe"
        ],
        "uri": None,
        "process_names": ["vlc.exe"],
        "confirm_close": False
    },
    "vlc media player": {
        "display_name": "VLC Media Player",
        "executables": [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            "vlc.exe"
        ],
        "uri": None,
        "process_names": ["vlc.exe"],
        "confirm_close": False
    },
    "media player": {
        "display_name": "Windows Media Player",
        "executables": [
            r"C:\Program Files\Windows Media Player\wmplayer.exe",
            r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe",
            "wmplayer.exe"
        ],
        "uri": None,
        "process_names": ["wmplayer.exe"],
        "confirm_close": False
    },
    "windows media player": {
        "display_name": "Windows Media Player",
        "executables": [
            r"C:\Program Files\Windows Media Player\wmplayer.exe",
            "wmplayer.exe"
        ],
        "uri": None,
        "process_names": ["wmplayer.exe"],
        "confirm_close": False
    },
    "steam": {
        "display_name": "Steam",
        "executables": [
            r"C:\Program Files (x86)\Steam\Steam.exe",
            r"C:\Program Files\Steam\Steam.exe",
            "Steam.exe"
        ],
        "uri": "steam:",
        "process_names": ["Steam.exe", "steam.exe"],
        "confirm_close": False
    },

    # ---------------------------------------------------------- #
    # System Utilities                                            #
    # ---------------------------------------------------------- #
    "paint": {
        "display_name": "Paint",
        "executables": ["mspaint.exe"],
        "uri": None,
        "process_names": ["mspaint.exe"],
        "confirm_close": True
    },
    "ms paint": {
        "display_name": "Paint",
        "executables": ["mspaint.exe"],
        "uri": None,
        "process_names": ["mspaint.exe"],
        "confirm_close": True
    },
    "snipping tool": {
        "display_name": "Snipping Tool",
        "executables": [
            "SnippingTool.exe",
            r"C:\Windows\System32\SnippingTool.exe"
        ],
        "uri": "ms-screenclip:",
        "process_names": ["SnippingTool.exe", "ScreenSketch.exe"],
        "confirm_close": False
    },
    "snip": {
        "display_name": "Snipping Tool",
        "executables": ["SnippingTool.exe"],
        "uri": "ms-screenclip:",
        "process_names": ["SnippingTool.exe", "ScreenSketch.exe"],
        "confirm_close": False
    },
    "task manager": {
        "display_name": "Task Manager",
        "executables": [
            r"C:\Windows\System32\Taskmgr.exe",
            "Taskmgr.exe"
        ],
        "uri": None,
        "process_names": ["Taskmgr.exe"],
        "confirm_close": False
    },
    "taskmgr": {
        "display_name": "Task Manager",
        "executables": ["Taskmgr.exe"],
        "uri": None,
        "process_names": ["Taskmgr.exe"],
        "confirm_close": False
    },
    "settings": {
        "display_name": "Windows Settings",
        "executables": [],
        "uri": "ms-settings:",
        "process_names": ["SystemSettings.exe"],
        "confirm_close": False
    },
    "windows settings": {
        "display_name": "Windows Settings",
        "executables": [],
        "uri": "ms-settings:",
        "process_names": ["SystemSettings.exe"],
        "confirm_close": False
    },
    "control panel": {
        "display_name": "Control Panel",
        "executables": [
            r"C:\Windows\System32\control.exe",
            "control.exe"
        ],
        "uri": None,
        "process_names": ["control.exe"],
        "confirm_close": False
    },
    "explorer": {
        "display_name": "File Explorer",
        "executables": ["explorer.exe"],
        "uri": None,
        "process_names": ["explorer.exe"],
        "confirm_close": False
    },
    "file explorer": {
        "display_name": "File Explorer",
        "executables": ["explorer.exe"],
        "uri": None,
        "process_names": ["explorer.exe"],
        "confirm_close": False
    },

    # ---------------------------------------------------------- #
    # Command Line & Shells                                       #
    # ---------------------------------------------------------- #
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
    "powershell": {
        "display_name": "PowerShell",
        "executables": [
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "powershell.exe"
        ],
        "uri": None,
        "process_names": ["powershell.exe", "pwsh.exe"],
        "confirm_close": False
    },
    "power shell": {
        "display_name": "PowerShell",
        "executables": [
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "powershell.exe"
        ],
        "uri": None,
        "process_names": ["powershell.exe", "pwsh.exe"],
        "confirm_close": False
    },

    # ---------------------------------------------------------- #
    # Development Tools                                           #
    # ---------------------------------------------------------- #
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
    "visual studio code": {
        "display_name": "Visual Studio Code",
        "executables": ["code.cmd", "code.exe"],
        "uri": "vscode:",
        "process_names": ["Code.exe"],
        "confirm_close": False
    },
    "pycharm": {
        "display_name": "PyCharm",
        "executables": [
            r"C:\Program Files\JetBrains\PyCharm Community Edition 2024.1\bin\pycharm64.exe",
            r"C:\Program Files\JetBrains\PyCharm Professional Edition 2024.1\bin\pycharm64.exe",
            "pycharm64.exe",
            "pycharm.exe"
        ],
        "uri": None,
        "process_names": ["pycharm64.exe", "pycharm.exe"],
        "confirm_close": False
    },
    "android studio": {
        "display_name": "Android Studio",
        "executables": [
            r"C:\Program Files\Android\Android Studio\bin\studio64.exe",
            "studio64.exe"
        ],
        "uri": None,
        "process_names": ["studio64.exe"],
        "confirm_close": False
    },
    "git bash": {
        "display_name": "Git Bash",
        "executables": [
            r"C:\Program Files\Git\git-bash.exe",
            "git-bash.exe"
        ],
        "uri": None,
        "process_names": ["bash.exe", "git-bash.exe"],
        "confirm_close": False
    },
    "postman": {
        "display_name": "Postman",
        "executables": [
            r"C:\Users\Lenovo\AppData\Local\Postman\Postman.exe",
            "Postman.exe"
        ],
        "uri": None,
        "process_names": ["Postman.exe"],
        "confirm_close": False
    },
}
