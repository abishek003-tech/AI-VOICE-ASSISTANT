import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add AI-Buddy to sys.path so we can test the modules directly
test_dir = Path(__file__).resolve().parent
repo_dir = test_dir.parent
ai_buddy_dir = repo_dir / "AI-Buddy"
if str(ai_buddy_dir) not in sys.path:
    sys.path.insert(0, str(ai_buddy_dir))

import config
from assistant.intent import IntentType, parse_intent
from assistant.actions import ActionResult
from assistant.app_control import resolve_app_key, launch_application, close_application
from assistant.media import play_youtube, open_youtube
import assistant.ai_brain as ai_brain

class TestIntentParser(unittest.TestCase):
    def test_youtube_play_variations(self):
        cases = [
            ("Play Kalyani song", IntentType.MEDIA_PLAY, "kalyani song"),
            ("play kalyani song", IntentType.MEDIA_PLAY, "kalyani song"),
            ("open youtube and play kalyani song", IntentType.MEDIA_PLAY, "kalyani song"),
            ("search youtube for kalyani songs", IntentType.MEDIA_PLAY, "kalyani songs"),
            ("play a tamil melody", IntentType.MEDIA_PLAY, "a tamil melody"),
            ("play ilayaraja hits on youtube", IntentType.MEDIA_PLAY, "ilayaraja hits"),
        ]
        for text, expected_intent, expected_entity in cases:
            with self.subTest(text=text):
                parsed = parse_intent(text)
                self.assertEqual(parsed.intent_type, expected_intent)
                self.assertEqual(parsed.entity.lower(), expected_entity.lower())

    def test_youtube_open(self):
        cases = ["open youtube", "launch youtube", "youtube"]
        for text in cases:
            with self.subTest(text=text):
                parsed = parse_intent(text)
                self.assertEqual(parsed.intent_type, IntentType.MEDIA_OPEN)

    def test_app_open_variations(self):
        cases = [
            ("open chrome", IntentType.APP_OPEN, "chrome"),
            ("can you launch notepad", IntentType.APP_OPEN, "notepad"),
            ("please start calculator", IntentType.APP_OPEN, "calculator"),
            ("open vs code", IntentType.APP_OPEN, "vs code"),
            ("start cmd", IntentType.APP_OPEN, "cmd"),
        ]
        for text, expected_intent, expected_entity in cases:
            with self.subTest(text=text):
                parsed = parse_intent(text)
                self.assertEqual(parsed.intent_type, expected_intent)
                self.assertEqual(parsed.entity, expected_entity)

    def test_app_close_variations(self):
        cases = [
            ("close chrome", IntentType.APP_CLOSE, "chrome"),
            ("terminate calculator", IntentType.APP_CLOSE, "calculator"),
            ("shut down notepad", IntentType.APP_CLOSE, "notepad"),
        ]
        for text, expected_intent, expected_entity in cases:
            with self.subTest(text=text):
                parsed = parse_intent(text)
                self.assertEqual(parsed.intent_type, expected_intent)
                self.assertEqual(parsed.entity, expected_entity)

    def test_utility_and_persona_intents(self):
        self.assertEqual(parse_intent("what time is it").intent_type, IntentType.TIME)
        self.assertEqual(parse_intent("tell me a joke").intent_type, IntentType.JOKE)
        self.assertEqual(parse_intent("who is god").intent_type, IntentType.WHO_IS_GOD)
        self.assertEqual(parse_intent("what is your name").intent_type, IntentType.NAME)
        self.assertEqual(parse_intent("stop").intent_type, IntentType.STOP)
        self.assertEqual(parse_intent("exit").intent_type, IntentType.STOP)

    def test_wikipedia_intent(self):
        parsed = parse_intent("search wikipedia for Albert Einstein")
        self.assertEqual(parsed.intent_type, IntentType.WIKIPEDIA)
        self.assertIn("albert einstein", parsed.entity.lower())

    def test_general_ai_fallback(self):
        parsed = parse_intent("Why is the sky blue?")
        self.assertEqual(parsed.intent_type, IntentType.GENERAL_AI)


class TestAppControl(unittest.TestCase):
    def test_resolve_app_key(self):
        self.assertEqual(resolve_app_key("google chrome"), "chrome")
        self.assertEqual(resolve_app_key("notepad"), "notepad")
        self.assertEqual(resolve_app_key("calculator"), "calculator")
        self.assertIsNone(resolve_app_key("unknown_game_123"))

    def test_unsupported_app_launch(self):
        res = launch_application("non_existent_app_xyz")
        self.assertFalse(res.success)
        self.assertIn("couldn't find", res.message)

    @patch("subprocess.Popen")
    @patch("assistant.app_control.find_executable", return_value="C:\\dummy\\notepad.exe")
    def test_supported_app_launch_mocked(self, mock_find, mock_popen):
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc

        res = launch_application("notepad")
        self.assertTrue(res.success)
        mock_popen.assert_called_once_with(["C:\\dummy\\notepad.exe"], shell=False)

    @patch("psutil.process_iter")
    def test_calculator_close_mapping(self, mock_process_iter):
        # Verify process names checked for calculator include CalculatorApp.exe and calc.exe
        proc_names_in_reg = config.APP_REGISTRY["calculator"]["process_names"]
        self.assertIn("CalculatorApp.exe", proc_names_in_reg)
        self.assertIn("calc.exe", proc_names_in_reg)

        mock_calc_proc = MagicMock()
        mock_calc_proc.info = {"pid": 1234, "name": "CalculatorApp.exe"}
        mock_process_iter.return_value = [mock_calc_proc]

        res = close_application("calculator")
        self.assertTrue(res.success)
        mock_calc_proc.terminate.assert_called_once()


class TestMediaControl(unittest.TestCase):
    def test_play_youtube_empty_query(self):
        res = play_youtube("")
        self.assertTrue("What song or video" in res.message or "Enna paatu" in res.message)

    @patch("pywhatkit.playonyt")
    def test_play_youtube_mocked(self, mock_playonyt):
        res = play_youtube("Kalyani song")
        self.assertTrue(res.success)
        mock_playonyt.assert_called_once_with("Kalyani song")


class TestAIBrain(unittest.TestCase):
    def test_missing_api_key_graceful_fallback(self):
        with patch.object(config, "OPENAI_API_KEY", ""):
            reply = ai_brain.ai_reply("What is quantum computing?")
            self.assertIsInstance(reply, str)
            self.assertIn("API key", reply)

    def test_placeholder_api_key_graceful_fallback(self):
        with patch.object(config, "OPENAI_API_KEY", "your_api_key_here"):
            reply = ai_brain.ai_reply("Hello there")
            self.assertIsInstance(reply, str)
            self.assertIn("API key", reply)

    @patch("assistant.ai_brain._get_client")
    def test_auth_error_handling(self, mock_get_client):
        class DummyAuthError(Exception):
            pass
        DummyAuthError.__name__ = "AuthenticationError"

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = DummyAuthError("Invalid key")
        mock_get_client.return_value = mock_client

        with patch.object(config, "OPENAI_API_KEY", "sk-dummy-test-key"):
            reply = ai_brain.ai_reply("Tell me something")
            self.assertIn("API key", reply)


class TestCommands(unittest.TestCase):
    @patch("assistant.commands.speak")
    def test_handle_command_stop(self, mock_speak):
        from assistant.commands import handle_command
        should_exit, msg = handle_command("stop")
        self.assertTrue(should_exit)
        mock_speak.assert_called_once()

    @patch("assistant.commands.speak")
    def test_handle_command_time(self, mock_speak):
        from assistant.commands import handle_command
        should_exit, msg = handle_command("what is the time")
        self.assertFalse(should_exit)
        self.assertTrue("time" in msg.lower() or ":" in msg)

    @patch("assistant.commands.speak")
    def test_handle_command_god_persona(self, mock_speak):
        from assistant.commands import handle_command
        should_exit, msg = handle_command("who is god")
        self.assertFalse(should_exit)
        self.assertEqual(msg, "Ajitheyyy Kadavuleyy")

    @patch("assistant.commands.speak")
    def test_handle_command_name_persona(self, mock_speak):
        from assistant.commands import handle_command
        should_exit, msg = handle_command("what is your name")
        self.assertFalse(should_exit)
        self.assertIn(config.ASSISTANT_NAME, msg)

    @patch("assistant.commands.speak")
    @patch("assistant.commands.launch_application")
    def test_handle_command_open_chrome(self, mock_launch, mock_speak):
        from assistant.commands import handle_command
        mock_launch.return_value = ActionResult(success=True, message="Google Chrome is open.")
        should_exit, msg = handle_command("open chrome")
        self.assertFalse(should_exit)
        mock_launch.assert_called_once_with("chrome")
        # Confirms two-phase spoken status: (1) status update, (2) verified outcome
        self.assertEqual(mock_speak.call_count, 2)

    @patch("assistant.commands.speak")
    @patch("assistant.commands.play_youtube")
    def test_handle_command_play_youtube(self, mock_play, mock_speak):
        from assistant.commands import handle_command
        mock_play.return_value = ActionResult(success=True, message="Playing Kalyani song now.")
        should_exit, msg = handle_command("Play Kalyani song")
        self.assertFalse(should_exit)
        mock_play.assert_called_once_with("kalyani song")
        # Confirms two-phase spoken status: (1) status update, (2) verified playback
        self.assertEqual(mock_speak.call_count, 2)

    @patch("assistant.commands.speak")
    @patch("assistant.commands.get_joke", return_value="Why did the chicken cross the road?")
    def test_handle_command_joke_spoken_intro_and_punchline(self, mock_get_joke, mock_speak):
        from assistant.commands import handle_command
        should_exit, joke = handle_command("tell me a joke")
        self.assertFalse(should_exit)
        # Confirms two spoken utterances: intro ("Here's a joke...") then the full joke aloud
        self.assertEqual(mock_speak.call_count, 2)
        mock_speak.assert_any_call("Why did the chicken cross the road?")

    @patch("assistant.commands.speak")
    def test_handle_command_empty_input(self, mock_speak):
        from assistant.commands import handle_command
        should_exit, msg = handle_command("   ")
        self.assertFalse(should_exit)
        self.assertEqual(msg, "")
        mock_speak.assert_not_called()


if __name__ == "__main__":
    unittest.main()
