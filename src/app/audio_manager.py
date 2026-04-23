"""
Audio Manager - Text-to-Speech and audio event handling

Handles TTS announcements for screen readers and sound effects for game events.
Uses pyttsx3 for cross-platform TTS that works alongside NVDA.
"""

import pyttsx3
import threading
from enum import Enum


class AudioLevel(Enum):
    """Verbosity levels for audio feedback."""

    SILENT = 0      # No TTS (only sound effects)
    MINIMAL = 1     # Only critical events
    NORMAL = 2      # Standard announcements (default)
    VERBOSE = 3     # All state changes and events
    DEBUG = 4       # Include debug information


class AudioManager:
    """Manage text-to-speech and audio events for accessibility."""

    def __init__(self, rate=150, volume=1.0):
        """Initialize audio manager.

        Args:
            rate (int): TTS speaking rate (0-300, default 150)
            volume (float): TTS volume (0.0-1.0, default 1.0)
        """
        self.level = AudioLevel.NORMAL
        self.enabled = True
        self.rate = rate
        self.volume = volume

        # Initialize pyttsx3
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
        except Exception as e:
            print(f"Warning: TTS initialization failed: {e}")
            self.engine = None

        # Thread for non-blocking TTS
        self.tts_thread = None

    def announce(self, message, level=None):
        """Announce a message via TTS.

        Args:
            message (str): The message to announce
            level (AudioLevel): Minimum level required to announce (default: NORMAL)
        """
        if not self.enabled or not self.engine:
            return

        if level is None:
            level = AudioLevel.NORMAL

        # Only announce if current level is >= required level
        if self.level.value < level.value:
            return

        # Run TTS in background thread to avoid blocking UI
        self.tts_thread = threading.Thread(
            target=self._speak, args=(message,), daemon=True
        )
        self.tts_thread.start()

    def _speak(self, message):
        """Internal method to speak message (runs in thread)."""
        try:
            if self.engine:
                self.engine.say(message)
                self.engine.runAndWait()
        except Exception as e:
            print(f"Error speaking message: {e}")

    def announce_state_change(self, state_name, new_value):
        """Announce a state change (for controls/status).

        Args:
            state_name (str): Name of the state (e.g., "Health")
            new_value (str): New value (e.g., "100 of 200")
        """
        message = f"{state_name}: {new_value}"
        self.announce(message, AudioLevel.NORMAL)

    def announce_event(self, event_name, details=""):
        """Announce a game event.

        Args:
            event_name (str): Name of the event
            details (str): Additional event details
        """
        if details:
            message = f"{event_name}: {details}"
        else:
            message = event_name

        self.announce(message, AudioLevel.MINIMAL)

    def announce_error(self, error_message):
        """Announce an error or alert.

        Args:
            error_message (str): The error message
        """
        message = f"Error: {error_message}"
        self.announce(message, AudioLevel.MINIMAL)

    def set_verbosity(self, level):
        """Set TTS verbosity level.

        Args:
            level (AudioLevel): The verbosity level
        """
        self.level = level
        self.announce(f"Verbosity set to {level.name.lower()}", AudioLevel.MINIMAL)

    def toggle_verbosity(self):
        """Toggle between normal and verbose modes."""
        if self.level == AudioLevel.NORMAL:
            self.set_verbosity(AudioLevel.VERBOSE)
        else:
            self.set_verbosity(AudioLevel.NORMAL)

    def set_enabled(self, enabled):
        """Enable or disable TTS.

        Args:
            enabled (bool): Whether to enable TTS
        """
        self.enabled = enabled
        if enabled:
            self.announce("TTS enabled", AudioLevel.MINIMAL)

    def set_rate(self, rate):
        """Set TTS speaking rate.

        Args:
            rate (int): Speaking rate (0-300, 150 is normal)
        """
        self.rate = rate
        if self.engine:
            self.engine.setProperty('rate', rate)
            self.announce(f"Speaking rate set to {rate}", AudioLevel.MINIMAL)

    def set_volume(self, volume):
        """Set TTS volume.

        Args:
            volume (float): Volume level (0.0-1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        if self.engine:
            self.engine.setProperty('volume', self.volume)
            pct = int(self.volume * 100)
            self.announce(f"Volume set to {pct} percent", AudioLevel.MINIMAL)

    def shutdown(self):
        """Shutdown audio manager and clean up resources."""
        if self.engine:
            try:
                self.engine.endLoop()
            except Exception:
                pass
            self.engine = None

    def __del__(self):
        """Cleanup on object destruction."""
        self.shutdown()
