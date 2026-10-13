import logging
import threading
import time
from typing import Optional
import pyttsx3
import speech_recognition as sr

import config

logger = logging.getLogger("ai_assistant.speech")

# Thread safety lock for pyttsx3 engine
_tts_lock = threading.Lock()
_is_speaking = threading.Event()
_is_calibrated = False

# Initialize pyttsx3 TTS Engine safely
_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        try:
            _engine = pyttsx3.init("sapi5")
            voices = _engine.getProperty("voices")
            if voices:
                v_idx = min(max(0, config.VOICE_INDEX), len(voices) - 1)
                _engine.setProperty("voice", voices[v_idx].id)
                logger.info(f"Using TTS Voice: {voices[v_idx].name}")
            _engine.setProperty("rate", config.TTS_RATE)
            _engine.setProperty("volume", config.TTS_VOLUME)
        except Exception as e:
            logger.error(f"Failed to initialize SAPI5 pyttsx3 engine: {e}")
            _engine = pyttsx3.init()
    return _engine

# Initialize Speech Recognizer
recognizer = sr.Recognizer()
recognizer.energy_threshold = config.ENERGY_THRESHOLD
recognizer.dynamic_energy_threshold = config.DYNAMIC_ENERGY_THRESHOLD
recognizer.pause_threshold = config.PAUSE_THRESHOLD

# Initialize Microphone
if config.MIC_INDEX is not None:
    try:
        mic = sr.Microphone(device_index=config.MIC_INDEX)
    except Exception as e:
        logger.warning(f"Specified MIC_INDEX {config.MIC_INDEX} invalid ({e}); using default microphone.")
        mic = sr.Microphone()
else:
    mic = sr.Microphone()

def calibrate_noise(duration: float = 1.0):
    """Calibrate ambient room noise once to stabilize energy thresholds."""
    global _is_calibrated
    try:
        with mic as source:
            logger.info("Calibrating microphone for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=duration)
            _is_calibrated = True
            logger.info(f"Microphone calibrated. Energy threshold set to: {recognizer.energy_threshold:.1f}")
    except Exception as e:
        logger.warning(f"Ambient noise calibration skipped due to: {e}")

def speak(text: str):
    """
    Audibly speak text via pyttsx3 with thread-safety and self-listening suppression.
    Also ensures the response is displayed on the screen.
    """
    global _engine
    if not text or not text.strip():
        return

    clean_text = text.strip()
    # Add trailing punctuation if missing to prevent SAPI5 from clipping final syllable
    if clean_text[-1] not in ".!?":
        clean_text += "."

    with _tts_lock:
        _is_speaking.set()
        try:
            print(f"[{config.ASSISTANT_NAME}]: {clean_text}")
            engine = _get_engine()
            try:
                engine.stop()
            except Exception:
                pass
            engine.say(clean_text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS playback error: {e}")
            _engine = None  # Cleanly reinitialize on next call
        finally:
            # Cooldown to ensure audio output fully clears before microphone reopens
            time.sleep(0.3)
            _is_speaking.clear()

def is_assistant_speaking() -> bool:
    """Returns True if the assistant is currently speaking."""
    return _is_speaking.is_set()

def wait_for_wake_word(on_detected_callback=None) -> tuple[bool, str]:
    """
    Listen continuously until the configured wake word is detected.
    Returns (True, initial_command) when wake word is heard.
    If the user said 'hello open notepad', initial_command is 'open notepad'.
    If the user said only 'hello', initial_command is empty.
    """
    if not _is_calibrated:
        calibrate_noise()

    wake_word = config.WAKE_WORD.lower()
    print(f"\n[Wake Word Mode] Say '{wake_word}' to activate {config.ASSISTANT_NAME}...")

    while True:
        # Avoid listening to ourselves
        if _is_speaking.is_set():
            time.sleep(0.1)
            continue

        try:
            with mic as source:
                audio = recognizer.listen(
                    source,
                    timeout=config.WAKE_WORD_TIMEOUT,
                    phrase_time_limit=4
                )
        except sr.WaitTimeoutError:
            continue
        except Exception as e:
            logger.error(f"Microphone capture error during wake-word listening: {e}")
            time.sleep(0.5)
            continue

        if _is_speaking.is_set():
            continue

        try:
            recognized_text = recognizer.recognize_google(
                audio,
                language=config.SPEECH_LANGUAGE
            ).lower()

            logger.debug(f"Wake loop heard: '{recognized_text}'")

            if wake_word in recognized_text:
                print(f"[{config.ASSISTANT_NAME}] Wake word '{wake_word}' detected!")
                # Check if a command was spoken in the same breath
                parts = recognized_text.split(wake_word, 1)
                initial_command = parts[1].strip() if len(parts) > 1 else ""

                if on_detected_callback:
                    on_detected_callback(initial_command)
                elif not initial_command:
                    if config.RESPONSE_MODE == "tanglish":
                        speak("Hi Abi, na ready iruken. Sollu.")
                    else:
                        speak("Yes, how can I help?")

                return True, initial_command

        except sr.UnknownValueError:
            # Normal: audio heard but speech not confident
            pass
        except sr.RequestError as e:
            logger.warning(f"Google STT request error: {e}")
            time.sleep(1.0)
        except Exception as e:
            logger.error(f"Unexpected recognition error in wake loop: {e}")

def listen(timeout: int = 5, phrase_time_limit: int = None, prompt_on_unknown: bool = False) -> str:
    """
    Capture user command speech and return transcribed text.
    If prompt_on_unknown is True, speaks an error message when speech is unintelligible.
    If prompt_on_unknown is False, stays quiet to prevent interrupting the user.
    """
    if not _is_calibrated:
        calibrate_noise()

    if phrase_time_limit is None:
        phrase_time_limit = config.PHRASE_TIME_LIMIT

    try:
        with mic as source:
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )
    except sr.WaitTimeoutError:
        return ""
    except Exception as e:
        logger.error(f"Audio capture error: {e}")
        return ""

    if _is_speaking.is_set():
        return ""

    try:
        text = recognizer.recognize_google(
            audio,
            language=config.SPEECH_LANGUAGE
        ).strip()
        print(f"[User]: {text}")
        return text
    except sr.UnknownValueError:
        logger.debug("Speech recognition: audio not intelligible")
        if prompt_on_unknown:
            if config.RESPONSE_MODE == "tanglish":
                speak("Sorry, puriyala. Thirumba sollunga.")
            else:
                speak("Sorry, I didn't quite catch that. Could you say it again?")
        return ""
    except sr.RequestError as e:
        logger.error(f"Google STT service unreachable: {e}")
        speak("I couldn't reach the speech recognition service. Please check your internet connection.")
        return ""
    except Exception as e:
        logger.error(f"Unexpected recognition error: {e}")
        return ""
