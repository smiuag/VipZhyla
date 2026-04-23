"""
MUD output parser for Reinos de Leyenda.

Identifies message channels based on text patterns.
This is a fallback when GMCP is not available; GMCP data takes priority.
"""

import re
from enum import Enum
from dataclasses import dataclass


class ChannelType(Enum):
    """Message channel types in Reinos de Leyenda."""
    GENERAL = "general"        # Room narration, emotes, combat text
    BANDO = "bando"            # Band messages
    TELEPATHY = "telepathy"    # Telepathy channel
    CITIZENSHIP = "citizenship"  # Citizenship messages
    GROUP = "group"            # Group messages
    SYSTEM = "system"          # Server messages (login, disconnect, etc.)


@dataclass
class ParsedMessage:
    """Parsed MUD message with channel identification."""
    channel: ChannelType
    text: str
    raw: str  # Original line before parsing


class MUDParser:
    """
    Parses MUD text output and identifies channels.

    Patterns (based on Reinos de Leyenda / VipMud):
    - [Bando] or (bando) → BANDO
    - [Telepátia] or (telepátia) → TELEPATHY
    - [Ciudad] or [Ciudadanía] → CITIZENSHIP
    - [Grupo] → GROUP
    - System messages (login, disconnect, stats) → SYSTEM
    - Default → GENERAL
    """

    # Pattern regexes (case-insensitive, whitespace-flexible)
    BANDO_PATTERN = re.compile(r'\[bando\]|\(bando\)', re.IGNORECASE)
    TELEPATHY_PATTERN = re.compile(r'\[telepát[ií]a\]|\(telepát[ií]a\)', re.IGNORECASE)
    CITIZENSHIP_PATTERN = re.compile(r'\[ciudad(anía)?\]', re.IGNORECASE)
    GROUP_PATTERN = re.compile(r'\[grupo\]|\(grupo\)', re.IGNORECASE)
    SYSTEM_PATTERN = re.compile(
        r'(^conectado|^desconectado|^vida:|^tu vida es|'
        r'^energía:|^nivel|^clase|^experiencia|^puntos de vida)',
        re.IGNORECASE | re.MULTILINE
    )

    def __init__(self):
        """Initialize parser."""
        pass

    def parse_line(self, line: str) -> ParsedMessage:
        """
        Parse a single line of MUD output.

        Args:
            line: Raw text line from MUD

        Returns:
            ParsedMessage with identified channel and cleaned text
        """
        line = line.rstrip()  # Remove trailing whitespace
        channel = self._detect_channel(line)

        # For text display, remove channel prefix if present
        # (GMCP handler will override this if module is Comm.Channel)
        display_text = self._clean_text(line, channel)

        return ParsedMessage(
            channel=channel,
            text=display_text,
            raw=line
        )

    def _detect_channel(self, line: str) -> ChannelType:
        """Detect which channel a line belongs to."""
        if self.BANDO_PATTERN.search(line):
            return ChannelType.BANDO
        elif self.TELEPATHY_PATTERN.search(line):
            return ChannelType.TELEPATHY
        elif self.CITIZENSHIP_PATTERN.search(line):
            return ChannelType.CITIZENSHIP
        elif self.GROUP_PATTERN.search(line):
            return ChannelType.GROUP
        elif self.SYSTEM_PATTERN.search(line):
            return ChannelType.SYSTEM
        else:
            return ChannelType.GENERAL

    def _clean_text(self, line: str, channel: ChannelType) -> str:
        """Remove channel markers from text for cleaner display."""
        # Only remove markers for identified channels
        if channel == ChannelType.BANDO:
            return self.BANDO_PATTERN.sub('', line).strip()
        elif channel == ChannelType.TELEPATHY:
            return self.TELEPATHY_PATTERN.sub('', line).strip()
        elif channel == ChannelType.CITIZENSHIP:
            return self.CITIZENSHIP_PATTERN.sub('', line).strip()
        elif channel == ChannelType.GROUP:
            return self.GROUP_PATTERN.sub('', line).strip()
        else:
            # SYSTEM and GENERAL: return as-is
            return line
