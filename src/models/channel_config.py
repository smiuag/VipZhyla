"""
Channel Configuration - Manage muted channels and display settings.

Implements VipMud's Silencio* variables (SilencioBando, SilencioChat, etc.)
to allow users to mute specific channels.
"""

from enum import Enum
from typing import Dict


class ChannelType(Enum):
    """Channel types for organization and filtering."""
    GENERAL = "general"
    BANDO = "bando"
    CIUDADANIA = "ciudadania"
    CHAT = "chat"
    GREMIO = "gremio"
    FAMILIA = "familia"
    ROL = "rol"
    TELEPATHY = "telepathy"
    ROOM = "room"
    EVENTS = "events"
    SPECIAL = "special"


class ChannelConfig:
    """
    Manage channel muting and display preferences.

    Each channel can be individually muted to prevent TTS announcements.
    """

    def __init__(self):
        """Initialize channel configuration."""
        # Track which channels are muted (True = muted, False = active)
        self.muted_channels: Dict[ChannelType, bool] = {
            channel: False for channel in ChannelType
        }

    def is_muted(self, channel: ChannelType) -> bool:
        """
        Check if a channel is muted.

        Args:
            channel: ChannelType to check

        Returns:
            bool: True if channel is muted, False if active
        """
        return self.muted_channels.get(channel, False)

    def set_muted(self, channel: ChannelType, muted: bool):
        """
        Mute or unmute a channel.

        Args:
            channel: ChannelType to modify
            muted: True to mute, False to unmute
        """
        self.muted_channels[channel] = muted

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
            str: "Muted" or "Active"
        """
        return "Muted" if self.is_muted(channel) else "Active"

    def get_all_channels(self) -> Dict[ChannelType, str]:
        """
        Get status of all channels.

        Returns:
            dict: ChannelType -> "Muted" or "Active"
        """
        return {
            channel: self.get_channel_status(channel)
            for channel in ChannelType
        }

    def mute_all(self):
        """Mute all channels."""
        for channel in ChannelType:
            self.set_muted(channel, True)

    def unmute_all(self):
        """Unmute all channels."""
        for channel in ChannelType:
            self.set_muted(channel, False)
