"""
Tests for message buffer.
"""

import pytest
from src.client.message_buffer import MessageBuffer, Message
from src.client.mud_parser import ChannelType, ParsedMessage


class TestMessageBuffer:
    """Test message buffer and navigation."""

    def test_add_message(self):
        """Add a message to buffer."""
        buffer = MessageBuffer()
        msg = ParsedMessage(
            channel=ChannelType.BANDO,
            text="Test message",
            raw="[Bando] Test message"
        )

        result = buffer.add(msg)

        assert result.text == "Test message"
        assert result.channel == ChannelType.BANDO
        assert result.index == 0

    def test_get_channel_messages(self):
        """Retrieve all messages from a channel."""
        buffer = MessageBuffer()

        msg1 = ParsedMessage(ChannelType.BANDO, "Message 1", "raw1")
        msg2 = ParsedMessage(ChannelType.BANDO, "Message 2", "raw2")

        buffer.add(msg1)
        buffer.add(msg2)

        messages = buffer.get_channel(ChannelType.BANDO)

        assert len(messages) == 2
        assert messages[0].text == "Message 1"
        assert messages[1].text == "Message 2"

    def test_get_latest(self):
        """Get N most recent messages."""
        buffer = MessageBuffer()

        for i in range(5):
            msg = ParsedMessage(ChannelType.GENERAL, f"Message {i}", f"raw{i}")
            buffer.add(msg)

        latest = buffer.get_latest(ChannelType.GENERAL, 2)

        assert len(latest) == 2
        assert latest[0].text == "Message 3"
        assert latest[1].text == "Message 4"

    def test_navigate_forward_backward(self):
        """Navigate through messages."""
        buffer = MessageBuffer()

        for i in range(3):
            msg = ParsedMessage(ChannelType.GENERAL, f"Msg {i}", f"raw{i}")
            buffer.add(msg)

        # Start at end (most recent) - position defaults to -1 which converts to last index
        current = buffer.navigate(ChannelType.GENERAL, 0)  # delta=0 means stay at end
        assert current.text == "Msg 2"

        # Go back one message
        current = buffer.navigate(ChannelType.GENERAL, -1)
        assert current.text == "Msg 1"

        # Go back one more
        current = buffer.navigate(ChannelType.GENERAL, -1)
        assert current.text == "Msg 0"

        # Go forward one
        current = buffer.navigate(ChannelType.GENERAL, 1)
        assert current.text == "Msg 1"

    def test_multiple_channels_isolated(self):
        """Messages in different channels don't mix."""
        buffer = MessageBuffer()

        bando_msg = ParsedMessage(ChannelType.BANDO, "Bando msg", "raw")
        telepathy_msg = ParsedMessage(ChannelType.TELEPATHY, "Telepathy msg", "raw")

        buffer.add(bando_msg)
        buffer.add(telepathy_msg)

        bando_list = buffer.get_channel(ChannelType.BANDO)
        telepathy_list = buffer.get_channel(ChannelType.TELEPATHY)

        assert len(bando_list) == 1
        assert len(telepathy_list) == 1
        assert bando_list[0].text == "Bando msg"
        assert telepathy_list[0].text == "Telepathy msg"

    def test_max_messages_per_channel(self):
        """Exceed max messages should evict oldest."""
        buffer = MessageBuffer()
        max_msg = buffer.MAX_MESSAGES_PER_CHANNEL

        # Add more than max
        for i in range(max_msg + 10):
            msg = ParsedMessage(ChannelType.GENERAL, f"Message {i}", f"raw{i}")
            buffer.add(msg)

        messages = buffer.get_channel(ChannelType.GENERAL)

        # Should have exactly max messages
        assert len(messages) == max_msg
        # Oldest should be evicted
        assert messages[0].text == f"Message {10}"

    def test_reset_position(self):
        """Reset position should go to end."""
        buffer = MessageBuffer()

        for i in range(5):
            msg = ParsedMessage(ChannelType.GENERAL, f"Msg {i}", f"raw{i}")
            buffer.add(msg)

        # Navigate to middle
        buffer.navigate(ChannelType.GENERAL, -2)

        # Reset to end
        buffer.reset_position(ChannelType.GENERAL)

        # Current should be last message
        current = buffer.get_current(ChannelType.GENERAL)
        assert current.text == "Msg 4"

    def test_get_all_channels_with_messages(self):
        """Get list of channels that have messages."""
        buffer = MessageBuffer()

        msg1 = ParsedMessage(ChannelType.BANDO, "Msg", "raw")
        msg2 = ParsedMessage(ChannelType.TELEPATHY, "Msg", "raw")

        buffer.add(msg1)
        buffer.add(msg2)

        channels = buffer.get_all_channels()

        assert ChannelType.BANDO in channels
        assert ChannelType.TELEPATHY in channels
        assert ChannelType.GENERAL not in channels

    def test_get_position_info(self):
        """Get (current, total) for UI display."""
        buffer = MessageBuffer()

        for i in range(10):
            msg = ParsedMessage(ChannelType.GENERAL, f"Msg {i}", f"raw{i}")
            buffer.add(msg)

        # At end
        current, total = buffer.get_position_info(ChannelType.GENERAL)
        assert current == 10
        assert total == 10

        # Navigate back
        buffer.navigate(ChannelType.GENERAL, -3)
        current, total = buffer.get_position_info(ChannelType.GENERAL)
        assert current == 7
        assert total == 10

    def test_clear_buffer(self):
        """Clear should remove all messages."""
        buffer = MessageBuffer()

        msg = ParsedMessage(ChannelType.BANDO, "Msg", "raw")
        buffer.add(msg)

        buffer.clear()

        assert len(buffer.get_channel(ChannelType.BANDO)) == 0
        assert buffer.get_all_channels() == []

    def test_thread_safety(self):
        """Buffer should handle concurrent access."""
        import threading
        buffer = MessageBuffer()

        results = []

        def add_messages(channel, count):
            for i in range(count):
                msg = ParsedMessage(channel, f"Msg {i}", f"raw{i}")
                buffer.add(msg)

        def get_messages(channel):
            msgs = buffer.get_channel(channel)
            results.append(len(msgs))

        # Add from multiple threads
        t1 = threading.Thread(target=add_messages, args=(ChannelType.BANDO, 50))
        t2 = threading.Thread(target=add_messages, args=(ChannelType.TELEPATHY, 50))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Should have 50 messages in each channel
        assert len(buffer.get_channel(ChannelType.BANDO)) == 50
        assert len(buffer.get_channel(ChannelType.TELEPATHY)) == 50
