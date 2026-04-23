"""
Script Loader - Integrates Lua scripts with VipZhyla Python runtime.

Loads reinos_de_leyenda.lua megaScript and connects Python callbacks
to Lua APIs (audio, TTS, state, etc.).
"""

import logging
from typing import Optional, Dict, Any, Callable
from pathlib import Path

from .lua_runtime import LuaRuntime
from .event_system import EventSystem, EventType

logger = logging.getLogger(__name__)


class ScriptLoader:
    """Loads and manages Lua scripts for MUD automation."""

    def __init__(self, script_dir: Optional[str] = None):
        """
        Initialize script loader.

        Args:
            script_dir: Path to scripts folder (default: scripts/)
        """
        self.script_dir = Path(script_dir or "scripts")
        self.lua_runtime = LuaRuntime(str(self.script_dir))
        self.event_system = EventSystem()
        self.game_script = None
        self.enabled = True

        # Callbacks to Python systems
        self.on_say: Optional[Callable[[str], None]] = None
        self.on_send_command: Optional[Callable[[str], None]] = None
        self.on_play_sound: Optional[Callable[[str], None]] = None
        self.on_play_pan: Optional[Callable[[str, int], None]] = None
        self.on_announce: Optional[Callable[[str], None]] = None
        self.on_get_room_data: Optional[Callable[[], Dict[str, Any]]] = None
        self.on_get_character: Optional[Callable[[], Dict[str, Any]]] = None
        self.on_play_directional_sound: Optional[Callable[[str, str, float, int, str], None]] = None
        self.on_update_sound_position: Optional[Callable[[str, str, float], None]] = None
        self.on_stop_sound: Optional[Callable[[str], None]] = None

    def load_scripts(self) -> bool:
        """
        Load main megaScript (reinos_de_leyenda.lua).

        Returns:
            True if successful, False otherwise
        """
        try:
            # Set up callbacks
            self._setup_callbacks()

            # Load main script
            self.game_script = self.lua_runtime.load_script("reinos_de_leyenda.lua")

            if not self.game_script:
                logger.error("Failed to load game script")
                return False

            # Initialize game
            self.lua_runtime.call_function("game.init")

            logger.info("Scripts loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load scripts: {e}", exc_info=True)
            return False

    def _setup_callbacks(self):
        """Connect Python callbacks to Lua APIs."""
        # Create callback functions
        callbacks = {
            'say': self._callback_say,
            'send_command': self._callback_send_command,
            'play_sound': self._callback_play_sound,
            'play_pan': self._callback_play_pan,
            'announce': self._callback_announce,
            'get_room_data': self._callback_get_room_data,
            'get_character': self._callback_get_character,
            'play_directional_sound': self._callback_play_directional_sound,
            'update_sound_position': self._callback_update_sound_position,
            'stop_sound': self._callback_stop_sound,
        }

        # Register each callback
        for api_name, callback in callbacks.items():
            try:
                self.lua_runtime.set_callback(api_name, callback)
                logger.debug(f"Registered callback: {api_name}")
            except Exception as e:
                logger.error(f"Failed to register callback {api_name}: {e}")

    # ===== Lua -> Python Callbacks =====

    def _callback_say(self, text: str):
        """Handle vipzhyla.say() from Lua."""
        if self.on_say:
            self.on_say(text)
        else:
            logger.info(f"[Lua Output] {text}")

    def _callback_send_command(self, cmd: str):
        """Handle vipzhyla.send_command() from Lua."""
        if self.on_send_command:
            self.on_send_command(cmd)
        else:
            logger.info(f"[Lua Command] {cmd}")

    def _callback_play_sound(self, path: str):
        """Handle vipzhyla.play_sound() from Lua."""
        if self.on_play_sound:
            self.on_play_sound(path)
        else:
            logger.info(f"[Lua Sound] {path}")

    def _callback_play_pan(self, path: str, pan: int):
        """Handle vipzhyla.play_pan() from Lua."""
        if self.on_play_pan:
            self.on_play_pan(path, pan)
        else:
            logger.info(f"[Lua Sound Pan] {path} pan={pan}")

    def _callback_announce(self, text: str):
        """Handle vipzhyla.announce() from Lua."""
        if self.on_announce:
            self.on_announce(text)
        else:
            logger.info(f"[Lua TTS] {text}")

    def _callback_get_room_data(self) -> Dict[str, Any]:
        """Handle vipzhyla.get_room_data() from Lua."""
        if self.on_get_room_data:
            return self.on_get_room_data()
        return {}

    def _callback_get_character(self) -> Dict[str, Any]:
        """Handle vipzhyla.get_character() from Lua."""
        if self.on_get_character:
            return self.on_get_character()
        return {}

    def _callback_play_directional_sound(
        self, sound_path: str, direction: str, distance: float, loop_count: int, sound_id: str
    ):
        """Handle vipzhyla.play_directional_sound() from Lua."""
        if self.on_play_directional_sound:
            self.on_play_directional_sound(sound_path, direction, distance, loop_count, sound_id)
        else:
            logger.info(f"[Lua Directional Sound] {sound_path} dir={direction} dist={distance} id={sound_id}")

    def _callback_update_sound_position(self, sound_id: str, direction: str, distance: float):
        """Handle vipzhyla.update_sound_position() from Lua."""
        if self.on_update_sound_position:
            self.on_update_sound_position(sound_id, direction, distance)
        else:
            logger.info(f"[Lua Update Position] {sound_id} dir={direction} dist={distance}")

    def _callback_stop_sound(self, sound_id: str):
        """Handle vipzhyla.stop_sound() from Lua."""
        if self.on_stop_sound:
            self.on_stop_sound(sound_id)
        else:
            logger.info(f"[Lua Stop Sound] {sound_id}")

    # ===== Python -> Lua Event Dispatching =====

    def on_mud_message(self, channel: str, text: str):
        """Dispatch MUD text message to Lua scripts."""
        if not self.enabled or not self.game_script:
            return

        try:
            # Call Lua handler
            self.lua_runtime.call_function("game.on_mud_message", channel, text)

            # Also dispatch through event system
            self.event_system.on_mud_message(channel, text)

        except Exception as e:
            logger.error(f"Error processing MUD message in Lua: {e}", exc_info=True)

    def on_gmcp_data(self, module: str, data: Dict[str, Any]):
        """Dispatch GMCP data to Lua scripts."""
        if not self.enabled or not self.game_script:
            return

        try:
            # Call Lua handler
            self.lua_runtime.call_function("game.on_gmcp_data", module, data)

            # Also dispatch through event system
            self.event_system.on_gmcp_module(module, data)

        except Exception as e:
            logger.error(f"Error processing GMCP data in Lua: {e}", exc_info=True)

    def on_vitals_changed(self, hp: int, maxhp: int, mp: int, maxmp: int):
        """Dispatch vitals change event."""
        if not self.enabled:
            return

        try:
            self.event_system.on_vitals_changed(hp, maxhp, mp, maxmp)
        except Exception as e:
            logger.error(f"Error in vitals event: {e}", exc_info=True)

    def on_room_entered(self, room_name: str, exits: list):
        """Dispatch room entered event."""
        if not self.enabled:
            return

        try:
            self.event_system.on_room_entered(room_name, exits)
        except Exception as e:
            logger.error(f"Error in room event: {e}", exc_info=True)

    def on_movement(self, direction: str):
        """Dispatch movement event."""
        if not self.enabled:
            return

        try:
            self.event_system.on_movement(direction)
        except Exception as e:
            logger.error(f"Error in movement event: {e}", exc_info=True)

    # ===== Script Control =====

    def enable(self):
        """Enable script processing."""
        self.enabled = True
        logger.info("Scripts enabled")

    def disable(self):
        """Disable script processing."""
        self.enabled = False
        logger.info("Scripts disabled")

    def get_status(self) -> Dict[str, Any]:
        """Get current script system status."""
        return {
            'loaded': self.game_script is not None,
            'enabled': self.enabled,
            'events': self.event_system.get_statistics(),
        }

    def call_game_function(self, func_name: str, *args) -> Any:
        """
        Call a public function on the game object.

        Args:
            func_name: Function name (e.g., "get_status")
            *args: Arguments

        Returns:
            Function return value
        """
        if not self.game_script:
            logger.error("Game script not loaded")
            return None

        try:
            return self.lua_runtime.call_function(f"game.{func_name}", *args)
        except Exception as e:
            logger.error(f"Error calling game.{func_name}: {e}")
            return None
