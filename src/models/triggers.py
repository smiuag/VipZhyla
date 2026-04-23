"""
Trigger/Alias/Timer system for MUD automation.

Features:
- Triggers: Pattern matching on MUD text → TTS, sound, gag actions
- Aliases: Command abbreviations (h → help)
- Timers: Periodic actions (every N seconds)

Persistence: saves/loads to triggers.json
"""

import json
import re
import threading
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import List, Optional, Callable, TYPE_CHECKING

from client.mud_parser import ParsedMessage
from app.audio_manager import AudioManager, AudioLevel

if TYPE_CHECKING:
    from models.character_state import CharacterState


class ActionType(Enum):
    """Action types for triggers and timers."""
    TTS = "tts"         # Text-to-speech announcement
    SOUND = "sound"     # Play sound file
    GAG = "gag"         # Hide line from output
    SEND = "send"       # Send command (reserved for future)


@dataclass
class TriggerAction:
    """Single action within a trigger or timer."""
    action_type: ActionType
    value: str = ""  # TTS text, sound path, or empty for gag


@dataclass
class Trigger:
    """Pattern-based trigger that fires on MUD text."""
    id: str
    name: str
    pattern: str
    is_regex: bool = False
    actions: List[TriggerAction] = field(default_factory=list)
    enabled: bool = True
    conditions: List[dict] = field(default_factory=list)  # List of condition dicts for future use


@dataclass
class Alias:
    """Command alias (abbreviation → expansion)."""
    id: str
    abbreviation: str
    expansion: str
    enabled: bool = True


@dataclass
class Timer:
    """Periodic timer that executes actions."""
    id: str
    name: str
    interval: float  # seconds
    actions: List[TriggerAction] = field(default_factory=list)
    enabled: bool = True


class TriggerManager:
    """Manages triggers, aliases, and timers."""

    SAVE_PATH = Path("triggers.json")

    def __init__(self, audio: AudioManager):
        """Initialize trigger manager.

        Args:
            audio: AudioManager instance for TTS/sound actions
        """
        self.triggers: List[Trigger] = []
        self.aliases: List[Alias] = []
        self.timers: List[Timer] = []
        self.audio = audio
        self.send_fn: Optional[Callable[[str], None]] = None
        self.character_state: Optional['CharacterState'] = None  # Will be set by main.py
        self._timer_threads: List[threading.Timer] = []
        self._running = False
        self.load()

    def _check_conditions(self, trigger: Trigger) -> bool:
        """Check if trigger conditions are met.

        Args:
            trigger: Trigger to check

        Returns:
            True if all conditions pass (or no conditions), False otherwise
        """
        if not trigger.conditions or not self.character_state:
            return True  # No conditions means always pass

        # Evaluate all conditions (AND logic)
        for condition in trigger.conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')

            if not field or not operator:
                continue

            # Get field value from character state
            if not hasattr(self.character_state, field):
                return False

            state_value = getattr(self.character_state, field)

            # Evaluate condition based on operator
            if operator == '==':
                if state_value != value:
                    return False
            elif operator == '<':
                if not (state_value < value):
                    return False
            elif operator == '>':
                if not (state_value > value):
                    return False
            elif operator == '<=':
                if not (state_value <= value):
                    return False
            elif operator == '>=':
                if not (state_value >= value):
                    return False
            elif operator == 'in':
                if state_value not in value:
                    return False
            elif operator == 'not_in':
                if state_value in value:
                    return False
            elif operator == 'changed':
                # For future use (detect when value changes)
                pass

        return True

    def evaluate(self, parsed: ParsedMessage) -> bool:
        """Evaluate triggers for a parsed message line.

        Args:
            parsed: ParsedMessage from MUD

        Returns:
            True if line should be gagged (hidden), False otherwise
        """
        should_gag = False

        for trigger in self.triggers:
            if not trigger.enabled:
                continue

            # Match pattern (skip if pattern-based and no pattern matches)
            if trigger.pattern:  # Only check pattern if pattern is provided
                if trigger.is_regex:
                    try:
                        if not re.search(trigger.pattern, parsed.raw, re.IGNORECASE):
                            continue
                    except re.error:
                        continue
                else:
                    if trigger.pattern.lower() not in parsed.raw.lower():
                        continue

            # Check conditions
            if not self._check_conditions(trigger):
                continue

            # Trigger matched, execute actions
            for action in trigger.actions:
                self._execute_action(action)

                # Track if any action is GAG
                if action.action_type == ActionType.GAG:
                    should_gag = True

        return should_gag

    def expand_alias(self, command: str) -> str:
        """Expand command alias if applicable.

        Args:
            command: User-entered command

        Returns:
            Expanded command, or original if no alias matches
        """
        words = command.split(None, 1)  # Split on first whitespace
        if not words:
            return command

        first_word = words[0]

        for alias in self.aliases:
            if not alias.enabled:
                continue

            if alias.abbreviation.lower() == first_word.lower():
                # Replace abbreviated word with expansion
                rest = words[1] if len(words) > 1 else ""
                return (alias.expansion + (" " + rest if rest else "")).rstrip()

        return command

    def execute_action(self, action: TriggerAction):
        """Execute a trigger action.

        Args:
            action: TriggerAction to execute
        """
        self._execute_action(action)

    def _execute_action(self, action: TriggerAction):
        """Internal method to execute actions."""
        if action.action_type == ActionType.TTS:
            if self.audio and action.value:
                # Interpolate variables in TTS value
                tts_text = self._interpolate_text(action.value)
                self.audio.announce(tts_text, AudioLevel.NORMAL)

        elif action.action_type == ActionType.SOUND:
            # Play sound effect
            if self.audio and action.value:
                sound_path = self._interpolate_text(action.value)
                self.audio.play_sound(sound_path)

        elif action.action_type == ActionType.GAG:
            # Gag is handled by evaluate() return value
            pass

    def _interpolate_text(self, text: str) -> str:
        """Interpolate variables in action text.

        Supports: {hp}, {maxhp}, {mp}, {maxmp}, {hp_pct}, {clase}, {name}, etc.

        Args:
            text: Text with variable placeholders

        Returns:
            Interpolated text
        """
        if not self.character_state or '{' not in text:
            return text

        result = text
        variables = {
            'hp': str(self.character_state.hp),
            'maxhp': str(self.character_state.maxhp),
            'hp_pct': str(self.character_state.hp_pct),
            'mp': str(self.character_state.mp),
            'maxmp': str(self.character_state.maxmp),
            'mp_pct': str(self.character_state.mp_pct),
            'clase': self.character_state.clase,
            'raza': self.character_state.raza,
            'name': self.character_state.name,
            'level': str(self.character_state.level),
        }

        for var_name, var_value in variables.items():
            result = result.replace('{' + var_name + '}', var_value)

        return result

    def add_trigger(self, trigger: Trigger):
        """Add a trigger."""
        # Remove if exists (update)
        self.triggers = [t for t in self.triggers if t.id != trigger.id]
        self.triggers.append(trigger)
        self.save()

    def remove_trigger(self, trigger_id: str):
        """Remove a trigger by ID."""
        self.triggers = [t for t in self.triggers if t.id != trigger_id]
        self.save()

    def add_alias(self, alias: Alias):
        """Add an alias."""
        self.aliases = [a for a in self.aliases if a.id != alias.id]
        self.aliases.append(alias)
        self.save()

    def remove_alias(self, alias_id: str):
        """Remove an alias by ID."""
        self.aliases = [a for a in self.aliases if a.id != alias_id]
        self.save()

    def add_timer(self, timer: Timer):
        """Add a timer."""
        self.timers = [t for t in self.timers if t.id != timer.id]
        self.timers.append(timer)
        self.save()

    def remove_timer(self, timer_id: str):
        """Remove a timer by ID."""
        self.timers = [t for t in self.timers if t.id != timer_id]
        self.stop_timers()  # Restart timers without the removed one
        if self._running:
            self.start_timers()
        self.save()

    def start_timers(self):
        """Start all enabled timers (call on connect)."""
        self.stop_timers()
        self._running = True

        for timer in self.timers:
            if not timer.enabled:
                continue

            def timer_callback(t=timer):
                # Execute timer's actions
                for action in t.actions:
                    self._execute_action(action)

                # Reschedule if still running
                if self._running:
                    thread = threading.Timer(t.interval, timer_callback)
                    thread.daemon = True
                    thread.start()
                    self._timer_threads.append(thread)

            thread = threading.Timer(timer.interval, timer_callback)
            thread.daemon = True
            thread.start()
            self._timer_threads.append(thread)

    def stop_timers(self):
        """Stop all timers (call on disconnect)."""
        self._running = False
        for thread in self._timer_threads:
            thread.cancel()
        self._timer_threads.clear()

    def save(self):
        """Save triggers, aliases, timers to JSON file."""
        data = {
            "triggers": [asdict(t) for t in self.triggers],
            "aliases": [asdict(a) for a in self.aliases],
            "timers": [asdict(t) for t in self.timers],
        }

        # Convert enums and dataclass to dict
        for trigger in data["triggers"]:
            trigger["actions"] = [
                {
                    "action_type": a["action_type"].value,
                    "value": a["value"]
                }
                for a in trigger["actions"]
            ]
            # Keep conditions as-is (they're already dicts)
            if "conditions" not in trigger:
                trigger["conditions"] = []

        for timer in data["timers"]:
            timer["actions"] = [
                {
                    "action_type": a["action_type"].value,
                    "value": a["value"]
                }
                for a in timer["actions"]
            ]

        try:
            with open(self.SAVE_PATH, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save triggers: {e}")

    def load(self):
        """Load triggers, aliases, timers from JSON file."""
        if not self.SAVE_PATH.exists():
            return

        try:
            with open(self.SAVE_PATH, "r") as f:
                data = json.load(f)

            # Load triggers
            for t in data.get("triggers", []):
                actions = [
                    TriggerAction(
                        action_type=ActionType(a["action_type"]),
                        value=a.get("value", "")
                    )
                    for a in t.get("actions", [])
                ]
                trigger = Trigger(
                    id=t["id"],
                    name=t["name"],
                    pattern=t["pattern"],
                    is_regex=t.get("is_regex", False),
                    actions=actions,
                    enabled=t.get("enabled", True),
                    conditions=t.get("conditions", [])
                )
                self.triggers.append(trigger)

            # Load aliases
            for a in data.get("aliases", []):
                alias = Alias(
                    id=a["id"],
                    abbreviation=a["abbreviation"],
                    expansion=a["expansion"],
                    enabled=a.get("enabled", True)
                )
                self.aliases.append(alias)

            # Load timers
            for t in data.get("timers", []):
                actions = [
                    TriggerAction(
                        action_type=ActionType(a["action_type"]),
                        value=a.get("value", "")
                    )
                    for a in t.get("actions", [])
                ]
                timer = Timer(
                    id=t["id"],
                    name=t["name"],
                    interval=t["interval"],
                    actions=actions,
                    enabled=t.get("enabled", True)
                )
                self.timers.append(timer)

        except Exception as e:
            print(f"Failed to load triggers: {e}")

    def new_id(self) -> str:
        """Generate a new unique ID."""
        return str(uuid.uuid4())
