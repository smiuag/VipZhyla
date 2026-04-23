"""
GMCP (Generic MUD Communication Protocol) handler.

Processes GMCP data from the MUD and emits high-level events:
- Character vitals (HP, MP changes)
- Room information (name, exits)
- Channel messages (with correct channel identification)
- Character status (name, level, class)

GMCP provides structured data alternative to fragile text parsing.
"""

from typing import Callable, Optional, Dict, Any
from .mud_parser import ChannelType, ParsedMessage
from src.app.audio_manager import AudioManager, AudioLevel


class GmcpHandler:
    """
    Processes GMCP modules and emits high-level events.

    Supported modules:
    - Core.Hello: Server/client version handshake
    - Char.Vitals: HP, MP, energy
    - Char.Status: Name, level, class, experience
    - Room.Info: Current room name and exits
    - Comm.Channel: Messages on game channels
    """

    def __init__(self, audio: Optional[AudioManager] = None):
        """
        Initialize GMCP handler.

        Args:
            audio: AudioManager instance for TTS announcements (optional)
        """
        self.audio = audio

        # Callbacks
        self.on_channel_message: Optional[Callable[[ParsedMessage], None]] = None
        self.on_vitals_changed: Optional[Callable[[int, int, int, int], None]] = None
        self.on_room_info: Optional[Callable[[str, list[str]], None]] = None
        self.on_status_changed: Optional[Callable[[Dict[str, Any]], None]] = None

        # Track previous vitals for change detection
        self.last_vitals = {
            'hp': None,
            'maxhp': None,
            'mp': None,
            'maxmp': None,
        }

    def handle(self, module: str, data: Dict[str, Any]):
        """
        Handle a GMCP module with data.

        Args:
            module: Module name (e.g., "Char.Vitals")
            data: Module data (dict)
        """
        if module == "Core.Hello":
            self._handle_core_hello(data)
        elif module == "Char.Vitals":
            self._handle_char_vitals(data)
        elif module == "Char.Status":
            self._handle_char_status(data)
        elif module == "Room.Info":
            self._handle_room_info(data)
        elif module == "Comm.Channel":
            self._handle_comm_channel(data)
        # Silently ignore unknown modules

    def _handle_core_hello(self, data: Dict[str, Any]):
        """Handle Core.Hello (server/client version info)."""
        # Just acknowledge, don't need to do anything
        pass

    def _handle_char_vitals(self, data: Dict[str, Any]):
        """
        Handle Char.Vitals — character HP/MP.

        Data format:
        {
            "hp": 320,
            "maxhp": 450,
            "mp": 120,
            "maxmp": 200
        }
        """
        try:
            hp = int(data.get('hp', 0))
            maxhp = int(data.get('maxhp', 0))
            mp = int(data.get('mp', 0))
            maxmp = int(data.get('maxmp', 0))

            # Save previous HP for TTS announcement (before updating)
            prev_hp = self.last_vitals.get('hp')

            # Check for changes
            changed = (
                hp != self.last_vitals['hp'] or
                maxhp != self.last_vitals['maxhp'] or
                mp != self.last_vitals['mp'] or
                maxmp != self.last_vitals['maxmp']
            )

            if changed:
                self.last_vitals = {
                    'hp': hp,
                    'maxhp': maxhp,
                    'mp': mp,
                    'maxmp': maxmp,
                }

                # Emit callback for UI (status bar)
                if self.on_vitals_changed:
                    self.on_vitals_changed(hp, maxhp, mp, maxmp)

                # TTS announcement if HP changed
                if hp != prev_hp:
                    if self.audio:
                        msg = f"Vida: {hp} de {maxhp}"
                        self.audio.announce(msg, AudioLevel.NORMAL)

        except (ValueError, KeyError):
            # Invalid data, ignore
            pass

    def _handle_char_status(self, data: Dict[str, Any]):
        """
        Handle Char.Status — character info.

        Data format:
        {
            "name": "Aeroth",
            "level": 42,
            "class": "Soldado",
            "experience": 50000
        }
        """
        if self.on_status_changed:
            self.on_status_changed(data)

    def _handle_room_info(self, data: Dict[str, Any]):
        """
        Handle Room.Info — current room.

        Data format:
        {
            "name": "El gran mercado",
            "exits": ["north", "east", "west"],
            "desc": "Eres en el mercado..."
        }
        """
        try:
            room_name = data.get('name', 'Unknown')
            exits = data.get('exits', [])

            if self.on_room_info:
                self.on_room_info(room_name, exits)

            # TTS announcement when entering new room
            if self.audio:
                exit_str = ", ".join(exits) if exits else "sin salidas"
                msg = f"Sala: {room_name}. Salidas: {exit_str}"
                self.audio.announce(msg, AudioLevel.MINIMAL)

        except (ValueError, KeyError):
            pass

    def _handle_comm_channel(self, data: Dict[str, Any]):
        """
        Handle Comm.Channel — channel message.

        Data format:
        {
            "channel": "bando",
            "talker": "Aeroth",
            "text": "Enemigo en Eldor"
        }

        This overrides text-based channel detection from MUDParser.
        """
        try:
            channel_name = data.get('channel', 'general').lower()
            talker = data.get('talker', 'Desconocido')
            text = data.get('text', '')

            # Map channel name to ChannelType
            channel_map = {
                'bando': ChannelType.BANDO,
                'telepátia': ChannelType.TELEPATHY,
                'telepathy': ChannelType.TELEPATHY,
                'ciudad': ChannelType.CITIZENSHIP,
                'ciudadanía': ChannelType.CITIZENSHIP,
                'grupo': ChannelType.GROUP,
                'group': ChannelType.GROUP,
                'general': ChannelType.GENERAL,
            }

            channel = channel_map.get(channel_name, ChannelType.GENERAL)

            # Format message with talker
            formatted_text = f"{talker}: {text}"

            # Create ParsedMessage
            msg = ParsedMessage(
                channel=channel,
                text=formatted_text,
                raw=formatted_text
            )

            # Emit callback
            if self.on_channel_message:
                self.on_channel_message(msg)

        except (ValueError, KeyError):
            pass

    def set_channel_callback(self, callback: Callable[[ParsedMessage], None]):
        """Register callback for channel messages."""
        self.on_channel_message = callback

    def set_vitals_callback(self, callback: Callable[[int, int, int, int], None]):
        """Register callback for vitals changes (hp, maxhp, mp, maxmp)."""
        self.on_vitals_changed = callback

    def set_room_callback(self, callback: Callable[[str, list[str]], None]):
        """Register callback for room info (name, exits)."""
        self.on_room_info = callback

    def set_status_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register callback for status changes."""
        self.on_status_changed = callback
