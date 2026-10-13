import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure AI-Buddy package is on sys.path
test_dir = Path(__file__).resolve().parent
repo_dir = test_dir.parent
ai_buddy_dir = repo_dir / "AI-Buddy"
if str(ai_buddy_dir) not in sys.path:
    sys.path.insert(0, str(ai_buddy_dir))

import config
from assistant.state import AssistantState, AssistantStateMachine

class TestAssistantStateMachine(unittest.TestCase):
    def setUp(self):
        # Default 5-minute timeout = 300 seconds
        self.sm = AssistantStateMachine(timeout_seconds=300)

    def test_initial_state_is_wake_word_mode(self):
        """Initial state must be WAKE_WORD_MODE."""
        self.assertEqual(self.sm.state, AssistantState.WAKE_WORD_MODE)
        self.assertIsNone(self.sm.last_interaction_time)

    def test_scenario_1_hello_once_then_three_commands_without_wake_word(self):
        """
        Acceptance Test 1 & 8:
        Say 'Hello' once, then give 3 consecutive commands.
        All three execute in ACTIVE_LISTENING_MODE without returning to WAKE_WORD_MODE.
        """
        # User says 'hello' at t=100.0
        self.sm.on_wake_word_detected(timestamp=100.0)
        self.assertEqual(self.sm.state, AssistantState.ACTIVE_LISTENING_MODE)

        # Command 1: "Open YouTube and play Kalyani song" at t=105.0
        self.sm.on_command_executed(timestamp=105.0)
        self.assertEqual(self.sm.state, AssistantState.ACTIVE_LISTENING_MODE, 
                         "Must NOT return to Wake Word Mode after command 1")

        # Command 2: "Open Chrome" at t=110.0
        self.sm.on_command_executed(timestamp=110.0)
        self.assertEqual(self.sm.state, AssistantState.ACTIVE_LISTENING_MODE,
                         "Must NOT return to Wake Word Mode after command 2")

        # Command 3: "What time is it?" at t=120.0
        self.sm.on_command_executed(timestamp=120.0)
        self.assertEqual(self.sm.state, AssistantState.ACTIVE_LISTENING_MODE,
                         "Must NOT return to Wake Word Mode after command 3")

    def test_scenario_2_wait_30_seconds_after_command_remains_active(self):
        """
        Acceptance Test 2:
        Complete a command and wait 30 seconds.
        The assistant must remain in Active Listening Mode.
        """
        self.sm.on_wake_word_detected(timestamp=100.0)
        self.sm.on_command_executed(timestamp=110.0)

        # 30 seconds elapse (t = 140.0)
        current_time = 140.0
        self.assertFalse(self.sm.is_inactive(current_time=current_time))
        self.assertFalse(self.sm.check_inactivity_timeout(current_time=current_time))
        self.assertEqual(self.sm.state, AssistantState.ACTIVE_LISTENING_MODE)
        self.assertEqual(self.sm.time_remaining(current_time=current_time), 270.0)

    def test_scenario_3_command_resets_inactivity_timer(self):
        """
        Acceptance Test 3:
        Give another valid command before timeout. Inactivity timer must reset.
        """
        self.sm.on_wake_word_detected(timestamp=100.0)
        self.sm.on_command_executed(timestamp=100.0)

        # 250 seconds elapse (close to 300s timeout)
        self.assertEqual(self.sm.time_remaining(current_time=350.0), 50.0)

        # New valid command executed at t=350.0
        self.sm.on_command_executed(timestamp=350.0)

        # Timer must be reset back to 300 seconds
        self.assertEqual(self.sm.time_remaining(current_time=350.0), 300.0)
        self.assertEqual(self.sm.time_remaining(current_time=400.0), 250.0)

    def test_scenario_4_five_minute_timeout_returns_to_wake_word_mode(self):
        """
        Acceptance Test 4:
        Configure 5-minute timeout (300s) and verify state returns to Wake Word Mode after 300s of inactivity.
        """
        sm = AssistantStateMachine(timeout_seconds=300)
        sm.on_wake_word_detected(timestamp=100.0)
        self.assertEqual(sm.state, AssistantState.ACTIVE_LISTENING_MODE)

        # Inactive for 299s -> still active
        self.assertFalse(sm.check_inactivity_timeout(current_time=399.0))
        self.assertEqual(sm.state, AssistantState.ACTIVE_LISTENING_MODE)

        # Inactive for 300s -> timeout expires, returns to WAKE_WORD_MODE
        did_timeout = sm.check_inactivity_timeout(current_time=400.0)
        self.assertTrue(did_timeout)
        self.assertEqual(sm.state, AssistantState.WAKE_WORD_MODE)

    def test_scenario_5_ten_minute_timeout_uses_600_seconds(self):
        """
        Acceptance Test 5:
        Change timeout to 10 minutes and verify it uses 600 seconds.
        """
        sm_10min = AssistantStateMachine(timeout_seconds=600)
        self.assertEqual(sm_10min.timeout_seconds, 600.0)

        sm_10min.on_wake_word_detected(timestamp=100.0)
        
        # After 5 minutes (300s at t=400.0), 10-minute timeout is NOT expired
        self.assertFalse(sm_10min.check_inactivity_timeout(current_time=400.0))
        self.assertEqual(sm_10min.state, AssistantState.ACTIVE_LISTENING_MODE)
        self.assertEqual(sm_10min.time_remaining(current_time=400.0), 300.0)

        # At t=700.0 (600s after wake word), it expires
        self.assertTrue(sm_10min.check_inactivity_timeout(current_time=700.0))
        self.assertEqual(sm_10min.state, AssistantState.WAKE_WORD_MODE)

    def test_scenario_6_silence_or_unintelligible_recovers_gracefully(self):
        """
        Acceptance Test 6:
        Speech recognition returning silence or unintelligible noise keeps the session alive.
        """
        self.sm.on_wake_word_detected(timestamp=100.0)

        # Simulating multiple empty/silent cycles
        for tick in range(105, 130, 5):
            self.assertFalse(self.sm.check_inactivity_timeout(current_time=float(tick)))
            self.assertEqual(self.sm.state, AssistantState.ACTIVE_LISTENING_MODE)

    def test_scenario_7_long_running_command_does_not_prematurely_expire(self):
        """
        Acceptance Test 7:
        Execute a command that takes a long time (e.g. 40 seconds).
        The assistant must not immediately return to Wake Word Mode when it finishes.
        """
        self.sm.on_wake_word_detected(timestamp=100.0)

        # Command takes from t=100.0 to t=140.0 (40 seconds)
        # on_command_executed is called when the command completes at t=140.0
        self.sm.on_command_executed(timestamp=140.0)

        # Right after finishing, 300s of inactivity remain!
        self.assertEqual(self.sm.state, AssistantState.ACTIVE_LISTENING_MODE)
        self.assertEqual(self.sm.time_remaining(current_time=140.0), 300.0)
        self.assertFalse(self.sm.check_inactivity_timeout(current_time=140.0))


if __name__ == "__main__":
    unittest.main()
