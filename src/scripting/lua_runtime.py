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

        # Clear unsafe functions
        for key in ['os', 'io', 'debug', 'load', 'loadstring', 'dofile']:
            if key in self.lua.globals():
                self.lua.globals()[key] = None

        # Set allowed globals
        for key, val in safe_libs.items():
            self.lua.globals()[key] = val

        logger.debug("Lua sandbox configured")

    def _expose_apis(self):
        """Expose VipZhyla Python APIs to Lua."""
        # Placeholder for APIs - will be populated by ScriptLoader
        self.lua.globals()['vipzhyla'] = {
            'say': lambda text: self._say(text),
            'send_command': lambda cmd: self._send_command(cmd),
            'play_sound': lambda path: self._play_sound(path),
            'play_pan': lambda path, pan: self._play_pan(path, pan),
            'announce': lambda text: self._announce(text),
            'set_var': lambda name, val: self._set_var(name, val),
            'get_var': lambda name: self._get_var(name),
            'register_trigger': lambda pattern, handler: self._register_trigger(pattern, handler),
            'register_alias': lambda abbr, handler: self._register_alias(abbr, handler),
            'get_room_data': lambda: self._get_room_data(),
            'get_character': lambda: self._get_character(),
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
        """
        if api_name in ('say', 'send_command', 'play_sound', 'play_pan',
                        'announce', 'get_room_data', 'get_character'):
            # Set the callback in vipzhyla table
            self.lua.globals()['vipzhyla'][api_name] = callback
            logger.debug(f"Set callback for vipzhyla.{api_name}")
        else:
            raise ValueError(f"Unknown API: {api_name}")
