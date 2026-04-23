"""
Audio panning and spatial sound engine for 3D positional audio.
Supports left/right panning, front/back distance simulation via volume/EQ, and elevation.

Phase 6E: Advanced audio features for immersive MUD gameplay.
"""

import math
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple


class SoundDirection(Enum):
    """Cardinal directions for sound panning."""
    FRONT = (0, 1)       # Forward
    FRONT_LEFT = (-45, 1)
    LEFT = (-90, 0)      # Direct left
    BACK_LEFT = (-135, 1)
    BACK = (180, 1)      # Behind
    BACK_RIGHT = (135, 1)
    RIGHT = (90, 0)      # Direct right
    FRONT_RIGHT = (45, 1)
    ABOVE = (0, 2)       # Elevation up
    BELOW = (0, -1)      # Elevation down
    CENTER = (0, 0)      # Mono/center


@dataclass
class PanningCoordinates:
    """3D panning coordinates: azimuth (angle), elevation, distance."""
    azimuth: float   # 0=center, +90=right, -90=left, 180=back
    elevation: float  # 0=ear level, +90=above, -90=below
    distance: float   # 0.0=very close, 1.0=far away


class AudioPanner:
    """
    Spatial audio engine for 3D panning and distance simulation.

    Features:
    - Azimuth panning (left/right stereo)
    - Elevation simulation (high/low)
    - Distance simulation (volume + frequency rolloff)
    - HRTF-inspired techniques (head-related transfer functions)
    """

    def __init__(self):
        """Initialize panning engine."""
        self.direction_map = {
            "front": SoundDirection.FRONT,
            "left": SoundDirection.LEFT,
            "right": SoundDirection.RIGHT,
            "back": SoundDirection.BACK,
            "front_left": SoundDirection.FRONT_LEFT,
            "front_right": SoundDirection.FRONT_RIGHT,
            "back_left": SoundDirection.BACK_LEFT,
            "back_right": SoundDirection.BACK_RIGHT,
            "above": SoundDirection.ABOVE,
            "below": SoundDirection.BELOW,
            "center": SoundDirection.CENTER,
        }

    def get_panning_values(
        self,
        direction: str,
        distance: float = 0.5,
    ) -> Tuple[float, float, float]:
        """
        Calculate panning values for a given direction and distance.

        Args:
            direction: Direction name (e.g., "left", "front_right", "above")
            distance: Distance factor 0.0 (close) to 1.0 (far). Affects volume.

        Returns:
            Tuple of (left_pan, right_pan, distance_factor)
            - left_pan: 0.0 (silent) to 1.0 (full volume)
            - right_pan: 0.0 (silent) to 1.0 (full volume)
            - distance_factor: 0.0 (silent) to 1.0 (loud), already accounts for distance
        """
        direction = direction.lower()
        if direction not in self.direction_map:
            direction = "center"

        sound_dir = self.direction_map[direction]
        azimuth, elevation = sound_dir.value

        # Clamp distance to valid range
        distance = max(0.0, min(1.0, distance))

        # Calculate azimuth panning (left/right)
        # -90 (left) to +90 (right), with 0 being center
        azimuth_rad = math.radians(azimuth)
        # Pan law: constant energy (3dB rule)
        left_pan = math.cos(azimuth_rad + math.pi / 4)
        right_pan = math.sin(azimuth_rad + math.pi / 4)
        left_pan = max(0.0, min(1.0, left_pan))
        right_pan = max(0.0, min(1.0, right_pan))

        # Distance factor: closer = louder, farther = quieter
        # Uses inverse square law approximation
        distance_factor = 1.0 / (1.0 + distance)

        # Elevation affects perceived distance (lower sounds seem farther)
        if elevation != 0:
            # Above = slightly louder/clearer
            # Below = slightly quieter/duller
            if elevation > 0:
                distance_factor *= (1.0 + elevation * 0.2)
            else:
                distance_factor *= (1.0 - abs(elevation) * 0.15)

        # Ensure distance factor is in valid range
        distance_factor = max(0.0, min(1.0, distance_factor))

        return (left_pan, right_pan, distance_factor)

    def get_direction_name(self, azimuth: float, elevation: float) -> str:
        """
        Get the closest cardinal direction name for azimuth/elevation.

        Args:
            azimuth: Angle in degrees (-180 to 180)
            elevation: Elevation in degrees

        Returns:
            Direction name (e.g., "front_left", "back")
        """
        # Normalize azimuth to -180 to 180
        azimuth = ((azimuth + 180) % 360) - 180

        # Check elevation first
        if elevation > 45:
            return "above"
        elif elevation < -45:
            return "below"

        # Map azimuth to direction
        if -22.5 <= azimuth <= 22.5:
            return "front"
        elif 22.5 < azimuth <= 67.5:
            return "front_right"
        elif 67.5 < azimuth <= 112.5:
            return "right"
        elif 112.5 < azimuth <= 157.5:
            return "back_right"
        elif azimuth > 157.5 or azimuth < -157.5:
            return "back"
        elif -157.5 <= azimuth <= -112.5:
            return "back_left"
        elif -112.5 < azimuth <= -67.5:
            return "left"
        elif -67.5 < azimuth <= -22.5:
            return "front_left"
        else:
            return "center"

    def apply_hrtf_filter(
        self,
        audio_data: bytes,
        direction: str,
        sample_rate: int = 44100,
    ) -> bytes:
        """
        Apply head-related transfer function (HRTF) filtering for elevation simulation.

        This is a simplified simulation. In production, you'd use actual HRTF impulse responses.
        For now, we adjust the audio characteristics based on direction.

        Args:
            audio_data: PCM audio data
            direction: Direction for HRTF
            sample_rate: Sample rate in Hz

        Returns:
            HRTF-filtered audio data
        """
        # Simplified HRTF: for now, return original audio
        # Full implementation would require DSP library (scipy.signal)
        # and HRTF impulse response files
        return audio_data

    def calculate_distance_volume(self, distance: float) -> float:
        """
        Calculate volume adjustment for distance perception.

        Args:
            distance: Distance factor 0.0 (close) to 1.0 (far)

        Returns:
            Volume multiplier (0.0 to 1.0)
        """
        distance = max(0.0, min(1.0, distance))
        # Inverse square law
        return 1.0 / (1.0 + distance * 2.0)

    def get_panning_string(self, direction: str) -> str:
        """
        Get a human-readable description of panning direction.

        Args:
            direction: Direction name

        Returns:
            Description string (e.g., "front left", "far behind")
        """
        direction = direction.lower()
        descriptions = {
            "front": "ahead",
            "front_left": "ahead and to the left",
            "left": "to your left",
            "back_left": "behind and to the left",
            "back": "behind",
            "back_right": "behind and to the right",
            "right": "to your right",
            "front_right": "ahead and to the right",
            "above": "above",
            "below": "below",
            "center": "all around",
        }
        return descriptions.get(direction, "around you")


class PositionalAudioTracker:
    """Track active sounds and their positions in 3D space."""

    def __init__(self):
        """Initialize position tracker."""
        self.sounds = {}  # sound_id -> {position, volume, direction}
        self.panner = AudioPanner()

    def add_sound(
        self,
        sound_id: str,
        direction: str,
        distance: float = 0.5,
        looping: bool = False,
    ) -> bool:
        """
        Register a new sound at a position.

        Args:
            sound_id: Unique sound identifier
            direction: Direction name
            distance: Distance factor (0.0=close, 1.0=far)
            looping: Whether sound loops

        Returns:
            True if added successfully
        """
        if sound_id in self.sounds:
            return False

        self.sounds[sound_id] = {
            "direction": direction,
            "distance": distance,
            "looping": looping,
            "panning": self.panner.get_panning_values(direction, distance),
        }
        return True

    def update_position(
        self,
        sound_id: str,
        direction: str,
        distance: float = 0.5,
    ) -> bool:
        """
        Update an existing sound's position.

        Args:
            sound_id: Sound identifier
            direction: New direction
            distance: New distance factor

        Returns:
            True if updated successfully
        """
        if sound_id not in self.sounds:
            return False

        self.sounds[sound_id]["direction"] = direction
        self.sounds[sound_id]["distance"] = distance
        self.sounds[sound_id]["panning"] = self.panner.get_panning_values(
            direction, distance
        )
        return True

    def remove_sound(self, sound_id: str) -> bool:
        """
        Stop tracking a sound.

        Args:
            sound_id: Sound identifier

        Returns:
            True if removed successfully
        """
        if sound_id in self.sounds:
            del self.sounds[sound_id]
            return True
        return False

    def get_sound_info(self, sound_id: str) -> Optional[dict]:
        """Get tracking info for a sound."""
        return self.sounds.get(sound_id)

    def get_all_sounds(self) -> dict:
        """Get all tracked sounds."""
        return self.sounds.copy()


# Module-level singleton
_panner = AudioPanner()
_tracker = PositionalAudioTracker()


def get_panner() -> AudioPanner:
    """Get the global audio panner instance."""
    return _panner


def get_tracker() -> PositionalAudioTracker:
    """Get the global position tracker instance."""
    return _tracker
