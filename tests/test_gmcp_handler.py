"""
Tests for GMCP handler module.
"""

import pytest
from src.client.gmcp_handler import GmcpHandler
from src.client.mud_parser import ChannelType


class TestGmcpHandler:
    """Test GMCP handler module."""

    def test_initialization(self):
        """Initialize GMCP handler without audio."""
        handler = GmcpHandler(audio=None)
        assert handler.audio is None
        assert handler.on_channel_message is None

    def test_vitals_callback_fires_on_change(self):
        """Char.Vitals callback fires when vitals change."""
        handler = GmcpHandler(audio=None)
        callbacks = []

        def vitals_cb(hp, maxhp, mp, maxmp):
            callbacks.append((hp, maxhp, mp, maxmp))

        handler.set_vitals_callback(vitals_cb)

        # First vitals
        handler.handle("Char.Vitals", {"hp": 100, "maxhp": 200, "mp": 50, "maxmp": 100})

        assert len(callbacks) == 1
        assert callbacks[0] == (100, 200, 50, 100)

    def test_vitals_callback_not_fired_if_no_change(self):
        """Callback not fired if vitals haven't changed."""
        handler = GmcpHandler(audio=None)
        callbacks = []

        handler.set_vitals_callback(lambda h, mh, m, mm: callbacks.append(True))

        # Send same vitals twice
        handler.handle("Char.Vitals", {"hp": 100, "maxhp": 200, "mp": 50, "maxmp": 100})
        handler.handle("Char.Vitals", {"hp": 100, "maxhp": 200, "mp": 50, "maxmp": 100})

        assert len(callbacks) == 1  # Only first one

    def test_room_info_callback(self):
        """Room.Info callback fires with room name and exits."""
        handler = GmcpHandler(audio=None)
        results = []

        handler.set_room_callback(lambda name, exits: results.append((name, exits)))

        data = {"name": "El mercado", "exits": ["north", "south", "east"]}
        handler.handle("Room.Info", data)

        assert len(results) == 1
        assert results[0] == ("El mercado", ["north", "south", "east"])

    def test_comm_channel_bando(self):
        """Comm.Channel with bando maps to BANDO channel."""
        handler = GmcpHandler(audio=None)
        messages = []

        handler.set_channel_callback(lambda msg: messages.append(msg))

        data = {
            "channel": "bando",
            "talker": "Aeroth",
            "text": "Enemigo en Eldor"
        }
        handler.handle("Comm.Channel", data)

        assert len(messages) == 1
        msg = messages[0]
        assert msg.channel == ChannelType.BANDO
        assert "Aeroth" in msg.text
        assert "Enemigo en Eldor" in msg.text

    def test_comm_channel_telepathy(self):
        """Comm.Channel with telepátia maps to TELEPATHY."""
        handler = GmcpHandler(audio=None)
        messages = []

        handler.set_channel_callback(lambda msg: messages.append(msg))

        data = {
            "channel": "telepátia",
            "talker": "Persona",
            "text": "Hola?"
        }
        handler.handle("Comm.Channel", data)

        assert len(messages) == 1
        assert messages[0].channel == ChannelType.TELEPATHY

    def test_comm_channel_citizenship(self):
        """Comm.Channel with ciudadanía maps to CITIZENSHIP."""
        handler = GmcpHandler(audio=None)
        messages = []

        handler.set_channel_callback(lambda msg: messages.append(msg))

        data = {
            "channel": "ciudadanía",
            "talker": "Mayor",
            "text": "Aviso"
        }
        handler.handle("Comm.Channel", data)

        assert len(messages) == 1
        assert messages[0].channel == ChannelType.CITIZENSHIP

    def test_comm_channel_unknown_defaults_to_general(self):
        """Unknown channel name defaults to GENERAL."""
        handler = GmcpHandler(audio=None)
        messages = []

        handler.set_channel_callback(lambda msg: messages.append(msg))

        data = {
            "channel": "unknownChannel",
            "talker": "Someone",
            "text": "Message"
        }
        handler.handle("Comm.Channel", data)

        assert messages[0].channel == ChannelType.GENERAL

    def test_char_status_callback(self):
        """Char.Status callback fires with status data."""
        handler = GmcpHandler(audio=None)
        statuses = []

        handler.set_status_callback(lambda s: statuses.append(s))

        data = {"name": "Aeroth", "level": 42, "class": "Soldado"}
        handler.handle("Char.Status", data)

        assert len(statuses) == 1
        assert statuses[0]["name"] == "Aeroth"
        assert statuses[0]["level"] == 42

    def test_unknown_module_no_crash(self):
        """Unknown GMCP module doesn't crash."""
        handler = GmcpHandler(audio=None)

        # Should not raise exception
        handler.handle("Unknown.Module", {"data": "value"})
        handler.handle("Foo.Bar.Baz", {"x": 1})

    def test_invalid_vitals_data_ignored(self):
        """Invalid vitals data doesn't crash."""
        handler = GmcpHandler(audio=None)
        callbacks = []

        handler.set_vitals_callback(lambda h, mh, m, mm: callbacks.append(True))

        # Invalid data (missing required fields)
        handler.handle("Char.Vitals", {"invalid": "data"})

        # Should not crash, should have default values
        assert len(callbacks) == 1

    def test_core_hello_no_crash(self):
        """Core.Hello module doesn't crash."""
        handler = GmcpHandler(audio=None)

        # Should not raise exception
        handler.handle("Core.Hello", {"version": "1.0", "client": "VipZhyla"})

    def test_multiple_callbacks_can_coexist(self):
        """Multiple callbacks can be registered simultaneously."""
        handler = GmcpHandler(audio=None)

        channel_msgs = []
        room_info = []
        vitals = []

        handler.set_channel_callback(lambda msg: channel_msgs.append(msg))
        handler.set_room_callback(lambda name, exits: room_info.append((name, exits)))
        handler.set_vitals_callback(lambda h, mh, m, mm: vitals.append((h, mh)))

        # Send various GMCP data
        handler.handle("Comm.Channel", {"channel": "bando", "talker": "X", "text": "Y"})
        handler.handle("Room.Info", {"name": "Sala", "exits": []})
        handler.handle("Char.Vitals", {"hp": 100, "maxhp": 100, "mp": 50, "maxmp": 100})

        assert len(channel_msgs) == 1
        assert len(room_info) == 1
        assert len(vitals) == 1
