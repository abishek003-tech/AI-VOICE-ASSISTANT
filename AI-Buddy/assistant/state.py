from enum import Enum, auto
import logging
import time
from typing import Optional

import config

logger = logging.getLogger("ai_assistant.state")

class AssistantState(Enum):
    WAKE_WORD_MODE = auto()
    ACTIVE_LISTENING_MODE = auto()

class AssistantStateMachine:
    """
    Manages state transitions and inactivity timing for the AI voice assistant.
    Tracks user interactions using a monotonic clock to ensure reliable timeouts.
    """
    def __init__(self, timeout_seconds: Optional[float] = None):
        self.timeout_seconds = float(
            timeout_seconds if timeout_seconds is not None 
            else config.ACTIVE_LISTENING_TIMEOUT_SECONDS
        )
        self.state = AssistantState.WAKE_WORD_MODE
        self.last_interaction_time: Optional[float] = None
        logger.info(
            f"State Machine initialized in {self.state.name} "
            f"(Active Listening Timeout: {self.timeout_seconds:.1f}s)"
        )

    def transition_to(self, new_state: AssistantState):
        """Execute a state transition with debug logging."""
        if self.state != new_state:
            logger.info(f"State transition: {self.state.name} -> {new_state.name}")
            self.state = new_state
        else:
            logger.debug(f"State maintained: {self.state.name}")

    def record_interaction(self, timestamp: Optional[float] = None):
        """Reset the inactivity timer to the current monotonic time."""
        now = timestamp if timestamp is not None else time.monotonic()
        self.last_interaction_time = now
        logger.debug(f"Interaction recorded. Inactivity timer reset at monotonic {now:.2f}")

    def time_inactive(self, current_time: Optional[float] = None) -> float:
        """Calculate total seconds elapsed since the last valid interaction."""
        if self.last_interaction_time is None:
            return 0.0
        now = current_time if current_time is not None else time.monotonic()
        return max(0.0, now - self.last_interaction_time)

    def time_remaining(self, current_time: Optional[float] = None) -> float:
        """Calculate remaining active listening seconds before timeout."""
        if self.state != AssistantState.ACTIVE_LISTENING_MODE or self.last_interaction_time is None:
            return self.timeout_seconds
        elapsed = self.time_inactive(current_time)
        return max(0.0, self.timeout_seconds - elapsed)

    def is_inactive(self, current_time: Optional[float] = None) -> bool:
        """Check whether the inactivity period has reached or exceeded the configured timeout."""
        if self.state != AssistantState.ACTIVE_LISTENING_MODE:
            return False
        if self.last_interaction_time is None:
            return False
        return self.time_inactive(current_time) >= self.timeout_seconds

    def on_wake_word_detected(self, timestamp: Optional[float] = None):
        """Handle wake-word trigger: enter Active Listening Mode and arm timer."""
        self.transition_to(AssistantState.ACTIVE_LISTENING_MODE)
        self.record_interaction(timestamp)
        logger.info(f"Entered ACTIVE_LISTENING_MODE. Timeout window: {self.timeout_seconds:.1f}s")

    def on_command_executed(self, timestamp: Optional[float] = None):
        """Handle completed command: reset inactivity timer and stay in Active Listening Mode."""
        self.record_interaction(timestamp)
        logger.info(
            f"Command finished. Timer reset. Remaining active window: {self.time_remaining():.1f}s"
        )

    def check_inactivity_timeout(self, current_time: Optional[float] = None) -> bool:
        """
        Evaluate inactivity. If the active listening window has expired,
        transition back to WAKE_WORD_MODE and return True.
        """
        if self.state == AssistantState.ACTIVE_LISTENING_MODE and self.is_inactive(current_time):
            elapsed = self.time_inactive(current_time)
            logger.info(
                f"Inactivity timeout reached ({elapsed:.1f}s >= {self.timeout_seconds:.1f}s). "
                f"Returning to WAKE_WORD_MODE."
            )
            self.transition_to(AssistantState.WAKE_WORD_MODE)
            self.last_interaction_time = None
            return True
        return False
