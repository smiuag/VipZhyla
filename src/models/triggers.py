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
    TTS = "tts"                     # Text-to-speech announcement
    SOUND = "sound"                 # Play sound file
    GAG = "gag"                     # Hide line from output
    SEND = "send"                   # Send command (reserved for future)
    STORAGE = "storage"             # Store/update character state (buffs, flags, etc.)
    EXECUTE_TRIGGER = "execute_trigger"  # Execute another trigger by ID


@dataclass
class TriggerAction:
    """Single action within a trigger or timer."""
    action_type: ActionType
    value: str = ""  # TTS text, sound path, or field name for storage
    operation: str = ""  # For storage: add, remove, set, update
    data: str = ""  # For storage: data to add/set


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

    MAX_CHAIN_DEPTH = 10  # Prevent infinite loops in trigger chaining

    # Try to find triggers.json in multiple locations
    @staticmethod
    def _find_save_path() -> Path:
        """Find triggers.json in src/data or root directory."""
        candidates = [
            Path("src/data/triggers.json"),
            Path("triggers.json"),
        ]
        for path in candidates:
            if path.exists():
                return path
        # Default to src/data (even if it doesn't exist yet, save there)
        return Path("src/data/triggers.json")

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
        self.SAVE_PATH = self._find_save_path()
        self.load()

    def _check_conditions(self, trigger: Trigger) -> bool:
        """Check if trigger conditions are met.

        Supports AND logic (all top-level conditions must pass), OR groups,
        and NOT negation.

        Condition structure:
        - Simple: {"field": "hp_pct", "operator": "<", "value": 30}
        - OR group: {"or": [condition1, condition2, ...]}
        - Negated: {"field": "in_combat", "operator": "==", "value": true, "negate": true}

        Args:
            trigger: Trigger to check

        Returns:
            True if all conditions pass (or no conditions), False otherwise
        """
        if not trigger.conditions or not self.character_state:
            return True  # No conditions means always pass

        # Evaluate all top-level conditions (AND logic)
        for condition in trigger.conditions:
            if not self._evaluate_condition_group(condition):
                return False

        return True

    def _evaluate_condition_group(self, condition: dict) -> bool:
        """Evaluate a single condition or OR group.

        Args:
            condition: Condition dict or OR group dict

        Returns:
            True if condition passes, False otherwise
        """
        # Check if this is an OR group
        if 'or' in condition:
            or_result = self._evaluate_or_group(condition['or'])
            # Apply negation if present
            if condition.get('negate', False):
                return not or_result
            return or_result

        # Regular condition
        result = self._evaluate_single_condition(condition)
        # Apply negation if present
        if condition.get('negate', False):
            return not result
        return result

    def _evaluate_or_group(self, or_conditions: list) -> bool:
        """Evaluate an OR group (any condition can be true).

        Args:
            or_conditions: List of condition dicts

        Returns:
            True if any condition is true, False if all are false
        """
        for condition in or_conditions:
            if self._evaluate_single_condition(condition):
                return True
        return False

    def _evaluate_single_condition(self, condition: dict) -> bool:
        """Evaluate a single atomic condition.

        Args:
            condition: Condition dict with field/operator/value

        Returns:
            True if condition passes, False otherwise
        """
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')

        if not field or not operator:
            return True  # Malformed condition passes

        # Get field value from character state
        if not hasattr(self.character_state, field):
            return False

        state_value = getattr(self.character_state, field)

        # Evaluate condition based on operator
        if operator == '==':
            return state_value == value
        elif operator == '<':
            return state_value < value
        elif operator == '>':
            return state_value > value
        elif operator == '<=':
            return state_value <= value
        elif operator == '>=':
            return state_value >= value
        elif operator == 'in':
            return state_value in value
        elif operator == 'not_in':
            return state_value not in value
        elif operator == 'changed':
            # For future use (detect when value changes)
            return True
        else:
            return True

    def evaluate(self, parsed: ParsedMessage) -> bool:
        """Evaluate triggers for a parsed message line.

        Args:
            parsed: ParsedMessage from MUD

        Returns:
            True if line should be gagged (hidden), False otherwise
        """
        should_gag = False
        visited_triggers = set()  # Track triggers in this evaluation to prevent loops

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

            # Trigger matched, mark as visited and execute actions
            visited_triggers.add(trigger.id)
            for action in trigger.actions:
                self._execute_action(action, visited_triggers, depth=0)

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
        self._execute_action(action, set(), depth=0)

    def _execute_action(self, action: TriggerAction, visited_triggers: set = None, depth: int = 0):
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

        elif action.action_type == ActionType.STORAGE:
            # Store/update character state
            if self.character_state and action.value:
                self._handle_storage_action(action)

        elif action.action_type == ActionType.EXECUTE_TRIGGER:
            # Execute another trigger by ID
            if action.value:
                if visited_triggers is None:
                    visited_triggers = set()
                self._execute_trigger(action.value, visited_triggers, depth)

        elif action.action_type == ActionType.GAG:
            # Gag is handled by evaluate() return value
            pass

    def _handle_storage_action(self, action: TriggerAction):
        """Handle storage action (update character state).

        Examples:
        - value="buffs", operation="add", data="Fuerza" → add "Fuerza" to buffs list
        - value="debuffs", operation="remove", data="Veneno" → remove "Veneno" from debuffs
        - value="in_combat", operation="set", data="true" → set in_combat to True
        - value="hp_threshold_flags", operation="update" → mark current HP threshold as announced
        """
        if not action.value:
            return

        field = action.value
        operation = action.operation or "set"
        data = action.data

        # Handle list operations (buffs, debuffs, state_history)
        if field in ["buffs", "debuffs", "state_history"]:
            field_list = getattr(self.character_state, field, None)
            if not isinstance(field_list, list):
                return

            if operation == "add":
                # Interpolate data if needed
                item = self._interpolate_text(data) if data else ""
                if item and item not in field_list:
                    field_list.append(item)
            elif operation == "remove":
                item = self._interpolate_text(data) if data else ""
                if item and item in field_list:
                    field_list.remove(item)
            elif operation == "clear":
                field_list.clear()

        # Handle dict operations (hp_threshold_flags)
        elif field == "hp_threshold_flags":
            if operation == "update":
                # Mark current HP threshold as announced
                threshold = self.character_state.get_hp_threshold()
                if threshold:
                    self.character_state.hp_threshold_flags[threshold] = True

        # Handle scalar fields
        elif hasattr(self.character_state, field):
            if operation == "set":
                # Try to parse data as appropriate type
                try:
                    if isinstance(getattr(self.character_state, field), bool):
                        setattr(self.character_state, field, data.lower() in ["true", "1", "yes"])
                    elif isinstance(getattr(self.character_state, field), int):
                        setattr(self.character_state, field, int(data))
                    else:
                        setattr(self.character_state, field, data)
                except (ValueError, AttributeError):
                    pass

    def _execute_trigger(self, trigger_id: str, visited_triggers: set = None, depth: int = 0):
        """Execute another trigger by ID.

        Args:
            trigger_id: ID of trigger to execute
            visited_triggers: Set of trigger IDs already visited (for loop prevention)
            depth: Current chain depth (for loop prevention)
        """
        # Initialize visited_triggers if not provided
        if visited_triggers is None:
            visited_triggers = set()

        # Check for loops: already visited or max depth exceeded
        if trigger_id in visited_triggers or depth >= self.MAX_CHAIN_DEPTH:
            return  # Stop the chain to prevent infinite loops

        # Find and execute the trigger
        for trigger in self.triggers:
            if trigger.id == trigger_id and trigger.enabled:
                # Mark as visited and execute all actions
                visited_triggers.add(trigger_id)
                for action in trigger.actions:
                    self._execute_action(action, visited_triggers, depth + 1)
                break

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
                    "value": a.get("value", ""),
                    "operation": a.get("operation", ""),
                    "data": a.get("data", "")
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
                    "value": a.get("value", ""),
                    "operation": a.get("operation", ""),
                    "data": a.get("data", "")
                }
                for a in timer["actions"]
            ]

        try:
            with open(self.SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save triggers: {e}")

    def load(self):
        """Load triggers, aliases, timers from JSON file."""
        if not self.SAVE_PATH.exists():
            return

        try:
            with open(self.SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load triggers
            for t in data.get("triggers", []):
                actions = [
                    TriggerAction(
                        action_type=ActionType(a["action_type"]),
                        value=a.get("value", ""),
                        operation=a.get("operation", ""),
                        data=a.get("data", "")
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
                        value=a.get("value", ""),
                        operation=a.get("operation", ""),
                        data=a.get("data", "")
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
