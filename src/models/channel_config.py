"""
Channel Configuration - Manage muted channels and display settings.

Implements per-channel muting to allow users to silence specific channels
while keeping others audible (muting suppresses TTS, not visual display).
"""

from typing import Dict
from client.mud_parser import ChannelType


class ChannelConfig:
    """
    Manage channel muting and display preferences.

    Each channel can be individually muted to prevent TTS announcements.
    Uses mud_parser.ChannelType as single source of truth for channels.
    """

    def __init__(self):
        """Initialize channel configuration."""
        # Track which channels are muted (True = muted, False = active)
        self.muted_channels: Dict[str, bool] = {
            channel.value: False for channel in ChannelType
        }

    def is_muted(self, channel: ChannelType) -> bool:
        """
        Check if a channel is muted.

        Args:
            channel: ChannelType to check

        Returns:
            bool: True if channel is muted, False if active
        """
        channel_value = channel.value if isinstance(channel, ChannelType) else str(channel)
        return self.muted_channels.get(channel_value, False)

    def set_muted(self, channel: ChannelType, muted: bool):
        """
        Mute or unmute a channel.

        Args:
            channel: ChannelType to modify
            muted: True to mute, False to unmute
        """
        channel_value = channel.value if isinstance(channel, ChannelType) else str(channel)
        self.muted_channels[channel_value] = muted

    def toggle_channel(self, channel: ChannelType) -> bool:
        """
        Toggle a channel's mute status.

        Args:
            channel: ChannelType to toggle

        Returns:
            bool: New mute status (True if muted)
        """
        current = self.is_muted(channel)
        self.set_muted(channel, not current)
        return not current

    def get_channel_status(self, channel: ChannelType) -> str:
        """
        Get human-readable status of a channel.

        Args:
            channel: ChannelType to check

        Returns:
            str: "Silenciado" or "Activo"
        """
        return "Silenciado" if self.is_muted(channel) else "Activo"

    def get_all_channels(self) -> Dict[str, str]:
        """
        Get status of all channels.

        Returns:
            dict: channel_value → "Silenciado" or "Activo"
        """
        return {
            channel_value: ("Silenciado" if self.muted_channels[channel_value] else "Activo")
            for channel_value in self.muted_channels.keys()
        }

    def mute_all(self):
        """Mute all channels."""
        for channel_value in self.muted_channels.keys():
            self.muted_channels[channel_value] = True

    def unmute_all(self):
        """Unmute all channels."""
        for channel_value in self.muted_channels.keys():
            self.muted_channels[channel_value] = False
