"""
Tests for MUD output parser.
"""

import pytest
from src.client.mud_parser import MUDParser, ChannelType


class TestMUDParser:
    """Test MUD output parsing and channel detection."""

    def test_detects_bando_channel(self):
        """Detect [Bando] messages."""
        parser = MUDParser()

        msg = parser.parse_line("[Bando] Alguien: Enemigo en el norte")

        assert msg.channel == ChannelType.BANDO
        assert "Alguien: Enemigo en el norte" in msg.text

    def test_detects_bando_lowercase(self):
        """Detect (bando) variant."""
        parser = MUDParser()

        msg = parser.parse_line("(bando) Aviso importante")

        assert msg.channel == ChannelType.BANDO

    def test_detects_telepathy_channel(self):
        """Detect [Telepátia] messages."""
        parser = MUDParser()

        msg = parser.parse_line("[Telepátia] Persona: Hola?")

        assert msg.channel == ChannelType.TELEPATHY

    def test_detects_citizenship_channel(self):
        """Detect [Ciudadanía] or [Ciudad]."""
        parser = MUDParser()

        msg1 = parser.parse_line("[Ciudadanía] Aviso")
        assert msg1.channel == ChannelType.CITIZENSHIP

        msg2 = parser.parse_line("[Ciudad] Aviso")
        assert msg2.channel == ChannelType.CITIZENSHIP

    def test_detects_group_channel(self):
        """Detect [Grupo] messages."""
        parser = MUDParser()

        msg = parser.parse_line("[Grupo] Compañero: Sígueme")

        assert msg.channel == ChannelType.GROUP

    def test_default_is_general(self):
        """Messages without channel markers default to GENERAL."""
        parser = MUDParser()

        msg = parser.parse_line("Narración de la sala: Ves a un enemigo.")

        assert msg.channel == ChannelType.GENERAL
        assert msg.text == "Narración de la sala: Ves a un enemigo."

    def test_system_messages_detected(self):
        """Detect system messages (login, disconnect, etc.)."""
        parser = MUDParser()

        msg1 = parser.parse_line("Conectado.")
        assert msg1.channel == ChannelType.SYSTEM

        msg2 = parser.parse_line("Tu vida es 100/200")
        assert msg2.channel == ChannelType.SYSTEM

    def test_cleans_channel_prefix(self):
        """Channel prefix should be removed from display text."""
        parser = MUDParser()

        msg = parser.parse_line("[Bando] Aviso importante")

        assert "[Bando]" not in msg.text
        assert "Aviso importante" in msg.text

    def test_raw_text_preserved(self):
        """Original raw text should be preserved."""
        parser = MUDParser()

        original = "[Telepátia] Mensaje"
        msg = parser.parse_line(original)

        assert msg.raw == original

    def test_whitespace_handling(self):
        """Extra whitespace should be handled."""
        parser = MUDParser()

        msg = parser.parse_line("  [Bando]   Mensaje   ")

        assert msg.channel == ChannelType.BANDO
        assert msg.text.strip() == "Mensaje"

    def test_case_insensitive(self):
        """Channel detection should be case-insensitive."""
        parser = MUDParser()

        msg = parser.parse_line("[BANDO] Mensaje")

        assert msg.channel == ChannelType.BANDO
