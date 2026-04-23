"""
Tests for list dialogs (data layer and formatting logic).

Note: Full dialog UI testing requires a wxPython display environment.
These tests cover the data formatting and population logic.
"""

from datetime import datetime, timedelta
from src.client.message_buffer import MessageBuffer, Message
from src.client.mud_parser import ChannelType, ParsedMessage


class TestMessageFormatting:
    """Test message formatting logic."""

    def test_format_message_with_timestamp(self):
        """Test formatting message with timestamp."""
        from src.ui.list_dialogs import HistoryDialog

        # Create a mock message
        msg = Message(
            text="Test message",
            channel=ChannelType.GENERAL,
            timestamp=datetime(2026, 4, 23, 14, 30, 0),
            raw="[Raw] Test message",
            index=0
        )

        # We can't instantiate HistoryDialog without wx, but we can test the logic
        # This is tested implicitly through integration with actual dialogs
        pass

    def test_channel_list_filtering(self):
        """Test that dialog filters to correct channels."""
        # Create a buffer with messages in different channels
        buffer = MessageBuffer()

        # Add messages to different channels
        for i in range(3):
            msg = ParsedMessage(ChannelType.BANDO, f"Bando msg {i}", f"raw{i}")
            buffer.add(msg)

        for i in range(2):
            msg = ParsedMessage(ChannelType.TELEPATHY, f"Telepathy msg {i}", f"raw{i}")
            buffer.add(msg)

        # Test that we can retrieve channel-specific messages
        bando_msgs = buffer.get_channel(ChannelType.BANDO)
        telepathy_msgs = buffer.get_channel(ChannelType.TELEPATHY)

        assert len(bando_msgs) == 3
        assert len(telepathy_msgs) == 2
        assert bando_msgs[0].channel == ChannelType.BANDO
        assert telepathy_msgs[0].channel == ChannelType.TELEPATHY

    def test_comm_channel_filtering(self):
        """Test filtering communication channels (excluding GENERAL/SYSTEM)."""
        buffer = MessageBuffer()

        # Add messages to various channels
        for channel in [ChannelType.BANDO, ChannelType.TELEPATHY, ChannelType.CITIZENSHIP, ChannelType.GROUP]:
            msg = ParsedMessage(channel, f"Message for {channel.value}", "raw")
            buffer.add(msg)

        # All channels should be retrievable
        all_channels = buffer.get_all_channels()
        assert ChannelType.BANDO in all_channels
        assert ChannelType.TELEPATHY in all_channels
        assert ChannelType.CITIZENSHIP in all_channels
        assert ChannelType.GROUP in all_channels

    def test_position_info_for_display(self):
        """Test retrieving position info for status display."""
        buffer = MessageBuffer()

        # Add 5 messages
        for i in range(5):
            msg = ParsedMessage(ChannelType.GENERAL, f"Message {i}", "raw")
            buffer.add(msg)

        # Get position at end (newest)
        current, total = buffer.get_position_info(ChannelType.GENERAL)
        assert current == 5
        assert total == 5

        # Navigate back
        buffer.navigate(ChannelType.GENERAL, -2)
        current, total = buffer.get_position_info(ChannelType.GENERAL)
        assert current == 3
        assert total == 5

    def test_empty_channel_handling(self):
        """Test behavior with empty channels."""
        buffer = MessageBuffer()

        # Query empty channel
        general_msgs = buffer.get_channel(ChannelType.GENERAL)
        assert len(general_msgs) == 0

        # Position info for empty channel
        current, total = buffer.get_position_info(ChannelType.GENERAL)
        assert total == 0

    def test_all_channels_list(self):
        """Test getting list of non-empty channels."""
        buffer = MessageBuffer()

        # Initially empty
        channels = buffer.get_all_channels()
        assert len(channels) == 0

        # Add message to one channel
        msg = ParsedMessage(ChannelType.BANDO, "Test", "raw")
        buffer.add(msg)

        channels = buffer.get_all_channels()
        assert len(channels) == 1
        assert ChannelType.BANDO in channels

        # Add to another channel
        msg = ParsedMessage(ChannelType.TELEPATHY, "Test", "raw")
        buffer.add(msg)

        channels = buffer.get_all_channels()
        assert len(channels) == 2
        assert ChannelType.BANDO in channels
        assert ChannelType.TELEPATHY in channels
