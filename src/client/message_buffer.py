"""
Message buffer for storing MUD messages by channel.

Implements ChannelHistory + VipMud pattern:
- Store up to 99 messages per channel (VipMud standard, prevents memory bloat)
- FIFO eviction (oldest messages removed when limit exceeded)
- Navigation support (forward, backward, jump to specific position)
- Thread-safe operations
"""

import threading
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

from .mud_parser import ChannelType, ParsedMessage


@dataclass
class Message:
    """A single message in the buffer."""
    text: str
    channel: ChannelType
    timestamp: datetime
    raw: str  # Original unprocessed text
    index: int  # Position in channel's message list


class MessageBuffer:
    """
    Stores messages organized by channel with navigation support.

    Thread-safe for concurrent read/write from network thread + UI thread.
    """

    MAX_MESSAGES_PER_CHANNEL = 99  # VipMud standard limit (prevents memory bloat in long sessions)

    def __init__(self):
        """Initialize message buffer."""
        # Channel -> list of Message objects
        self.messages: dict[ChannelType, list[Message]] = {
            channel: [] for channel in ChannelType
        }
        # Channel -> current navigation index (-1 means at end)
        self.positions: dict[ChannelType, int] = {
            channel: -1 for channel in ChannelType
        }
        # Lock for thread-safe operations
        self.lock = threading.RLock()

    def add(self, parsed_msg: ParsedMessage) -> Message:
        """
        Add a message to the buffer.

        Args:
            parsed_msg: ParsedMessage from MUDParser

        Returns:
            Message object added to buffer
        """
        with self.lock:
            channel = parsed_msg.channel
            messages = self.messages[channel]

            # Create message object
            msg = Message(
                text=parsed_msg.text,
                channel=channel,
                timestamp=datetime.now(),
                raw=parsed_msg.raw,
                index=len(messages)
            )

            # Add to channel's list
            messages.append(msg)

            # Evict oldest if exceeds limit
            if len(messages) > self.MAX_MESSAGES_PER_CHANNEL:
                messages.pop(0)
                # Renumber indices
                for i, m in enumerate(messages):
                    m.index = i

            # Reset position to end (show newest messages)
            self.positions[channel] = -1

            return msg

    def get_channel(self, channel: ChannelType) -> List[Message]:
        """Get all messages in a channel."""
        with self.lock:
            return list(self.messages[channel])

    def get_latest(self, channel: ChannelType, n: int = 1) -> List[Message]:
        """
        Get the N most recent messages in a channel.

        Args:
            channel: ChannelType
            n: Number of messages (default 1)

        Returns:
            List of Message objects (oldest to newest)
        """
        with self.lock:
            messages = self.messages[channel]
            return messages[-n:] if messages else []

    def navigate(self, channel: ChannelType, delta: int) -> Optional[Message]:
        """
        Navigate by delta (+1 next, -1 previous).

        Args:
            channel: ChannelType
            delta: +1 for next, -1 for previous

        Returns:
            Message at new position, or None if out of bounds
        """
        with self.lock:
            messages = self.messages[channel]
            if not messages:
                return None

            pos = self.positions[channel]

            # Convert -1 (end) to actual index, then apply delta
            if pos == -1:
                pos = len(messages) - 1

            # Apply delta to move forward/backward
            pos += delta

            # Clamp to bounds
            pos = max(0, min(pos, len(messages) - 1))
            self.positions[channel] = pos

            return messages[pos]

    def reset_position(self, channel: ChannelType):
        """Reset navigation position to end (show newest messages)."""
        with self.lock:
            self.positions[channel] = -1

    def get_all_channels(self) -> List[ChannelType]:
        """Get list of channels that have messages."""
        with self.lock:
            return [ch for ch in ChannelType if self.messages[ch]]

    def clear(self):
        """Clear all messages (for disconnection/cleanup)."""
        with self.lock:
            for channel in ChannelType:
                self.messages[channel] = []
                self.positions[channel] = -1

    def get_current(self, channel: ChannelType) -> Optional[Message]:
        """
        Get message at current position without navigation.

        Returns:
            Message at current position, or None
        """
        with self.lock:
            messages = self.messages[channel]
            if not messages:
                return None

            pos = self.positions[channel]
            if pos == -1:
                return messages[-1] if messages else None
            return messages[pos]

    def get_position_info(self, channel: ChannelType) -> tuple[int, int]:
        """
        Get (current_index, total_count) for UI display.

        Example: "Message 5 of 142"
        """
        with self.lock:
            messages = self.messages[channel]
            if not messages:
                return (0, 0)

            pos = self.positions[channel]
            if pos == -1:
                current_index = len(messages)
            else:
                current_index = pos + 1

            return (current_index, len(messages))
