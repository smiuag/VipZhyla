"""
Lua 5.1 Runtime for VipZhyla script system.

Initializes a Lua VM, sandboxes it for security, and exposes VipZhyla APIs
(audio, TTS, file I/O, state management) to Lua scripts.
"""

import os
import sys
import logging
from typing import Callable, Optional, Dict, Any
from pathlib import Path

try:
    import lupa
except ImportError:
    raise ImportError(
        "lupa (Lua 5.1 binding) not found. "
        "Install with: pip install lupa"
    )

logger = logging.getLogger(__name__)


class LuaRuntime:
    """Manages Lua 5.1 VM for VipZhyla scripts."""

    def __init__(self, script_dir: Optional[str] = None):
        """
        Initialize Lua runtime.

        Args:
            script_dir: Path to scripts folder (default: scripts/ relative to project)
        """
        self.script_dir = Path(script_dir or "scripts")
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        self._setup_sandbox()
        self._expose_apis()
        self._globals = {}  # Store global state accessible to Lua

    def _setup_sandbox(self):
        """Configure Lua sandbox for security (limited standard library)."""
        import time as python_time

        # Allow only safe standard library functions
        safe_libs = {
            'string': self.lua.globals()['string'],
            'table': self.lua.globals()['table'],
            'math': self.lua.globals()['math'],
            'pairs': self.lua.globals()['pairs'],
            'ipairs': self.lua.globals()['ipairs'],
            'next': self.lua.globals()['next'],
            'type': self.lua.globals()['type'],
            'tonumber': self.lua.globals()['tonumber'],
            'tostring': self.lua.globals()['tostring'],
        }

        # Create safe os module with only time function
        safe_os = {
            'time': lambda: int(python_time.time()),
        }

        # Clear unsafe functions and replace with safe versions
        for key in ['io', 'debug', 'load', 'loadstring', 'dofile']:
            if key in self.lua.globals():
                self.lua.globals()[key] = None

        # Set allowed globals
        for key, val in safe_libs.items():
            self.lua.globals()[key] = val

        # Add safe os module
        self.lua.globals()['os'] = safe_os

        logger.debug("Lua sandbox configured")

    def _expose_apis(self):
        """Expose VipZhyla Python APIs to Lua."""
        # Placeholder for APIs - will be populated by ScriptLoader via set_callback()
        self.lua.globals()['vipzhyla'] = {
            # Core APIs
            'say': lambda text: self._say(text),
            'send_command': lambda cmd: self._send_command(cmd),
            'announce': lambda text: self._announce(text),

            # Audio APIs
            'play_sound': lambda path: self._play_sound(path),
            'play_pan': lambda path, pan: self._play_pan(path, pan),
            'play_directional_sound': lambda path, dir, dist, loop, id: self._placeholder("play_directional_sound"),
            'update_sound_position': lambda id, dir, dist: self._placeholder("update_sound_position"),
            'stop_sound': lambda id: self._placeholder("stop_sound"),

            # Game State APIs
            'get_room_data': lambda: self._get_room_data(),
            'get_character': lambda: self._get_character(),

            # Dialog APIs (Phase 6E prompts)
            'show_list_dialog': lambda title, msg, items, ok, cancel: self._placeholder("show_list_dialog"),
            'show_yes_no_dialog': lambda title, msg: self._placeholder("show_yes_no_dialog"),
            'show_text_dialog': lambda title, msg, default: self._placeholder("show_text_dialog"),
            'show_multi_select_dialog': lambda title, msg, items, ok, cancel: self._placeholder("show_multi_select_dialog"),

            # Config APIs
            'save_character_config': lambda class_name, config: self._placeholder("save_character_config"),
            'load_character_config': lambda class_name: self._placeholder("load_character_config"),

            # Variable storage
            'set_var': lambda name, val: self._set_var(name, val),
            'get_var': lambda name: self._get_var(name),

            # Event registration
            'register_trigger': lambda pattern, handler: self._register_trigger(pattern, handler),
            'register_alias': lambda abbr, handler: self._register_alias(abbr, handler),
        }

        logger.debug("VipZhyla APIs exposed to Lua")

    def load_script(self, script_name: str) -> Any:
        """
        Load and execute a Lua script from scripts/ directory.

        Args:
            script_name: Script filename (e.g., "reinos_de_leyenda.lua")

        Returns:
            Script return value (typically a module table)

        Raises:
            FileNotFoundError: If script not found
            lupa.LuaSyntaxError: If Lua syntax error
            lupa.LuaError: If Lua runtime error
        """
        script_path = self.script_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        logger.info(f"Loading Lua script: {script_name}")

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Add script directory to Lua package.path for require()
            self.lua.execute(f"""
                package.path = '{self.script_dir}' .. '/?.lua;' .. package.path
            """)

            # Execute script
            result = self.lua.execute(code)
            logger.info(f"Script loaded successfully: {script_name}")
            return result

        except lupa.LuaSyntaxError as e:
            logger.error(f"Lua syntax error in {script_name}: {e}")
            raise
        except lupa.LuaError as e:
            logger.error(f"Lua runtime error in {script_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading script {script_name}: {e}")
            raise

    def call_function(self, func_name: str, *args) -> Any:
        """
        Call a global Lua function.

        Args:
            func_name: Lua function name (e.g., "game.init")
            *args: Arguments to pass

        Returns:
            Function return value
        """
        try:
            parts = func_name.split('.')
            func = self.lua.globals()[parts[0]]
            for part in parts[1:]:
                func = func[part]

            result = func(*args)
            logger.debug(f"Called Lua function: {func_name}")
            return result

        except Exception as e:
            logger.error(f"Error calling Lua function {func_name}: {e}")
            raise

    # ===== Internal API implementations (placeholders for now) =====

    def _placeholder(self, api_name: str):
        """Placeholder for callbacks not yet connected."""
        logger.debug(f"[Placeholder] {api_name} called but not connected to Python callback")
        return None

    def _say(self, text: str):
        """Output text to game (will be connected to UI)."""
        logger.info(f"[Lua Output] {text}")

    def _send_command(self, cmd: str):
        """Send command to MUD (will be connected to connection)."""
        logger.info(f"[Lua Command] {cmd}")

    def _play_sound(self, path: str):
        """Play audio file (will be connected to audio_manager)."""
        logger.info(f"[Lua Sound] {path}")

    def _play_pan(self, path: str, pan: int):
        """Play audio with panning (will be connected to audio_manager)."""
        logger.info(f"[Lua Sound Pan] {path} pan={pan}")

    def _announce(self, text: str):
        """TTS announcement (will be connected to audio_manager)."""
        logger.info(f"[Lua TTS] {text}")

    def _set_var(self, name: str, val: Any):
        """Store variable in global state."""
        self._globals[name] = val
        logger.debug(f"Set Lua var {name} = {val}")

    def _get_var(self, name: str) -> Any:
        """Retrieve variable from global state."""
        return self._globals.get(name)

    def _register_trigger(self, pattern: str, handler):
        """Register trigger pattern handler (will connect to EventSystem)."""
        logger.info(f"[Lua Trigger] {pattern}")

    def _register_alias(self, abbr: str, handler):
        """Register alias handler (will connect to AliasSystem)."""
        logger.info(f"[Lua Alias] {abbr}")

    def _get_room_data(self) -> Dict[str, Any]:
        """Get current room from GMCP."""
        return {}

    def _get_character(self) -> Dict[str, Any]:
        """Get character data from GMCP."""
        return {}

    def set_callback(self, api_name: str, callback: Callable):
        """
        Set callback function for Lua API (runtime connection).

        Args:
            api_name: API function name (e.g., "say", "send_command")
            callback: Python function to call

        Supports all Phase 6E-7D APIs:
        - Basic: say, send_command, announce
        - Audio: play_sound, play_pan, play_directional_sound, stop_sound, update_sound_position
        - Game State: get_room_data, get_character
        - Dialogs: show_list_dialog, show_yes_no_dialog, show_text_dialog, show_multi_select_dialog
        - Config: save_character_config, load_character_config
        """
        # Allow any API (dynamic registration)
        if callback is not None:
            self.lua.globals()['vipzhyla'][api_name] = callback
            logger.debug(f"Set callback for vipzhyla.{api_name}")
        else:
            logger.warning(f"Attempted to set None callback for vipzhyla.{api_name}")
