# AI-Buddy: Desktop AI Voice Assistant

A modular, reliable desktop AI voice assistant built in Python for Windows. It features wake-word listening, natural language command routing, desktop application automation, YouTube media playback, and audible confirmations with graceful offline fallback.

---

## Key Features

- **Wake-Word Activation:** Listens for the configurable wake word (`hello` by default) with one-time ambient noise calibration and acoustic self-listening suppression.
- **Natural Language Command Routing:** Parses spoken commands using an intent-and-entity extractor. Supports queries like:
  - *"Play Kalyani song on YouTube"*
  - *"Open YouTube and play a Tamil melody"*
  - *"Can you please launch Chrome?"*
  - *"Close Calculator"*
  - *"Search Wikipedia for Python programming"*
  - *"What time is it?"*
  - *"Tell me a joke"*
- **Safe Desktop Automation:** Uses a controlled action registry (`config.APP_REGISTRY`) with dynamic executable discovery (`shutil.which` and standard paths) and safe process termination via `psutil`.
- **Verified Spoken Confirmations:** Confirms actions through speech *only after* verifying execution success (no false positives). Supports both **Tanglish** and **English** response modes.
- **Resilient AI Fallback:** Integrates OpenAI `gpt-4o-mini` with secure `.env` credential management. If no API key is provided, the assistant gracefully falls back to local tools without crashing.
- **Offline TTS Engine:** Uses Microsoft SAPI5 (`pyttsx3`) with voice bounds checking, customizable speech rate, and thread-safe audio playback.

---

## Project Structure

```
sample_speech_recognition/
│
├── speechyAi.py                   # Root launcher bridging to the modular assistant
├── test_voice.py                  # Standalone microphone capture test
├── tests/
│   ├── __init__.py
│   └── test_assistant.py          # Comprehensive test suite (23 unit tests)
│
└── AI-Buddy/
    ├── .env.example               # Template for environment variables
    ├── config.py                  # Centralized, validated application configuration
    ├── main.py                    # Modular application entry point
    ├── requirements.txt           # Verified dependency manifest
    ├── speechyAi.py               # Compatibility redirect to main.py
    ├── test_speaker.py            # SAPI5 TTS speaker diagnostic test
    │
    └── assistant/                 # Core engine package
        ├── __init__.py
        ├── actions.py             # Structured ActionResult dataclass
        ├── ai_brain.py            # OpenAI client with credential protection
        ├── app_control.py         # Application discovery, launch & close verification
        ├── commands.py            # Command dispatcher and response orchestrator
        ├── features.py            # Wikipedia & pyjokes information tools
        ├── intent.py              # Natural language intent & entity parser
        ├── media.py               # Dedicated YouTube search and playback
        └── speech.py              # Audio capture, wake-word loop & TTS engine
```

---

## Quickstart

### 1. Requirements
Ensure your Python 3.12 environment has dependencies installed:
```bash
pip install -r AI-Buddy/requirements.txt
```

### 2. Optional: Configure AI Brain
To enable general AI conversation via OpenAI, copy `.env.example` to `.env` in `AI-Buddy/` or repository root:
```bash
cp AI-Buddy/.env.example .env
```
Edit `.env` and set your key:
```env
OPENAI_API_KEY=sk-...
RESPONSE_MODE=tanglish    # or english
WAKE_WORD=hello
```
*(If no API key is set, all local desktop, YouTube, time, Wikipedia, and joke commands continue to function normally!)*

### 3. Launch the Assistant
You can run the assistant from either the root or the `AI-Buddy/` directory:

**From project root:**
```powershell
python speechyAi.py
```

**Or directly:**
```powershell
python AI-Buddy/main.py
```

---

## Running the Automated Test Suite

Run the full unit test suite (runs in ~3 seconds with mocked hardware/processes):
```powershell
python tests/test_assistant.py
```

---

## Voice Model & Custom Voice Evaluation

- **Current Implementation:** Microsoft SAPI5 system voices (`Microsoft David` and `Microsoft Zira`) via `pyttsx3`.
- **Offline / Local Status:** Fully offline, zero VRAM usage, instantaneous response.
- **Custom Voice Roadmap:** PyTorch in this environment is currently CPU-only (`2.10.0+cpu`). Running neural zero-shot cloning (such as Coqui XTTS-v2) on CPU causes noticeable latency (~8–15s per sentence) on 8GB RAM. For real-time custom voice cloning, a CUDA-enabled PyTorch build with an NVIDIA GPU and authorized 10–30s reference WAV audio is recommended.
