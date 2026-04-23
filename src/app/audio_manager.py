"""
Audio Manager - Text-to-Speech and audio event handling

Handles TTS announcements for screen readers and sound effects for game events.
Uses pyttsx3 for cross-platform TTS that works alongside NVDA.
"""

import pyttsx3
import threading
from enum import Enum
from pathlib import Path

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False


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

    def play_sound(self, sound_path, pan=0.5, volume=1.0):
        """Play a sound effect file.

        Args:
            sound_path (str): Path to sound file (WAV, MP3, etc.)
            pan (float): Pan left/right (0.0=left, 1.0=right, 0.5=center)
            volume (float): Volume level (0.0-1.0)

        Returns:
            bool: True if sound started playing, False if failed
        """
        if not self.enabled:
            return False

        sound_path = str(sound_path)
        file_path = Path(sound_path)

        # Check if file exists (with common locations)
        if not file_path.is_absolute():
            # Try relative to src/data/sounds/
            alt_paths = [
                Path("src/data/sounds") / sound_path,
                Path("src/sounds") / sound_path,
                Path("sounds") / sound_path,
                Path(sound_path)
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    file_path = alt_path
                    break

        if not file_path.exists():
            print(f"Warning: Sound file not found: {sound_path}")
            return False

        # Try pygame first (cross-platform)
        if PYGAME_AVAILABLE:
            try:
                return self._play_sound_pygame(str(file_path), pan, volume)
            except Exception as e:
                print(f"Warning: pygame sound playback failed: {e}")

        # Fallback to winsound (Windows only)
        if WINSOUND_AVAILABLE:
            try:
                return self._play_sound_winsound(str(file_path))
            except Exception as e:
                print(f"Warning: winsound playback failed: {e}")

        print(f"Warning: No sound playback available (install pygame for cross-platform support)")
        return False

    def _play_sound_pygame(self, file_path, pan=0.5, volume=1.0):
        """Play sound using pygame mixer."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(max(0.0, min(1.0, volume)))

            # Play in background thread to avoid blocking
            def play_in_thread():
                try:
                    sound.play()
                except Exception as e:
                    print(f"Error playing sound: {e}")

            thread = threading.Thread(target=play_in_thread, daemon=True)
            thread.start()
            return True
        except Exception as e:
            print(f"pygame playback failed: {e}")
            return False

    def _play_sound_winsound(self, file_path):
        """Play sound using winsound (Windows only)."""
        try:
            # winsound.SND_FILENAME plays WAV files
            winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except Exception as e:
            print(f"winsound playback failed: {e}")
            return False

    def shutdown(self):
        """Shutdown audio manager and clean up resources."""
        if self.engine:
            try:
                self.engine.endLoop()
            except Exception:
                pass
            self.engine = None

        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.quit()
            except Exception:
                pass

    def __del__(self):
        """Cleanup on object destruction."""
        self.shutdown()
