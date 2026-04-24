"""
Macro Executor - Execute command sequences bound to hotkeys (F12-F15).

Macros are lists of steps (send command, TTS, sound) executed sequentially
in background threads. Can be cancelled by pressing the same hotkey again.
"""

import json
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Callable, Dict

from app.audio_manager import AudioManager, AudioLevel


@dataclass
class MacroStep:
    """A single step in a macro execution."""
    action_type: str           # "send" | "tts" | "sound"
    value: str = ""            # command, TTS text, or sound path
    delay_before_ms: int = 0   # milliseconds to wait before this step


@dataclass
class MacroDefinition:
    """Definition of a macro bound to a hotkey (F12-F15)."""
    id: str                                      # UUID string
    name: str                                    # User-friendly name
    hotkey: str = ""                             # "F12", "F13", "F14", "F15", or ""
    steps: List[MacroStep] = field(default_factory=list)
    enabled: bool = True
    description: str = ""

    SAVE_PATH = Path("src/data/user_macros.json")


class MacroManager:
    """Manages macro definitions and execution."""

    MAX_CONCURRENT = 4

    def __init__(self, audio: AudioManager, send_fn: Callable[[str], None]):
        """Initialize macro manager.

        Args:
            audio: AudioManager for TTS/sound actions
            send_fn: Callback to send command to MUD (takes command string)
        """
        self.macros: List[MacroDefinition] = []
        self.audio = audio
        self.send_fn = send_fn
        self._running: Dict[str, threading.Thread] = {}  # macro_id → thread
        self._cancel_events: Dict[str, threading.Event] = {}  # macro_id → event
        self.SAVE_PATH = MacroDefinition.SAVE_PATH
        self.load()

    def execute(self, macro: MacroDefinition) -> None:
        """Execute macro in background thread.

        If macro is already running, cancel it (toggle behavior).

        Args:
            macro: MacroDefinition to execute
        """
        if macro.id in self._running and self._running[macro.id].is_alive():
            # Already running — cancel it
            self._cancel_events[macro.id].set()
            return

        # Start new execution
        cancel = threading.Event()
        self._cancel_events[macro.id] = cancel

        t = threading.Thread(target=self._run, args=(macro, cancel), daemon=True)
        self._running[macro.id] = t
        t.start()

    def _run(self, macro: MacroDefinition, cancel: threading.Event) -> None:
        """Execute macro steps in sequence.

        Args:
            macro: Macro to execute
            cancel: Threading.Event to signal cancellation
        """
        for step in macro.steps:
            if cancel.is_set():
                break

            # Wait before this step
            if step.delay_before_ms > 0:
                if cancel.wait(timeout=step.delay_before_ms / 1000.0):
                    # Event was set during wait = cancel requested
                    break

            # Execute step
            if step.action_type == "send" and self.send_fn:
                self.send_fn(step.value)

            elif step.action_type == "tts" and self.audio:
                self.audio.announce(step.value, AudioLevel.NORMAL)

            elif step.action_type == "sound" and self.audio:
                self.audio.play_sound(step.value)

    def get_by_hotkey(self, hotkey: str) -> Optional[MacroDefinition]:
        """Get enabled macro bound to a hotkey.

        Args:
            hotkey: "F12", "F13", "F14", or "F15"

        Returns:
            MacroDefinition or None if not found/disabled
        """
        for macro in self.macros:
            if macro.enabled and macro.hotkey == hotkey:
                return macro
        return None

    def add_macro(self, macro: MacroDefinition) -> None:
        """Add or update macro (upsert).

        Args:
            macro: MacroDefinition to add/update
        """
        for i, m in enumerate(self.macros):
            if m.id == macro.id:
                self.macros[i] = macro
                self.save()
                return

        self.macros.append(macro)
        self.save()

    def remove_macro(self, macro_id: str) -> None:
        """Remove macro by ID.

        Args:
            macro_id: UUID of macro to remove
        """
        self.macros = [m for m in self.macros if m.id != macro_id]
        self.save()

    def save(self) -> None:
        """Save macros to JSON."""
        self.SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'macros': [
                {
                    'id': m.id,
                    'name': m.name,
                    'hotkey': m.hotkey,
                    'enabled': m.enabled,
                    'description': m.description,
                    'steps': [
                        {
                            'action_type': s.action_type,
                            'value': s.value,
                            'delay_before_ms': s.delay_before_ms,
                        }
                        for s in m.steps
                    ]
                }
                for m in self.macros
            ]
        }

        with open(self.SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self) -> None:
        """Load macros from JSON."""
        if not self.SAVE_PATH.exists():
            return

        try:
            with open(self.SAVE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.macros = []
            for macro_data in data.get('macros', []):
                macro = MacroDefinition(
                    id=macro_data['id'],
                    name=macro_data['name'],
                    hotkey=macro_data.get('hotkey', ''),
                    enabled=macro_data.get('enabled', True),
                    description=macro_data.get('description', ''),
                    steps=[
                        MacroStep(
                            action_type=step['action_type'],
                            value=step['value'],
                            delay_before_ms=step.get('delay_before_ms', 0),
                        )
                        for step in macro_data.get('steps', [])
                    ]
                )
                self.macros.append(macro)

        except (json.JSONDecodeError, IOError, KeyError):
            pass  # File corrupted or unreadable; use empty list

    def get_stats(self) -> dict:
        """Get macro statistics.

        Returns:
            dict with total count and count by hotkey
        """
        return {
            'total': len(self.macros),
            'by_hotkey': {
                hk: len([m for m in self.macros if m.enabled and m.hotkey == hk])
                for hk in ['F12', 'F13', 'F14', 'F15']
            }
        }
